from pathlib import Path
from typing import Callable, Coroutine, Self

from textual.app import ComposeResult
from textual.widgets import Input

from cplayer.src.components.hidden_widget import HiddenWidget


class InputLabelWidget(HiddenWidget):
    """An input with a label."""

    BINDINGS = [
        ('escape', 'quit', 'Quit'),
    ]

    DEFAULT_CSS = Path(__file__).parent.joinpath('styles.css').read_text(encoding='UTF-8')

    def __init__(
        self,
        input_label: str,
        on_enter: Callable[[], Coroutine[None, None, None]],
        on_quit: Callable[['InputLabelWidget'], None],
        *args,
        **kwargs,
    ) -> None:
        """Initializes the Widget object.

        :param input_label: The label text to display.
        :param on_enter: A coroutine function to be called when Enter key is pressed.
        :param on_quit: A function to be called when quitting the input label widget.
        :param *args: Variable length argument list.
        :param **kwargs: Arbitrary keyword arguments.
        """
        super().__init__(*args, **kwargs)

        self.input_widget = Input(placeholder=input_label)

        self.on_enter = on_enter
        self.on_quit = on_quit

    def compose(self) -> ComposeResult:
        """Composes the layout for the Widget.

        :returns: The ComposeResult object representing the composed layout.
        """
        self.input_widget.action_submit = self.on_enter  # type: ignore
        yield self.input_widget

    @property
    def value(self) -> str:
        """Gets the current value of the input widget.

        :returns: The current value of the input widget.
        """
        return self.input_widget.value

    @value.setter
    def value(self, text: str) -> None:
        self.input_widget.value = text

    def action_quit(self) -> None:
        """Perform the action associated with quitting the input label widget."""
        self.on_quit(self)

    def focus(self, scroll_visible: bool = True) -> Self:
        """Sets the focus on the input widget.

        :param scroll_visible: Whether to scroll the widget into the visible area.
        """
        self.input_widget.focus(scroll_visible)
        return self
