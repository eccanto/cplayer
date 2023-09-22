import random
from difflib import SequenceMatcher
from enum import Enum
from pathlib import Path
from typing import Callable, List, Optional

import numpy
from pydub import AudioSegment
from pydub.logging_utils import logging
from rich.console import Console
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import VerticalScroll
from textual.widgets import Label
from typing_extensions import Self

from cplayer.src.elements import CONFIG


class Song:
    """Song item."""

    def __init__(self, path: Path, on_play: Callable[['Song'], None], *args, **kwargs) -> None:
        """Initializes the Widget object.

        :param path: The path to the audio file.
        :param *args: Variable length argument list.
        :param **kwargs: Arbitrary keyword arguments.
        """
        super().__init__(*args, **kwargs)

        self.path = path
        self.on_play = on_play

        self._seconds = None
        self._audio = None
        self.frame_rate = None
        self._buffer = None
        self._selected = False

    @property
    def selected(self) -> bool:
        """Indicates whether the song is selected."""
        return self._selected

    @selected.setter
    def selected(self, is_selected: bool) -> None:
        if is_selected:
            logging.info('selecting song "%s"', self.path)

        self._selected = is_selected

    def play(self) -> None:
        """Plays the audio associated with the song."""
        self.on_play(self)

    @property
    def seconds(self):
        """Calculates and returns the duration of the audio in seconds.

        :returns: The duration of the audio in seconds.
        """
        if self._seconds is None:
            self._audio = AudioSegment.from_mp3(self.path)
            self._seconds = len(self._audio) / 1000.0
            self.frame_rate = self._audio.frame_rate
        return self._seconds

    @property
    def buffer(self):
        """Returns the audio data as a numpy array.

        :returns: The audio data as a numpy array.
        """
        if self._buffer is None and self._audio:
            self._buffer = numpy.array(self._audio.get_array_of_samples())
        return self._buffer


class PlaylistOrder(Enum):
    """Orders in which the playlist is played."""

    ASCENDING = 'ascending'
    DESCENDANT = 'descendant'
    RANDOM = 'random'


