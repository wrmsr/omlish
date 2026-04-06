import abc
import typing as ta

from omlish import lang

from ...chat.messages import Chat
from .types import DriverState


##


class DriverStateManager(lang.Abstract):
    @abc.abstractmethod
    def get_driver_state(self) -> ta.Awaitable[DriverState]:
        raise NotImplementedError

    @abc.abstractmethod
    def extend_chat(self, chat_additions: Chat) -> ta.Awaitable[DriverState]:
        raise NotImplementedError
