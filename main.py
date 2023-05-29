import os
from pathlib import Path

os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = 'hide'

import click
from pygame import mixer
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.widgets import Footer, Header

from pages.help.page import HelpPage
from pages.home.page import HomePage


class Application(App):
    TITLE = ' Playlist'
    CSS_PATH = 'resources/styles/application.css'
    BINDINGS = [
        Binding('q', 'quit', 'Quit', show=True),
        Binding('h', 'home', 'Home', show=True),
        Binding('i', 'info', 'Info', show=True),
    ]

    def __init__(self, path: Path, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.path = path

    def compose(self) -> ComposeResult:
        yield Header()

        yield HomePage(self.path)
        yield HelpPage(start_hidden=True)

        yield Footer()

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
@click.option(
    '-p', '--path', help=f'Songs directory path.', type=click.Path(exists=True, path_type=Path), required=True
)
def main(path):
    mixer.init()
    mixer.music.set_volume(1)

    app = Application(path)
    app.run()


if __name__ == '__main__':
    main()
