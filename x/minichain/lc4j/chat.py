import abc
import dataclasses as dc
import typing as ta

from omlish import lang

from .content import Content
from .models import Model
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


@dc.dataclass(frozen=True)
class ChatRequest(lang.Final):
    chat: Chat
    tool_specs: ta.Sequence[ToolSpecification]
    resp_fmt: ResponseFormat


ChatModel: ta.TypeAlias = Model[ChatRequest, AiMessage]


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
