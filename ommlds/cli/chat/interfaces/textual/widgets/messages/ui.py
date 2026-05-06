# ruff: noqa: SLF001
import typing as ta

from omdev.tui import textual as tx

from .base import StaticMessage
from .divider import MessageDivider


##


class UiMessage(StaticMessage):
    init_add_class = 'ui-message'

    def __init__(
            self,
            content: tx.VisualType,
            **kwargs: ta.Any,
    ) -> None:
        super().__init__(**kwargs)

        self._content = content

    @property
    def message_content(self) -> ta.Any | None:
        return self._content

    def compose(self) -> tx.ComposeResult:
        with tx.Vertical(classes='ui-message-divider-container message-divider-container'):
            yield MessageDivider.for_message(self)

            with tx.Horizontal(classes='ui-message-outer message-outer'):
                yield tx.Static('~ ', classes='ui-message-glyph message-glyph')
                with tx.Vertical(classes='ui-message-inner message-inner'):
                    yield tx.Static(self._content)
