import abc
import datetime
import typing as ta

from omlish import dataclasses as dc
from omlish import lang

from ...... import minichain as mc


##


@dc.dataclass(frozen=True)
class ChatState:
    name: str | None = None

    created_at: datetime.datetime = dc.field(default_factory=lang.utcnow)
    updated_at: datetime.datetime = dc.field(default_factory=lang.utcnow)

    chat: mc.Chat = ()


##


class ChatStateManager(lang.Abstract):
    @abc.abstractmethod
    def get_state(self) -> ta.Awaitable[ChatState]:
        raise NotImplementedError

    @abc.abstractmethod
    def clear_state(self) -> ta.Awaitable[ChatState]:
        raise NotImplementedError

    @abc.abstractmethod
    def extend_chat(self, chat_additions: 'mc.Chat') -> ta.Awaitable[ChatState]:
        raise NotImplementedError
