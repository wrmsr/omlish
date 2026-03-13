import abc
import datetime
import typing as ta
import uuid

from omlish import dataclasses as dc
from omlish import lang
from omlish import typedvalues as tv

from ...chat.messages import Chat


##


class ChatId(tv.UniqueScalarTypedValue[uuid.UUID]):
    pass


##


@dc.dataclass(frozen=True)
class State:
    name: str | None = None

    created_at: datetime.datetime = dc.field(default_factory=lang.utcnow)
    updated_at: datetime.datetime = dc.field(default_factory=lang.utcnow)

    chat: Chat = ()

    # raw_chats: ta.Sequence[ta.Any] | None = None


##


class StateManager(lang.Abstract):
    @abc.abstractmethod
    def get_state(self) -> ta.Awaitable[State]:
        raise NotImplementedError

    @abc.abstractmethod
    def extend_chat(self, chat_additions: Chat) -> ta.Awaitable[State]:
        raise NotImplementedError
