from pathlib import Path
from typing import Callable, Coroutine

from textual.app import ComposeResult
from textual.containers import Center
from textual.widgets import Input, Label

from src.components.hidden_widget import WidgetHidden


class WidgetInputLabel(WidgetHidden):
    """An input with a label."""

    BINDINGS = [
        ('escape', 'quit', 'Quit'),
    ]

    DEFAULT_CSS = Path(__file__).parent.joinpath('styles.css').read_text(encoding='UTF-8')

    def __init__(
        self,
        input_label: str,
        on_enter: Callable[[], Coroutine[None, None, None]],
        on_quit: Callable[['WidgetInputLabel'], None],
        *args,
        **kwargs,
    ) -> None:
        super().__init__(*args, **kwargs)

        self.input_label = input_label

        self.on_enter = on_enter
        self.on_quit = on_quit

    def compose(self) -> ComposeResult:
        with Center():
            yield Label(self.input_label)

            input_widget = Input()
            input_widget.action_submit = self.on_enter

            yield input_widget

    @property
    def value(self):
        input_widget = self.query_one(Input)
        return input_widget.value

    def action_quit(self):
        self.on_quit(self)

    def focus(self, scroll_visible: bool = True) -> None:
        input_widget = self.query_one(Input)
        input_widget.focus(scroll_visible)
