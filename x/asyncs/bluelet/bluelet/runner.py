"""
TDOO:
 - (unit)tests lol
 - amalgify? prefix everything w/ Blue? prob want some helper Namespace or smth
 - task groups
 - gather
 - locks / semaphores / events / etc
 - subprocesses
 - ensure no unknown event types - Waitable subtypes okay
 - rename Coro to Bluelet?
 - shutdown
 - ensure resource cleanup
"""
# ruff: noqa: UP006 UP007
import collections
import dataclasses as dc
import errno
import select
import sys
import time
import traceback
import types
import typing as ta
import weakref

from .core import CoreEvent
from .core import Coro
from .core import DelegationEvent
from .core import ExceptionEvent
from .core import ExcInfo
from .core import JoinEvent
from .core import KillEvent
from .core import ReturnEvent
from .core import SleepEvent
from .core import SpawnEvent
from .core import ValueEvent
from .events import Event
from .events import Waitable
from .events import WaitableEvent


##


def _exc_info() -> ExcInfo:
    return sys.exc_info()  # type: ignore


def _reraise(typ: ta.Type[BaseException], exc: BaseException, tb: types.TracebackType) -> ta.NoReturn:
    raise exc.with_traceback(tb)


class CoroException(Exception):  # noqa
    def __init__(self, coro: Coro, exc_info: ExcInfo) -> None:
        super().__init__()
        self.coro = coro
        self.exc_info = exc_info

    def reraise(self) -> ta.NoReturn:
        _reraise(self.exc_info[0], self.exc_info[1], self.exc_info[2])


##


def _event_select(events: ta.Iterable[Event]) -> ta.Set[WaitableEvent]:
    """
    Perform a select() over all the Events provided, returning the ones ready to be fired. Only WaitableEvents
    (including SleepEvents) matter here; all other events are ignored (and thus postponed).
    """

    waitable_to_event: ta.Dict[ta.Tuple[str, Waitable], WaitableEvent] = {}
    rlist: ta.List[Waitable] = []
    wlist: ta.List[Waitable] = []
    xlist: ta.List[Waitable] = []
    earliest_wakeup: ta.Optional[float] = None

    # Gather waitables and wakeup times.
    for event in events:
        if isinstance(event, SleepEvent):
            if not earliest_wakeup:
                earliest_wakeup = event.wakeup_time
            else:
                earliest_wakeup = min(earliest_wakeup, event.wakeup_time)

        elif isinstance(event, WaitableEvent):
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
        rready, wready, xready = select.select(rlist, wlist, xlist, timeout)
    else:
        rready, wready, xready = [], [], []
        if timeout:
            time.sleep(timeout)

    # Gather ready events corresponding to the ready waitables.
    ready_events: ta.Set[WaitableEvent] = set()
    for ready in rready:
        ready_events.add(waitable_to_event[('r', ready)])
    for ready in wready:
        ready_events.add(waitable_to_event[('w', ready)])
    for ready in xready:
        ready_events.add(waitable_to_event[('x', ready)])

    # Gather any finished sleeps.
    for event in events:
        if isinstance(event, SleepEvent) and not event.time_left():
            ready_events.add(event)

    return ready_events


##


class _SuspendedEvent(CoreEvent):
    pass


_SUSPENDED = _SuspendedEvent()  # Special sentinel placeholder for suspended coros.


@dc.dataclass(frozen=True, eq=False)
class _DelegatedEvent(CoreEvent):
    """Placeholder indicating that a coro has delegated execution to a different coro."""

    child: Coro


