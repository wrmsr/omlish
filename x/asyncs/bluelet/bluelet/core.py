# ruff: noqa: UP006 UP007
import abc
import dataclasses as dc
import time
import types
import typing as ta

from .events import Event
from .events import WaitableEvent


ExcInfo: ta.TypeAlias = ta.Tuple[ta.Type[BaseException], BaseException, types.TracebackType]

Coro: ta.TypeAlias = ta.Generator[ta.Union['Event', 'Coro'], ta.Any, None]


##


class CoreEvent(Event, abc.ABC):  # noqa
    pass


##


@dc.dataclass(frozen=True, eq=False)
class ValueEvent(CoreEvent):
    """An event that does nothing but return a fixed value."""

    value: ta.Any


def null() -> Event:
    """Event: yield to the scheduler without doing anything special."""

    return ValueEvent(None)


##


@dc.dataclass(frozen=True, eq=False)
class ExceptionEvent(CoreEvent):
    """Raise an exception at the yield point. Used internally."""

    exc_info: ExcInfo


##


@dc.dataclass(frozen=True, eq=False)
class SpawnEvent(CoreEvent):
    """Add a new coroutine thread to the scheduler."""

    spawned: Coro


def spawn(coro: Coro) -> Event:
    """Event: add another coroutine to the scheduler. Both the parent and child coroutines run concurrently."""

    if not isinstance(coro, types.GeneratorType):
        raise TypeError(f'{coro} is not a coroutine')
    return SpawnEvent(coro)


##


@dc.dataclass(frozen=True, eq=False)
class JoinEvent(CoreEvent):
    """Suspend the thread until the specified child thread has completed."""

    child: Coro


def join(coro: Coro) -> Event:
    """Suspend the thread until another, previously `spawn`ed thread completes."""

    return JoinEvent(coro)


##


@dc.dataclass(frozen=True, eq=False)
class KillEvent(CoreEvent):
    """Unschedule a child thread."""

    child: Coro


def kill(coro: Coro) -> Event:
    """Halt the execution of a different `spawn`ed thread."""

    return KillEvent(coro)


##


@dc.dataclass(frozen=True, eq=False)
class DelegationEvent(CoreEvent):
    """
    Suspend execution of the current thread, start a new thread and, once the child thread finished, return control to
    the parent thread.
    """

    spawned: Coro


def call(coro: Coro) -> Event:
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
    """Return a value the current thread's delegator at the point of delegation. Ends the current (delegate) thread."""

    value: ta.Any


def end(value: ta.Any = None) -> Event:
    """Event: ends the coroutine and returns a value to its delegator."""

    return ReturnEvent(value)


##


@dc.dataclass(frozen=True, eq=False)
class SleepEvent(WaitableEvent, CoreEvent):
    """Suspend the thread for a given duration."""

    wakeup_time: float

    def time_left(self) -> float:
        return max(self.wakeup_time - time.time(), 0.0)


def sleep(duration: float) -> Event:
    """Event: suspend the thread for ``duration`` seconds."""

    return SleepEvent(time.time() + duration)
