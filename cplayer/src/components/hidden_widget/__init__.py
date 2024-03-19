from textual.widget import Widget


class HiddenWidget(Widget):
    """Hidden widget representation."""

    def __init__(  # noqa: PLR0913
        self,
        *children: Widget,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
        start_hidden: bool = True,
    ) -> None:
        """Initializes the Widget object.

        :param start_hidden: Whether the widget should start as hidden. Defaults to True.
        :param **kwargs: Arbitrary keyword arguments.
        """
        super().__init__(*children, name=name, id=id, classes=classes, disabled=disabled)

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
        self.classes = 'hidden'

    def show(self, focus: bool = True) -> None:  # noqa: FBT002
        """Show the widget."""
        self.display = True
        self.classes = 'displayed'
        if focus:
            self.focus()
