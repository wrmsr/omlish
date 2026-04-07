import abc
import typing as ta

from omlish import lang

from ...chat.messages import Chat


##


class DriverStateManager(lang.Abstract):
    @abc.abstractmethod
    def get_chat(self) -> ta.Awaitable[Chat]:
        raise NotImplementedError

    @abc.abstractmethod
    def extend_chat(self, chat_additions: Chat) -> ta.Awaitable[None]:
        raise NotImplementedError
