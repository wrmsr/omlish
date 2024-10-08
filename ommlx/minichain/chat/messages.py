import typing as ta

from omlish import dataclasses as dc
from omlish import lang

from ..content import Content
from .tools import ToolExecutionRequest


##


class Message(lang.Abstract, lang.Sealed):
    pass


@dc.dataclass(frozen=True)
class SystemMessage(Message, lang.Final):
    s: str


@dc.dataclass(frozen=True)
class UserMessage(Message, lang.Final):
    content: Content
    name: str | None = None


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
