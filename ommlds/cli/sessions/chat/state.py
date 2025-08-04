import dataclasses as dc
import datetime

from omlish import lang

from .... import minichain as mc


##


@dc.dataclass(frozen=True)
class ChatState:
    name: str | None = None

    created_at: datetime.datetime = dc.field(default_factory=lang.utcnow)
    updated_at: datetime.datetime = dc.field(default_factory=lang.utcnow)

    chat: mc.Chat = ()
