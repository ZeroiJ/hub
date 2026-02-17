import os
from pathlib import Path

from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal
from textual.widgets import Label

from hub.panels.git_panel import GitPanel


class HubApp(App):
    CSS = """
    Horizontal {
        height: 100%;
    }
    #left-panel {
        width: 25%;
        border: solid green;
        height: 100%;
    }
    #middle-panel {
        width: 40%;
        border: solid blue;
        height: 100%;
    }
    #right-panel {
        width: 35%;
        border: solid red;
        height: 100%;
    }
    """

    BINDINGS = [
        ("t", "toggle_git_folder", "Toggle Git/Folder"),
    ]

    def compose(self) -> ComposeResult:
        with Horizontal():
            # Use GitPanel in the left panel
            yield Container(GitPanel(Path(os.getcwd())), id="left-panel")
            yield Container(Label("Middle Panel (40%)"), id="middle-panel")
            yield Container(Label("Right Panel (35%)"), id="right-panel")

    def action_toggle_git_folder(self) -> None:
        git_panel = self.query_one(GitPanel)
        git_panel.action_toggle_view()


def main():
    app = HubApp()
    app.run()


if __name__ == "__main__":
    main()
