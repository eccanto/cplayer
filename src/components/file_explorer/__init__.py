import logging
from pathlib import Path
from typing import Callable, Iterable

from textual.binding import Binding
from textual.widgets import DirectoryTree

from src.components.hidden_widget import HiddenWidget


class FileExplorerWidget(DirectoryTree, HiddenWidget):  # pylint: disable=too-many-ancestors
    """File explorer widget."""

    DEFAULT_CSS = Path(__file__).parent.joinpath('styles.css').read_text(encoding='UTF-8')

    BINDINGS = [
        Binding('enter', 'select', 'Select', show=True),
        Binding('right', 'open', 'Open', show=True),
    ]

    def __init__(self, path: Path, on_select: Callable[[Path], None], **kwargs) -> None:
        """Initializes the Widget object.

        :param on_select: A function to be called when a file or directory is selected.
        :param *args: Variable length argument list.
        :param **kwargs: Arbitrary keyword arguments.
        """
        super().__init__(path=path, **kwargs)

        self.on_select = on_select

    def filter_paths(self, paths: Iterable[Path]) -> Iterable[Path]:
        """Filters the provided iterable of paths based on some criteria.

        :param paths: An iterable of paths to be filtered.

        :returns: An iterable of filtered paths.
        """
        return [
            path for path in paths if (not path.name.startswith('.')) and (path.is_dir() or path.name.endswith('.mp3'))
        ]

    def action_open(self) -> None:
        """Selects the selected cursor."""
        super().action_select_cursor()

    def action_select(self) -> None:
        """Runs the `self.on_select` callback with the selected path."""
        line = self._tree_lines[self.cursor_line]
        node = line.path[-1]

        if node.data:
            self.on_select(node.data.path)
        else:
            logging.warning('node.data is None: %s', node)

        self.hide()
