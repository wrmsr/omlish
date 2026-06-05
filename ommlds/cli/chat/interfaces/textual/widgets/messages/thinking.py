# ruff: noqa: SLF001
import abc
import typing as ta

from omdev.tui import textual as tx
from omlish import lang

from .base import Message
from .base import StaticMessage
from .divider import MessageDivider
from .stream import MarkdownStreamMessage


##


class ThinkingMessage(Message, lang.Abstract):
    init_add_class = 'thinking-message'

    def compose(self) -> tx.ComposeResult:
        with tx.Vertical(classes='thinking-message-divider-container message-divider-container'):
            yield MessageDivider.for_message(self)

            with tx.Horizontal(classes='thinking-message-outer message-outer'):
                yield tx.Static('% ', classes='thinking-message-glyph message-glyph')
                with tx.Vertical(classes='thinking-message-inner message-inner'):
                    yield from self._compose_content()

    @abc.abstractmethod
    def _compose_content(self) -> ta.Generator:
        raise NotImplementedError


##


class StaticThinkingMessage(StaticMessage, ThinkingMessage):
    init_add_class = 'static-thinking-message'

    def __init__(
            self,
            content: str,
            **kwargs: ta.Any,
    ) -> None:
        super().__init__(**kwargs)

        self._content = content

    @property
    def message_content(self) -> ta.Any | None:
        return self._content

    def _compose_content(self) -> ta.Generator:
        yield tx.Static(self._content)


##


class StreamThinkingMessage(ThinkingMessage, MarkdownStreamMessage):
    init_add_class = 'stream-thinking-message'

    def _compose_content(self) -> ta.Generator:
        yield tx.Markdown('')
