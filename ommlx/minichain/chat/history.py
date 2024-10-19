import abc
import typing as ta

from omlish import dataclasses as dc
from omlish import lang

from .messages import Chat
from .messages import Message
from .models import ChatModel
from .models import ChatRequest
from .models import ChatResponse


class ChatHistory(lang.Abstract):
    @abc.abstractmethod
    def add(self, *msgs: Message) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def get(self) -> Chat:
        raise NotImplementedError

    @abc.abstractmethod
    def clear(self) -> None:
        raise NotImplementedError


class ListChatHistory(ChatHistory):
    def __init__(self, init: ta.Iterable[Message] | None = None) -> None:
        super().__init__()
        self._lst = list(init or ())

    def add(self, *msgs: Message) -> None:
        self._lst.extend(msgs)

    def get(self) -> Chat:
        return self._lst

    def clear(self) -> None:
        self._lst.clear()


class ChatHistoryModel(ChatModel):
    def __init__(
            self,
            underlying: ChatModel,
            history: ChatHistory,
    ) -> None:
        super().__init__()
        self._underlying = underlying
        self._history = history

    def invoke(self, request: ChatRequest) -> ChatResponse:
        new_req = dc.replace(request, v=[*self._history.get(), *request.v])
        response = self._underlying.invoke(new_req)
        self._history.add(
            *request.v,
            response.v[0].m,
        )
        return response
