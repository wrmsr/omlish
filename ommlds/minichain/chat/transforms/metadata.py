import datetime
import typing as ta
import uuid

from omlish import dataclasses as dc
from omlish import lang
from omlish import typedvalues as tv

from ...metadata import CreatedAt
from ...metadata import Uuid
from ..messages import Chat
from ..messages import Message
from ..metadata import MessageMetadata
from .base import MessageTransform


MessageT = ta.TypeVar('MessageT', bound=Message)


##


@dc.dataclass(frozen=True)
class UuidAddingMessageTransform(MessageTransform):
    uuid_factory: ta.Callable[[], uuid.UUID] = dc.field(default_factory=lambda: uuid.uuid4)

    def transform_message(self, m: Message) -> Chat:
        if Uuid not in m.metadata:
            m = m.with_metadata(Uuid(self.uuid_factory()))
        return [m]


@dc.dataclass(frozen=True)
class CreatedAtAddingMessageTransform(MessageTransform):
    clock: ta.Callable[[], datetime.datetime] = dc.field(default=datetime.datetime.now)

    def transform_message(self, m: Message) -> Chat:
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

    def transform_message(self, m: Message) -> Chat:
        return [
            o.with_metadata(TransformedMessageOrigin(m)) if TransformedMessageOrigin not in o.metadata else m
            for o in self.child.transform_message(m)
        ]
