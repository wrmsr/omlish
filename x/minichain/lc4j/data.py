import abc
import dataclasses as dc
import enum
import typing as ta

from omlish import lang


#


class Content(lang.Abstract, lang.Sealed):
    pass


@dc.dataclass(frozen=True)
class Text(Content, lang.Final):
    s: str


#


class Message(lang.Abstract, lang.Sealed):
    pass


class SystemMessage(Message, lang.Final):
    pass


class UserMessage(Message, lang.Final):
    pass


class AiMessage(Message, lang.Final):
    s: str
    tool_execution_requests: ta.Sequence['ToolExecutionRequest'] | None = None


class ToolExecutionResultMessage(Message, lang.Final):
    pass


##


@dc.dataclass(frozen=True)
class ToolParameters(lang.Final):
    type: str
    props: ta.Mapping[str, ta.Mapping[str, ta.Any]]
    req: ta.AbstractSet[str]


@dc.dataclass(frozen=True)
class ToolSpecification(lang.Final):
    name: str
    desc: str
    params: ToolParameters


@dc.dataclass(frozen=True)
class ToolExecutionRequest(lang.Final):
    id: str
    name: str
    args: str
