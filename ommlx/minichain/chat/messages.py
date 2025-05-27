import typing as ta

from omlish import dataclasses as dc
from omlish import dispatch
from omlish import lang

from ..content.content import Content
from ..content.transforms import ContentTransform
from ..tools.types import ToolExecRequest


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


##


class _MessageContentTransform(ContentTransform, lang.Final, lang.NotInstantiable):
    @dispatch.install_method(ContentTransform.apply)
    def apply_system_message(self, m: SystemMessage) -> SystemMessage:
        return dc.replace(m, s=self.apply(m.s))

    @dispatch.install_method(ContentTransform.apply)
    def apply_user_message(self, m: UserMessage) -> UserMessage:
        return dc.replace(m, c=self.apply(m.c))

    @dispatch.install_method(ContentTransform.apply)
    def apply_ai_message(self, m: AiMessage) -> AiMessage:
        return dc.replace(m, s=self.apply(m.s))

    @dispatch.install_method(ContentTransform.apply)
    def apply_tool_exec_result_message(self, m: ToolExecResultMessage) -> ToolExecResultMessage:
        return m
