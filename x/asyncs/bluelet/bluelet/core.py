# Based on bluelet ( https://github.com/sampsyo/bluelet ) by Adrian Sampson, original license:
# THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
# WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
# COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
# OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
# ruff: noqa: UP006 UP007
import abc
import dataclasses as dc
import time
import types
import typing as ta

from .events import BlueletEvent
from .events import WaitableBlueletEvent


T = ta.TypeVar('T')

BlueletEventT = ta.TypeVar('BlueletEventT', bound='BlueletEvent')

BlueletExcInfo = ta.Tuple[ta.Type[BaseException], BaseException, types.TracebackType]  # ta.TypeAlias

BlueletCoro = ta.Generator[ta.Union['BlueletEvent', 'BlueletCoro'], ta.Any, None]  # ta.TypeAlias


##


class CoreBlueletEvent(BlueletEvent, abc.ABC):  # noqa
    pass


##


@dc.dataclass(frozen=True, eq=False)
class ValueBlueletEvent(CoreBlueletEvent, ta.Generic[T]):
    """An event that does nothing but return a fixed value."""

    value: T


def bluelet_value(v: T) -> ValueBlueletEvent[T]:
    """Event: yield a value."""

    return ValueBlueletEvent(v)


def bluelet_null() -> ValueBlueletEvent[None]:
    """Event: yield to the scheduler without doing anything special."""

    return ValueBlueletEvent(None)


##


@dc.dataclass(frozen=True, eq=False)
class ExceptionBlueletEvent(CoreBlueletEvent):
    """Raise an exception at the yield point. Used internally."""

    exc_info: BlueletExcInfo


##


@dc.dataclass(frozen=True, eq=False)
class SpawnBlueletEvent(CoreBlueletEvent):
    """Add a new coroutine coro to the scheduler."""

    spawned: BlueletCoro


def bluelet_spawn(coro: BlueletCoro) -> SpawnBlueletEvent:
    """Event: add another coroutine to the scheduler. Both the parent and child coroutines run concurrently."""

    if not isinstance(coro, types.GeneratorType):
        raise TypeError(f'{coro} is not a coroutine')
    return SpawnBlueletEvent(coro)


##


@dc.dataclass(frozen=True, eq=False)
class JoinBlueletEvent(CoreBlueletEvent):
    """Suspend the coro until the specified child coro has completed."""

    child: BlueletCoro


def bluelet_join(coro: BlueletCoro) -> JoinBlueletEvent:
    """Suspend the coro until another, previously `spawn`ed coro completes."""

    return JoinBlueletEvent(coro)


##


@dc.dataclass(frozen=True, eq=False)
class KillBlueletEvent(CoreBlueletEvent):
    """Unschedule a child coro."""

    child: BlueletCoro


def bluelet_kill(coro: BlueletCoro) -> KillBlueletEvent:
    """Halt the execution of a different `spawn`ed coro."""

    return KillBlueletEvent(coro)


##


@dc.dataclass(frozen=True, eq=False)
class DelegationBlueletEvent(CoreBlueletEvent):
    """
    Suspend execution of the current coro, start a new coro and, once the child coro finished, return control to
    the parent coro.
    """

    spawned: BlueletCoro


def bluelet_call(coro: BlueletCoro) -> DelegationBlueletEvent:
    """
    Event: delegate to another coroutine. The current coroutine is resumed once the sub-coroutine finishes. If the
    sub-coroutine returns a value using end(), then this event returns that value.
    """

    if not isinstance(coro, types.GeneratorType):
        raise TypeError(f'{coro} is not a coroutine')
    return DelegationBlueletEvent(coro)


##


@dc.dataclass(frozen=True, eq=False)
class ReturnBlueletEvent(CoreBlueletEvent, ta.Generic[T]):
    """Return a value the current coro's delegator at the point of delegation. Ends the current (delegate) coro."""

    value: T


def bluelet_end(value: T = None) -> ReturnBlueletEvent[T]:
    """Event: ends the coroutine and returns a value to its delegator."""

    return ReturnBlueletEvent(value)


##


@dc.dataclass(frozen=True, eq=False)
class SleepBlueletEvent(WaitableBlueletEvent, CoreBlueletEvent):
    """Suspend the coro for a given duration."""

    wakeup_time: float

    def time_left(self) -> float:
        return max(self.wakeup_time - time.time(), 0.)


def bluelet_sleep(duration: float) -> SleepBlueletEvent:
    """Event: suspend the coro for ``duration`` seconds."""

    return SleepBlueletEvent(time.time() + duration)
