import abc
import dataclasses as dc
import enum
import typing as ta

from omlish import collections as col
from omlish import lang


T = ta.TypeVar('T')
U = ta.TypeVar('U')


#


class Content(lang.Abstract, lang.Sealed):
    pass


@dc.dataclass(frozen=True)
class Text(Content, lang.Final):
    s: str


#


##


##


class ChatHistory(lang.Abstract):
    @abc.abstractmethod
    def add(self, msg: Message) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def get(self) -> Chat:
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
    chat: Chat
    tool_specs: ta.Sequence[ToolSpecification]
    resp_fmt: ResponseFormat


ChatResponse: ta.TypeAlias = Response[AiMessage]

ChatModel: ta.TypeAlias = Model[ChatRequest, ChatResponse]


##


@dc.dataclass(frozen=True)
class Embedding:
    """array.array('f' | 'd', ...) preferred"""

    v: ta.Sequence[float]


EmbeddingModel: ta.TypeAlias = Model[str, Response[Embedding]]


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

