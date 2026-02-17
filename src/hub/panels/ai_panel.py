import asyncio
import os
import shlex
from typing import Optional

from textual import on, work
from textual.app import App, ComposeResult
from textual.containers import Container, Vertical, Horizontal
from textual.message import Message
from textual.reactive import reactive
from textual.widgets import Input, RichLog, Label, Static


class AIPanel(Static):
    """
    A panel that runs AI CLI commands and displays their output.
    """

    DEFAULT_CSS = """
    AIPanel {
        height: 100%;
        width: 100%;
        background: $surface;
        border: solid $accent;
        layout: vertical;
    }
    
    AIPanel:focus-within {
        border: double $primary;
    }
    
    .header {
        dock: top;
        text-align: center;
        text-style: bold;
        padding: 1;
        background: $primary;
        color: $text;
        width: 100%;
    }
    
    Input {
        dock: top;
        margin: 1;
    }
    
    RichLog {
        height: 1fr;
        border: solid $secondary;
        overflow-y: scroll;
        background: $surface-darken-1;
    }
    """

    current_ai = reactive("None")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.process: Optional[asyncio.subprocess.Process] = None
        self.can_focus = True

    def compose(self) -> ComposeResult:
        yield Label("AI: None", id="header", classes="header")
        yield Input(
            placeholder="Type AI CLI name (claude, gemini, opencode) and press Enter...",
            id="cmd-input",
        )
        yield RichLog(id="output-log", wrap=True, highlight=True, markup=True)

    def watch_current_ai(self, value: str) -> None:
        try:
            self.query_one("#header", Label).update(f"AI: {value}")
        except:
            pass

    @on(Input.Submitted, "#cmd-input")
    async def on_command_submit(self, event: Input.Submitted) -> None:
        command = event.value.strip()
        if not command:
            return

        # Only allow specific commands for safety/scope as requested
        if command not in ["claude", "gemini", "opencode"]:
            self.write_log(
                f"[red]Error: Unsupported command '{command}'. Supported: claude, gemini, opencode[/]"
            )
            event.input.value = ""
            return

        # Update reactive var first
        self.current_ai = command
        event.input.value = ""  # Clear input
        self.query_one("#output-log", RichLog).clear()
        self.write_log(f"[green]Starting {command}...[/]")

        # Stop existing process if running
        if self.process and self.process.returncode is None:
            try:
                self.process.terminate()
                await self.process.wait()
                self.write_log("[yellow]Terminated previous process.[/]")
            except Exception as e:
                self.write_log(f"[red]Error terminating process: {e}[/]")

        # Run the command
        self.run_command(command)

    @work(exclusive=True)
    async def run_command(self, command: str) -> None:
        try:
            # Using shlex to split correctly if arguments were allowed, though we are restricting to single words currently
            args = shlex.split(command)

            # Start the subprocess
            self.process = await asyncio.create_subprocess_exec(
                args[0],
                *args[1:],
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env=os.environ.copy(),
            )

            # Read stdout and stderr concurrently
            if self.process.stdout:
                stdout_task = asyncio.create_task(
                    self._read_stream(self.process.stdout, "stdout")
                )
            if self.process.stderr:
                stderr_task = asyncio.create_task(
                    self._read_stream(self.process.stderr, "stderr")
                )

            await self.process.wait()

            self.write_log(
                f"[bold]Process finished with code {self.process.returncode}[/]"
            )
            self.current_ai = "None"

        except FileNotFoundError:
            self.write_log(
                f"[red]Error: Command '{command}' not found. Please ensure it is installed and in your PATH.[/]"
            )
            self.current_ai = "None"
        except Exception as e:
            self.write_log(f"[red]Error starting process: {e}[/]")
            self.current_ai = "None"

    async def _read_stream(
        self, stream: asyncio.StreamReader, stream_name: str
    ) -> None:
        while True:
            line = await stream.readline()
            if not line:
                break
            try:
                decoded_line = line.decode("utf-8").strip()
                if decoded_line:
                    style = "" if stream_name == "stdout" else "[red]"
                    end_style = "" if stream_name == "stdout" else "[/]"
                    self.write_log(f"{style}{decoded_line}{end_style}")
            except UnicodeDecodeError:
                self.write_log(f"[dim]<{stream_name}: binary data>[/]")

    def write_log(self, message: str) -> None:
        log = self.query_one("#output-log", RichLog)
        log.write(message)