class _Runner:
    """
    Schedules a coroutine, running it to completion. This encapsulates the Bluelet scheduler, which the root coroutine
    can add to by spawning new coroutines.
    """

    def __init__(self, root_coro: Coro) -> None:
        super().__init__()

        self._root_coro = root_coro

        # The "coros" dictionary keeps track of all the currently-executing and suspended coroutines. It maps
        # coroutines to their currently "blocking" event. The event value may be SUSPENDED if the coroutine is waiting
        # on some other condition: namely, a delegated coroutine or a joined coroutine. In this case, the coroutine
        # should *also* appear as a value in one of the below dictionaries `delegators` or `joiners`.
        self._coros: ta.Dict[Coro, Event] = {self._root_coro: ValueEvent(None)}

        # Maps child coroutines to delegating parents.
        self._delegators: ta.Dict[Coro, Coro] = {}

        # Maps child coroutines to joining (exit-waiting) parents.
        self._joiners: ta.MutableMapping[Coro, ta.List[Coro]] = collections.defaultdict(list)

        # History of spawned coroutines for joining of already completed coroutines.
        self._history: ta.MutableMapping[Coro, ta.Optional[Event]] = weakref.WeakKeyDictionary({self._root_coro: None})

    def _complete_coro(self, coro: Coro, return_value: ta.Any) -> None:
        """
        Remove a coroutine from the scheduling pool, awaking delegators and joiners as necessary and returning the
        specified value to any delegating parent.
        """

        del self._coros[coro]

        # Resume delegator.
        if coro in self._delegators:
            self._coros[self._delegators[coro]] = ValueEvent(return_value)
            del self._delegators[coro]

        # Resume joiners.
        if coro in self._joiners:
            for parent in self._joiners[coro]:
                self._coros[parent] = ValueEvent(None)
            del self._joiners[coro]

    def _advance_coro(self, coro: Coro, value: ta.Any, is_exc: bool = False) -> None:
        """
        After an event is fired, run a given coroutine associated with it in the coros dict until it yields again. If
        the coroutine exits, then the coro is removed from the pool. If the coroutine raises an exception, it is
        reraised in a CoroException. If is_exc is True, then the value must be an exc_info tuple and the exception is
        thrown into the coroutine.
        """

        try:
            if is_exc:
                next_event = coro.throw(*value)
            else:
                next_event = coro.send(value)

        except StopIteration:
            # Coro is done.
            self._complete_coro(coro, None)

        except:  # noqa
            # Coro raised some other exception.
            del self._coros[coro]
            # Note: Don't use `raise from` as this should support 3.8.
            raise CoroException(coro, _exc_info())  # noqa

        else:
            if isinstance(next_event, ta.Generator):
                # Automatically invoke sub-coroutines. (Shorthand for explicit bluelet.call().)
                next_event = DelegationEvent(next_event)
            self._coros[coro] = next_event

    def _kill_coro(self, coro: Coro) -> None:
        """Unschedule this coro and its (recursive) delegates."""

        # Collect all coroutines in the delegation stack.
        coros = [coro]
        while isinstance((cur := self._coros[coro]), _DelegatedEvent):
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

    def _handle_core_event(self, coro: Coro, event: CoreEvent) -> bool:
        if isinstance(event, SpawnEvent):
            self._coros[event.spawned] = ValueEvent(None)  # Spawn.
            self._history[event.spawned] = None  # Record in history.
            self._advance_coro(coro, None)
            return True

        elif isinstance(event, ValueEvent):
            self._advance_coro(coro, event.value)
            return True

        elif isinstance(event, ExceptionEvent):
            self._advance_coro(coro, event.exc_info, True)
            return True

        elif isinstance(event, DelegationEvent):
            self._coros[coro] = _DelegatedEvent(event.spawned)  # Suspend.
            self._coros[event.spawned] = ValueEvent(None)  # Spawn.
            self._history[event.spawned] = None  # Record in history.
            self._delegators[event.spawned] = coro
            return True

        elif isinstance(event, ReturnEvent):
            # Coro is done.
            self._complete_coro(coro, event.value)
            return True

        elif isinstance(event, JoinEvent):
            if event.child not in self._coros and event.child in self._history:
                self._coros[coro] = ValueEvent(None)
            else:
                self._coros[coro] = _SUSPENDED  # Suspend.
                self._joiners[event.child].append(coro)
            return True

        elif isinstance(event, KillEvent):
            self._coros[coro] = ValueEvent(None)
            self._kill_coro(event.child)
            return True

        elif isinstance(event, (_DelegatedEvent, _SuspendedEvent)):
            return False

        else:
            raise TypeError(event)

    def _step(self) -> ta.Optional[CoroException]:
        try:
            # Look for events that can be run immediately. Continue running immediate events until nothing is ready.
            while True:
                have_ready = False
                for coro, event in list(self._coros.items()):
                    if isinstance(event, CoreEvent) and not isinstance(event, SleepEvent):
                        have_ready = self._handle_core_event(coro, event)
                    elif isinstance(event, WaitableEvent):
                        pass
                    else:
                        raise TypeError(event)

                # Only start the select when nothing else is ready.
                if not have_ready:
                    break

            # Wait and fire.
            event2coro = {v: k for k, v in self._coros.items()}
            for event in _event_select(self._coros.values()):
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
                    self._coros[event2coro[event]] = ReturnEvent(None)
                else:
                    self._advance_coro(event2coro[event], value)

        except CoroException as te:
            # Exception raised from inside a coro.
            event = ExceptionEvent(te.exc_info)
            if te.coro in self._delegators:
                # The coro is a delegate. Raise exception in its delegator.
                self._coros[self._delegators[te.coro]] = event
                del self._delegators[te.coro]
            else:
                # The coro is root-level. Raise in client code.
                return te

        except:  # noqa
            # For instance, KeyboardInterrupt during select(). Raise into root coro and terminate others.
            self._coros = {self._root_coro: ExceptionEvent(_exc_info())}

        return None

    def run(self) -> None:
        # Continue advancing coros until root coro exits.
        exit_ce: CoroException | None = None
        while self._coros:
            exit_ce = self._step()

        self.close()

        # If we're exiting with an exception, raise it in the client.
        if exit_ce:
            exit_ce.reraise()


def run(root_coro: Coro) -> None:
    _Runner(root_coro).run()
