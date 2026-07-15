# ruff: noqa: UP007
import abc
import typing as ta

from omcore import dataclasses as dc
from omcore import lang

from .content import TextContent
from .content import TextContentBuilder
from .content import ThinkingContent
from .content import ThinkingContentBuilder
from .content import ToolCall
from .content import ToolCallBuilder


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
    content: str | TextContent


@ta.final
class UserMessageBuilder(MessageBuilder[UserMessage]):
    def __init__(self) -> None:
        super().__init__()

        self.content: str | TextContent = ''

    def build(self) -> UserMessage:
        return UserMessage(
            content=self.content,
        )


##


@ta.final
@dc.dataclass(frozen=True)
@dc.extra_class_params(cache_hash=True, terse_repr=True)
class AiMessage(Message):
    content: ta.Sequence[ta.Union[
        TextContent,
        ThinkingContent,
        ToolCall,
    ]]


@ta.final
class AiMessageBuilder(MessageBuilder[AiMessage]):
    def __init__(self) -> None:
        super().__init__()

        self.content: list[ta.Union[
            TextContentBuilder,
            ThinkingContentBuilder,
            ToolCallBuilder,
        ]] = []

    def build(self) -> AiMessage:
        return AiMessage(
            content=[cb.build() for cb in self.content],
        )


##


@ta.final
@dc.dataclass(frozen=True, kw_only=True)
@dc.extra_class_params(cache_hash=True, terse_repr=True)
class ToolResultMessage(Message):
    tool_call_id: str
    tool_name: str

    content: ta.Sequence[TextContent] = ()
