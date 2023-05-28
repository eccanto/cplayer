from pathlib import Path
from typing import Optional

from textual.app import ComposeResult
from textual.widget import Widget
from textual.widgets import Label

from components.hidden_widget.widget import HiddenWidget


class Notification(HiddenWidget):
    """Notification widget representation."""

    DEFAULT_CSS = Path(__file__).parent.joinpath('styles.css').read_text()

    def __init__(self, label: str, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.label = label

    def compose(self) -> ComposeResult:
        yield Label(self.label)

    def update(self, message: str) -> None:
        label = self.query_one(Label)
        label.update(message)

    def show(self, message: Optional[str] = None) -> None:
        self.display = True

        if message is not None:
            self.update(message)
