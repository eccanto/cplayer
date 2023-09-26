"""Entry point for the Song Player Console Application.

The application provides a console-based user interface to manage and play songs, create and manage playlists,
adjust volume levels, and control song playback.

Author: Erik Ccanto
Date: 30 Jul 2023
"""

import os


os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = 'hide'

# pylint: disable=wrong-import-order, wrong-import-position

import logging
from pathlib import Path
from typing import Optional

import click
from pygame import mixer
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.widgets import Footer, Header

from cplayer import __version__
from cplayer.src.elements import CONFIG
from cplayer.src.elements.downloader import YoutubeDownloader
from cplayer.src.pages.help import HelpPage
from cplayer.src.pages.home import HomePage


__LOGGING_FORMAT = '[%(asctime)s] [%(process)d] %(filename)s:%(lineno)d - %(levelname)s - %(message)s'


class Application(App):
    """Class that represent the main application and inherits from the textual App class."""

    TITLE = f'{CONFIG.data.appearance.style.icons.playlist} Playlist'
    CSS = (
        f'$primary: {CONFIG.data.appearance.style.colors.primary}; '
        f'$background: {CONFIG.data.appearance.style.colors.background};'
    )
    CSS_PATH = Path(__file__).parent.joinpath('resources/styles/application.css')
    BINDINGS = [
        Binding(CONFIG.data.general.shortcuts.pages.quit, 'quit', 'Quit', show=True),
        Binding(CONFIG.data.general.shortcuts.pages.home, 'home', 'Home', show=True),
        Binding(CONFIG.data.general.shortcuts.pages.information, 'info', 'Info', show=True),
    ]

    def __init__(self, path: Optional[Path], *args, **kwargs) -> None:
        """Initializes the Application object.

        :param path: The optional path of the directory songs.
        :param *args: Variable length argument list.
        :param **kwargs: Arbitrary keyword arguments.
        """
        super().__init__(*args, **kwargs)

        self.home_page = HomePage(path, change_title=self.set_title, start_hidden=False)
        self.help_page = HelpPage(change_title=self.set_title)

    def compose(self) -> ComposeResult:
        """Composes the application layout.

        :returns: The ComposeResult object representing the composed layout.
        """
        yield Header()

        yield self.home_page
        yield self.help_page

        if CONFIG.data.appearance.style.footer:
            yield Footer()

    def set_title(self, title: str) -> None:
        """Sets the title of the application window.

        :param title: The title of the application window.
        """
        self.title = title

    def action_info(self) -> None:
        """Opens the information window."""
        help_page = self.query_one(HelpPage)
        help_page.show()

        home_path = self.query_one(HomePage)
        home_path.hide()

    def action_home(self) -> None:
        """Opens the home window."""
        home_path = self.query_one(HomePage)
        home_path.show()

        help_page = self.query_one(HelpPage)
        help_page.hide()


@click.command()
@click.option(
    '-p',
    '--path',
    help='Path to the directory containing your music files.',
    type=click.Path(exists=True, path_type=Path),
)
@click.option(
    '-u',
    '--url',
    help='URL of the song to download from YouTube.',
)
@click.version_option(version=__version__)
def main(path: Optional[Path], url: Optional[str]) -> None:
    # noqa: D413, D407, D412, D406
    """Command Line Python player CLI.

    This command line tool plays music files from a specified directory or last used playlist.

    Examples:

        - Play music from the current directory or the last used playlist if it exists:

          $ cplayer

        - Play music from a specific directory:

          $ cplayer --path /path/to/music_directory

        - Download song from YouTube

          $ cplayer --url 'https://www.youtube.com/watch?v=xyz'

    For more information, visit https://github.com/eccanto/cplayer
    """
    if url:
        downloader = YoutubeDownloader(url)
        downloader.download()
    else:
        mixer.init()

        app = Application(path)
        app.run()


if __name__ == '__main__':
    logging.basicConfig(
        filename=Path(CONFIG.data.development.logfile).expanduser(),
        level=logging.getLevelName(CONFIG.data.development.level),
        format=__LOGGING_FORMAT,
    )

    main()  # pylint: disable=no-value-for-parameter
