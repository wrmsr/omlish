import abc
import dataclasses as dc
import enum
import typing as ta

from omlish import collections as col
from omlish import lang


T = ta.TypeVar('T')


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
    s: str


class UserMessage(Message, lang.Final):
    content: ta.Sequence[Content]
    name: str | None = None


class AiMessage(Message, lang.Final):
    s: str
    tool_execution_requests: ta.Sequence['ToolExecutionRequest'] | None = None


class ToolExecutionResultMessage(Message, lang.Final):
    id: str
    tool_name: str
    s: str


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


##


@dc.dataclass(frozen=True)
class Embedding:
    """array.array('f' | 'd', ...) preferred"""

    v: ta.Sequence[float]


##


class Chat(lang.Abstract):
    @abc.abstractmethod
    def add(self, msg: Message) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def messages(self) -> ta.Sequence[Message]:
        raise NotImplementedError

    @abc.abstractmethod
    def clear(self) -> None:
        raise NotImplementedError


##


@dc.dataclass(frozen=True)
class JsonSchema(lang.Final):
    name: str
    root: ta.Any


##


class ResponseFormat(lang.Abstract, lang.Sealed):
    pass


class TextResponseFormat(ResponseFormat, lang.Final):
    pass


class JsonResponseFormat(lang.Final):
    schema: JsonSchema | None = None


##


@dc.dataclass(frozen=True)
class ChatRequest(lang.Final):
    msgs: ta.Sequence[Message]
    tool_specs: ta.Sequence[ToolSpecification]
    resp_fmt: ResponseFormat


##


@dc.dataclass(frozen=True)
class Prompt(lang.Final):
    s: str


##


class FinishReason(enum.Enum):
    STOP = enum.auto()
    LENGTH = enum.auto()
    TOOL_EXECUTION = enum.auto()
    CONTENT_FILTER = enum.auto()
    OTHER = enum.auto()


@dc.dataclass(frozen=True)
class TokenUsage(lang.Final):
    input: int
    output: int
    total: int


@dc.dataclass(frozen=True)
class Response(lang.Final, ta.Generic[T]):
    v: T
    usage: TokenUsage
    reason: FinishReason


ChatResponse: ta.TypeAlias = Response[AiMessage]


##


@dc.dataclass(frozen=True)
class Metadata(lang.Final):
    dct: ta.Mapping[ta.Any, ta.Any] = col.frozendict()


@dc.dataclass(frozen=True)
class TextSegment(lang.Final):
    s: str
    md: Metadata = Metadata()


# @dc.dataclass(frozen=True)
# class Document:
#     ...

