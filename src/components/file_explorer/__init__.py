import logging
from pathlib import Path
from typing import Callable, Iterable

from textual.binding import Binding
from textual.widgets import DirectoryTree

from src.components.hidden_widget import WidgetHidden


class FileExplorer(DirectoryTree, WidgetHidden):  # pylint: disable=too-many-ancestors
    DEFAULT_CSS = Path(__file__).parent.joinpath('styles.css').read_text(encoding='UTF-8')

    BINDINGS = [
        Binding('enter', 'select', 'Select', show=True),
        Binding('right', 'open', 'Open', show=True),
    ]

    def __init__(self, on_select: Callable[[Path], None], *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.on_select = on_select

    def filter_paths(self, paths: Iterable[Path]) -> Iterable[Path]:
        return [
            path for path in paths if (not path.name.startswith('.')) and (path.is_dir() or path.name.endswith('.mp3'))
        ]

    def action_open(self) -> None:
        super().action_select_cursor()

    def action_select(self) -> None:
        line = self._tree_lines[self.cursor_line]
        node = line.path[-1]

        if node.data:
            self.on_select(node.data.path)
        else:
            logging.warning('node.data is None: %s', node)

        self.hide()
