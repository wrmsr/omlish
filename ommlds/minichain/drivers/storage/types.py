import typing as ta
import uuid

from omlish import dataclasses as dc
from omlish import typedvalues as tv

from ...chat.messages import Message


##


class ChatId(tv.UniqueScalarTypedValue[uuid.UUID]):
    pass


##


@dc.dataclass(frozen=True, kw_only=True)
class ChatPage:
    messages: ta.Sequence[Message]

    has_before: bool = False
    has_after: bool = False

    before_seq: int | None = None
    after_seq: int | None = None
