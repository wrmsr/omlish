import datetime
import typing as ta
import uuid

from omlish import check
from omlish import dataclasses as dc
from omlish import lang
from omlish import typedvalues as tv

from ...metadata import CreatedAt
from ..messages import Chat
from ..messages import Message
from ..messages import MessageOriginal
from ..metadata import MessageMetadata
from ..metadata import MessageUuid
from .messages import MessageTransform


##


class OriginalMetadataStrippingMessageTransform(MessageTransform):
    def transform(self, m: Message) -> ta.Sequence[Message]:
        return [m._with_metadata(discard=[MessageOriginal])]  # noqa


def strip_message_original_metadata(c: Message) -> Message:
    return check.single(OriginalMetadataStrippingMessageTransform().transform(c))


##


@dc.dataclass(frozen=True)
class UuidAddingMessageTransform(MessageTransform):
    uuid_factory: ta.Callable[[], uuid.UUID] = dc.field(default_factory=lambda: uuid.uuid4)

    def transform(self, m: Message) -> Chat:
        if MessageUuid not in m.metadata:
            m = m.with_metadata(MessageUuid(self.uuid_factory()))
        return [m]


@dc.dataclass(frozen=True)
class CreatedAtAddingMessageTransform(MessageTransform):
    clock: ta.Callable[[], datetime.datetime] = dc.field(default=lang.utcnow)

    def transform(self, m: Message) -> Chat:
        if CreatedAt not in m.metadata:
            m = m.with_metadata(CreatedAt(self.clock()))
        return [m]


##


# FIXME: Unique?
class TransformedMessageOrigin(tv.ScalarTypedValue[Message], MessageMetadata, lang.Final):
    pass


@dc.dataclass(frozen=True)
class OriginAddingMessageTransform(MessageTransform):
    child: MessageTransform

    def transform(self, m: Message) -> Chat:
        return [
            o.with_metadata(TransformedMessageOrigin(m)) if TransformedMessageOrigin not in o.metadata else m
            for o in self.child.transform(m)
        ]
