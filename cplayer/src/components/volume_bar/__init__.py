from pathlib import Path

from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.widget import Widget
from textual.widgets import Label, ProgressBar

from cplayer.src.elements import CONFIG


class VolumeBarWidget(Widget):
    """Volume bar widget."""

    DEFAULT_CSS = Path(__file__).parent.joinpath('styles.css').read_text(encoding='UTF-8')

    def __init__(self, default_volume: float) -> None:
        """Initializes the Widget object.

        :param default_volume: The default volume value to display.
        """
        super().__init__()

        self.default_volume = default_volume

        self._label = Label(CONFIG.data.appearance.style.icons.volume)
        self._progress_bar = ProgressBar(show_eta=False, show_percentage=False, total=1)

        self._muted = False

    @property
    def muted(self) -> bool:
        """Indicates whether the song is muted."""
        return self._muted

    @muted.setter
    def muted(self, is_muted) -> None:
        self._muted = is_muted
        self._label.update(
            CONFIG.data.appearance.style.icons.mute if is_muted else CONFIG.data.appearance.style.icons.volume
        )

    def compose(self) -> ComposeResult:
        """Composes the layout for the Widget.

        :yields: Widgets representing the volume bar.
        """
        with Horizontal():
            yield self._label
            yield self._progress_bar

    def on_mount(self) -> None:
        """Handles the on-mount event for the volume bar widget."""
        self._progress_bar.advance(self.default_volume)
        self._progress_bar.query_one('#bar').styles.width = 12

    def update(self, *args, **kwargs) -> None:
        """Updates the volume bar widget with the given arguments.

        :param *args: Variable length argument list.
        :param **kwargs: Arbitrary keyword arguments.
        """
        self._progress_bar.update(*args, **kwargs)
