from pathlib import Path
from typing import Callable, List, Union, cast

from textual._node_list import NodeList
from textual.app import ComposeResult
from textual.containers import Middle
from textual.widget import Widget
from textual.widgets import Label, ListItem, ListView

from src.components.hidden_widget import WidgetHidden


class CustomListView(ListView):
    BINDINGS = [
        ('escape', 'quit', 'Quit'),
        ('enter', 'select_option', 'Select Option'),
    ]

    def __init__(
        self,
        on_quit: Callable[[Widget], None],
        on_select: Callable[[Union[Path, str]], None],
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
            self._on_select(cast(WidgetOption, self.highlighted_child).data)


class WidgetOption(ListItem):
    def __init__(self, data: Union[Path, str], prefix: str, *args, **kwargs) -> None:
        super().__init__(
            Label(
                f'{prefix} {data.name if isinstance(data, Path) else data}'
                if prefix
                else (data.name if isinstance(data, Path) else data)
            ),
            *args,
            **kwargs,
        )

        self.data = data


class WidgetOptionsList(WidgetHidden):
    DEFAULT_CSS = Path(__file__).parent.joinpath('styles.css').read_text(encoding='UTF-8')

    def __init__(
        self,
        label: str,
        on_quit: Callable[[Widget], None],
        on_select: Callable[[Union[Path, str]], None],
        *children,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)

        self._label = label
        self._on_quit = on_quit
        self._on_select = on_select

        self.label = Label(self._label, classes='bold')
        self.list_view = CustomListView(self._on_quit, self._on_select, *children)

    def compose(self) -> ComposeResult:
        with Middle():
            yield self.label
            yield self.list_view

    def focus(self, scroll_visible: bool = True) -> None:
        self.list_view.focus(scroll_visible)
