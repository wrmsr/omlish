# ruff: noqa: SLF001
import typing as ta
import uuid

from omdev.tui import textual as tx

from .base import StaticMessage
from .divider import MessageDivider


##


class UserMessage(StaticMessage):
    init_add_class = 'user-message'

    def __init__(
            self,
            content: tx.VisualType,
            *,
            message_uuid: uuid.UUID | None = None,
    ) -> None:
        super().__init__(
            message_uuid=message_uuid,
        )

        self._content = content

    @property
    def message_content(self) -> ta.Any | None:
        return self._content

    def compose(self) -> tx.ComposeResult:
        with tx.Vertical(classes='user-message-divider-container message-divider-container'):
            yield MessageDivider.for_message(self)

            with tx.Horizontal(classes='user-message-outer message-outer'):
                yield tx.Static('> ', classes='user-message-glyph message-glyph')
                with tx.Vertical(classes='user-message-inner message-inner'):
                    yield tx.Static(self._content)
