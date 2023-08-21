from enum import Enum
from pathlib import Path
from typing import cast

from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.widget import Widget
from textual.widgets import Label


class ProgressStatusWidget(Widget):
    """Progress and status widget."""

    class Status(Enum):
        """Playback statuses.

        The `Status` enum represents the possible playback statuses of a song or an ongoing process.
        """

        UNSELECTED = '[#FF8000]❱ unselected'.ljust(22)
        PLAYING = '[#00CC00]❱ playing'.ljust(22)
        PAUSED = '[#0080FF]❱ paused'.ljust(22)

    DEFAULT_CSS = Path(__file__).parent.joinpath('styles.css').read_text(encoding='UTF-8')

    def __init__(self, *args, **kwargs) -> None:
        """Initializes the widget object."""
        super().__init__(*args, **kwargs)

        self.total_seconds = '00:00'
        self.progress_label = Label('00:00/00:00')

    def compose(self) -> ComposeResult:
        """Composes the layout for the Widget.

        :yields: Widgets representing the status and progress display.
        """
        with Horizontal():
            yield Label(self.Status.UNSELECTED.value, id='reproduce-label')
            yield self.progress_label

    def set_status(self, status: Status) -> None:
        """Sets the status label to the given status.

        :param status: The status enum value to set.
        """
        reproduce_label = cast(Label, self.query_one('#reproduce-label'))
        reproduce_label.update(status.value)

    def set_progress(self, current_seconds: float) -> None:
        """Sets the progress label to the given progress.

        :param current_seconds: The current progress in seconds.
        """
        self.progress_label.update(f'{(current_seconds // 60):02}:{(current_seconds % 60):02}/{self.total_seconds}')
