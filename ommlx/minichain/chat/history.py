import abc
import typing as ta

from omlish import dataclasses as dc
from omlish import lang

from .messages import Chat
from .messages import Message
from .services import ChatRequest
from .services import ChatResponse
from .services import ChatService


##


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


class ChatHistoryService(ChatService):
    def __init__(
            self,
            underlying: ChatService,
            history: ChatHistory,
    ) -> None:
        super().__init__()
        self._underlying = underlying
        self._history = history

    def invoke(self, request: ChatRequest) -> ChatResponse:
        new_req = dc.replace(request, chat=[*self._history.get(), *request.chat])
        response = self._underlying.invoke(new_req)
        self._history.add(
            *request.chat,
            response.choices[0].m,
        )
        return response
