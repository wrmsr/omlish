import datetime
import typing as ta
import uuid

from omlish import check
from omlish import dataclasses as dc
from omlish import lang
from omlish import typedvalues as tv

from ...metadata import CreatedAt
from ...metadata import Uuid
from ..messages import Chat
from ..messages import Message
from ..messages import MessageOriginal
from ..metadata import MessageMetadata
from .messages import MessageTransform


C = ta.TypeVar('C')


##


class OriginalMetadataStrippingMessageTransform(MessageTransform[C]):
    def transform(self, m: Message, ctx: C) -> ta.Sequence[Message]:
        return [m.with_metadata(discard=[MessageOriginal])]


def strip_message_original_metadata(c: Message) -> Message:
    return check.single(OriginalMetadataStrippingMessageTransform[None]().transform(c, None))


##


@dc.dataclass(frozen=True)
class UuidAddingMessageTransform(MessageTransform[C]):
    uuid_factory: ta.Callable[[], uuid.UUID] = dc.field(default_factory=lambda: uuid.uuid4)

    def transform(self, m: Message, ctx: C) -> Chat:
        if Uuid not in m.metadata:
            m = m.with_metadata(Uuid(self.uuid_factory()))
        return [m]


@dc.dataclass(frozen=True)
class CreatedAtAddingMessageTransform(MessageTransform[C]):
    clock: ta.Callable[[], datetime.datetime] = dc.field(default=datetime.datetime.now)

    def transform(self, m: Message, ctx: C) -> Chat:
        if CreatedAt not in m.metadata:
            m = m.with_metadata(CreatedAt(self.clock()))
        return [m]


##


# FIXME: Unique?
class TransformedMessageOrigin(tv.ScalarTypedValue[Message], MessageMetadata, lang.Final):
    pass


@dc.dataclass(frozen=True)
class OriginAddingMessageTransform(MessageTransform[C]):
    child: MessageTransform[C]

    def transform(self, m: Message, ctx: C) -> Chat:
        return [
            o.with_metadata(TransformedMessageOrigin(m)) if TransformedMessageOrigin not in o.metadata else m
            for o in self.child.transform(m, ctx)
        ]
