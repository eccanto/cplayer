import logging
from pathlib import Path
from typing import Callable, List, Optional

import numpy
from pydub import AudioSegment
from pygame import mixer
from textual.binding import Binding

from textual.widgets import Label, ListItem, ListView
from textual._node_list import NodeList


class WidgetSong(ListItem):
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


class WidgetPlaylist(ListView):
    CSS_PATH = 'resources/styles/application.css'
    BINDINGS = [
        Binding('up', 'cursor_up', 'Cursor Up', show=False),
        Binding('down', 'cursor_down', 'Cursor Down', show=False),
        Binding('left', 'cursor_left', '-5 secs', show=False),
        Binding('right', 'cursor_right', '+5 secs', show=False),
        Binding('enter', 'select_cursor', 'Reproduce', show=False),
    ]

    highlighted_child: Optional[WidgetSong]
    current_song: Optional[WidgetSong]
    children: List[WidgetSong]
    displayed_children: List[WidgetSong]

    def __init__(
        self,
        on_select: Callable[[WidgetSong], None],
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

    def action_cursor_down(self) -> None:
        """Highlight the next item in the list."""
        if self.index is not None:
            for index in range(self.index + 1, len(self.children)):
                if self.children[index].display:
                    self.index = index
                    break
            else:
                self.select_index(0)
        else:
            self.select_index(0)

    def action_cursor_up(self) -> None:
        """Highlight the previous item in the list."""
        if self.index is not None:
            for index in range(self.index - 1, -1, -1):
                if self.children[index].display:
                    self.index = index
                    break
            else:
                self.select_index(len(self.displayed_children) - 1)
        else:
            self.select_index(0)

    def add(self, *song: WidgetSong) -> None:
        self._add_children(*song)

    def update(self, songs: List[WidgetSong], position: Optional[int] = 0) -> None:
        self.clear()

        self._nodes = NodeList()

        for index, song in enumerate(songs):
            song.highlighted = index == position
            self._add_child(song)
            self.append(song)

        self.index = position

    def select(self, path: Path) -> None:
        for index, song in enumerate(self.displayed_children):
            if song.path == path:
                self.select_index(index)
                break

    def select_index(self, index: int) -> None:
        if index < len(self.displayed_children):
            item = self.displayed_children[index]
            children_index = self.children.index(item)

            self.index = children_index

    def filter(self, pattern: str) -> None:
        for song in self.children:
            song.display = pattern in song.path.name.lower()

    @property
    def displayed_index(self):
        if self.index is not None:
            child = self.children[self.index]
            index = self.displayed_children.index(child)
        else:
            index = None

        return index

    async def swap(self, position: int) -> None:
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
