import random
from enum import Enum
from pathlib import Path
from typing import Callable, List, Optional, cast

import numpy
from pydub import AudioSegment
from pygame import mixer
from rich.console import Console
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal
from textual.widgets import Label, ListItem, ListView
from typing_extensions import Self


class SongWidget(ListItem):
    """Song widget."""

    def __init__(self, path: Path, *args, **kwargs) -> None:
        """Initializes the Widget object.

        :param path: The path to the audio file.
        :param *args: Variable length argument list.
        :param **kwargs: Arbitrary keyword arguments.
        """
        super().__init__(*args, **kwargs)

        self.label = Label(f'♪ {path.name}')
        self.path = path

        self._seconds = None
        self._audio = None
        self.frame_rate = None
        self._buffer = None
        self._selected = False

    def __repr__(self) -> str:
        """Returns the string representation of the Widget.

        :returns: The name of the audio file.
        """
        return self.path.name

    @property
    def selected(self) -> bool:
        return self._selected

    @selected.setter
    def selected(self, is_selected: bool) -> None:
        pass
        # self._selected = is_selected

        # status_label = cast(Label, self.query_one('#status'))
        # if is_selected:
        #     status_label.update('x')
        # else:
        #     status_label.update('')

    def compose(self) -> ComposeResult:
        """Composes the elements for the List Item.

        :returns: The composed elements for the widget.
        """
        with Horizontal():
            yield Label('', id='status')
            yield self.label

    def play(self) -> None:
        """Plays the audio associated with the song."""
        mixer.music.load(self.path)
        mixer.music.play()

    def update(self, path: Path) -> None:
        """Updates the song widget with a new audio file.

        :param path: The path to the new audio file.
        """
        self.path = path
        self.label.update(f'♪ {path.name}')

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


