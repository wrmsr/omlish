# ruff: noqa: UP007
import abc
import dataclasses as dc
import typing as ta


##


class Event(abc.ABC):  # noqa
    """
    Just a base class identifying Bluelet events. An event is an object yielded from a Bluelet coro coroutine to
    suspend operation and communicate with the scheduler.
    """


##


class HasFileno(ta.Protocol):
    def fileno(self) -> int: ...


Waitable = ta.Union[int, HasFileno]  # ta.TypeAlias


@dc.dataclass(frozen=True)
class Waitables:
    r: ta.Sequence[Waitable] = ()
    w: ta.Sequence[Waitable] = ()
    x: ta.Sequence[Waitable] = ()


class WaitableEvent(Event, abc.ABC):  # noqa
    """
    A waitable event is one encapsulating an action that can be waited for using a select() call. That is, it's an event
    with an associated file descriptor.
    """

    def waitables(self) -> Waitables:
        """
        Return "waitable" objects to pass to select(). Should return three iterables for input readiness, output
        readiness, and exceptional conditions (i.e., the three lists passed to select()).
        """
        return Waitables()

    def fire(self) -> ta.Any:
        """Called when an associated file descriptor becomes ready (i.e., is returned from a select() call)."""
