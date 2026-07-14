import uuid

from omcore import dataclasses as dc
from omcore import lang
from omcore import marshal as msh

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
@dc.extra_class_params(default_repr_fn=lang.opt_repr)
@msh.update_field_options(
    'exception',
    marshal_via=msh.MarshalVia(lang.OpaqueRepr | None),
    unmarshal_via=msh.UnmarshalVia(lang.OpaqueRepr | None),
)
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
