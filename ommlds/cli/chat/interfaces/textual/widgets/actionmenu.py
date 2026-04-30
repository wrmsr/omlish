import typing as ta

from omdev.tui import textual as tx


##


class ActionMenuButton(tx.Button):
    def __init__(
            self,
            label: str,
            value: ta.Any,
            **kwargs: ta.Any,
    ) -> None:
        super().__init__(
            label,
            compact=True,
            **kwargs,
        )

        self._value = value


class ActionMenu(tx.Vertical):
    DEFAULT_CSS = """
        ActionMenu {
            width: 16;
            height: auto;
            border: none;
            background: $surface;
            padding: 0;
        }

        ActionMenu ActionMenuButton {
            width: 100%;
        }
    """

    def __init__(
            self,
            items: ta.Sequence[tuple[str, ta.Any]],
    ) -> None:
        super().__init__()

        self._items = items

    def compose(self) -> tx.ComposeResult:
        for label, value in self._items:
            yield ActionMenuButton(label, value)

    def on_click(self, event: tx.Click) -> None:
        # Don't let clicks inside the menu bubble to the modal screen, because the modal screen treats clicks as
        # "outside" clicks.
        event.stop()


class ActionMenuScreen(tx.ModalScreen[ta.Any | None]):
    BINDINGS = [  # noqa
        tx.Binding('escape', 'cancel', show=False),
    ]

    DEFAULT_CSS = """
        ActionMenuScreen {
            background: transparent;
        }

        ActionMenu {
            position: absolute;
        }
    """

    def __init__(
            self,
            position: tuple[int, int],
            items: ta.Sequence[tuple[str, ta.Any]],
            **kwargs: ta.Any,
    ) -> None:
        super().__init__(**kwargs)

        self._position = position
        self._items = items

    def compose(self) -> tx.ComposeResult:
        yield ActionMenu(self._items)

    def on_mount(self) -> None:
        menu = self.query_one(ActionMenu)

        # Crude but effective clamp. You can compute this from measured menu.outer_size after first layout if you want
        # it exact.
        menu_width = 16
        menu_height = 4

        x, y = self._position

        x = min(x, max(0, self.size.width - menu_width))
        y = min(y, max(0, self.size.height - menu_height))

        menu.styles.offset = (x, y)
        menu.focus()

    def on_click(self, event: tx.Click) -> None:
        # Any click that reaches the screen was outside the menu.
        self.dismiss(None)

    def action_cancel(self) -> None:
        self.dismiss(None)

    def on_button_pressed(self, event: tx.Button.Pressed) -> None:
        event.stop()

        if isinstance(amb := event.button, ActionMenuButton):
            self.dismiss(amb._value)  # noqa
        else:
            self.dismiss(None)
