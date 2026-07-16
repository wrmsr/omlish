import typing as ta

from omcore import dataclasses as dc
from omcore import lang


##


@dc.dataclass(frozen=True)
class Event(lang.Abstract):
    pass


type EventSink = ta.Callable[[Event], ta.Awaitable[None]]
