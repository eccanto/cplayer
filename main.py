import os
from typing import Tuple
import numpy

from textual.widgets._list_item import ListItem

os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = 'hide'

from pathlib import Path

import click
from pygame import mixer
from pydub import AudioSegment
from textual.app import App, ComposeResult
from textual.containers import Center, Middle, Horizontal, Vertical
from textual.timer import Timer
from textual.widgets import Label, Footer, ProgressBar, ListView, ListItem, Header


class Song(ListItem):
    def __init__(self, path: Path, *args, **kwargs) -> None:
        super().__init__(Label(path.name), *args, **kwargs)

        self.path = path

        self._seconds = None
        self._audio = None
        self.frame_rate = None
        self._buffer = None

    def __str__(self) -> str:
        return self.path.name

    def __repr__(self) -> str:
        return self.path.name

    def play(self):
        mixer.music.load(self.path)
        mixer.music.play()

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
        ('up', 'cursor_up', 'Cursor Up'),
        ('down', 'cursor_down', 'Cursor Down'),
        ('enter', 'select_cursor', 'Reproduce'),
    ]

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.current_song = None

    def action_select_cursor(self) -> None:
        self.current_song = self.highlighted_child
        self.current_song.play()


class Application(App):
    TITLE = '♪ Pochita playlist'
    CSS_PATH = 'resources/styles/application.css'
    BINDINGS = [
        ('q', 'quit', 'Quit'),
        ('space', 'play_pause', 'Play/Pause'),
        ('-', 'decrease_volume', 'Decrease Volume'),
        ('+', 'increase_volume', 'Increase Volume'),
    ]

    progress_timer: Timer

    def __init__(self, songs, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._songs = songs

    def __spectrum(self, data, shape: Tuple[int, int]):
        if not len(data):
            points = [f'[rgb(100,100,100)]●' for _ in range(shape[0] * shape[1])]
        else:
            max_value = max([abs(v) for v in data])
            grades = [v/max_value for v in data] if max_value else []
            points = [f'[rgb({int(255 * abs(v))},{int(255 * abs(v))},{int(255 * abs(v))})]●' for v in grades]

            if len(points) < (shape[0] * shape[1]):
                points = [f'[rgb(100,100,100)]●' for _ in range(shape[0] * shape[1])]

        return ' '.join(points[:shape[1]]) + '\n' + ' '.join(points[shape[1]:2 * shape[1]])

    def action_decrease_volume(self):
        mixer.music.set_volume((mixer.music.get_volume() - 0.1) if (mixer.music.get_volume() > 0) else 0)

        volume_bar = self.query_one('#volume-bar')
        volume_bar.update(total=1, progress=mixer.music.get_volume())

    def action_increase_volume(self):
        mixer.music.set_volume(1 if (mixer.music.get_volume() > 1) else (mixer.music.get_volume() + 0.1))

        volume_bar = self.query_one('#volume-bar')
        volume_bar.update(total=1, progress=mixer.music.get_volume())

    def action_play_pause(self):
        if mixer.music.get_busy():
            mixer.music.pause()
        else:
            mixer.music.unpause()

    def compose(self) -> ComposeResult:
        yield Header()

        yield Playlist(*[Song(path) for path in self._songs.glob('*.mp3')])

        with Middle():
            with Center():
                with Horizontal():
                    with Vertical(classes='panel'):
                        yield Label('-', id='song-label', classes='bold')
                        with Horizontal():
                            yield Label('⏵⏸⏹', id='reproduce-label')
                            yield ProgressBar(show_eta=False, show_percentage=False, id='song-time-bar')
                            yield Label('00:00/00:00', id='progress-label', classes='bold')
                            yield Label('', id='volume-label')
                            yield ProgressBar(show_eta=False, show_percentage=False, id='volume-bar')
                    with Vertical(classes='panel'):
                        yield Label(self.__spectrum([], (2, 12)), id='effects-label', classes='bold')

        yield Footer()

    def on_mount(self) -> None:
        self.progress_timer = self.set_interval(1 / 10, self.make_progress, pause=False)

        progress_bar = self.query_one('#song-time-bar').query_one('#bar')
        progress_bar.styles.width = 60

        volume_bar = self.query_one('#volume-bar')
        volume_bar.update(total=1)
        volume_bar.advance(1)
        volume_bar.query_one('#bar').styles.width = 12

        playlist = self.query_one(Playlist)
        playlist.focus()

    def make_progress(self) -> None:
        """Called automatically to advance the progress bar."""
        song = self.query_one(Playlist).current_song
        if song is not None:
            current_position = int(mixer.music.get_pos() / 1000)
            self.query_one('#song-time-bar').update(total=song.seconds, progress=current_position)

            duration_label = self.query_one('#progress-label')
            duration_label.update(
                f'{(current_position // 60):02}:{(current_position % 60):02}'
                '/'
                f'{(int(song.seconds) // 60):02}:{(int(song.seconds) % 60):02}'
            )

            song_label = self.query_one('#song-label')
            song_label.update(song.path.name)

            effects_label = self.query_one('#effects-label')
            current_ms = int(mixer.music.get_pos() * song.frame_rate / 1000)
            effects_label.update(self.__spectrum(song.buffer[current_ms : current_ms + 100:2], (2, 12)))


@click.command()
@click.option( '-s', '--songs', help=f'Songs directory.', type=click.Path(exists=True, path_type=Path), required=True)
def main(songs):
    mixer.init()
    mixer.music.set_volume(1)

    app = Application(songs)
    app.run()


if __name__ == '__main__':
    main()
