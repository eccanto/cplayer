"""Module that contains the implementation of a music player application."""

import logging
from pathlib import Path
from typing import Optional, Self, Tuple, Union, cast

from pygame import mixer
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Center, Horizontal, Middle, Vertical
from textual.widgets import Label

from src.components.file_explorer import FileExplorerWidget
from src.components.input_label import InputLabelWidget
from src.components.notification import NotificationWidget
from src.components.options_list import OptionsListWidget, OptionWidget
from src.components.progress_bar import ProgressStatusWidget
from src.components.tracklist import PlaylistOrder, SongWidget, TracklistWidget
from src.components.volume_bar import VolumeBarWidget
from src.elements.config import Config
from src.elements.playlist import PlayList
from src.pages.base import PageBase


class HomePage(PageBase):  # pylint: disable=too-many-public-methods
    """HomePage Class that represents the home page of the application."""

    DEFAULT_CSS = Path(__file__).parent.joinpath('styles.css').read_text(encoding='UTF-8')

    BINDINGS = [
        Binding('space', 'play_pause', 'Play/Pause', show=False),
        Binding('-', 'decrease_volume', 'Decrease Volume', show=True),
        Binding('+', 'increase_volume', 'Increase Volume', show=True),
        Binding('l', 'load_playlist', 'Load Playlist', show=False),
        Binding('d', 'load_path', 'File Explorer', show=False),
        Binding('ctrl+d', 'load_directory_path', 'Load Directory Path', show=False),
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
        Binding('o', 'change_order', 'Change playlist order', show=False),
    ]

    def __init__(self, path: Optional[Path], *args, **kwargs) -> None:
        """Initializes the Page object.

        :param path: The initial songs path to be loaded.
        :param *args: Variable length argument list.
        :param **kwargs: Arbitrary keyword arguments.
        """
        super().__init__(*args, **kwargs)

        self.config = Config()

        self.playlists_directory = Path(self.config.general.playlist.directory).expanduser()
        self.playlists_directory.mkdir(parents=True, exist_ok=True)

        self._start_position = 0
        self._playing = False

        self.selected_directory = path
        self.selected_playlist: Optional[PlayList] = None

    def __spectrum(self, data, shape: Tuple[int, int]) -> str:
        """Generates audio spectrum data as a string.

        :param data: The audio spectrum data.
        :param shape: The shape of the data as a tuple (rows, cols).
        """
        if data:
            max_value = max(abs(v) for v in data)
            grades = [v / max_value for v in data] if max_value else []
            points = [f'[rgb({int(255 * abs(v))},{int(255 * abs(v))},{int(255 * abs(v))})]●' for v in grades]

            if len(points) < (shape[0] * shape[1]):
                points = ['[rgb(100,100,100)]●' for _ in range(shape[0] * shape[1])]
        else:
            points = ['[rgb(100,100,100)]●' for _ in range(shape[0] * shape[1])]

        return ' '.join(points[: shape[1]]) + '\n' + ' '.join(points[shape[1] : 2 * shape[1]])

    def action_decrease_volume(self) -> None:
        """Decreases the volume level."""
        mixer.music.set_volume((mixer.music.get_volume() - 0.1) if (mixer.music.get_volume() > 0) else 0)

        volume_bar = self.query_one(VolumeBarWidget)
        volume_bar.update(total=1, progress=mixer.music.get_volume())

    def action_increase_volume(self) -> None:
        """Increases the volume level."""
        mixer.music.set_volume(1 if (mixer.music.get_volume() > 1) else (mixer.music.get_volume() + 0.1))

        volume_bar = self.query_one(VolumeBarWidget)
        volume_bar.update(total=1, progress=mixer.music.get_volume())

    def action_play_pause(self) -> None:
        """Toggles play/pause for the currently playing song."""
        progress_bar = self.query_one(ProgressStatusWidget)

        self._playing = not mixer.music.get_busy()
        if self._playing:
            progress_bar.set_status(ProgressStatusWidget.Status.PLAYING)
            mixer.music.unpause()
        else:
            progress_bar.set_status(ProgressStatusWidget.Status.PAUSED)
            mixer.music.pause()

    def action_cursor_left(self, seconds: int = 5) -> None:
        """Move the playback position `seconds` backward."""
        if mixer.music.get_busy():
            self._start_position = max(int(self._start_position + mixer.music.get_pos() / 1000.0 - seconds), 0)
            mixer.music.play(0, self._start_position)

    def action_cursor_right(self, seconds: int = 5) -> None:
        """Move the playback position `seconds` forward."""
        if mixer.music.get_busy():
            self._start_position += int(mixer.music.get_pos() / 1000.0) + seconds
            mixer.music.play(0, self._start_position)

    def action_filter(self) -> None:
        """Opens the file explorer to filter songs in the current playlist."""
        search_input = self.query_one('#search-input')
        search_input.display = True
        search_input.focus()

    def play_song(self, song: SongWidget) -> None:
        """Plays the selected song.

        :param song: The song to be played.
        """
        self._start_position = 0
        song.play()

        self._playing = True

        progress_bar = self.query_one(ProgressStatusWidget)
        progress_bar.set_status(ProgressStatusWidget.Status.PLAYING)

        if self.selected_playlist:
            self.selected_playlist.select(song.path)

    def action_reset(self) -> None:
        """Resets the currently selected song."""
        if mixer.music.get_busy():
            self._start_position = 0
            mixer.music.play(0, 0)

    def on_input_quit(self, input_widget: InputLabelWidget) -> None:
        """Handles quit event for the input widget.

        :param input_widget: The input widget.
        """
        input_widget.display = False
        playlist = self.query_one(TracklistWidget)
        playlist.focus()

        notification = self.query_one(NotificationWidget)
        notification.hide()

    async def filter_songs(self) -> None:
        """Filters and loads songs based on user input."""
        search_input = cast(InputLabelWidget, self.query_one('#search-input'))
        search_input.hide()

        pattern = search_input.value.lower()
        logging.info('applying "%s" filter...', pattern)

        playlist = self.query_one(TracklistWidget)
        playlist.filter(pattern)
        playlist.display = True
        playlist.select_index(0)
        playlist.focus()

        self.refresh()

    def action_previous_song(self) -> None:
        """Plays the previous song in the tracklist."""
        playlist = self.query_one(TracklistWidget)
        if playlist.index:
            playlist.index -= 1
            playlist.action_select_cursor()

    def action_next_song(self) -> None:
        """Plays the next song in the tracklist."""
        playlist = self.query_one(TracklistWidget)
        if playlist.index is not None:
            playlist.index += 1
            playlist.action_select_cursor()

    def action_load_directory_path(self) -> None:
        """Opens the input widget to load a directory path."""
        directory_input = self.query_one('#directory-input')
        directory_input.display = True
        directory_input.focus()

    def action_load_path(self) -> None:
        """Opens the file explorer to load a directory or song path."""
        playlist = self.query_one(TracklistWidget)
        playlist.display = False

        file_explorer = self.query_one(FileExplorerWidget)
        file_explorer.show()

    def on_select_path(self, path: Path) -> None:
        """Handles the selection of a file path.

        :param path: The selected file path.
        """
        self._load_directory(path)

    async def load_directory(self) -> None:
        """Loads the selected directory path."""
        search_input = cast(InputLabelWidget, self.query_one('#directory-input'))

        self._load_directory(Path(search_input.value))

    def _load_directory(self, path: Path) -> None:
        """Loads the contents of the selected directory.

        :param path: The selected directory path.
        """
        logging.info('loadding path: "%s" (exists=%s)...', path, path.exists())

        search_input = cast(InputLabelWidget, self.query_one('#directory-input'))

        notification = self.query_one(NotificationWidget)
        notification.hide()

        if path.exists():
            search_input.hide()

            playlist = self.query_one(TracklistWidget)
            playlist.update(list(path.glob('*.mp3')), sort=True)
            playlist.display = True
            playlist.focus()
        else:
            notification.show(f'[#FFFF00] [#CC0000]directory "{path}" not found')
            search_input.focus()

    def make_progress(self) -> None:
        """Called automatically to advance the progress bar."""
        playlist = self.query_one(TracklistWidget)
        song = cast(SongWidget, playlist.current_song)

        if song is not None and song.frame_rate and song.buffer:
            if self._playing:
                current_position = int((mixer.music.get_pos() / 1000) + self._start_position)
                song_time_bar = self.query_one(ProgressStatusWidget)
                song_time_bar.update(total=song.seconds, progress=current_position)

                progress_bar = self.query_one(ProgressStatusWidget)
                progress_bar.set_progress(current_position, song.seconds)

                song_label = cast(Label, self.query_one('#song-label'))
                song_label.update(song.path.name)

                if self.config.appearance.widgets.home.spectrum:
                    effects_label = cast(Label, self.query_one('#effects-label'))
                    current_ms = int(mixer.music.get_pos() * song.frame_rate / 1000)
                    effects_label.update(self.__spectrum(song.buffer[current_ms : current_ms + 100 : 2], (2, 12)))

                if not mixer.music.get_busy() and playlist.index is not None:
                    playlist.index += 1
                    playlist.action_select_cursor()

    def action_save_playlist(self) -> None:
        """Saves the current playlist."""
        playlist_name_input = self.query_one('#playlist-name-input')
        playlist_name_input.display = True
        playlist_name_input.focus()

    def action_load_playlist(self) -> None:
        """Opens the playlists selector widget."""
        playlist = self.query_one(TracklistWidget)
        playlist.display = False

        playlists = cast(OptionsListWidget, self.query_one('#playlist-choices'))
        playlists.list_view.update([OptionWidget(name, ' ') for name in self.playlists_directory.glob('*.playlist')])
        playlists.show()

    def select_order(self, option: Union[Path, str]) -> None:
        """Selects the playlist order.

        :param option: The selected playlist order option.
        """
        order_choices = cast(OptionsListWidget, self.query_one('#order-choices'))
        order_choices.hide()

        playlist = self.query_one(TracklistWidget)

        playlist.order = next((order for order in PlaylistOrder if order.value == option), PlaylistOrder.ASCENDING)
        self.config.general.playlist.order = playlist.order.value
        self.config.save()

        playlist.update(playlist.items, sort=True)
        playlist.display = True
        playlist.focus()

    def action_change_order(self) -> None:
        """Changes the current playlist order."""
        playlist = self.query_one(TracklistWidget)
        playlist.display = False

        order_choices = cast(OptionsListWidget, self.query_one('#order-choices'))
        order_choices.list_view.update([OptionWidget(order.value, ' ') for order in PlaylistOrder])
        order_choices.show()

    def select_playlist(self, path: Union[Path, str]) -> None:
        """Selects a playlist from the available options.

        :param path: The selected playlist path.
        """
        self.selected_playlist = PlayList(Path(path))
        self.load_playlist()

    def load_playlist(self) -> None:
        """Loads the selected playlist."""
        if self.selected_playlist and self.selected_playlist.path.exists():
            playlists = cast(OptionsListWidget, self.query_one('#playlist-choices'))
            playlists.hide()

            songs = [Path(path) for path in self.selected_playlist.songs]

            self.change_title(f' {self.selected_playlist.name} Playlist')

            logging.info('loading playlist "%s" with %s items...', self.selected_playlist.name, len(songs))

            playlist = self.query_one(TracklistWidget)
            playlist.update(songs)
            playlist.display = True
            playlist.focus()

            if self.selected_playlist.selected:
                playlist.select(Path(self.selected_playlist.selected))

            self.config.general.playlist.selected = str(self.selected_playlist.path)
            self.config.save()

            self.refresh()
        elif self.selected_playlist:
            notification = self.query_one(NotificationWidget)
            notification.show(f'[#FFFF00] [#CC0000]playlist "{self.selected_playlist.path}" not found')

    async def enter_playlist_name(self) -> None:
        """Enters the name for a new playlist."""
        playlist_name_input = cast(InputLabelWidget, self.query_one('#playlist-name-input'))

        notification = self.query_one(NotificationWidget)
        notification.hide()

        playlist_widget = self.query_one(TracklistWidget)

        self.selected_playlist = PlayList(
            self.playlists_directory.joinpath(playlist_name_input.value).with_suffix('.playlist')
        )
        self.selected_playlist.selected = playlist_widget.current_song.path if playlist_widget.current_song else None
        self.selected_playlist.songs = playlist_widget.items
        self.selected_playlist.save()

        self.config.general.playlist.selected = str(self.selected_playlist.path)
        self.config.save()

        playlist_name_input.hide()
        playlist_widget.focus()

    async def action_up_song_position(self) -> None:
        """Moves the selected song up in the playlist."""
        playlist = self.query_one(TracklistWidget)
        if playlist.displayed_index is not None:
            await playlist.swap(playlist.displayed_index - 1)

    async def action_down_song_position(self) -> None:
        """Moves the selected song down in the playlist."""
        playlist = self.query_one(TracklistWidget)
        if playlist.displayed_index is not None:
            await playlist.swap(playlist.displayed_index + 1)

    async def action_delete_song(self) -> None:
        """Deletes the selected song from the playlist."""
        playlist = self.query_one(TracklistWidget)
        if playlist.index is not None:
            songs = [widget.path for widget in playlist.children]
            del songs[playlist.index]

            playlist.update(
                songs,
                position=(len(playlist.children) - 1) if (playlist.index >= len(playlist.children)) else playlist.index,
            )

    async def action_add_songs(self) -> None:
        """Opens input widget to add songs to the playlist."""
        add_songs_input = cast(InputLabelWidget, self.query_one('#add-songs-input'))
        add_songs_input.show()

    async def add_songs(self) -> None:
        """Add songs to the playlist from user input."""
        add_songs_input = cast(InputLabelWidget, self.query_one('#add-songs-input'))

        notification = self.query_one(NotificationWidget)
        notification.hide()

        path = Path(add_songs_input.value)
        if path.exists():
            playlist = self.query_one(TracklistWidget)

            if path.is_file():
                songs = [path]
            else:
                songs = list(path.glob('*.mp3'))

            if songs:
                add_songs_input.hide()
                playlist.add(songs)
                playlist.focus()
            else:
                notification.show(f'[#FFFF00] [#CC0000]songs "{path}" not found')
        else:
            notification.show(f'[#FFFF00] [#CC0000]file "{path}" not found')

    def compose(self) -> ComposeResult:
        """Composes the elements for the home page.

        :returns: The composed elements for the home page.
        """
        yield InputLabelWidget(
            ' filter text:',
            on_enter=self.filter_songs,
            on_quit=self.on_input_quit,
            id='search-input',
        )
        yield InputLabelWidget(
            ' directory path:',
            on_enter=self.load_directory,
            on_quit=self.on_input_quit,
            id='directory-input',
        )
        yield InputLabelWidget(
            '󰆓 playlist name:',
            on_enter=self.enter_playlist_name,
            on_quit=self.on_input_quit,
            id='playlist-name-input',
        )
        yield InputLabelWidget(
            ' add songs (mp3/directory):',
            on_enter=self.add_songs,
            on_quit=self.on_input_quit,
            id='add-songs-input',
        )

        yield NotificationWidget('')

        yield OptionsListWidget('Select a playlist:', lambda _: None, self.select_playlist, id='playlist-choices')
        yield OptionsListWidget('Select an order:', lambda _: None, self.select_order, id='order-choices')

        yield TracklistWidget(
            self.play_song,
            self.action_cursor_left,
            self.action_cursor_right,
            order=next(
                (order for order in PlaylistOrder if order.value == self.config.general.playlist.order),
                PlaylistOrder.ASCENDING,
            ),
        )

        yield FileExplorerWidget(Path('~').expanduser(), on_select=self.on_select_path)

        with Middle(classes='bottom'):
            with Center(classes='player-panel'):
                with Horizontal(classes='full-width'):
                    with Vertical(classes='panel'):
                        yield Label('-', id='song-label', classes='bold')
                        with Horizontal():
                            yield ProgressStatusWidget()
                            yield VolumeBarWidget()
                    if self.config.appearance.widgets.home.spectrum:
                        with Vertical(classes='panel'):
                            yield Label(self.__spectrum([], (2, 12)), id='effects-label', classes='bold')

    def on_mount(self) -> None:
        """Handles events on the mounting of the home page."""
        super().on_mount()

        self.set_interval(1 / 10, self.make_progress, pause=False)

        if self.selected_directory is not None:
            self._load_directory(self.selected_directory)
        elif self.config.general.playlist.selected:
            self.selected_playlist = PlayList(Path(self.config.general.playlist.selected))
            self.load_playlist()

    def focus(self, scroll_visible: bool = True) -> Self:
        """Sets the focus on the home page.

        :param scroll_visible: Whether to show the scroll.
        """
        playlist = self.query_one(TracklistWidget)
        playlist.focus(scroll_visible)
        return self
