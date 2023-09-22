from pathlib import Path
from typing import Any, Callable, List, Self, Union

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Middle, VerticalScroll
from textual.widgets import Label

from cplayer.src.components.hidden_widget import HiddenWidget
from cplayer.src.elements import CONFIG


class CustomListView(VerticalScroll):
    """Custom list view."""

    BINDINGS = [
        Binding('up', 'cursor_up', 'Cursor Up', show=False),
        Binding('down', 'cursor_down', 'Cursor Down', show=False),
        Binding('escape', 'quit', 'Quit'),
        Binding('enter', 'select_option', 'Select Option'),
    ]

    def __init__(
        self,
        on_quit: Callable[[], None],
        on_select: Callable[[Union[Path, str]], None],
        *children,
    ) -> None:
        """Initializes the Widget object.

        :param on_quit: A function to be called when quitting the list view.
        :param on_select: A function to be called when an option is selected.
        :param *children: Variable length argument list for child elements to add initially.
        """
        super().__init__(*children)

        self._on_quit = on_quit
        self._on_select = on_select

        self.options: List[Option] = []
        self.index = 0

        self._colors = CONFIG.data.appearance.style.colors

        self.content = Label('No data.')

    def compose(self) -> ComposeResult:
        """Composes the widget.

        :returns: The widget object representing the composed widget.
        """
        yield self.content

    def draw(self) -> None:
        """Draws the listview with the current status."""
        rows = []
        for index, option in enumerate(self.options):
            rows.append(
                f'[{self._colors.primary if (index == self.index) else self._colors.text}]'
                f'{option.prefix}{option.to_string(option.data)}'
            )
        self.content.update('\n'.join(rows))

    def update(self, options: List['Option']) -> None:
        """Updates the list view with a new set of options.

        :param options: A list of option objects representing the new options.
        """
        self.options = options
        self.index = 0
        self.draw()

    def action_quit(self) -> None:
        """Calls the quit callback."""
        self._on_quit()

    def action_cursor_down(self) -> None:
        """Highlight the previous item in the list."""
        if self.index < len(self.options) - 1:
            self.index += 1
            self.draw()

    def action_cursor_up(self) -> None:
        """Highlight the next item in the list."""
        if self.index > 0:
            self.index -= 1
            self.draw()

    def action_select_option(self) -> None:
        """Runs the `self.on_select` callback with the selected option."""
        if self.options:
            self._on_select(self.options[self.index].data)


class Option:  # pylint: disable=too-few-public-methods
    """Option in the list view."""

    def __init__(self, data: Union[Path, str], prefix: str, to_string: Callable[[Any], str]) -> None:
        """Initializes the Widget object.

        :param data: The data associated with the option.
        :param prefix: A prefix to display before the option text.
        :param *args: Variable length argument list.
        :param **kwargs: Arbitrary keyword arguments.
        """
        self.data = data
        self.prefix = prefix
        self.to_string = to_string


class OptionsListWidget(HiddenWidget):
    """Options list widget."""

    DEFAULT_CSS = Path(__file__).parent.joinpath('styles.css').read_text(encoding='UTF-8')

    def __init__(
        self,
        label: str,
        on_quit: Callable[[HiddenWidget], None],
        on_select: Callable[[Union[Path, str]], None],
        *children,
        **kwargs,
    ) -> None:
        """Initializes the Widget object.

        :param label: The label text to display for the options list.
        :param on_quit: A function to be called when quitting the options list.
        :param on_select: A function to be called when an option is selected.
        :param *children: Variable length argument list for child elements.
        :param **kwargs: Arbitrary keyword arguments.
        """
        super().__init__(**kwargs)

        self._label = label
        self._on_quit = on_quit
        self._on_select = on_select

        self.label = Label(self._label, classes='bold')
        self.list_view = CustomListView(lambda: self._on_quit(self), self._on_select, *children)

    def compose(self) -> ComposeResult:
        """Composes the layout for the Widget.

        :yields: The widget objects that represent the options list.
        """
        with Middle():
            yield self.label
            yield self.list_view

    def focus(self, scroll_visible: bool = True) -> Self:
        """Sets the focus on the options list.

        :param scroll_visible: Whether to scroll the options list into the visible area.
        """
        self.list_view.focus(scroll_visible)
        return self
