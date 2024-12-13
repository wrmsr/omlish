# ruff: noqa: UP006 UP007
# @omlish-lite
# Based on bluelet ( https://github.com/sampsyo/bluelet ) by Adrian Sampson, original license:
# THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
# WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
# COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
# OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
import abc
import dataclasses as dc
import time
import types
import typing as ta

from .events import BlueletEvent
from .events import BlueletFuture
from .events import WaitableBlueletEvent


T = ta.TypeVar('T')

BlueletExcInfo = ta.Tuple[ta.Type[BaseException], BaseException, types.TracebackType]  # ta.TypeAlias

BlueletCoro = ta.Generator[ta.Union['BlueletEvent', 'BlueletCoro'], ta.Any, None]  # ta.TypeAlias

BlueletSpawnable = ta.Union[BlueletCoro, ta.Awaitable]  # ta.TypeAlias


##


@dc.dataclass(frozen=True, eq=False)
class _BlueletAwaitableDriver:
    a: ta.Awaitable

    def __call__(self) -> BlueletCoro:
        g = self.a.__await__()
        gi = iter(g)
        while True:
            try:
                f = gi.send(None)
            except StopIteration as e:
                yield ReturnBlueletEvent(e.value)
                break
            else:
                if not isinstance(f, BlueletFuture):
                    raise TypeError(f)
                res = yield f.event
                f.done = True
                f.result = res


##


class CoreBlueletEvent(BlueletEvent, abc.ABC):  # noqa
    pass


@dc.dataclass(frozen=True, eq=False)
class ValueBlueletEvent(CoreBlueletEvent, ta.Generic[T]):
    """An event that does nothing but return a fixed value."""

    value: T


@dc.dataclass(frozen=True, eq=False)
class ExceptionBlueletEvent(CoreBlueletEvent):
    """Raise an exception at the yield point. Used internally."""

    exc_info: BlueletExcInfo


@dc.dataclass(frozen=True, eq=False)
class SpawnBlueletEvent(CoreBlueletEvent):
    """Add a new coroutine coro to the scheduler."""

    spawned: BlueletSpawnable


@dc.dataclass(frozen=True, eq=False)
class JoinBlueletEvent(CoreBlueletEvent):
    """Suspend the coro until the specified child coro has completed."""

    child: BlueletCoro


@dc.dataclass(frozen=True, eq=False)
class KillBlueletEvent(CoreBlueletEvent):
    """Unschedule a child coro."""

    child: BlueletCoro


@dc.dataclass(frozen=True, eq=False)
class DelegationBlueletEvent(CoreBlueletEvent):
    """
    Suspend execution of the current coro, start a new coro and, once the child coro finished, return control to
    the parent coro.
    """

    spawned: BlueletCoro


@dc.dataclass(frozen=True, eq=False)
class ReturnBlueletEvent(CoreBlueletEvent, ta.Generic[T]):
    """Return a value the current coro's delegator at the point of delegation. Ends the current (delegate) coro."""

    value: ta.Optional[T]


@dc.dataclass(frozen=True, eq=False)
class SleepBlueletEvent(WaitableBlueletEvent, CoreBlueletEvent):
    """Suspend the coro for a given duration."""

    wakeup_time: float

    def time_left(self) -> float:
        return max(self.wakeup_time - time.time(), 0.)


##


class _CoreBlueletApi:
    def value(self, v: T) -> ValueBlueletEvent[T]:
        """Event: yield a value."""

        return ValueBlueletEvent(v)

    def null(self) -> ValueBlueletEvent[None]:
        """Event: yield to the scheduler without doing anything special."""

        return ValueBlueletEvent(None)

    def spawn(self, spawned: BlueletSpawnable) -> SpawnBlueletEvent:
        """Event: add another coroutine to the scheduler. Both the parent and child coroutines run concurrently."""

        if isinstance(spawned, types.CoroutineType):
            spawned = _BlueletAwaitableDriver(spawned)()

        if not isinstance(spawned, types.GeneratorType):
            raise TypeError(f'{spawned} is not spawnable')

        return SpawnBlueletEvent(spawned)

    def join(self, coro: BlueletCoro) -> JoinBlueletEvent:
        """Suspend the coro until another, previously `spawn`ed coro completes."""

        return JoinBlueletEvent(coro)

    def kill(self, coro: BlueletCoro) -> KillBlueletEvent:
        """Halt the execution of a different `spawn`ed coro."""

        return KillBlueletEvent(coro)

    def call(self, spawned: BlueletSpawnable) -> DelegationBlueletEvent:
        """
        Event: delegate to another coroutine. The current coroutine is resumed once the sub-coroutine finishes. If the
        sub-coroutine returns a value using end(), then this event returns that value.
        """

        if isinstance(spawned, types.CoroutineType):
            spawned = _BlueletAwaitableDriver(spawned)()

        if not isinstance(spawned, types.GeneratorType):
            raise TypeError(f'{spawned} is not spawnable')

        return DelegationBlueletEvent(spawned)

    def end(self, value: ta.Optional[T] = None) -> ReturnBlueletEvent[T]:
        """Event: ends the coroutine and returns a value to its delegator."""

        return ReturnBlueletEvent(value)

    def sleep(self, duration: float) -> SleepBlueletEvent:
        """Event: suspend the coro for ``duration`` seconds."""

        return SleepBlueletEvent(time.time() + duration)
