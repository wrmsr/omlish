# ruff: noqa: SLF001
import typing as ta

from omdev import clipboard as cpb
from omdev.tui import textual as tx

from .base import StaticMessage


##


class WelcomeMessage(StaticMessage):
    init_add_class = 'welcome-message'

    def __init__(
            self,
            content: tx.VisualType,
            *,
            copy_contents: ta.Mapping[str, tuple[str, str]] | None = None,
            **kwargs: ta.Any,
    ) -> None:
        super().__init__(**kwargs)

        self._content = content
        self._copy_contents = copy_contents

    @property
    def message_content(self) -> ta.Any | None:
        return self._content

    def compose(self) -> tx.ComposeResult:
        with tx.Vertical(classes='welcome-message-outer message-outer'):
            yield tx.Static(self._content, classes='welcome-message-content')

    def on_click(self, event: tx.Click) -> None:
        if event.button != 1:
            return

        event.stop()

        if not (cc := self._copy_contents):
            return

        if (clipboard := self.messages_container._clipboard) is None:
            return

        def handle_action(k: str | None) -> None:
            if not k:
                return

            v, _ = cc[k]

            clipboard.put(cpb.TextClipboardContents(v))

        self.app.push_screen(
            tx.ActionMenuScreen(
                (event.screen_x, event.screen_y),
                [('Copy ' + t, k) for k, (t, _) in cc.items()],
            ),
            handle_action,
        )
