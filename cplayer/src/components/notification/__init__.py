"""Module that contains the implementation of a notification widget."""

from pathlib import Path

from textual.app import ComposeResult
from textual.widget import Widget
from textual.widgets import Label

from cplayer.src.components.hidden_widget import HiddenWidget


class NotificationWidget(HiddenWidget):
    """Notification widget representation."""

    DEFAULT_CSS = Path(__file__).parent.joinpath('styles.css').read_text(encoding='UTF-8')

    def __init__(  # noqa: PLR0913
        self,
        label: str,
        *children: Widget,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
        start_hidden: bool = True,
    ) -> None:
        """Initializes the Widget object.

        :param label: The label text to display in the notification.
        :param *args: Variable length argument list.
        :param **kwargs: Arbitrary keyword arguments.
        """
        super().__init__(*children, name=name, id=id, classes=classes, disabled=disabled, start_hidden=start_hidden)

        self.label = label

    def compose(self) -> ComposeResult:
        """Composes the layout for the Widget.

        :yields: The Label widget representing the notification.
        """
        yield Label(self.label)

    def update(self, message: str) -> None:
        """Updates the content of the notification with the given message.

        :param message: The new message to display in the notification.
        """
        label = self.query_one(Label)
        label.update(message)

    def show(self, focus: bool = True, message: str | None = None) -> None:  # noqa: FBT002
        """Shows the notification.

        :param message: Optional message to update the content of the notification before showing it.
        """
        if message is not None:
            self.update(message)

        super().show(focus)
