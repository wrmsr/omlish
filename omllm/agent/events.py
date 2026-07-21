import typing as ta

from omcore import dataclasses as dc
from omcore import lang

from .contexts import Context
from .messages import Message


##


@dc.dataclass(frozen=True)
class Event(lang.Abstract):
    pass


type EventSink = ta.Callable[[Event], ta.Awaitable[None]]


##


@ta.final
@dc.dataclass(frozen=True)
class AgentStartEvent(Event):
    pass


@ta.final
@dc.dataclass(frozen=True, kw_only=True)
class AgentEndEvent(Event):
    context: Context

    new_messages: ta.Sequence[Message] | None = None


##


@ta.final
@dc.dataclass(frozen=True)
class TurnStartEvent(Event):
    pass


@ta.final
@dc.dataclass(frozen=True, kw_only=True)
class TurnEndEvent(Event):
    message: Message
