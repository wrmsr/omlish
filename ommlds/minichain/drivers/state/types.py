import datetime
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
class DriverState:
    name: str | None = None

    created_at: datetime.datetime = dc.field(default_factory=lang.utcnow)
    updated_at: datetime.datetime = dc.field(default_factory=lang.utcnow)

    chat: Chat = ()

    # raw_chats: ta.Sequence[ta.Any] | None = None
