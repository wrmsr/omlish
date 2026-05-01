import typing as ta

from omlish import dataclasses as dc
from omlish import lang
from omlish import marshal as msh

from ..types import Event


##


class EventCallback(lang.Func1[Event, ta.Awaitable[None]]):
    pass


async def _nop_event_callback(event: Event) -> None:
    pass


NOP_EVENT_CALLBACK = EventCallback(_nop_event_callback)


EventCallbacks = ta.NewType('EventCallbacks', ta.Sequence[EventCallback])


##


@dc.dataclass(frozen=True)
@msh.update_fields_options(['error'], marshal_as=lang.OpaqueRepr | None, unmarshal_as=lang.OpaqueRepr | None)
class ErrorEvent(Event, lang.Final):
    message: str | None = None
    error: BaseException | lang.OpaqueRepr | None = None


##


@msh.register_global_lazy_init
def _setup_marshal(cfgs: msh.ConfigRegistry) -> None:
    msh.install_standard_factories_to(
        cfgs,
        msh.OpenPolymorphismMarshalerFactory(Event, opo := msh.OpenPolymorphismOptions(
            naming=msh.Naming.SNAKE,
            strip_suffix=True,
        )),
        msh.OpenPolymorphismUnmarshalerFactory(Event, opo),
    )

    cfgs.update(Event, msh.OpenPolymorphismImpl(ErrorEvent))
