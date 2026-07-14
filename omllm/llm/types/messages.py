import abc
import typing as ta

from omcore import dataclasses as dc
from omcore import lang

from .content import TextContent
from .content import TextContentBuilder
from .content import ThinkingContent
from .content import ThinkingContentBuilder


MessageT = ta.TypeVar('MessageT', bound='Message')


##


@dc.dataclass(frozen=True)
class Message(lang.Abstract):
    pass


class MessageBuilder(lang.Abstract, ta.Generic[MessageT]):
    @abc.abstractmethod
    def build(self) -> MessageT:
        raise NotImplementedError


##


@ta.final
@dc.dataclass(frozen=True)
@dc.extra_class_params(cache_hash=True, terse_repr=True)
class UserMessage(Message):
    c: str | TextContent


@ta.final
class UserMessageBuilder(MessageBuilder[UserMessage]):
    def __init__(self) -> None:
        super().__init__()

        self.c: str | TextContent = ''

    def build(self) -> UserMessage:
        return UserMessage(
            c=self.c,
        )


##


@ta.final
@dc.dataclass(frozen=True)
@dc.extra_class_params(cache_hash=True, terse_repr=True)
class AiMessage(Message):
    c: ta.Sequence[TextContent | ThinkingContent]


@ta.final
class AiMessageBuilder(MessageBuilder[AiMessage]):
    def __init__(self) -> None:
        super().__init__()

        self.c: list[TextContentBuilder | ThinkingContentBuilder] = []

    def build(self) -> AiMessage:
        return AiMessage(
            c=tuple(cb.build() for cb in self.c),
        )
