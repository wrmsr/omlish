import uuid

from omlish import dataclasses as dc
from omlish import lang
from omlish import marshal as msh

from ...events.types import Event
from .types import AiDelta


##


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
@msh.update_field_options('exception', marshal_as=lang.OpaqueRepr | None, unmarshal_as=lang.OpaqueRepr | None)
class AiStreamEndEvent(AiStreamEvent, lang.Final):
    _: dc.KW_ONLY

    exception: BaseException | lang.OpaqueRepr | None = None


##


@msh.register_global_lazy_init
def _setup_marshal(cfgs: msh.ConfigRegistry) -> None:
    cfgs.update(Event, *[msh.OpenPolymorphismImpl(et) for et in [
        AiStreamBeginEvent,
        AiStreamDeltaEvent,
        AiStreamEndEvent,
    ]])
