import asyncio
import os
import pty
import select
import shlex
import struct
import fcntl
import termios
import tty
from typing import Optional, Dict

import pyte
from textual import events
from textual.app import ComposeResult
from textual.containers import Container
from textual.message import Message
from textual.reactive import reactive
from textual.widgets import Static


class ShellPanel(Static):
    """
    A terminal emulator widget using pyte and pty.
    """

    DEFAULT_CSS = """
    ShellPanel {
        height: 100%;
        background: $surface;
        border: solid $accent;
        overflow: hidden;
    }
    
    ShellPanel:focus {
        border: double $accent;
    }
    """

    # Extended key mapping for better shell experience
    KEY_MAPPING: Dict[str, bytes] = {
        "enter": b"\r",
        "return": b"\r",
        "tab": b"\t",
        "backspace": b"\x7f",
        "space": b" ",
        "left": b"\x1b[D",
        "right": b"\x1b[C",
        "up": b"\x1b[A",
        "down": b"\x1b[B",
        "home": b"\x1b[H",
        "end": b"\x1b[F",
        "pageup": b"\x1b[5~",
        "pagedown": b"\x1b[6~",
        "delete": b"\x1b[3~",
        "escape": b"\x1b",
    }

    # Add control keys programmatically to avoid huge dict
    for char_code in range(1, 27):
        char = chr(char_code + 96)  # a-z
        KEY_MAPPING[f"ctrl+{char}"] = bytes([char_code])

    class OutputReady(Message):
        """Emitted when there is new output from the shell."""

        pass

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._master_fd: Optional[int] = None
        self._pid: Optional[int] = None
        self._emulator: Optional[pyte.Screen] = None
        self._stream: Optional[pyte.ByteStream] = None
        self._read_task: Optional[asyncio.Task] = None
        self.can_focus = True

        # Determine shell to run
        self.shell_cmd = os.environ.get("SHELL", "/bin/bash")

    def on_mount(self) -> None:
        """Initialize the PTY and start the shell."""
        # Use call_after_refresh to ensure we have size
        self.call_after_refresh(self._start_shell)

    def _start_shell(self) -> None:
        """Fork a PTY and start the shell process."""
        cols, rows = self.size.width, self.size.height
        if cols <= 0:
            cols = 80
        if rows <= 0:
            rows = 24

        self._emulator = pyte.Screen(cols, rows)
        self._stream = pyte.ByteStream(self._emulator)

        # Fork the PTY
        self._pid, self._master_fd = pty.fork()

        if self._pid == 0:  # Child process
            # Set terminal size
            winsize = struct.pack("HHHH", rows, cols, 0, 0)
            # fcntl.ioctl(0, termios.TIOCSWINSZ, winsize) # stdin is 0

            # Execute the shell
            env = os.environ.copy()
            env["TERM"] = "linux"  # Basic TERM type
            env["COLUMNS"] = str(cols)
            env["LINES"] = str(rows)
            try:
                os.execlp(self.shell_cmd, self.shell_cmd)
            except OSError:
                os._exit(1)
        else:  # Parent process
            # Create task to read from PTY
            self._read_task = asyncio.create_task(self._read_loop())
            self.refresh()

    def on_resize(self, event: events.Resize) -> None:
        cols, rows = event.size.width, event.size.height
        if cols <= 0 or rows <= 0:
            return

        if self._emulator:
            self._emulator.resize(lines=rows, columns=cols)

        if self._master_fd is not None:
            try:
                winsize = struct.pack("HHHH", rows, cols, 0, 0)
                fcntl.ioctl(self._master_fd, termios.TIOCSWINSZ, winsize)
            except OSError:
                pass
        self.refresh()

    async def _read_loop(self) -> None:
        """Read output from the PTY and feed it to pyte."""
        loop = asyncio.get_running_loop()

        while True:
            if self._master_fd is None:
                break

            try:
                # Use loop.run_in_executor to read without blocking
                data = await loop.run_in_executor(None, os.read, self._master_fd, 1024)

                if not data:
                    break  # EOF

                # Feed data to pyte
                if self._stream:
                    try:
                        self._stream.feed(data.decode("utf-8", errors="replace"))
                    except Exception:
                        pass  # Ignore decoding errors

                # Trigger a refresh
                self.post_message(self.OutputReady())

            except OSError:
                break  # PTY closed
            except Exception:
                break

    def on_shell_panel_output_ready(self, message: OutputReady) -> None:
        """Handle new output by refreshing the widget."""
        self.refresh()

    def render(self) -> str:
        """Render the screen content."""
        if not self._emulator:
            return "Starting shell..."

        # pyte.Screen.display returns a list of strings (lines)
        return "\n".join(self._emulator.display)

    async def on_key(self, event: events.Key) -> None:
        """Handle key presses and send them to the PTY."""
        if self._master_fd is None:
            return

        # IMPORTANT: Stop propagation so other widgets don't handle this key
        event.stop()
        event.prevent_default()

        char = event.character
        key = event.key

        data = b""

        if key in self.KEY_MAPPING:
            data = self.KEY_MAPPING[key]
        elif char:
            data = char.encode("utf-8")
        elif (
            key.isprintable()
        ):  # Fallback for keys that Textual might not treat as char
            data = key.encode("utf-8")

        if data:
            try:
                os.write(self._master_fd, data)
            except OSError:
                pass  # PTY closed

    def on_unmount(self) -> None:
        """Clean up the PTY and process."""
        if self._read_task:
            self._read_task.cancel()

        if self._master_fd is not None:
            try:
                os.close(self._master_fd)
            except OSError:
                pass
            self._master_fd = None

        if self._pid is not None:
            try:
                # Send SIGHUP to the shell group
                os.kill(self._pid, 9)
                os.waitpid(self._pid, 0)
            except OSError:
                pass
            self._pid = None
