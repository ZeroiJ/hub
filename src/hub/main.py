import os
from pathlib import Path

from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal
from textual.widgets import Label

from hub.panels.git_panel import GitPanel
from hub.panels.shell_panel import ShellPanel


class HubApp(App):
    CSS = """
    Horizontal {
        height: 100%;
    }
    
    /* Default panel styling */
    #left-panel, #middle-panel, #right-panel {
        height: 100%;
        border: solid $accent;
    }

    #left-panel { width: 25%; }
    #middle-panel { width: 40%; }
    #right-panel { width: 35%; }

    /* Focus styling */
    GitPanel:focus, ShellPanel:focus, #middle-panel:focus-within {
        border: double $primary;
    }
    """

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("ctrl+h", "focus_left", "Focus Left"),
        ("ctrl+l", "focus_middle", "Focus Middle"),
        ("ctrl+right", "focus_right", "Focus Right"),
        ("ctrl+;", "focus_right", "Focus Right"),
        ("f1", "focus_left", "Focus Left"),
        ("f2", "focus_middle", "Focus Middle"),
        ("f3", "focus_right", "Focus Right"),
        ("t", "toggle_git_folder", "Toggle Git/Folder"),
    ]

    def compose(self) -> ComposeResult:
        with Horizontal():
            # Use GitPanel in the left panel
            # Give panels IDs so we can target them
            # The widgets inside are what gets focus
            yield Container(GitPanel(Path(os.getcwd()), id="git-view"), id="left-panel")
            yield Container(Label("Middle Panel (40%)"), id="middle-panel")
            yield Container(ShellPanel(id="shell-view"), id="right-panel")

    def on_mount(self) -> None:
        self.query_one("#git-view").focus()

    def action_focus_left(self) -> None:
        self.query_one("#git-view").focus()

    def action_focus_middle(self) -> None:
        # Placeholder focus for middle panel
        self.query_one("#middle-panel").focus()

    def action_focus_right(self) -> None:
        self.query_one("#shell-view").focus()

    def action_toggle_git_folder(self) -> None:
        git_panel = self.query_one(GitPanel)
        git_panel.action_toggle_view()


def main():
    app = HubApp()
    app.run()


if __name__ == "__main__":
    main()