class TracklistWidget(VerticalScroll):  # pylint: disable=too-many-instance-attributes
    """Tracklist widget."""

    DEFAULT_CSS = Path(__file__).parent.joinpath('styles.css').read_text(encoding='UTF-8')

    BINDINGS = [
        Binding(CONFIG.data.general.shortcuts.playlist.up, 'cursor_up', 'Cursor Up', show=False),
        Binding(CONFIG.data.general.shortcuts.playlist.down, 'cursor_down', 'Cursor Down', show=False),
        Binding(CONFIG.data.general.shortcuts.playlist.rewind, 'cursor_left', '-5 secs', show=False),
        Binding(CONFIG.data.general.shortcuts.playlist.forward, 'cursor_right', '+5 secs', show=False),
        Binding(CONFIG.data.general.shortcuts.playlist.select, 'select_cursor', 'Reproduce', show=False),
    ]

    def __init__(  # pylint: disable=too-many-arguments
        self,
        on_select: Callable[[Song], None],
        on_cursor_left: Callable[[], None],
        on_cursor_right: Callable[[], None],
        on_change_position: Callable[[int, int], None],
        order: PlaylistOrder = PlaylistOrder.ASCENDING,
        fixed_size: int = 0,
        **kwargs,
    ) -> None:
        """Initializes the Widget object.

        :param on_select: A function to be called when selecting a song in the tracklist.
        :param on_cursor_left: A function to be called when moving the cursor to the left.
        :param on_cursor_right: A function to be called when moving the cursor to the right.
        :param order: The order in which the playlist is played.
        :param **kwargs: Arbitrary keyword arguments.
        """
        super().__init__(**kwargs)

        self._fixed_size = fixed_size

        self.on_select = on_select
        self.on_cursor_left = on_cursor_left
        self.on_cursor_right = on_cursor_right
        self.on_change_position = on_change_position

        self.order = order

        self.current_song: Optional[Song] = None

        self.console = Console()
        self.length = self.console.size.height - self._fixed_size

        self.items: List[Song] = []
        self.items_unfilter: List[Song] = []
        self.items_length = 0
        self.index = 0

        self.filter_pattern: Optional[str] = None

        self.content = Label('No data.')

        self._colors = CONFIG.data.appearance.style.colors

    def on_mount(self) -> None:
        """Handle the on-mount event for the tracklist widget."""
        self.focus()

    def compose(self) -> ComposeResult:
        """Composes the widget.

        :returns: The widget object representing the composed widget.
        """
        yield self.content

    def refresh(self, *args, **kwargs) -> Self:
        """Refresh the tracklist widget.

        :param *args: Variable length argument list.
        :param **kwargs: Arbitrary keyword arguments.
        """
        new_length = self.console.size.height - self._fixed_size
        if new_length > self.length:
            delta = self.length - new_length

            self.length = new_length
            self.index += delta
            self.draw()

            if self.current_song:
                self.select(self.current_song.path)

        return super().refresh(*args, **kwargs)

    def clean(self) -> None:
        """Cleans seleted song in the tracklist."""
        self.content.update('No data.')

    def go_to(self, position: int) -> None:
        """Moves the highlighted position to a specified position.

        :param position: The destination position.
        """
        if position <= 0:
            self.index = 0
        else:
            self.index = min(position - 1, self.items_length - 1)
        self.draw()

    def next_song(self) -> None:
        """Goes to the next song."""
        self.action_cursor_down()
        self.action_select_cursor()

    def previous_song(self) -> None:
        """Goes to the previous song."""
        self.action_cursor_up()
        self.action_select_cursor()

    def action_select_cursor(self) -> None:
        """Performs the action associated with selecting a song in the tracklist."""
        self.current_song = self.items[self.index]
        self.draw()
        self.on_select(self.current_song)

    def action_cursor_left(self) -> None:
        """Performs the action associated with moving the cursor to the left."""
        self.on_cursor_left()

    def action_cursor_right(self) -> None:
        """Performs the action associated with moving the cursor to the right."""
        self.on_cursor_right()

    def draw(self) -> None:
        """Draws the tracklist to display new songs."""
        if self.filter_pattern is not None:
            items = [song for song in self.items if self.filter_pattern in song.path.name]
        else:
            items = self.items

        rows = []
        for index, song in enumerate(items[self.index : self.index + self.length]):
            is_current_song = self.current_song is not None and song.path == self.current_song.path
            rows.append(
                f'[{self._colors.text}]'
                f'{f"[{self._colors.playing_label}]" if is_current_song else CONFIG.data.appearance.style.icons.song} '
                f'[{self._colors.primary if (index == 0) else self._colors.text}]{song.path.name}'
            )

        self.content.update('\n'.join(rows))
        self.on_change_position(self.index, self.items_length)

    def action_cursor_down(self) -> None:
        """Highlight the previous item in the list."""
        if self.index < self.items_length - 1:
            self.index += 1
            self.draw()

    def action_cursor_up(self) -> None:
        """Highlight the next item in the list."""
        if self.index:
            self.index -= 1
            self.draw()

    def set_songs(self, paths: List[Path], position: int = 0, sort: bool = False) -> None:
        """Updates the tracklist with a new list of audio file paths.

        :param paths: A list of paths to the audio files.
        :param position: The position to set as the currently highlighted song.
        :param sort: Whether to sort the playlist based on the specified order.
        """
        if sort:
            if self.order == PlaylistOrder.ASCENDING:
                paths.sort(key=lambda path: path.stem)
            elif self.order == PlaylistOrder.DESCENDANT:
                paths.sort(key=lambda path: path.stem, reverse=True)
            elif self.order == PlaylistOrder.RANDOM:
                random.shuffle(paths)

        self.items = [Song(path, on_play=self.on_select) for path in paths]
        self.items_unfilter = self.items.copy()
        self.items_length = len(paths)
        self.index = position
        self.draw()

    def add(self, paths: List[Path]) -> None:
        """Adds new file paths to the tracklist.

        :param items: A list of paths to the audio files.
        """
        songs = [Song(path, on_play=self.on_select) for path in paths]

        self.items_unfilter.extend(songs)

        self.items.extend(songs)
        self.items_length = len(self.items)

        self.draw()

    def select(self, path: Path) -> None:
        """Selects a song in the tracklist based on its path.

        :param path: The path to the audio file.
        """
        for index, song in enumerate(self.items):
            if song.path == path:
                self.index = index
                self.draw()
                break

    def filter(self, pattern: str) -> None:
        """Filters the tracklist based on a search pattern.

        :param pattern: The filter pattern.
        """
        if pattern:
            self.items = [song for song in self.items_unfilter if pattern.lower() in song.path.name.lower()]
        else:
            self.items = self.items_unfilter.copy()

        self.items_length = len(self.items)
        self.index = 0
        self.draw()

        if self.current_song:
            self.select(self.current_song.path)

    def search(self, pattern: str) -> None:
        """Searchs a song in the the tracklist.

        :param pattern: The search pattern.
        """
        if pattern:
            song = next((song for song in self.items if pattern.lower() in song.path.name.lower()), None)
            if not song:
                song = max(
                    ((SequenceMatcher(None, song.path.name, pattern).ratio(), song) for song in self.items),
                    key=lambda data: data[0],
                )[1]
            self.select(song.path)

    async def swap(self, position: int) -> None:
        """Swaps the position of the currently highlighted song with another song.

        :param position: The position to swap with.
        """
        if self.index < position:
            new_index = min(position, self.items_length - 1)
        else:
            new_index = max(position, 0)

        current_item = self.items[self.index]
        new_item = self.items[new_index]

        self.items[self.index] = new_item
        self.items[new_index] = current_item

        self.index = new_index
        self.draw()
