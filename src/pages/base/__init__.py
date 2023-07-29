from pathlib import Path
from typing import Callable

from src.components.hidden_widget import WidgetHidden


class PageBase(WidgetHidden):
    DEFAULT_CSS = Path(__file__).parent.joinpath('styles.css').read_text(encoding='UTF-8')

    def __init__(self, change_title: Callable[[str], None], *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.change_title = change_title
