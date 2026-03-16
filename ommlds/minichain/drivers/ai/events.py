from omlish import dataclasses as dc
from omlish import lang

from ...chat.messages import Chat
from ...chat.stream.types import AiDelta
from ..types import Event


##


@dc.dataclass(frozen=True)
class AiMessagesEvent(Event, lang.Final):
    chat: Chat

    _: dc.KW_ONLY

    streamed: bool = False


#


@dc.dataclass(frozen=True)
class AiStreamBeginEvent(Event, lang.Final):
    pass


@dc.dataclass(frozen=True)
class AiStreamDeltaEvent(Event, lang.Final):
    delta: AiDelta


@dc.dataclass(frozen=True)
class AiStreamEndEvent(Event, lang.Final):
    pass
