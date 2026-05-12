import typing as ta

from omlish import dataclasses as dc
from omlish import lang
from omlish import marshal as msh

from .events.types import Event


##


@dc.dataclass(frozen=True, kw_only=True)
@msh.update_field_options(['service', 'request'], marshal_as=lang.OpaqueRepr, unmarshal_as=lang.OpaqueRepr)
class ExternalServiceRequestEvent(Event, lang.Final):
    service: ta.Any | lang.OpaqueRepr
    request: ta.Any | lang.OpaqueRepr


@dc.dataclass(frozen=True, kw_only=True)
@msh.update_field_options(['service', 'response'], marshal_as=lang.OpaqueRepr, unmarshal_as=lang.OpaqueRepr)
class ExternalServiceResponseEvent(Event, lang.Final):
    service: ta.Any | lang.OpaqueRepr
    response: ta.Any | lang.OpaqueRepr


##


@msh.register_global_lazy_init
def _setup_marshal(cfgs: msh.ConfigRegistry) -> None:
    cfgs.update(Event, *[msh.OpenPolymorphismImpl(et) for et in [
        ExternalServiceRequestEvent,  # type: ignore[list-item]
        ExternalServiceResponseEvent,
    ]])
