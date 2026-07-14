import typing as ta

from omcore import dataclasses as dc
from omcore import lang
from omcore import marshal as msh

from .events.types import Event


##


_MARSHAL_FIELD_OPAQUE_REPR_KWARGS: ta.Mapping[str, ta.Any] = dict(
    marshal_via=msh.MarshalVia(lang.OpaqueRepr),
    unmarshal_via=msh.UnmarshalVia(lang.OpaqueRepr),
)


#


@dc.dataclass(frozen=True, kw_only=True)
@msh.update_field_options('service', **_MARSHAL_FIELD_OPAQUE_REPR_KWARGS)
class ExternalServiceEvent(Event, lang.Abstract, lang.Sealed):
    service: ta.Any | lang.OpaqueRepr


#


@dc.dataclass(frozen=True, kw_only=True)
class ExternalServiceRequestEvent(ExternalServiceEvent, lang.Final):
    request: ta.Any


@dc.dataclass(frozen=True, kw_only=True)
class ExternalServiceResponseEvent(ExternalServiceEvent, lang.Final):
    response: ta.Any


#


class ExternalServiceStreamResponseEvent(ExternalServiceEvent, lang.Abstract):
    pass


@dc.dataclass(frozen=True, kw_only=True)
class ExternalServiceStreamResponseStartEvent(ExternalServiceStreamResponseEvent, lang.Final):
    pass


@dc.dataclass(frozen=True, kw_only=True)
class ExternalServiceStreamResponseDataEvent(ExternalServiceStreamResponseEvent, lang.Final):
    data: ta.Any


@dc.dataclass(frozen=True, kw_only=True)
class ExternalServiceStreamResponseEndEvent(ExternalServiceStreamResponseEvent, lang.Final):
    pass


##


@msh.register_global_lazy_init
def _setup_marshal(cfgs: msh.ConfigRegistry) -> None:
    cfgs.update(Event, *[msh.OpenPolymorphismImpl(et) for et in [
        ExternalServiceRequestEvent,
        ExternalServiceResponseEvent,

        ExternalServiceStreamResponseStartEvent,
        ExternalServiceStreamResponseDataEvent,
        ExternalServiceStreamResponseEndEvent,
    ]])
