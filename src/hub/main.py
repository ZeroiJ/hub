import os
from pathlib import Path

from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal
from textual.widgets import Label

from hub.panels.git_panel import GitPanel
from hub.panels.terminal_panel import TerminalPanel


class HubApp(App):
    CSS = """
    Horizontal {
        height: 100%;
    }
    
    #left-panel { width: 30%; height: 100%; }
    #right-panel { width: 70%; height: 100%; }
    
    /* Remove borders from the container wrappers so we only have one border per panel */
    #left-panel, #right-panel {
        border: none;
        padding: 0;
        margin: 0;
    }
    """

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("ctrl+h", "focus_left", "Focus Left"),
        ("ctrl+l", "focus_right", "Focus Right"),
        ("f1", "focus_left", "Focus Left"),
        ("f2", "focus_right", "Focus Right"),
        ("t", "toggle_git_folder", "Toggle Git/Folder"),
    ]

    def compose(self) -> ComposeResult:
        with Horizontal():
            # Use GitPanel in the left panel and TerminalPanel in the right
            yield Container(GitPanel(Path(os.getcwd()), id="git-view"), id="left-panel")
            yield Container(TerminalPanel(id="terminal-view"), id="right-panel")

    def on_mount(self) -> None:
        self.query_one("#git-view").focus()

    def action_focus_left(self) -> None:
        self.query_one("#git-view").focus()

    def action_focus_right(self) -> None:
        # Focus the input inside the Terminal panel
        terminal_panel = self.query_one(TerminalPanel)
        terminal_panel.query_one("Input").focus()

    def action_toggle_git_folder(self) -> None:
        try:
            # Only toggle if left panel is focused or we explicitly want to
            git_panel = self.query_one(GitPanel)
            git_panel.action_toggle_view()
        except:
            pass


def main():
    app = HubApp()
    app.run()


if __name__ == "__main__":
    main()
