from pathlib import Path

from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.widget import Widget
from textual.widgets import Label, ProgressBar


class VolumeBar(Widget):
    DEFAULT_CSS = Path(__file__).parent.joinpath('styles.css').read_text()

    def __init__(self, default_volume: float = 0.75) -> None:
        super().__init__()

        self.default_volume = default_volume

    def compose(self) -> ComposeResult:
        with Horizontal():
            yield Label('')
            yield ProgressBar(show_eta=False, show_percentage=False)

    def on_mount(self) -> None:
        bar = self.query_one(ProgressBar)
        bar.update(total=1)
        bar.advance(self.default_volume)
        bar.query_one('#bar').styles.width = 12

    def update(self, *args, **kwargs) -> None:
        bar = self.query_one(ProgressBar)
        bar.update(*args, **kwargs)
