import logging
from collections.abc import Callable, Iterable
from pathlib import Path
from typing import ClassVar

from textual.binding import Binding, BindingType
from textual.widget import Widget
from textual.widgets import DirectoryTree

from cplayer.src.components.hidden_widget import HiddenWidget


class FileExplorerWidget(DirectoryTree, HiddenWidget):  # pylint: disable=too-many-ancestors
    """File explorer widget."""

    DEFAULT_CSS = Path(__file__).parent.joinpath('styles.css').read_text(encoding='UTF-8')

    BINDINGS: ClassVar[list[BindingType]] = [
        Binding('enter', 'select', 'Select', show=True),
        Binding('right', 'open', 'Open', show=True),
    ]

    def __init__(  # noqa: PLR0913
        self,
        *children: Widget,
        path: str | Path,
        on_select: Callable[[Path], None],
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
        start_hidden: bool = True,
    ) -> None:
        """Initializes the Widget object.

        :param on_select: A function to be called when a file or directory is selected.
        :param *args: Variable length argument list.
        :param **kwargs: Arbitrary keyword arguments.
        """
        DirectoryTree.__init__(self, path=path, name=name, id=id, classes=classes, disabled=disabled)
        HiddenWidget.__init__(
            self, *children, name=name, id=id, classes=classes, disabled=disabled, start_hidden=start_hidden
        )

        self.default_path = path
        self.on_select = on_select

    def on_mount(self) -> None:
        """Handles events on the mounting of the file explorer."""
        super().on_mount()

        self.path = self.default_path

    def filter_paths(self, paths: Iterable[Path]) -> Iterable[Path]:
        """Filters the provided iterable of paths based on some criteria.

        :param paths: An iterable of paths to be filtered.

        :returns: An iterable of filtered paths.
        """
        return [
            path for path in paths
            if (not path.name.startswith('.')) and (path.is_dir() or path.suffix in ('.mp3', '.wav'))
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
