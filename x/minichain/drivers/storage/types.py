import typing as ta
import uuid

from omlish import dataclasses as dc
from omlish import lang
from omlish import typedvalues as tv

from ...chat.messages import Message


##


class ChatId(tv.UniqueScalarTypedValue[uuid.UUID]):
    pass


##


@dc.dataclass(frozen=True)
class StoredMessage(lang.Final):
    """A persisted chat message together with its storage sequence number (1-based, dense, per chat)."""

    seq: int
    message: Message


@dc.dataclass(frozen=True, kw_only=True)
class ChatPage(lang.Final):
    """A contiguous slice of a chat's stored messages, ascending by seq."""

    rows: ta.Sequence[StoredMessage]

    has_before: bool = False
    has_after: bool = False

    @property
    def first_seq(self) -> int | None:
        return self.rows[0].seq if self.rows else None

    @property
    def last_seq(self) -> int | None:
        return self.rows[-1].seq if self.rows else None
