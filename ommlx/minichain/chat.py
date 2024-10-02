import abc
import typing as ta

from omlish import dataclasses as dc
from omlish import lang

from .content import Content
from .json import JsonSchema
from .models import Model
from .models import Request
from .models import RequestOption
from .models import Response
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


class ChatRequestOption(Option, lang.Abstract):
    pass


ChatRequestOptions: ta.TypeAlias = RequestOption | ChatRequestOption


@dc.dataclass(frozen=True, kw_only=True)
class ChatRequest(Request[Chat, ChatRequestOptions], lang.Final):
    pass


@dc.dataclass(frozen=True, kw_only=True)
class ChatResponse(Response[AiMessage], lang.Final):
    pass


class ChatModel(Model[ChatRequest, ChatRequestOptions, ChatResponse], lang.Abstract):
    @abc.abstractmethod
    def generate(self, request: ChatRequest) -> ChatResponse:
        raise NotImplementedError


##


@dc.dataclass(frozen=True)
class Tool(ChatRequestOption, lang.Final):
    spec: ToolSpecification


@dc.dataclass(frozen=True)
class ResponseFmt(ChatRequestOption, lang.Final):
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
