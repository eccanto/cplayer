"""Module that contains the implementation of a music player application."""

import logging
from pathlib import Path
from typing import Optional, Self, Union

from pygame import mixer
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Middle, Vertical

from cplayer.src.components.file_explorer import FileExplorerWidget
from cplayer.src.components.hidden_widget import HiddenWidget
from cplayer.src.components.input_label import InputLabelWidget
from cplayer.src.components.notification import NotificationWidget
from cplayer.src.components.options_list import Option, OptionsListWidget
from cplayer.src.components.progress_bar import ProgressStatusWidget
from cplayer.src.components.status_song import StatusSong
from cplayer.src.components.tracklist import PlaylistOrder, Song, TracklistWidget
from cplayer.src.elements import CONFIG
from cplayer.src.elements.playlist import PlayList
from cplayer.src.pages.base import PageBase


class HomePage(PageBase):  # pylint: disable=too-many-public-methods, too-many-instance-attributes
    """HomePage Class that represents the home page of the application."""

    DEFAULT_CSS = Path(__file__).parent.joinpath('styles.css').read_text(encoding='UTF-8')

    BINDINGS = [
        Binding(CONFIG.data.general.shortcuts.songs.play_pause, 'play_pause', 'Play/Pause', show=False),
        Binding(CONFIG.data.general.shortcuts.songs.decrease_volume, 'decrease_volume', 'Decrease Volume', show=True),
        Binding(CONFIG.data.general.shortcuts.songs.increase_volume, 'increase_volume', 'Increase Volume', show=True),
        Binding(CONFIG.data.general.shortcuts.songs.restart, 'reset', 'Restart', show=True),
        Binding(CONFIG.data.general.shortcuts.songs.mute, 'mute_song', 'Mute', show=True),
        Binding(CONFIG.data.general.shortcuts.playlist.load, 'load_playlist', 'Load Playlist', show=False),
        Binding(CONFIG.data.general.shortcuts.playlist.file_explorer, 'load_path', 'File Explorer', show=False),
        Binding(CONFIG.data.general.shortcuts.playlist.load_directory, 'load_directory', 'Load Directory', show=False),
        Binding(CONFIG.data.general.shortcuts.playlist.previous_song, 'previous_song', 'Previous', show=True),
        Binding(CONFIG.data.general.shortcuts.playlist.next_song, 'next_song', 'Next', show=True),
        Binding(CONFIG.data.general.shortcuts.playlist.search_songs, 'search', 'Search', show=False),
        Binding(CONFIG.data.general.shortcuts.playlist.filter_songs, 'filter', 'Filter', show=False),
        Binding(CONFIG.data.general.shortcuts.playlist.save, 'save_playlist', 'Save Playlist', show=False),
        Binding(CONFIG.data.general.shortcuts.playlist.delete_song, 'delete_song', 'Delete Song', show=False),
        Binding(CONFIG.data.general.shortcuts.playlist.add_songs, 'add_songs', 'Add songs', show=False),
        Binding(CONFIG.data.general.shortcuts.playlist.up_song, 'up_song_position', 'Up Song', show=False),
        Binding(CONFIG.data.general.shortcuts.playlist.down_song, 'down_song_position', 'Down Song', show=False),
        Binding(CONFIG.data.general.shortcuts.playlist.change_order, 'change_order', 'Playlist order', show=False),
        Binding(CONFIG.data.general.shortcuts.playlist.go_to_position, 'go_to_position', 'Go to position', show=False),
    ]

    def __init__(self, path: Optional[Path], *args, **kwargs) -> None:
        """Initializes the Page object.

        :param path: The initial songs path to be loaded.
        :param *args: Variable length argument list.
        :param **kwargs: Arbitrary keyword arguments.
        """
        super().__init__(*args, **kwargs)

        self.playlists_directory = Path(CONFIG.data.general.playlist.directory).expanduser()
        self.playlists_directory.mkdir(parents=True, exist_ok=True)

        self._start_position = 0
        self._playing = False
        self._volume = 0.75

        self.status_song_widget = StatusSong(self._volume, start_hidden=False)
        self.tracklist_widget = TracklistWidget(
            self.play_song,
            self.action_cursor_left,
            self.action_cursor_right,
            on_change_position=self.on_change_position,
            order=next(
                (order for order in PlaylistOrder if order.value == CONFIG.data.general.playlist.order),
                PlaylistOrder.ASCENDING,
            ),
            fixed_size=11 if CONFIG.data.appearance.style.footer else 8,
        )
        self.file_explorer_widget = FileExplorerWidget(Path('~').expanduser(), on_select=self.on_select_path)

        self.notification_widget = NotificationWidget('')

        self.select_playlist_widget = OptionsListWidget('Select a playlist:', self.on_quit, self.select_playlist)
        self.select_order_widget = OptionsListWidget('Select an order:', self.on_quit, self.select_order)

        self.goto_position_widget = InputLabelWidget(
            f'{CONFIG.data.appearance.style.icons.go_to_position} go to position',
            on_enter=self.on_go_to_position,
            on_quit=self.on_quit,
        )
        self.filter_widget = InputLabelWidget(
            f'{CONFIG.data.appearance.style.icons.filter} filter text',
            on_enter=self.filter_songs,
            on_quit=self.on_quit,
        )
        self.search_widget = InputLabelWidget(
            f'{CONFIG.data.appearance.style.icons.search} search text',
            on_enter=self.search_songs,
            on_quit=self.on_quit,
        )
        self.directory_widget = InputLabelWidget(
            f'{CONFIG.data.appearance.style.icons.directory} directory path',
            on_enter=self.load_directory,
            on_quit=self.on_quit,
        )
        self.playlist_name_widget = InputLabelWidget(
            f'{CONFIG.data.appearance.style.icons.save} playlist name',
            on_enter=self.enter_playlist_name,
            on_quit=self.on_quit,
        )
        self.add_songs_widget = InputLabelWidget(
            f'{CONFIG.data.appearance.style.icons.add_songs} add songs (mp3/directory)',
            on_enter=self.add_songs,
            on_quit=self.on_quit,
        )

        self.selected_directory = path
        self.selected_playlist: Optional[PlayList] = None

    def action_go_to_position(self) -> None:
        """Opens position navigator widget."""
        self.status_song_widget.hide()

        self.goto_position_widget.value = ''
        self.goto_position_widget.show()

    async def on_go_to_position(self) -> None:
        """Goes to the indicated position."""
        self.goto_position_widget.hide()
        self.status_song_widget.show()
        try:
            self.tracklist_widget.go_to(int(self.goto_position_widget.value))
        except ValueError:
            logging.error('invalid position value: %s', self.goto_position_widget.value)

        self.tracklist_widget.focus()

    def action_decrease_volume(self) -> None:
        """Decreases the volume level."""
        self._volume = (mixer.music.get_volume() - 0.1) if (mixer.music.get_volume() > 0) else 0
        mixer.music.set_volume(self._volume)

        self.status_song_widget.volume.update(progress=self._volume)

    def action_increase_volume(self) -> None:
        """Increases the volume level."""
        self._volume = 1 if (mixer.music.get_volume() > 1) else (mixer.music.get_volume() + 0.1)
        mixer.music.set_volume(self._volume)

        self.status_song_widget.volume.update(progress=self._volume)

    def action_play_pause(self) -> None:
        """Toggles play/pause for the currently playing song."""
        self._playing = not mixer.music.get_busy()
        if self._playing:
            self.status_song_widget.progress.set_status(ProgressStatusWidget.Status.PLAYING)
            mixer.music.unpause()
        else:
            self.status_song_widget.progress.set_status(ProgressStatusWidget.Status.PAUSED)
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
        """Opens a input text to filter songs in the current playlist."""
        self.status_song_widget.hide()

        self.filter_widget.show()

    def action_search(self) -> None:
        """Opens a input text to search songs in the current playlist."""
        self.status_song_widget.hide()

        self.search_widget.value = ''
        self.search_widget.show()

    def action_mute_song(self) -> None:
        """Mutes the songs."""
        mixer.music.set_volume(0 if mixer.music.get_volume() else self._volume)

        self.status_song_widget.volume.muted = mixer.music.get_volume() == 0
        self.status_song_widget.volume.update(progress=mixer.music.get_volume())

    def play_song(self, song: Song) -> None:
        """Plays the selected song.

        :param song: The song to be played.
        """
        try:
            self._start_position = 0
            mixer.music.load(song.path)
            mixer.music.play()

            self._playing = True

            self.status_song_widget.progress.set_status(ProgressStatusWidget.Status.PLAYING)
            self.status_song_widget.progress.total_seconds = (
                f'{(int(song.seconds) // 60):02}:{(int(song.seconds) % 60):02}'
            )

            if self.selected_playlist:
                self.selected_playlist.select(song.path)
        except Exception as error:  # pylint: disable=broad-exception-caught
            logging.error('Error playing the song "%s": %s', song.path, error)

            self.tracklist_widget.next_song()

            if self.parent:
                self.parent.refresh()

    def action_reset(self) -> None:
        """Resets the currently selected song."""
        if mixer.music.get_busy():
            self._start_position = 0
            mixer.music.play(0, 0)

    def on_quit(self, widget: HiddenWidget) -> None:
        """Handles quit event for the input widget.

        :param input_widget: The input widget.
        """
        widget.hide()

        self.tracklist_widget.display = True
        self.tracklist_widget.focus()

        self.notification_widget.hide()
        self.status_song_widget.show()

    async def filter_songs(self) -> None:
        """Filters and loads songs based on user input."""
        self.filter_widget.hide()
        self.status_song_widget.show()

        pattern = self.filter_widget.value.lower()
        logging.info('applying "%s" filter...', pattern)

        self.tracklist_widget.filter(pattern)
        self.tracklist_widget.display = True
        self.tracklist_widget.focus()

        self.refresh()

    async def search_songs(self) -> None:
        """Searchs a song based on user input."""
        self.search_widget.hide()
        self.status_song_widget.show()

        pattern = self.search_widget.value.lower()
        logging.info('applying "%s" search...', pattern)

        self.tracklist_widget.search(pattern)
        self.tracklist_widget.display = True
        self.tracklist_widget.focus()

    def action_previous_song(self) -> None:
        """Plays the previous song in the tracklist."""
        self.tracklist_widget.previous_song()

    def action_next_song(self) -> None:
        """Plays the next song in the tracklist."""
        self.tracklist_widget.next_song()

    def action_load_directory(self) -> None:
        """Opens the input widget to load a directory path."""
        self.status_song_widget.hide()

        self.directory_widget.show()

    def action_load_path(self) -> None:
        """Opens the file explorer to load a directory or song path."""
        self.tracklist_widget.display = False
        self.file_explorer_widget.show()

    def on_select_path(self, path: Path) -> None:
        """Handles the selection of a file path.

        :param path: The selected file path.
        """
        self._load_directory(path)

    async def load_directory(self) -> None:
        """Loads the selected directory path."""
        self._load_directory(Path(self.directory_widget.value))

    def _load_directory(self, path: Path) -> None:
        """Loads the contents of the selected directory.

        :param path: The selected directory path.
        """
        logging.info('loadding path: "%s" (exists=%s)...', path, path.exists())

        self.notification_widget.hide()

        if path.exists():
            self.directory_widget.hide()

            self.tracklist_widget.set_songs(list(path.glob('*.mp3')), sort=True)
            self.tracklist_widget.display = True
            self.tracklist_widget.focus()
            self.status_song_widget.show()
        else:
            self.notification_widget.show(message=f'[#FFFF00] [#CC0000]directory "{path}" not found')
            self.directory_widget.focus()

    async def make_progress(self) -> None:
        """Called automatically to advance the progress bar."""
        if self.tracklist_widget.current_song is not None and self._playing:
            song = self.tracklist_widget.current_song
            current_position = int((mixer.music.get_pos() / 1000) + self._start_position)

            self.status_song_widget.progress.set_progress(current_position)

            self.status_song_widget.song.update(song.path.name)

            if not mixer.music.get_busy() and self.tracklist_widget.index is not None:
                self.tracklist_widget.next_song()

    def action_save_playlist(self) -> None:
        """Saves the current playlist."""
        self.status_song_widget.hide()
        self.playlist_name_widget.show()

    def action_load_playlist(self) -> None:
        """Opens the playlists selector widget."""
        self.tracklist_widget.display = False

        self.select_playlist_widget.list_view.update(
            [
                Option(path, f'{CONFIG.data.appearance.style.icons.playlist} ', lambda path: path.stem)
                for path in self.playlists_directory.glob('*.playlist')
            ]
        )
        self.select_playlist_widget.show()

    def select_order(self, option: Union[Path, str]) -> None:
        """Selects the playlist order.

        :param option: The selected playlist order option.
        """
        self.select_order_widget.hide()

        self.tracklist_widget.order = next(
            (order for order in PlaylistOrder if order.value == option), PlaylistOrder.ASCENDING
        )
        CONFIG.data.general.playlist.order = self.tracklist_widget.order.value
        CONFIG.save()

        self.tracklist_widget.set_songs([song.path for song in self.tracklist_widget.items], sort=True)
        self.tracklist_widget.display = True
        self.tracklist_widget.focus()

        if self.tracklist_widget.current_song:
            self.tracklist_widget.select(self.tracklist_widget.current_song.path)

    def action_change_order(self) -> None:
        """Changes the current playlist order."""
        self.tracklist_widget.display = False

        self.select_order_widget.list_view.update(
            [
                Option(order.value, f'{CONFIG.data.appearance.style.icons.order} ', lambda order: order)
                for order in PlaylistOrder
            ]
        )
        self.select_order_widget.show()

    def select_playlist(self, path: Union[Path, str]) -> None:
        """Selects a playlist from the available options.

        :param path: The selected playlist path.
        """
        self.selected_playlist = PlayList(Path(path))
        self.load_playlist()

    def load_playlist(self) -> None:
        """Loads the selected playlist."""
        if self.selected_playlist and self.selected_playlist.path.exists():
            self.select_playlist_widget.hide()

            songs = [Path(path) for path in self.selected_playlist.songs]

            self.change_title(f'{CONFIG.data.appearance.style.icons.playlist} {self.selected_playlist.name}')

            logging.info('loading playlist "%s" with %s items...', self.selected_playlist.name, len(songs))

            self.tracklist_widget.set_songs(songs)
            self.tracklist_widget.display = True
            self.tracklist_widget.focus()

            if self.selected_playlist.selected:
                self.tracklist_widget.select(Path(self.selected_playlist.selected))

            CONFIG.data.general.playlist.selected = str(self.selected_playlist.path)
            CONFIG.save()

            self.refresh()
        elif self.selected_playlist:
            self.notification_widget.show(
                message=f'[#FFFF00] [#CC0000]playlist "{self.selected_playlist.path}" not found'
            )

    async def enter_playlist_name(self) -> None:
        """Enters the name for a new playlist."""
        self.notification_widget.hide()

        self.selected_playlist = PlayList(
            self.playlists_directory.joinpath(self.playlist_name_widget.value).with_suffix('.playlist')
        )
        self.selected_playlist.selected = (
            self.tracklist_widget.current_song.path if self.tracklist_widget.current_song else None
        )
        self.selected_playlist.songs = [song.path for song in self.tracklist_widget.items]
        self.selected_playlist.save()

        CONFIG.data.general.playlist.selected = str(self.selected_playlist.path)
        CONFIG.save()

        self.playlist_name_widget.hide()
        self.tracklist_widget.focus()
        self.status_song_widget.show()

    async def action_up_song_position(self) -> None:
        """Moves the selected song up in the playlist."""
        await self.tracklist_widget.swap(self.tracklist_widget.index - 1)

    async def action_down_song_position(self) -> None:
        """Moves the selected song down in the playlist."""
        await self.tracklist_widget.swap(self.tracklist_widget.index + 1)

    async def action_delete_song(self) -> None:
        """Deletes the selected song from the playlist."""
        if self.tracklist_widget.index is not None:
            songs = [song.path for song in self.tracklist_widget.items]
            del songs[self.tracklist_widget.index]

            new_size = len(songs)
            self.tracklist_widget.set_songs(
                songs,
                position=(new_size - 1) if (self.tracklist_widget.index >= new_size) else self.tracklist_widget.index,
            )

    async def action_add_songs(self) -> None:
        """Opens input widget to add songs to the playlist."""
        self.status_song_widget.hide()

        self.add_songs_widget.value = ''
        self.add_songs_widget.show()

    async def add_songs(self) -> None:
        """Add songs to the playlist from user input."""
        self.notification_widget.hide()

        path = Path(self.add_songs_widget.value)
        if path.exists():
            songs = [path] if path.is_file() else list(path.glob('*.mp3'))
            if songs:
                self.add_songs_widget.hide()
                self.tracklist_widget.add(songs)
                self.tracklist_widget.focus()
                self.status_song_widget.show()
            else:
                self.notification_widget.show(message=f'[#FFFF00] [#CC0000]songs "{path}" not found')
        else:
            self.notification_widget.show(message=f'[#FFFF00] [#CC0000]file "{path}" not found')

    def on_change_position(self, index: int, total: int) -> None:
        """Updates the position indicator widget."""
        self.status_song_widget.position.update(f'{index + 1}/{total}')

    def compose(self) -> ComposeResult:
        """Composes the elements for the home page.

        :returns: The composed elements for the home page.
        """
        yield self.select_playlist_widget
        yield self.select_order_widget

        yield self.tracklist_widget
        yield self.file_explorer_widget

        with Middle(classes='bottom full-width'):
            with Vertical(classes='bottom full-width panel'):
                with Horizontal(classes='full-width'):
                    yield self.status_song_widget

                    yield self.goto_position_widget
                    yield self.filter_widget
                    yield self.search_widget
                    yield self.directory_widget
                    yield self.playlist_name_widget
                    yield self.add_songs_widget

                yield self.notification_widget

    def on_mount(self) -> None:
        """Handles events on the mounting of the home page."""
        super().on_mount()

        self.set_interval(0.5, self.make_progress, pause=False)

        if self.selected_directory is not None:
            self._load_directory(self.selected_directory)
        elif CONFIG.data.general.playlist.selected:
            self.selected_playlist = PlayList(Path(CONFIG.data.general.playlist.selected))
            self.load_playlist()
        else:
            path = Path('.')
            self._load_directory(path)
            self.change_title(f'{CONFIG.data.appearance.style.icons.directory} {path.absolute()}')

        mixer.music.set_volume(self._volume)

    def focus(self, scroll_visible: bool = True) -> Self:
        """Sets the focus on the home page.

        :param scroll_visible: Whether to show the scroll.
        """
        self.tracklist_widget.focus(scroll_visible)
        return self
