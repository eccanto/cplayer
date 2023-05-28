from pathlib import Path
from typing import Callable, List, Optional, cast

import numpy
from pydub import AudioSegment
from pygame import mixer
from textual.binding import Binding

from textual.widgets import Label, ListItem, ListView
from textual._node_list import NodeList


class Song(ListItem):
    def __init__(self, path: Path, *args, **kwargs) -> None:
        self.label = Label(f'♪ {path.name}')

        super().__init__(self.label, *args, **kwargs)

        self.path = path

        self._seconds = None
        self._audio = None
        self.frame_rate = None
        self._buffer = None

    def __repr__(self) -> str:
        return self.path.name

    def play(self):
        mixer.music.load(self.path)
        mixer.music.play()

    def update(self, path: Path) -> None:
        self.path = path
        self.label.update(f'♪ {path.name}')

    @property
    def seconds(self):
        if self._seconds is None:
            self._audio = AudioSegment.from_mp3(self.path)
            self._seconds = len(self._audio) / 1000.0
            self.frame_rate = self._audio.frame_rate
        return self._seconds

    @property
    def buffer(self):
        if self._buffer is None:
            self._buffer = numpy.array(self._audio.get_array_of_samples())
        return self._buffer


class Playlist(ListView):
    CSS_PATH = 'resources/styles/application.css'
    BINDINGS = [
        Binding('up', 'cursor_up', 'Cursor Up', show=False),
        Binding('down', 'cursor_down', 'Cursor Down', show=False),
        Binding('left', 'cursor_left', '-5 secs', show=False),
        Binding('right', 'cursor_right', '+5 secs', show=False),
        Binding('enter', 'select_cursor', 'Reproduce', show=False),
    ]

    highlighted_child: Optional[Song]
    current_song: Optional[Song]

    def __init__(
        self,
        on_select: Callable[[Song], None],
        on_cursor_left: Callable[[], None],
        on_cursor_right: Callable[[], None],
        *args,
        **kwargs
    ) -> None:
        super().__init__(*args, **kwargs)

        self.on_select = on_select
        self.on_cursor_left = on_cursor_left
        self.on_cursor_right = on_cursor_right

        self.current_song = None

    def on_mount(self) -> None:
        self.focus()

    def action_select_cursor(self) -> None:
        if self.highlighted_child:
            self.current_song = self.highlighted_child
            self.on_select(self.highlighted_child)

    def action_cursor_left(self):
        self.on_cursor_left()

    def action_cursor_right(self):
        self.on_cursor_right()

    def add(self, *song: Song) -> None:
        self._add_children(*song)

    def update(self, songs: List[Song], position: Optional[int] = 0) -> None:
        self._nodes = NodeList()

        for index, song in enumerate(songs):
            song.highlighted = index == position
            self._add_child(song)

        self.index = position

    async def swap(self, position: int) -> None:
        if self.index is not None:
            if self.index < position:
                new_index = min(position, len(self._nodes) - 1)
            else:
                new_index = max(position, 0)

            items = self.displayed_children
            current_item = cast(Song, items[self.index])
            new_item = cast(Song, items[new_index])

            current_item_path = current_item.path
            new_item_path = new_item.path

            current_item.update(new_item_path)
            new_item.update(current_item_path)

            self.index = new_index
