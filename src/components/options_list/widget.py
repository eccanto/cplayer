from pathlib import Path
from typing import Callable, List, cast
from textual.app import ComposeResult
from textual.containers import Middle
from textual.widget import Widget
from textual.widgets import Label, ListItem, ListView
from textual._node_list import NodeList

from src.components.hidden_widget.widget import WidgetHidden


class CustomListView(ListView):
    BINDINGS = [
        ('escape', 'quit', 'Quit'),
        ('enter', 'select_option', 'Select Option'),
    ]

    def __init__(
        self,
        on_quit: Callable[[Widget], None],
        on_select: Callable[[Path], None],
        *children,
    ) -> None:
        super().__init__(*children)

        self._on_quit = on_quit
        self._on_select = on_select

    def clean(self) -> None:
        self._nodes = NodeList()

    def add(self, items: List['WidgetOption']) -> None:
        self._add_children(*items)

    def update(self, options: List['WidgetOption']) -> None:
        self._nodes = NodeList()

        for option in options:
            option.highlighted = False
            self._add_child(option)

        self.index = 0

    def action_select_option(self):
        if self.highlighted_child:
            self._on_select(cast(WidgetOption, self.highlighted_child).path)


class WidgetOption(ListItem):
    def __init__(self, path: Path, prefix: str, *args, **kwargs) -> None:
        super().__init__(Label(f'{prefix} {path.name}' if prefix else path.name), *args, **kwargs)

        self.path = path


class WidgetOptionsList(WidgetHidden):
    DEFAULT_CSS = Path(__file__).parent.joinpath('styles.css').read_text()

    def __init__(
        self,
        label: str,
        on_quit: Callable[[Widget], None],
        on_select: Callable[[Path], None],
        *children,
    ) -> None:
        super().__init__()

        self._label = label
        self._on_quit = on_quit
        self._on_select = on_select

        self.label = Label(self._label, classes='bold')
        self.list_view = CustomListView(self._on_quit, self._on_select, *children)

    def compose(self) -> ComposeResult:
        with Middle():
            yield self.label
            yield self.list_view

    def focus(self):
        self.list_view.focus()
