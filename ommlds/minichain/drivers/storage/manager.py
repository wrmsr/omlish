import abc
import typing as ta

from omlish import lang

from ...chat.messages import Chat
from .types import ChatPage


##


class DriverStorageManager(lang.Abstract):
    @abc.abstractmethod
    def get_chat(self) -> ta.Awaitable[Chat]:
        raise NotImplementedError

    @abc.abstractmethod
    def get_latest_chat_page(self, limit: int) -> ta.Awaitable[ChatPage]:
        raise NotImplementedError

    @abc.abstractmethod
    def get_chat_page_before(self, seq: int, limit: int) -> ta.Awaitable[ChatPage]:
        raise NotImplementedError

    @abc.abstractmethod
    def get_chat_page_after(self, seq: int, limit: int) -> ta.Awaitable[ChatPage]:
        raise NotImplementedError

    @abc.abstractmethod
    def extend_chat(self, chat_additions: Chat) -> ta.Awaitable[None]:
        raise NotImplementedError
