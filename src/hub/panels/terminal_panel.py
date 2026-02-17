import asyncio
import os
import shlex
from typing import Optional

from textual import on, work
from textual.app import ComposeResult
from textual.widgets import Input, RichLog, Static


class TerminalPanel(Static):
    """
    A simple terminal panel that runs shell commands and supports interactive processes.
    """

    DEFAULT_CSS = """
    TerminalPanel {
        height: 100%;
        width: 100%;
        background: $surface;
        border: solid grey;
        layout: vertical;
    }
    
    TerminalPanel:focus-within {
        border: solid white;
    }
    
    RichLog {
        height: 1fr;
        border-top: solid grey;
        overflow-y: scroll;
        background: $surface-darken-1;
        scrollbar-size: 1 1;
    }

    Input {
        dock: bottom;
        margin: 0;
        border: none;
        padding: 0 1;
    }
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.process: Optional[asyncio.subprocess.Process] = None
        # Start in current working directory
        self.cwd = os.getcwd()
        self.history = []
        self.history_index = -1
        self.can_focus = True

    def on_focus(self) -> None:
        """When the panel gets focus, transfer it to the input."""
        self.query_one("#cmd-input", Input).focus()

    def on_click(self) -> None:
        """When the panel is clicked, focus the input."""
        self.query_one("#cmd-input", Input).focus()

    def compose(self) -> ComposeResult:
        log = RichLog(id="terminal-log", wrap=True, highlight=True, markup=True)
        log.can_focus = False  # Prevent log from stealing focus on click
        yield log
        yield Input(
            placeholder="Type a command...",
            id="cmd-input",
        )

    def on_mount(self) -> None:
        self.write_log(f"[bold blue]Welcome to the Terminal Panel![/]")
        self.write_log(f"[dim]Current directory: {self.cwd}[/]")
        self.write_log(
            "[dim]Type 'exit' to clear history or 'cd <path>' to change directory.[/]"
        )
        self.focus_input()

    def focus_input(self) -> None:
        self.query_one("#cmd-input", Input).focus()

    @on(Input.Submitted, "#cmd-input")
    async def on_command_submit(self, event: Input.Submitted) -> None:
        command = event.value
        # If we have a running process, send input to it
        if self.process and self.process.returncode is None:
            # Echo input to local terminal
            self.write_log(f"{command}")

            if self.process.stdin:
                try:
                    # Write input + newline to process stdin
                    self.process.stdin.write(f"{command}\n".encode("utf-8"))
                    await self.process.stdin.drain()
                except Exception as e:
                    self.write_log(f"[red]Error writing to process: {e}[/]")

            event.input.value = ""
            return

        # No running process - treat as shell command
        command = command.strip()
        if not command:
            return

        # Add to history
        self.history.append(command)
        self.history_index = len(self.history)

        # Display command in log with prompt style
        prompt = f"[bold green]{os.path.basename(self.cwd) or '/'} $[/]"
        self.write_log(f"{prompt} {command}")

        event.input.value = ""  # Clear input

        # Handle built-in commands
        if command == "exit":
            self.query_one("#terminal-log", RichLog).clear()
            return

        if command.startswith("cd "):
            try:
                parts = shlex.split(command)
                if len(parts) > 1:
                    new_dir = os.path.expanduser(parts[1])
                    # Handle relative paths
                    if not os.path.isabs(new_dir):
                        new_dir = os.path.join(self.cwd, new_dir)

                    # Normalize path
                    new_dir = os.path.normpath(new_dir)

                    if os.path.isdir(new_dir):
                        self.cwd = new_dir
                    else:
                        self.write_log(
                            f"[red]cd: no such file or directory: {parts[1]}[/]"
                        )
                else:
                    # cd without args goes to home
                    self.cwd = os.path.expanduser("~")
            except Exception as e:
                self.write_log(f"[red]Error changing directory: {e}[/]")
            return

        # Run external command
        self.run_command(command)

    @work(exclusive=True)
    async def run_command(self, command: str) -> None:
        try:
            # Prepare environment
            env = os.environ.copy()
            # Ensure unbuffered output for Python scripts
            env["PYTHONUNBUFFERED"] = "1"

            # Start the subprocess with pipes for all streams
            # using create_subprocess_shell allows us to run 'command' as typed
            self.process = await asyncio.create_subprocess_shell(
                command,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=self.cwd,
                env=env,
            )

            # Read stdout and stderr concurrently
            tasks = []
            if self.process.stdout:
                tasks.append(
                    asyncio.create_task(
                        self._read_stream(self.process.stdout, "stdout")
                    )
                )
            if self.process.stderr:
                tasks.append(
                    asyncio.create_task(
                        self._read_stream(self.process.stderr, "stderr")
                    )
                )

            # Wait for process to finish
            await self.process.wait()

            # Ensure all output is read
            if tasks:
                await asyncio.gather(*tasks)

            if self.process.returncode != 0:
                self.write_log(f"[bold red]Exit code: {self.process.returncode}[/]")

        except Exception as e:
            self.write_log(f"[red]Error executing command: {e}[/]")
        finally:
            self.process = None

    async def _read_stream(
        self, stream: asyncio.StreamReader, stream_name: str
    ) -> None:
        while True:
            try:
                # Read line by line for smoother output updates
                line = await stream.readline()
                if not line:
                    break

                decoded_line = line.decode("utf-8", errors="replace").rstrip()
                if decoded_line:
                    style = "" if stream_name == "stdout" else "[red]"
                    end_style = "" if stream_name == "stdout" else "[/]"
                    self.write_log(f"{style}{decoded_line}{end_style}")
            except Exception:
                break

    def write_log(self, message: str) -> None:
        log = self.query_one("#terminal-log", RichLog)
        log.write(message)
