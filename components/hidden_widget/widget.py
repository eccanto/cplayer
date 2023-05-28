from textual.widget import Widget


class HiddenWidget(Widget):
    """Hidden widget representation."""

    def on_mount(self) -> None:
        self.hide()

    def hide(self) -> None:
        self.display = False

    def show(self) -> None:
        self.display = True
        self.focus()
