import abc
import dataclasses as dc
import typing as ta

from omlish import lang

from .content import Content
from .json import JsonSchema
from .models import Model
from .models import Request
from .models import Response
from .tool import ToolExecutionRequest
from .tool import ToolSpecification


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


@dc.dataclass(frozen=True)
class AiMessage(Message, lang.Final):
    s: str
    tool_execution_requests: ta.Sequence['ToolExecutionRequest'] | None = None


@dc.dataclass(frozen=True)
class ToolExecutionResultMessage(Message, lang.Final):
    id: str
    tool_name: str
    s: str


Chat: ta.TypeAlias = ta.Sequence[Message]


##


class ResponseFormat(lang.Abstract, lang.Sealed):
    pass


class TextResponseFormat(ResponseFormat, lang.Final):
    pass


TEXT_RESPONSE_FORMAT = TextResponseFormat()


@dc.dataclass(frozen=True)
class JsonResponseFormat(lang.Final):
    schema: JsonSchema | None = None


##


@dc.dataclass(frozen=True)
class ChatRequest(lang.Final):
    chat: Chat

    _: dc.KW_ONLY

    tool_specs: ta.Sequence[ToolSpecification] = ()
    resp_fmt: ResponseFormat = TEXT_RESPONSE_FORMAT


ChatModel: ta.TypeAlias = Model[ChatRequest, AiMessage]


class ChatModel_(ChatModel, lang.Abstract):  # noqa
    @abc.abstractmethod
    def generate(self, request: Request[ChatRequest]) -> Response[AiMessage]:
        raise NotImplementedError


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
