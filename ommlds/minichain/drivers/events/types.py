import typing as ta

from omlish import dataclasses as dc
from omlish import lang


##


class Event(lang.Abstract):
    pass


class EventCallback(lang.Func1[Event, ta.Awaitable[None]]):
    pass


EventCallbacks = ta.NewType('EventCallbacks', ta.Sequence[EventCallback])


##


@dc.dataclass(frozen=True)
class ErrorEvent(Event, lang.Final):
    message: str | None = None
    error: BaseException | None = None
