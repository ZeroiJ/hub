from pathlib import Path
from typing import Optional

from git import Repo, InvalidGitRepositoryError
from textual.app import ComposeResult
from textual.containers import Vertical
from textual.reactive import reactive
from textual.widgets import Static, Label, ListItem, ListView


class GitPanel(Static):
    """
    A panel that displays Git status or a folder browser.

    Attributes:
        repo_path (Path): The path to the git repository.
        mode (str): Current mode, either "git" or "folder".
    """

    DEFAULT_CSS = """
    GitPanel {
        height: 100%;
        background: $surface;
    }
    
    .header {
        text-align: center;
        text-style: bold;
        padding: 1;
        background: $primary;
        color: $text;
    }

    .section-title {
        color: $text-muted;
        padding-top: 1;
        padding-left: 1;
    }

    .status-item {
        padding-left: 2;
    }

    .mode-indicator {
        dock: bottom;
        text-align: center;
        background: $accent;
        color: $text;
    }
    """

    mode = reactive("git")

    def __init__(self, repo_path: Path, **kwargs):
        super().__init__(**kwargs)
        self.repo_path = repo_path
        self.repo: Optional[Repo] = None
        self.can_focus = True
        try:
            self.repo = Repo(str(repo_path))
        except InvalidGitRepositoryError:
            self.repo = None

    def compose(self) -> ComposeResult:
        yield Label("", id="header", classes="header")
        yield Vertical(id="content")
        yield Label("Press 't' to toggle view", classes="mode-indicator")

    def on_mount(self) -> None:
        self.update_view()

    def watch_mode(self, mode: str) -> None:
        self.update_view()

    def update_view(self) -> None:
        header = self.query_one("#header", Label)
        content = self.query_one("#content", Vertical)

        # Clear existing content
        content.remove_children()

        if self.mode == "git":
            self._render_git_status(header, content)
        else:
            self._render_folder_browser(header, content)

    def _render_git_status(self, header: Label, content: Vertical) -> None:
        if not self.repo:
            header.update("Git Status")
            content.mount(Label("Not a git repository", classes="status-item"))
            return

        try:
            # Get current branch
            try:
                branch_name = self.repo.active_branch.name
            except TypeError:
                branch_name = "DETACHED HEAD"

            # Get changes
            changed_files = [item.a_path for item in self.repo.index.diff(None)]
            staged_files = [item.a_path for item in self.repo.index.diff("HEAD")]
            untracked_files = self.repo.untracked_files

            total_changes = (
                len(changed_files) + len(staged_files) + len(untracked_files)
            )

            header.update(f"Git: {branch_name} ({total_changes})")

            if total_changes == 0:
                content.mount(Label("No changes", classes="status-item"))
                return

            if staged_files:
                content.mount(Label("Staged:", classes="section-title"))
                for file in staged_files:
                    content.mount(Label(f"A {file}", classes="status-item"))

            if changed_files:
                content.mount(Label("Modified:", classes="section-title"))
                for file in changed_files:
                    content.mount(Label(f"M {file}", classes="status-item"))

            if untracked_files:
                content.mount(Label("Untracked:", classes="section-title"))
                for file in untracked_files:
                    content.mount(Label(f"? {file}", classes="status-item"))

        except Exception as e:
            header.update("Git Status (Error)")
            content.mount(Label(str(e), classes="status-item"))

    def _render_folder_browser(self, header: Label, content: Vertical) -> None:
        header.update("Folder Browser")
        content.mount(Label("Folder Browser - Coming soon", classes="status-item"))

    def action_toggle_view(self) -> None:
        self.mode = "folder" if self.mode == "git" else "git"
