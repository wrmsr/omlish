import uuid

from omlish import dataclasses as dc
from omlish import lang
from omlish import marshal as msh

from ...chat.messages import Chat
from ...chat.stream.types import AiDelta
from ..types import Event


##


@dc.dataclass(frozen=True)
class AiMessagesEvent(Event, lang.Final):
    chat: Chat

    _: dc.KW_ONLY

    streamed: bool = False

    message_uuid: uuid.UUID | None = None


#


@dc.dataclass(frozen=True)
class AiStreamEvent(Event, lang.Abstract):
    _: dc.KW_ONLY

    message_uuid: uuid.UUID | None = None


@dc.dataclass(frozen=True)
class AiStreamBeginEvent(AiStreamEvent, lang.Final):
    pass


@dc.dataclass(frozen=True)
class AiStreamDeltaEvent(AiStreamEvent, lang.Final):
    delta: AiDelta


@dc.dataclass(frozen=True)
@msh.update_fields_options(['exception'], marshal_as=msh.OpaqueRepr, unmarshal_as=msh.OpaqueRepr)
class AiStreamEndEvent(AiStreamEvent, lang.Final):
    _: dc.KW_ONLY

    exception: BaseException | None = None
