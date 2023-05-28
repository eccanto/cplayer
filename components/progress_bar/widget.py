from enum import Enum
from pathlib import Path
from typing import cast

from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.widget import Widget
from textual.widgets import Label, ProgressBar


class ProgressStatus(Widget):
    class Status(Enum):
        UNSELECTED = '[#FF8000]❱ unselected'.ljust(22)
        PLAYING = '[#00CC00]❱ playing'.ljust(22)
        PAUSED = '[#0080FF]❱ paused'.ljust(22)

    DEFAULT_CSS = Path(__file__).parent.joinpath('styles.css').read_text()

    def compose(self) -> ComposeResult:
        with Horizontal():
            yield Label(self.Status.UNSELECTED.value, id='reproduce-label')
            yield ProgressBar(show_eta=False, show_percentage=False)
            yield Label('00:00/00:00', id='progress-label')

    def update(self, *args, **kwargs) -> None:
        bar = self.query_one(ProgressBar)
        bar.update(*args, **kwargs)

    def set_status(self, status: Status) -> None:
        reproduce_label = cast(Label, self.query_one('#reproduce-label'))
        reproduce_label.update(status.value)

    def set_progress(self, current_seconds: float, total_seconds: float) -> None:
        progress_label = cast(Label, self.query_one('#progress-label'))
        progress_label.update(
            f'{(current_seconds // 60):02}:{(current_seconds % 60):02}'
            '/'
            f'{(int(total_seconds) // 60):02}:{(int(total_seconds) % 60):02}'
        )
