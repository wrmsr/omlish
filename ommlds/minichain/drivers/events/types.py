import typing as ta

from omlish import dataclasses as dc
from omlish import lang
from omlish import marshal as msh

from ..types import Event


##


class EventCallback(lang.Func1[Event, ta.Awaitable[None]]):
    pass


EventCallbacks = ta.NewType('EventCallbacks', ta.Sequence[EventCallback])


##


@dc.dataclass(frozen=True)
@msh.update_fields_options(['error'], marshal_as=msh.OpaqueRepr, unmarshal_as=msh.OpaqueRepr)
class ErrorEvent(Event, lang.Final):
    message: str | None = None
    error: BaseException | None = None
