import os
from typing import Tuple, cast

from pydub.utils import json
from textual.binding import Binding

from components.hidden_widget.widget import HiddenWidget
from components.input_label.widget import InputLabel
from components.notification.widget import Notification
from components.options_list.widget import Option, OptionsList
from components.playlist.widget import Playlist, Song
from components.progress_bar.widget import ProgressStatus
from components.volume_bar.widget import VolumeBar

os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = 'hide'

from pathlib import Path

from pygame import mixer
from textual.app import ComposeResult
from textual.containers import Center, Middle, Horizontal, Vertical
from textual.timer import Timer
from textual.widgets import Label
from textual._node_list import NodeList


class HomePage(HiddenWidget):
    DEFAULT_CSS = Path(__file__).parent.joinpath('styles.css').read_text()

    BINDINGS = [
        Binding('space', 'play_pause', 'Play/Pause', show=False),
        Binding('-', 'decrease_volume', 'Decrease Volume', show=True),
        Binding('+', 'increase_volume', 'Increase Volume', show=True),
        Binding('l', 'load_playlist', 'Load Playlist', show=False),
        Binding('d', 'load_directory', 'Load Directory', show=False),
        Binding('p', 'previous_song', 'Previous', show=True),
        Binding('n', 'next_song', 'Next', show=True),
        Binding('r', 'reset', 'Restart', show=True),
        Binding('s', 'search', 'Search', show=False),
        Binding('f', 'filter', 'Filter', show=False),
        Binding('S', 'save_playlist', 'Save Playlist', show=False),
        Binding('delete', 'delete_song', 'Delete Song', show=False),
        Binding('A', 'add_songs', 'Add songs', show=False),
        Binding('ctrl+up', 'up_song_position', 'Up Song', show=False),
        Binding('ctrl+down', 'down_song_position', 'Down Song', show=False),
    ]

    _PLAYLISTS_DIRECTORY = Path('~/.playlists/').expanduser()

    progress_timer: Timer

    def __init__(self, songs, start_hidden: bool = False, *args, **kwargs):
        super().__init__(*args, start_hidden=start_hidden, **kwargs)

        self._directory = songs

        self._start_position = 0
        self._playing = False
        self._playlist = None

        self._songs = [Song(path) for path in self._directory.glob('*.mp3')][:20]

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

        volume_bar = self.query_one(VolumeBar)
        volume_bar.update(total=1, progress=mixer.music.get_volume())

    def action_increase_volume(self):
        mixer.music.set_volume(1 if (mixer.music.get_volume() > 1) else (mixer.music.get_volume() + 0.1))

        volume_bar = self.query_one(VolumeBar)
        volume_bar.update(total=1, progress=mixer.music.get_volume())

    def action_play_pause(self):
        bar = self.query_one(ProgressStatus)

        self._playing = not mixer.music.get_busy()
        if self._playing:
            bar.set_status(ProgressStatus.Status.PLAYING)
            mixer.music.unpause()
        else:
            bar.set_status(ProgressStatus.Status.PAUSED)
            mixer.music.pause()

    def action_cursor_left(self):
        if mixer.music.get_busy():
            self._start_position = max(self._start_position + mixer.music.get_pos() / 1000. - 5, 0)
            mixer.music.play(0, self._start_position)

    def action_cursor_right(self):
        if mixer.music.get_busy():
            self._start_position += mixer.music.get_pos() / 1000. + 5
            mixer.music.play(0, self._start_position)

    def action_filter(self):
        search_input = self.query_one('#search-input')
        search_input.display = True
        search_input.focus()

    def play_song(self, song: Song):
        self._start_position = 0
        song.play()

        self._playing = True

        bar = self.query_one(ProgressStatus)
        bar.set_status(ProgressStatus.Status.PLAYING)

    def action_reset(self):
        if mixer.music.get_busy():
            self._start_position = 0
            mixer.music.play(0, 0)

    def on_input_quit(self, input_widget: InputLabel):
        input_widget.display = False
        playlist = self.query_one(Playlist)
        playlist.focus()

        notification = self.query_one(Notification)
        notification.hide()

    async def filter_songs(self):
        search_input = cast(InputLabel, self.query_one('#search-input'))
        search_input.hide()

        playlist = cast(Playlist, self.query_one(Playlist))
        playlist.update([song for song in self._songs if search_input.value.lower() in song.path.name.lower()])
        playlist.focus()

    def action_previous_song(self) -> None:
        playlist = self.query_one(Playlist)
        if playlist.index:
            playlist.index -= 1
            playlist.action_select_cursor()

    def action_next_song(self) -> None:
        playlist = self.query_one(Playlist)
        if playlist.index is not None:
            playlist.index += 1
            playlist.action_select_cursor()

    def action_load_directory(self):
        directory_input = self.query_one('#directory-input')
        directory_input.display = True
        directory_input.focus()

    async def load_directory(self):
        search_input = cast(InputLabel, self.query_one('#directory-input'))

        notification = self.query_one(Notification)
        notification.hide()

        playlist = self.query_one(Playlist)
        playlist._nodes = NodeList()

        self._directory = Path(search_input.value)

        if self._directory.exists():
            self._songs = [Song(path) for path in self._directory.glob('*.mp3')][:10]
            if self._songs:
                search_input.hide()

                for song in self._songs:
                    song.highlighted = False
                    playlist._add_child(song)

                playlist.focus()
                playlist.index = 0
            else:
                notification.show(f'[#FFFF00] [#CC0000]songs "{self._directory}" not found')
        else:
            notification.show(f'[#FFFF00] [#CC0000]directory "{self._directory}" not found')
            search_input.focus()

    def make_progress(self) -> None:
        """Called automatically to advance the progress bar."""
        playlist = self.query_one(Playlist)
        song = cast(Song, playlist.current_song)

        if song is not None:
            if self._playing:
                current_position = int((mixer.music.get_pos() / 1000) + self._start_position)
                song_time_bar = self.query_one(ProgressStatus)
                song_time_bar.update(total=song.seconds, progress=current_position)

                bar = self.query_one(ProgressStatus)
                bar.set_progress(current_position, song.seconds)

                song_label = cast(Label, self.query_one('#song-label'))
                song_label.update(song.path.name)

                effects_label = cast(Label, self.query_one('#effects-label'))
                current_ms = int(mixer.music.get_pos() * song.frame_rate / 1000)
                effects_label.update(self.__spectrum(song.buffer[current_ms : current_ms + 100:2], (2, 12)))

                if not mixer.music.get_busy() and playlist.index is not None:
                    playlist.index += 1
                    playlist.action_select_cursor()

    def action_save_playlist(self) -> None:
        playlist_name_input = self.query_one('#playlist-name-input')
        playlist_name_input.display = True
        playlist_name_input.focus()

    def action_load_playlist(self) -> None:
        playlist = self.query_one(Playlist)
        playlist.display = False

        playlists = self.query_one(OptionsList)
        playlists.list_view.update([Option(path, '') for path in self._PLAYLISTS_DIRECTORY.glob('*.playlist')])
        playlists.show()
        playlists.focus()

    def load_playlist(self, path: Path) -> None:
        if path.exists():
            playlists = self.query_one(OptionsList)
            playlists.hide()

            with open(path) as playlist_file:
                playlist_data = json.load(playlist_file)

            self._songs = [Song(Path(path)) for path in playlist_data['songs']]

            self.title = f' {path.stem.title()} Playlist'

            playlist = self.query_one(Playlist)
            playlist.update(self._songs)
            playlist.display = True
            playlist.focus()
        else:
            notification = self.query_one(Notification)
            notification.show(f'[#FFFF00] [#CC0000]playlist "{path}" not found')

    async def enter_playlist_name(self) -> None:
        playlist_name_input = cast(InputLabel, self.query_one('#playlist-name-input'))

        notification = self.query_one(Notification)
        notification.hide()

        playlist = self.query_one(Playlist)

        self._playlist = self._PLAYLISTS_DIRECTORY.joinpath(playlist_name_input.value).with_suffix('.playlist')
        self._PLAYLISTS_DIRECTORY.mkdir(parents=True, exist_ok=True)

        with open(self._playlist, 'w') as playlist_file:
            json.dump(
                {
                    'name': self._playlist.name,
                    'path': str(self._playlist),
                    'selected': str(playlist.current_song.path) if playlist.current_song else None,
                    'songs': [str(song.path) for song in self._songs]
                },
                playlist_file,
                indent=2,
            )

        playlist_name_input.hide()
        playlist.focus()

    async def action_up_song_position(self) -> None:
        playlist = self.query_one(Playlist)
        if playlist.index is not None:
            await playlist.swap(playlist.index - 1)

    async def action_down_song_position(self) -> None:
        playlist = self.query_one(Playlist)
        if playlist.index is not None:
            await playlist.swap(playlist.index + 1)

    async def action_delete_song(self) -> None:
        playlist = self.query_one(Playlist)
        if playlist.index is not None:
            del self._songs[playlist.index]

            playlist.update(self._songs, position=(len(self._songs) - 1) if (playlist.index >= len(self._songs)) else playlist.index)

    async def action_add_songs(self) -> None:
        add_songs_input = cast(InputLabel, self.query_one('#add-songs-input'))
        add_songs_input.show()

    async def add_songs(self) -> None:
        add_songs_input = cast(InputLabel, self.query_one('#add-songs-input'))

        notification = self.query_one(Notification)
        notification.hide()

        path = Path(add_songs_input.value)
        if path.exists():
            playlist = self.query_one(Playlist)

            if path.is_file():
                songs = [Song(path)]
            else:
                songs = [Song(song_path) for song_path in path.glob('*.mp3')]

            if songs:
                add_songs_input.hide()

                self._songs.extend(songs)

                playlist.add(*songs)
                playlist.focus()
            else:
                notification.show(f'[#FFFF00] [#CC0000]songs "{path}" not found')
        else:
            notification.show(f'[#FFFF00] [#CC0000]file "{path}" not found')

    def compose(self) -> ComposeResult:
        yield InputLabel(
            ' filter:',
            on_enter=self.filter_songs,
            on_quit=self.on_input_quit,
            id='search-input',
        )
        yield InputLabel(
            ' directory:',
            on_enter=self.load_directory,
            on_quit=self.on_input_quit,
            id='directory-input',
        )
        yield InputLabel(
            ' playlist name:',
            on_enter=self.enter_playlist_name,
            on_quit=self.on_input_quit,
            id='playlist-name-input',
        )
        yield InputLabel(
            ' add songs (mp3/directory):',
            on_enter=self.add_songs,
            on_quit=self.on_input_quit,
            id='add-songs-input',
        )

        yield Notification('')

        yield OptionsList('Select a playlist:', lambda _: None, self.load_playlist)

        yield Playlist(
            self.play_song,
            self.action_cursor_left,
            self.action_cursor_right,
            *self._songs,
        )

        with Middle(classes='bottom'):
            with Center(classes='player-panel'):
                with Horizontal(classes='full-width'):
                    with Vertical(classes='panel'):
                        yield Label('-', id='song-label', classes='bold')
                        with Horizontal():
                            yield ProgressStatus()
                            yield VolumeBar()
                    with Vertical(classes='panel'):
                        yield Label(self.__spectrum([], (2, 12)), id='effects-label', classes='bold')

    def on_mount(self) -> None:
        self.progress_timer = self.set_interval(1 / 10, self.make_progress, pause=False)

    def focus(self) -> None:
        playlist = self.query_one(Playlist)
        playlist.focus()
