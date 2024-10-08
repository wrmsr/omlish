import typing as ta

from omlish import dataclasses as dc
from omlish import lang

from ..content import Content
from ..content import Contentable
from .tools import ToolExecutionRequest


##


class Message(lang.Abstract, lang.Sealed):
    pass


@dc.dataclass(frozen=True)
class SystemMessage(Message, lang.Final):
    s: str


@dc.dataclass(frozen=True)
class UserMessage(Message, lang.Final):
    content: ta.Sequence[Content]
    name: str | None = None

    @classmethod
    def of(cls, c: ta.Iterable[Contentable] | Contentable, **kwargs: ta.Any) -> 'UserMessage':
        if isinstance(c, ta.Iterable) and not isinstance(c, str):
            content = [Content.of(e) for e in c]
        else:
            content = [Content.of(c)]
        return cls(
            content,
            **kwargs,
        )


@dc.dataclass(frozen=True)
class AiMessage(Message, lang.Final):
    s: str
    tool_execution_requests: ta.Sequence['ToolExecutionRequest'] | None = None


@dc.dataclass(frozen=True)
class ToolExecutionResultMessage(Message, lang.Final):
    id: str
    tool_name: str
    s: str


##


Chat: ta.TypeAlias = ta.Sequence[Message]
