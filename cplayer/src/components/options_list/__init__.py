from pathlib import Path
from typing import Callable, List, Self, Union, cast

from textual._node_list import NodeList
from textual.app import ComposeResult
from textual.containers import Middle
from textual.widget import Widget
from textual.widgets import Label, ListItem, ListView

from src.components.hidden_widget import HiddenWidget


class CustomListView(ListView):
    """Custom list view."""

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
        """Initializes the Widget object.

        :param on_quit: A function to be called when quitting the list view.
        :param on_select: A function to be called when an option is selected.
        :param *children: Variable length argument list for child elements to add initially.
        """
        super().__init__(*children)

        self._on_quit = on_quit
        self._on_select = on_select

    def clean(self) -> None:
        """Removes all child nodes from the list view."""
        self._nodes = NodeList()

    def add(self, items: List['OptionWidget']) -> None:
        """Add a list of option objects to the list view.

        :param items: A list of option objects to add.
        """
        self._add_children(*items)

    def update(self, options: List['OptionWidget']) -> None:
        """Updates the list view with a new set of options.

        :param options: A list of option objects representing the new options.
        """
        self._nodes = NodeList()

        for option in options:
            option.highlighted = False
            self._add_child(option)

        self.index = 0

    def action_select_option(self) -> None:
        """Runs the `self.on_select` callback with the selected option."""
        if self.highlighted_child:
            self._on_select(cast(OptionWidget, self.highlighted_child).data)


class OptionWidget(ListItem):
    """Option in the list view."""

    def __init__(self, data: Union[Path, str], prefix: str, *args, **kwargs) -> None:
        """Initializes the Widget object.

        :param data: The data associated with the option.
        :param prefix: A prefix to display before the option text.
        :param *args: Variable length argument list.
        :param **kwargs: Arbitrary keyword arguments.
        """
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


class OptionsListWidget(HiddenWidget):
    """Options list widget."""

    DEFAULT_CSS = Path(__file__).parent.joinpath('styles.css').read_text(encoding='UTF-8')

    def __init__(
        self,
        label: str,
        on_quit: Callable[[Widget], None],
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
        self.list_view = CustomListView(self._on_quit, self._on_select, *children)

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
