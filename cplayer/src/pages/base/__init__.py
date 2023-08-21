from pathlib import Path
from typing import Callable

from cplayer.src.components.hidden_widget import HiddenWidget


class PageBase(HiddenWidget):
    """PageBase Class that represents the base class for all pages in the application."""

    DEFAULT_CSS = Path(__file__).parent.joinpath('styles.css').read_text(encoding='UTF-8')

    def __init__(self, change_title: Callable[[str], None], *args, **kwargs) -> None:
        """Initializes the Page object.

        :param change_title: A callable function to change the title of the page.
        :param *args: Variable length argument list.
        :param **kwargs: Arbitrary keyword arguments.
        """
        super().__init__(*args, **kwargs)

        self.change_title = change_title