class TracklistWidget(ListView):  # pylint: disable=too-many-instance-attributes
    """Tracklist widget."""

    DEFAULT_CSS = Path(__file__).parent.joinpath('styles.css').read_text(encoding='UTF-8')

    BINDINGS = [
        Binding('up', 'cursor_up', 'Cursor Up', show=False),
        Binding('down', 'cursor_down', 'Cursor Down', show=False),
        Binding('left', 'cursor_left', '-5 secs', show=False),
        Binding('right', 'cursor_right', '+5 secs', show=False),
        Binding('enter', 'select_cursor', 'Reproduce', show=False),
    ]

    highlighted_child: Optional[SongWidget]
    children: List[SongWidget]
    displayed_children: List[SongWidget]  # type: ignore

    _FIXED_SIZE = 14
    _MAX_SIZE = 100

    def __init__(
        self,
        on_select: Callable[[SongWidget], None],
        on_cursor_left: Callable[[], None],
        on_cursor_right: Callable[[], None],
        order: PlaylistOrder = PlaylistOrder.ASCENDING,
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

        self.on_select = on_select
        self.on_cursor_left = on_cursor_left
        self.on_cursor_right = on_cursor_right

        self.order = order

        self.current_song: Optional[Path] = None

        self.console = Console()
        self.length = self.console.size.height - self._FIXED_SIZE

        self.items: List[Path] = []
        self.items_length = 0
        self.items_offset = 0

        self._add_children(*[SongWidget(Path()) for i in range(self._MAX_SIZE)])
        self._hide()

    def on_mount(self) -> None:
        """Handle the on-mount event for the tracklist widget."""
        self.focus()

    def refresh(self, *args, **kwargs) -> Self:
        """Refresh the tracklist widget.

        :param *args: Variable length argument list.
        :param **kwargs: Arbitrary keyword arguments.
        """
        new_length = self.console.size.height - self._FIXED_SIZE
        if new_length < self.length and self.index:
            delta = self.length - new_length

            self.items_offset += delta
            self._scroll()

            self.length = new_length
            self.index -= delta
        else:
            self.length = new_length

        return super().refresh(*args, **kwargs)

    def next_song(self) -> None:
        self.action_cursor_down()
        self.action_select_cursor()

    def previous_song(self) -> None:
        self.action_cursor_up()
        self.action_select_cursor()

    def action_select_cursor(self) -> None:
        """Performs the action associated with selecting a song in the tracklist."""
        if self.highlighted_child:
            self.current_song = self.highlighted_child.path
            self.highlighted_child.selected = True
            self.on_select(self.highlighted_child)

    def action_cursor_left(self) -> None:
        """Performs the action associated with moving the cursor to the left."""
        self.on_cursor_left()

    def action_cursor_right(self) -> None:
        """Performs the action associated with moving the cursor to the right."""
        self.on_cursor_right()

    def _hide(self) -> None:
        """Hides all child songs in the tracklist."""
        for song in self.children:
            song.visible = False

    def _scroll(self) -> None:
        """Scrolls the tracklist to display new songs."""
        for index, song in enumerate(self.children):
            raw_index = self.items_offset + index
            if 0 <= raw_index < self.items_length:
                song.update(self.items[raw_index])
                song.visible = True
            else:
                break

    async def action_cursor_down(self) -> None:
        """Highlight the previous item in the list."""
        if self.index is not None and self.items_length:
            if self.index < self.items_length - 1:
                # self.select_index(self.index + 1)
                self.index += 1
            elif self.index >= self.length - 1:
                self.items_offset = min(self.items_length - 1, self.items_offset + 1)
                self._scroll()
            else:
                self.items_offset = 0
                self._scroll()
                self.index = 0
        else:
            self.index = 0

    async def action_cursor_up(self) -> None:
        """Highlight the next item in the list."""
        if self.index is not None and self.items_length:
            if self.index > 0:
                # self.select_index(self.index - 1)
                self.index -= 1
            else:
                self.items_offset = max(self.items_offset - 1, 0)
                self._scroll()
        else:
            self.index = 0

    def update(self, paths: List[Path], position: Optional[int] = 0, sort: bool = False) -> None:
        """Updates the tracklist with a new list of audio file paths.

        :param paths: A list of paths to the audio files.
        :param position: The position to set as the currently highlighted song.
        :param sort: Whether to sort the playlist based on the specified order.
        """
        if sort:
            if self.order == PlaylistOrder.ASCENDING:
                paths.sort()
            elif self.order == PlaylistOrder.DESCENDANT:
                paths.sort(reverse=True)
            elif self.order == PlaylistOrder.RANDOM:
                random.shuffle(paths)

        self._hide()
        self.items = paths
        self.items_length = len(paths)
        self.items_offset = 0
        self._scroll()

        self.index = position

    def add(self, paths: List[Path]) -> None:
        """Adds new file paths to the tracklist.

        :param items: A list of paths to the audio files.
        """
        self.items.extend(paths)
        self.items_length = len(self.items)

    def select(self, path: Path) -> None:
        """Selects a song in the tracklist based on its path.

        :param path: The path to the audio file.
        """
        for index, song_path in enumerate(self.items):
            if song_path == path:
                self.items_offset = index
                self._scroll()
                self.select_index(0)
                break

    def select_index(self, index: int) -> None:
        """Selects a song in the tracklist based on its index.

        :param index: The index of the song in the tracklist.
        """
        if index < len(self.displayed_children):
            item = self.displayed_children[index]
            children_index = self.children.index(item)

            self.index = children_index

    def filter(self, pattern: str) -> None:
        """Filters the tracklist based on a search pattern.

        :param pattern: The search pattern.
        """
        for song in self.children:
            song.display = pattern in song.path.name.lower()

    @property
    def displayed_index(self):
        """Gets the displayed index of the currently highlighted song.

        :returns: The displayed index of the currently highlighted song.
        """
        if self.index is not None:
            child = self.children[self.index]
            index = self.displayed_children.index(child)
        else:
            index = None

        return index

    async def swap(self, position: int) -> None:
        """Swaps the position of the currently highlighted song with another song.

        :param position: The position to swap with.
        """
        if self.displayed_index is not None:
            if self.displayed_index < position:
                new_index = min(position, len(self.displayed_children) - 1)
            else:
                new_index = max(position, 0)

            current_item = self.displayed_children[self.displayed_index]
            new_item = self.displayed_children[new_index]

            current_item_path = current_item.path
            new_item_path = new_item.path

            current_item.update(new_item_path)
            new_item.update(current_item_path)

            self.index = self.children.index(new_item)
