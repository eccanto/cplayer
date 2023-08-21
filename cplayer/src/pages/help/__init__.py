from pathlib import Path
from typing import Self

from textual.app import ComposeResult
from textual.widgets import MarkdownViewer

from cplayer.src.pages.base import PageBase


class HelpPage(PageBase):
    """HelpPage Class that represents the help page in the application."""

    DEFAULT_CSS = Path(__file__).parent.joinpath('styles.css').read_text(encoding='UTF-8')

    _CONTENT = Path(__file__).parent.parent.parent.parent.joinpath('documentation/help.md').read_text(encoding='UTF-8')

    def compose(self) -> ComposeResult:
        """Composes the layout for the Page.

        :yields: Widget displaying the help content.
        """
        yield MarkdownViewer(self._CONTENT, show_table_of_contents=True)

    def focus(self, scroll_visible: bool = True) -> Self:
        """Focus on the MarkdownViewer widget.

        :param scroll_visible: Whether to make the scroll visible when focusing.
        """
        viewer = self.query_one(MarkdownViewer)
        viewer.focus(scroll_visible)
        return self
