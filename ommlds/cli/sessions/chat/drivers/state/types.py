import abc
import datetime
import typing as ta
import uuid

from omlish import dataclasses as dc
from omlish import lang
from omlish import typedvalues as tv

from ...... import minichain as mc


##


class ChatId(tv.UniqueScalarTypedValue[uuid.UUID]):
    pass


##


@dc.dataclass(frozen=True)
class ChatState:
    name: str | None = None

    created_at: datetime.datetime = dc.field(default_factory=lang.utcnow)
    updated_at: datetime.datetime = dc.field(default_factory=lang.utcnow)

    chat: 'mc.Chat' = ()


##


class ChatStateManager(lang.Abstract):
    @abc.abstractmethod
    def get_state(self) -> ta.Awaitable[ChatState]:
        raise NotImplementedError

    @abc.abstractmethod
    def extend_chat(self, chat_additions: 'mc.Chat') -> ta.Awaitable[ChatState]:
        raise NotImplementedError
