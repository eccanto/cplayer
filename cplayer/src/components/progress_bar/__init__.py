from enum import Enum
from pathlib import Path
from typing import cast

from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.widget import Widget
from textual.widgets import Label

from cplayer.src.elements import CONFIG


class ProgressStatusWidget(Widget):
    """Progress and status widget."""

    class Status(Enum):
        """Playback statuses.

        The `Status` enum represents the possible playback statuses of a song or an ongoing process.
        """

        UNSELECTED = (
            f'[{CONFIG.data.appearance.style.colors.primary}]{CONFIG.data.appearance.style.icons.reproduce} '
            'unselected'
        ).ljust(22)
        PLAYING = (
            f'[{CONFIG.data.appearance.style.colors.playing_label}]{CONFIG.data.appearance.style.icons.reproduce} '
            'playing'
        ).ljust(22)
        PAUSED = (
            f'[{CONFIG.data.appearance.style.colors.paused_label}]{CONFIG.data.appearance.style.icons.reproduce} '
            'paused'
        ).ljust(22)

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
