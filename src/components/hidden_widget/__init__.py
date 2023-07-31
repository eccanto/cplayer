from textual.widget import Widget


class HiddenWidget(Widget):
    """Hidden widget representation."""

    def __init__(self, start_hidden: bool = True, **kwargs) -> None:
        """Initializes the Widget object.

        :param start_hidden: Whether the widget should start as hidden. Defaults to True.
        :param **kwargs: Arbitrary keyword arguments.
        """
        super().__init__(**kwargs)

        self._start_hidden = start_hidden

    def on_mount(self) -> None:
        """Event handler called when the widget is mounted in the application."""
        if self._start_hidden:
            self.hide()
        else:
            self.show()

    def hide(self) -> None:
        """Hide the widget."""
        self.display = False

    def show(self) -> None:
        """Show the widget."""
        self.display = True
        self.focus()
