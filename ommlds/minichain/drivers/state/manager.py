import abc
import typing as ta

from omlish import lang

from ...chat.messages import Chat
from .types import State


##


class StateManager(lang.Abstract):
    @abc.abstractmethod
    def get_state(self) -> ta.Awaitable[State]:
        raise NotImplementedError

    @abc.abstractmethod
    def extend_chat(self, chat_additions: Chat) -> ta.Awaitable[State]:
        raise NotImplementedError
