import typing as ta

from omlish import dataclasses as dc
from omlish import lang

from ..content.content import Content
from .tools import ToolExecRequest


##


class Message(lang.Abstract, lang.Sealed):
    pass


@dc.dataclass(frozen=True)
class SystemMessage(Message, lang.Final):
    s: str


@dc.dataclass(frozen=True)
class UserMessage(Message, lang.Final):
    c: Content
    name: str | None = dc.xfield(None, repr_fn=dc.opt_repr)


@dc.dataclass(frozen=True)
class AiMessage(Message, lang.Final):
    s: str | None = dc.xfield(None, repr_fn=dc.opt_repr)
    tool_exec_requests: ta.Sequence['ToolExecRequest'] | None = dc.xfield(None, repr_fn=dc.opt_repr)


@dc.dataclass(frozen=True)
class ToolExecResultMessage(Message, lang.Final):
    id: str
    name: str
    s: str


##


Chat: ta.TypeAlias = ta.Sequence[Message]
