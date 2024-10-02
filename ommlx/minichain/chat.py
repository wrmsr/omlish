import abc
import typing as ta

from omlish import dataclasses as dc
from omlish import lang

from .content import Content
from .json import JsonSchema
from .models import Model
from .options import Option
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


class ChatModel(Model['ChatModel.Request', 'ChatModel.Response'], lang.Abstract):
    class RequestOption(Option, lang.Abstract):
        pass

    @dc.dataclass(frozen=True, kw_only=True)
    class Request(Model.Request[Chat, Model.RequestOption | RequestOption]):
        pass

    @dc.dataclass(frozen=True, kw_only=True)
    class Response(Model.Response[AiMessage]):
        pass

    @abc.abstractmethod
    def generate(self, request: Request) -> Response:
        raise NotImplementedError


##


@dc.dataclass(frozen=True)
class Tool(ChatModel.RequestOption, lang.Final):
    spec: ToolSpecification


@dc.dataclass(frozen=True)
class ResponseFmt(ChatModel.RequestOption, lang.Final):
    fmt: ResponseFormat


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
