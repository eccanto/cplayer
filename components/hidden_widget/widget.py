from textual.widget import Widget


class HiddenWidget(Widget):
    """Hidden widget representation."""

    def __init__(self, start_hidden: bool = True, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self._start_hidden = start_hidden

    def on_mount(self) -> None:
        if self._start_hidden:
            self.hide()

    def hide(self) -> None:
        self.display = False

    def show(self) -> None:
        self.display = True
        self.focus()
