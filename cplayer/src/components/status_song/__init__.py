from pathlib import Path

from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.widget import Widget
from textual.widgets import Label

from cplayer.src.components.hidden_widget import HiddenWidget
from cplayer.src.components.progress_bar import ProgressStatusWidget
from cplayer.src.components.volume_bar import VolumeBarWidget


class StatusSong(HiddenWidget):
    """Panel displaying the current song status."""

    DEFAULT_CSS = Path(__file__).parent.joinpath('styles.css').read_text(encoding='UTF-8')

    def __init__(  # noqa: PLR0913
        self,
        volume: float,
        *children: Widget,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
        start_hidden: bool = True,
    ) -> None:
        """Initializes the widget object.

        :param volume: The default volume.
        """
        super().__init__(*children, name=name, id=id, classes=classes, disabled=disabled, start_hidden=start_hidden)

        self.position = Label('NaN/NaN')
        self.progress = ProgressStatusWidget()
        self.song = Label('-', classes='bold')
        self.volume = VolumeBarWidget(default_volume=volume)

    def compose(self) -> ComposeResult:
        """Composes the elements for the home page.

        :returns: The composed elements for the home page.
        """
        with Horizontal():
            yield self.position
            yield self.progress
            yield self.song
            yield self.volume
