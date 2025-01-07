# ruff: noqa: UP006 UP007
# @omlish-lite
# Based on bluelet ( https://github.com/sampsyo/bluelet ) by Adrian Sampson, original license:
# THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
# WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
# COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
# OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""
TODO:
 - use fdio
 - wrap coros in Tasks :|
 - (unit)tests lol
 - * subprocesses
 - canceling
 - timeouts
 - task groups
 - gather
 - locks / semaphores / events / etc
 - rename Coro to Bluelet?
 - shutdown
 - ensure resource cleanup
 - run_thread? whatever?

Subprocs:
 - https://github.com/python/cpython/issues/120804 - GH-120804: Remove get_child_watcher and set_child_watcher from
   asyncio
 - https://github.com/python/cpython/pull/17063/files bpo-38692: Add os.pidfd_open
 - clone PidfdChildWatcher + ThreadedChildWatcher
"""
import collections
import dataclasses as dc
import errno
import logging
import select
import sys
import time
import traceback
import types
import typing as ta
import weakref

from .core import BlueletCoro
from .core import BlueletExcInfo
from .core import CoreBlueletEvent
from .core import DelegationBlueletEvent
from .core import ExceptionBlueletEvent
from .core import JoinBlueletEvent
from .core import KillBlueletEvent
from .core import ReturnBlueletEvent
from .core import SleepBlueletEvent
from .core import SpawnBlueletEvent
from .core import ValueBlueletEvent
from .core import _BlueletAwaitableDriver
from .events import BlueletEvent
from .events import BlueletWaitable
from .events import WaitableBlueletEvent


##


class BlueletCoroException(Exception):  # noqa
    def __init__(self, coro: BlueletCoro, exc_info: BlueletExcInfo) -> None:
        super().__init__()
        self.coro = coro
        self.exc_info = exc_info

    @staticmethod
    def _exc_info() -> BlueletExcInfo:
        return sys.exc_info()  # type: ignore

    @staticmethod
    def _reraise(typ: ta.Type[BaseException], exc: BaseException, tb: types.TracebackType) -> ta.NoReturn:  # noqa
        raise exc.with_traceback(tb)

    def reraise(self) -> ta.NoReturn:
        self._reraise(self.exc_info[0], self.exc_info[1], self.exc_info[2])


##


def _bluelet_event_select(
        events: ta.Iterable[BlueletEvent],
        *,
        log: ta.Optional[logging.Logger] = None,
) -> ta.Set[WaitableBlueletEvent]:
    """
    Perform a select() over all the Events provided, returning the ones ready to be fired. Only WaitableEvents
    (including SleepEvents) matter here; all other events are ignored (and thus postponed).
    """

    waitable_to_event: ta.Dict[ta.Tuple[str, BlueletWaitable], WaitableBlueletEvent] = {}
    rlist: ta.List[BlueletWaitable] = []
    wlist: ta.List[BlueletWaitable] = []
    xlist: ta.List[BlueletWaitable] = []
    earliest_wakeup: ta.Optional[float] = None

    # Gather waitables and wakeup times.
    for event in events:
        if isinstance(event, SleepBlueletEvent):
            if not earliest_wakeup:
                earliest_wakeup = event.wakeup_time
            else:
                earliest_wakeup = min(earliest_wakeup, event.wakeup_time)

        elif isinstance(event, WaitableBlueletEvent):
            ew = event.waitables()
            rlist.extend(ew.r)
            wlist.extend(ew.w)
            xlist.extend(ew.x)
            for waitable in ew.r:
                waitable_to_event[('r', waitable)] = event
            for waitable in ew.w:
                waitable_to_event[('w', waitable)] = event
            for waitable in ew.x:
                waitable_to_event[('x', waitable)] = event

    # If we have a any sleeping coros, determine how long to sleep.
    if earliest_wakeup:
        timeout = max(earliest_wakeup - time.time(), 0.)
    else:
        timeout = None

    # Perform select() if we have any waitables.
    if rlist or wlist or xlist:
        if log:
            log.debug('_bluelet_event_select: +select: %r %r %r %r', rlist, wlist, xlist, timeout)
        rready, wready, xready = select.select(rlist, wlist, xlist, timeout)
        if log:
            log.debug('_bluelet_event_select: -select: %r %r %r', rready, wready, xready)

    else:
        rready, wready, xready = [], [], []
        if timeout:
            if log:
                log.debug('_bluelet_event_select: sleep: %r', timeout)
            time.sleep(timeout)

    # Gather ready events corresponding to the ready waitables.
    ready_events: ta.Set[WaitableBlueletEvent] = set()
    for ready in rready:
        ready_events.add(waitable_to_event[('r', ready)])
    for ready in wready:
        ready_events.add(waitable_to_event[('w', ready)])
    for ready in xready:
        ready_events.add(waitable_to_event[('x', ready)])

    # Gather any finished sleeps.
    for event in events:
        if isinstance(event, SleepBlueletEvent) and not event.time_left():
            ready_events.add(event)

    return ready_events


##


class _SuspendedBlueletEvent(CoreBlueletEvent):
    pass


_BLUELET_SUSPENDED = _SuspendedBlueletEvent()  # Special sentinel placeholder for suspended coros.


@dc.dataclass(frozen=True, eq=False)
class _DelegatedBlueletEvent(CoreBlueletEvent):
    """Placeholder indicating that a coro has delegated execution to a different coro."""

    child: BlueletCoro


class _BlueletRunner:
    """
    Schedules a coroutine, running it to completion. This encapsulates the Bluelet scheduler, which the root coroutine
    can add to by spawning new coroutines.
    """

    def __init__(
            self,
            root_coro: BlueletCoro,
            *,
            log: ta.Optional[logging.Logger] = None,
    ) -> None:
        super().__init__()

        self._root_coro = root_coro
        self._log = log

        # The "coros" dictionary keeps track of all the currently-executing and suspended coroutines. It maps
        # coroutines to their currently "blocking" event. The event value may be SUSPENDED if the coroutine is waiting
        # on some other condition: namely, a delegated coroutine or a joined coroutine. In this case, the coroutine
        # should *also* appear as a value in one of the below dictionaries `delegators` or `joiners`.
        self._coros: ta.Dict[BlueletCoro, BlueletEvent] = {self._root_coro: ValueBlueletEvent(None)}

        # Maps child coroutines to delegating parents.
        self._delegators: ta.Dict[BlueletCoro, BlueletCoro] = {}

        # Maps child coroutines to joining (exit-waiting) parents.
        self._joiners: ta.MutableMapping[BlueletCoro, ta.List[BlueletCoro]] = collections.defaultdict(list)

        # History of spawned coroutines for joining of already completed coroutines.
        self._history: ta.MutableMapping[BlueletCoro, ta.Optional[BlueletEvent]] = \
            weakref.WeakKeyDictionary({self._root_coro: None})

    def _complete_coro(self, coro: BlueletCoro, return_value: ta.Any) -> None:
        """
        Remove a coroutine from the scheduling pool, awaking delegators and joiners as necessary and returning the
        specified value to any delegating parent.
        """

        del self._coros[coro]

        # Resume delegator.
        if coro in self._delegators:
            self._coros[self._delegators[coro]] = ValueBlueletEvent(return_value)
            del self._delegators[coro]

        # Resume joiners.
        if coro in self._joiners:
            for parent in self._joiners[coro]:
                self._coros[parent] = ValueBlueletEvent(None)
            del self._joiners[coro]

    def _advance_coro(self, coro: BlueletCoro, value: ta.Any, is_exc: bool = False) -> None:
        """
        After an event is fired, run a given coroutine associated with it in the coros dict until it yields again. If
        the coroutine exits, then the coro is removed from the pool. If the coroutine raises an exception, it is
        reraised in a CoroException. If is_exc is True, then the value must be an exc_info tuple and the exception is
        thrown into the coroutine.
        """

        try:
            if is_exc:
                next_event = coro.throw(value[0])
            else:
                next_event = coro.send(value)

        except StopIteration:
            # Coro is done.
            self._complete_coro(coro, None)

        except BaseException:  # noqa
            # Coro raised some other exception.
            del self._coros[coro]
            # Note: Don't use `raise from` as this should support 3.8.
            raise BlueletCoroException(coro, BlueletCoroException._exc_info())  # noqa

        else:
            if isinstance(next_event, ta.Generator):
                # Automatically invoke sub-coroutines. (Shorthand for explicit bluelet.call().)
                next_event = DelegationBlueletEvent(next_event)

            if isinstance(next_event, types.CoroutineType):  # type: ignore[unreachable]
                next_event = DelegationBlueletEvent(_BlueletAwaitableDriver(next_event)())  # type: ignore[unreachable]

            if not isinstance(next_event, BlueletEvent):
                raise TypeError(next_event)

            self._coros[coro] = next_event

    def _kill_coro(self, coro: BlueletCoro) -> None:
        """Unschedule this coro and its (recursive) delegates."""

        # Collect all coroutines in the delegation stack.
        coros = [coro]
        while isinstance((cur := self._coros[coro]), _DelegatedBlueletEvent):
            coro = cur.child  # noqa
            coros.append(coro)

        # Complete each coroutine from the top to the bottom of the stack.
        for coro in reversed(coros):
            self._complete_coro(coro, None)

    def close(self) -> None:
        # If any coros still remain, kill them.
        for coro in self._coros:
            coro.close()

        self._coros.clear()

    def _handle_core_event(self, coro: BlueletCoro, event: CoreBlueletEvent) -> bool:
        if self._log:
            self._log.debug(f'{self.__class__.__name__}._handle_core_event: %r %r', coro, event)

        if isinstance(event, SpawnBlueletEvent):
            sc = ta.cast(BlueletCoro, event.spawned)  # FIXME
            self._coros[sc] = ValueBlueletEvent(None)  # Spawn.
            self._history[sc] = None  # Record in history.
            self._advance_coro(coro, None)
            return True

        elif isinstance(event, ValueBlueletEvent):
            self._advance_coro(coro, event.value)
            return True

        elif isinstance(event, ExceptionBlueletEvent):
            self._advance_coro(coro, event.exc_info, True)
            return True

        elif isinstance(event, DelegationBlueletEvent):
            self._coros[coro] = _DelegatedBlueletEvent(event.spawned)  # Suspend.
            self._coros[event.spawned] = ValueBlueletEvent(None)  # Spawn.
            self._history[event.spawned] = None  # Record in history.
            self._delegators[event.spawned] = coro
            return True

        elif isinstance(event, ReturnBlueletEvent):
            # Coro is done.
            self._complete_coro(coro, event.value)
            return True

        elif isinstance(event, JoinBlueletEvent):
            if event.child not in self._coros and event.child in self._history:
                self._coros[coro] = ValueBlueletEvent(None)
            else:
                self._coros[coro] = _BLUELET_SUSPENDED  # Suspend.
                self._joiners[event.child].append(coro)
            return True

        elif isinstance(event, KillBlueletEvent):
            self._coros[coro] = ValueBlueletEvent(None)
            self._kill_coro(event.child)
            return True

        elif isinstance(event, (_DelegatedBlueletEvent, _SuspendedBlueletEvent)):
            return False

        else:
            raise TypeError(event)

    def _step(self) -> ta.Optional[BlueletCoroException]:
        if self._log:
            self._log.debug(f'{self.__class__.__name__}._step')  # Noqa

        try:
            # Look for events that can be run immediately. Continue running immediate events until nothing is ready.
            while True:
                have_ready = False
                for coro, event in list(self._coros.items()):
                    if isinstance(event, CoreBlueletEvent) and not isinstance(event, SleepBlueletEvent):
                        have_ready |= self._handle_core_event(coro, event)
                    elif isinstance(event, WaitableBlueletEvent):
                        pass
                    else:
                        raise TypeError(f'Unknown event type: {event}')  # noqa

                # Only start the select when nothing else is ready.
                if not have_ready:
                    break

            # Wait and fire.
            event2coro = {v: k for k, v in self._coros.items()}
            for event in _bluelet_event_select(self._coros.values()):
                # Run the IO operation, but catch socket errors.
                try:
                    value = event.fire()
                except OSError as exc:
                    if isinstance(exc.args, tuple) and exc.args[0] == errno.EPIPE:
                        # Broken pipe. Remote host disconnected.
                        pass
                    elif isinstance(exc.args, tuple) and exc.args[0] == errno.ECONNRESET:
                        # Connection was reset by peer.
                        pass
                    else:
                        traceback.print_exc()
                    # Abort the coroutine.
                    self._coros[event2coro[event]] = ReturnBlueletEvent(None)
                else:
                    self._advance_coro(event2coro[event], value)

        except BlueletCoroException as te:
            if self._log and self._log.isEnabledFor(logging.DEBUG):
                self._log.exception(f'{self.__class__.__name__}._step')

            # Exception raised from inside a coro.
            event = ExceptionBlueletEvent(te.exc_info)
            if te.coro in self._delegators:
                # The coro is a delegate. Raise exception in its delegator.
                self._coros[self._delegators[te.coro]] = event
                del self._delegators[te.coro]
            else:
                # The coro is root-level. Raise in client code.
                return te

        except BaseException:  # noqa
            ei = BlueletCoroException._exc_info()  # noqa

            if self._log and self._log.isEnabledFor(logging.DEBUG):
                self._log.exception(f'{self.__class__.__name__}._step')

            # For instance, KeyboardInterrupt during select(). Raise into root coro and terminate others.
            self._coros = {self._root_coro: ExceptionBlueletEvent(ei)}  # noqa

        return None

    def run(self) -> None:
        # Continue advancing coros until root coro exits.
        exit_ce: BlueletCoroException | None = None
        while self._coros:
            exit_ce = self._step()

        self.close()

        # If we're exiting with an exception, raise it in the client.
        if exit_ce:
            exit_ce.reraise()


##


class _RunnerBlueletApi:
    def run(self, root_coro: BlueletCoro) -> None:
        _BlueletRunner(root_coro).run()
