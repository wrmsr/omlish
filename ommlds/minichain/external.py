import typing as ta

from omlish import dataclasses as dc
from omlish import lang
from omlish import marshal as msh

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
@msh.update_field_options('request', **_MARSHAL_FIELD_OPAQUE_REPR_KWARGS)
class ExternalServiceRequestEvent(ExternalServiceEvent, lang.Final):
    request: ta.Any | lang.OpaqueRepr


@dc.dataclass(frozen=True, kw_only=True)
@msh.update_field_options('response', **_MARSHAL_FIELD_OPAQUE_REPR_KWARGS)
class ExternalServiceResponseEvent(ExternalServiceEvent, lang.Final):
    response: ta.Any | lang.OpaqueRepr


#


class ExternalServiceStreamResponseEvent(ExternalServiceEvent, lang.Abstract):
    pass


@dc.dataclass(frozen=True, kw_only=True)
class ExternalServiceStreamResponseStartEvent(ExternalServiceStreamResponseEvent, lang.Final):
    pass


@dc.dataclass(frozen=True, kw_only=True)
@msh.update_field_options('data', **_MARSHAL_FIELD_OPAQUE_REPR_KWARGS)
class ExternalServiceStreamResponseDataEvent(ExternalServiceStreamResponseEvent, lang.Final):
    data: ta.Any | lang.OpaqueRepr


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
