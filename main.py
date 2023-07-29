import os


os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = 'hide'

# pylint: disable=wrong-import-position

import logging
from pathlib import Path
from typing import Optional

import click
from pygame import mixer
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.widgets import Footer, Header

from src.elements.config import Config
from src.pages.help import HelpPage
from src.pages.home import HomePage


__LOGGING_FORMAT = '[%(asctime)s] [%(process)d] %(filename)s:%(lineno)d - %(levelname)s - %(message)s'
__DEFAULT_CONFIG = Path('./resources/config/default.yaml')


class Application(App):
    TITLE = ' Playlist'
    CSS_PATH = 'resources/styles/application.css'
    BINDINGS = [
        Binding('q', 'quit', 'Quit', show=True),
        Binding('h', 'home', 'Home', show=True),
        Binding('i', 'info', 'Info', show=True),
    ]

    def __init__(self, path: Optional[Path], *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.path = path

    def compose(self) -> ComposeResult:
        yield Header()

        yield HomePage(self.path, change_title=self.set_title, start_hidden=False)
        yield HelpPage(change_title=self.set_title)

        yield Footer()

    def set_title(self, title) -> None:
        self.title = title

    def action_info(self) -> None:
        help_page = self.query_one(HelpPage)
        help_page.show()

        home_path = self.query_one(HomePage)
        home_path.hide()

    def action_home(self) -> None:
        home_path = self.query_one(HomePage)
        home_path.show()

        help_page = self.query_one(HelpPage)
        help_page.hide()


@click.command()
@click.option('-p', '--path', help='Songs directory path.', type=click.Path(exists=True, path_type=Path))
def main(path: Optional[Path]):
    mixer.init()
    mixer.music.set_volume(1)

    app = Application(path)
    app.run()


if __name__ == '__main__':
    config = Config(default_data=__DEFAULT_CONFIG)

    logging.basicConfig(
        filename=Path(config.development.logfile).expanduser(),
        level=logging.getLevelName(config.development.level),
        format=__LOGGING_FORMAT,
    )

    main()  # pylint: disable=no-value-for-parameter
