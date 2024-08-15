# ruff: noqa: UP006 UP007
import abc
import dataclasses as dc
import time
import types
import typing as ta

from .events import Event
from .events import WaitableEvent


BlueletExcInfo = ta.Tuple[ta.Type[BaseException], BaseException, types.TracebackType]  # ta.TypeAlias

BlueletCoro = ta.Generator[ta.Union['Event', 'BlueletCoro'], ta.Any, None]  # ta.TypeAlias


##


class CoreEvent(Event, abc.ABC):  # noqa
    pass


##


@dc.dataclass(frozen=True, eq=False)
class ValueEvent(CoreEvent):
    """An event that does nothing but return a fixed value."""

    value: ta.Any


def value(v: ta.Any) -> Event:
    """Event: yield a value."""

    return ValueEvent(v)


def null() -> Event:
    """Event: yield to the scheduler without doing anything special."""

    return ValueEvent(None)


##


@dc.dataclass(frozen=True, eq=False)
class ExceptionEvent(CoreEvent):
    """Raise an exception at the yield point. Used internally."""

    exc_info: BlueletExcInfo


##


@dc.dataclass(frozen=True, eq=False)
class SpawnEvent(CoreEvent):
    """Add a new coroutine coro to the scheduler."""

    spawned: BlueletCoro


def spawn(coro: BlueletCoro) -> Event:
    """Event: add another coroutine to the scheduler. Both the parent and child coroutines run concurrently."""

    if not isinstance(coro, types.GeneratorType):
        raise TypeError(f'{coro} is not a coroutine')
    return SpawnEvent(coro)


##


@dc.dataclass(frozen=True, eq=False)
class JoinEvent(CoreEvent):
    """Suspend the coro until the specified child coro has completed."""

    child: BlueletCoro


def join(coro: BlueletCoro) -> Event:
    """Suspend the coro until another, previously `spawn`ed coro completes."""

    return JoinEvent(coro)


##


@dc.dataclass(frozen=True, eq=False)
class KillEvent(CoreEvent):
    """Unschedule a child coro."""

    child: BlueletCoro


def kill(coro: BlueletCoro) -> Event:
    """Halt the execution of a different `spawn`ed coro."""

    return KillEvent(coro)


##


@dc.dataclass(frozen=True, eq=False)
class DelegationEvent(CoreEvent):
    """
    Suspend execution of the current coro, start a new coro and, once the child coro finished, return control to
    the parent coro.
    """

    spawned: BlueletCoro


def call(coro: BlueletCoro) -> Event:
    """
    Event: delegate to another coroutine. The current coroutine is resumed once the sub-coroutine finishes. If the
    sub-coroutine returns a value using end(), then this event returns that value.
    """

    if not isinstance(coro, types.GeneratorType):
        raise TypeError(f'{coro} is not a coroutine')
    return DelegationEvent(coro)


##


@dc.dataclass(frozen=True, eq=False)
class ReturnEvent(CoreEvent):
    """Return a value the current coro's delegator at the point of delegation. Ends the current (delegate) coro."""

    value: ta.Any


def end(value: ta.Any = None) -> Event:
    """Event: ends the coroutine and returns a value to its delegator."""

    return ReturnEvent(value)


##


@dc.dataclass(frozen=True, eq=False)
class SleepEvent(WaitableEvent, CoreEvent):
    """Suspend the coro for a given duration."""

    wakeup_time: float

    def time_left(self) -> float:
        return max(self.wakeup_time - time.time(), 0.)


def sleep(duration: float) -> Event:
    """Event: suspend the coro for ``duration`` seconds."""

    return SleepEvent(time.time() + duration)
