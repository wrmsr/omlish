# ruff: noqa: SLF001
import abc
import typing as ta

from omdev.tui import textual as tx
from omcore import lang

from .base import Message
from .base import StaticMessage
from .divider import MessageDivider
from .stream import MarkdownStreamMessage


##


class AiMessage(Message, lang.Abstract):
    init_add_class = 'ai-message'

    def compose(self) -> tx.ComposeResult:
        with tx.Vertical(classes='ai-message-divider-container message-divider-container'):
            yield MessageDivider.for_message(self)

            with tx.Horizontal(classes='ai-message-outer message-outer'):
                yield tx.Static('< ', classes='ai-message-glyph message-glyph')
                with tx.Vertical(classes='ai-message-inner message-inner'):
                    yield from self._compose_content()

    @abc.abstractmethod
    def _compose_content(self) -> ta.Generator:
        raise NotImplementedError


##


class StaticAiMessage(StaticMessage, AiMessage):
    init_add_class = 'static-ai-message'

    def __init__(
            self,
            content: str,
            *,
            markdown: bool = False,
            **kwargs: ta.Any,
    ) -> None:
        super().__init__(**kwargs)

        self._content = content
        self._markdown = markdown

    @property
    def message_content(self) -> ta.Any | None:
        return self._content

    def _compose_content(self) -> ta.Generator:
        if self._markdown:
            yield tx.Markdown(self._content)
        else:
            yield tx.Static(self._content)


##


class StreamAiMessage(AiMessage, MarkdownStreamMessage):
    init_add_class = 'stream-ai-message'

    def _compose_content(self) -> ta.Generator:
        yield tx.Markdown('')
