import typing as ta
import uuid

from omlish import check
from omlish import dataclasses as dc
from omlish import lang
from omlish import typedvalues as tv

from ...transform.metadata import CreatedAtAddingGeneralTransform
from ..messages import Chat
from ..messages import Message
from ..messages import MessageOriginal
from ..metadata import MessageMetadata
from ..metadata import MessageUuid
from ..metadata import TurnUuid
from .types import MessageTransform


##


class OriginalMetadataStrippingMessageTransform(MessageTransform):
    def transform(self, m: Message) -> ta.Sequence[Message]:
        return [m._with_metadata(discard=[MessageOriginal])]  # noqa


def strip_message_original_metadata(c: Message) -> Message:
    return check.single(OriginalMetadataStrippingMessageTransform().transform(c))


##


class CreatedAtAddingMessageTransform(CreatedAtAddingGeneralTransform[Message], MessageTransform):
    pass


@dc.dataclass(frozen=True)
class MessageUuidAddingMessageTransform(MessageTransform):
    uuid_factory: ta.Callable[[], uuid.UUID] = dc.field(default_factory=lambda: uuid.uuid4)

    _: dc.KW_ONLY

    check_not_already_present: bool = False

    def transform(self, m: Message) -> Chat:
        if self.check_not_already_present:
            check.not_in(MessageUuid, m.metadata)
        if MessageUuid not in m.metadata:
            m = m.with_metadata(MessageUuid(self.uuid_factory()))
        return [m]


@dc.dataclass(frozen=True)
class TurnUuidAddingMessageTransform(MessageTransform):
    turn_uuid: uuid.UUID | None = dc.field(default_factory=uuid.uuid4)

    _: dc.KW_ONLY

    no_check: bool = False

    def transform(self, m: Message) -> Chat:
        try:
            tu = m.metadata[TurnUuid]
        except KeyError:
            m = m.with_metadata(TurnUuid(self.turn_uuid))
        else:
            if not self.no_check:
                check.equal(tu.v, self.turn_uuid)
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
