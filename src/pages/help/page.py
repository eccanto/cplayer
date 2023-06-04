from pathlib import Path

from textual.app import ComposeResult
from textual.widgets import MarkdownViewer

from src.pages.base.page import PageBase


class HelpPage(PageBase):
    DEFAULT_CSS = Path(__file__).parent.joinpath('styles.css').read_text()

    _CONTENT = Path('./documentation/help.md').read_text()

    def compose(self) -> ComposeResult:
        yield MarkdownViewer(self._CONTENT, show_table_of_contents=True)

    def focus(self) -> None:
        viewer = self.query_one(MarkdownViewer)
        viewer.focus()
