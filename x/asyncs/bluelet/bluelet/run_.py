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


class ThreadException(Exception):  # noqa
    def __init__(self, coro: Coro, exc_info: ExcInfo) -> None:
        super().__init__()
        self.coro = coro
        self.exc_info = exc_info

    def reraise(self) -> ta.NoReturn:
        _reraise(self.exc_info[0], self.exc_info[1], self.exc_info[2])


##


def _event_select(events: ta.Iterable[Event]) -> set[WaitableEvent]:
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

    # If we have a any sleeping threads, determine how long to sleep.
    if earliest_wakeup:
        timeout = max(earliest_wakeup - time.time(), 0.0)
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
    ready_events: set[WaitableEvent] = set()
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


_SUSPENDED = _SuspendedEvent()  # Special sentinel placeholder for suspended threads.


@dc.dataclass(frozen=True, eq=False)
class _DelegatedEvent(CoreEvent):
    """Placeholder indicating that a thread has delegated execution to a different thread."""

    child: Coro


def run(root_coro: Coro) -> None:
    """
    Schedules a coroutine, running it to completion. This encapsulates the Bluelet scheduler, which the root coroutine
    can add to by spawning new coroutines.
    """

    # The "threads" dictionary keeps track of all the currently-executing and suspended coroutines. It maps coroutines
    # to their currently "blocking" event. The event value may be SUSPENDED if the coroutine is waiting on some other
    # condition: namely, a delegated coroutine or a joined coroutine. In this case, the coroutine should *also* appear
    # as a value in one of the below dictionaries `delegators` or `joiners`.
    threads: ta.Dict[Coro, Event] = {root_coro: ValueEvent(None)}

    # Maps child coroutines to delegating parents.
    delegators: ta.Dict[Coro, Coro] = {}

    # Maps child coroutines to joining (exit-waiting) parents.
    joiners: ta.MutableMapping[Coro, ta.List[Coro]] = collections.defaultdict(list)

    # History of spawned coroutines for joining of already completed coroutines.
    history: ta.MutableMapping[Coro, ta.Optional[Event]] = weakref.WeakKeyDictionary({root_coro: None})

    def complete_thread(coro: Coro, return_value: ta.Any) -> None:
        """
        Remove a coroutine from the scheduling pool, awaking delegators and joiners as necessary and returning the
        specified value to any delegating parent.
        """

        del threads[coro]

        # Resume delegator.
        if coro in delegators:
            threads[delegators[coro]] = ValueEvent(return_value)
            del delegators[coro]

        # Resume joiners.
        if coro in joiners:
            for parent in joiners[coro]:
                threads[parent] = ValueEvent(None)
            del joiners[coro]

    def advance_thread(coro: Coro, value, is_exc=False) -> None:
        """
        After an event is fired, run a given coroutine associated with it in the threads dict until it yields again. If
        the coroutine exits, then the thread is removed from the pool. If the coroutine raises an exception, it is
        reraised in a ThreadException. If is_exc is True, then the value must be an exc_info tuple and the exception is
        thrown into the coroutine.
        """

        try:
            if is_exc:
                next_event = coro.throw(*value)
            else:
                next_event = coro.send(value)

        except StopIteration:
            # Thread is done.
            complete_thread(coro, None)

        except:  # noqa
            # Thread raised some other exception.
            del threads[coro]
            # Note: Don't use `raise from` as this should support 3.8.
            raise ThreadException(coro, _exc_info())  # noqa

        else:
            if isinstance(next_event, ta.Generator):
                # Automatically invoke sub-coroutines. (Shorthand for explicit bluelet.call().)
                next_event = DelegationEvent(next_event)
            threads[coro] = next_event

    def kill_thread(coro):
        """Unschedule this thread and its (recursive) delegates."""

        # Collect all coroutines in the delegation stack.
        coros = [coro]
        while isinstance((cur := threads[coro]), _DelegatedEvent):
            coro = cur.child  # noqa
            coros.append(coro)

        # Complete each coroutine from the top to the bottom of the stack.
        for coro in reversed(coros):
            complete_thread(coro, None)

    # Continue advancing threads until root thread exits.
    exit_te = None
    while threads:
        try:
            # Look for events that can be run immediately. Continue running immediate events until nothing is ready.
            while True:
                have_ready = False
                for coro, event in list(threads.items()):
                    if isinstance(event, SpawnEvent):
                        threads[event.spawned] = ValueEvent(None)  # Spawn.
                        history[event.spawned] = None  # Record in history.
                        advance_thread(coro, None)
                        have_ready = True

                    elif isinstance(event, ValueEvent):
                        advance_thread(coro, event.value)
                        have_ready = True

                    elif isinstance(event, ExceptionEvent):
                        advance_thread(coro, event.exc_info, True)
                        have_ready = True

                    elif isinstance(event, DelegationEvent):
                        threads[coro] = _DelegatedEvent(event.spawned)  # Suspend.
                        threads[event.spawned] = ValueEvent(None)  # Spawn.
                        history[event.spawned] = None  # Record in history.
                        delegators[event.spawned] = coro
                        have_ready = True

                    elif isinstance(event, ReturnEvent):
                        # Thread is done.
                        complete_thread(coro, event.value)
                        have_ready = True

                    elif isinstance(event, JoinEvent):
                        if event.child not in threads and event.child in history:
                            threads[coro] = ValueEvent(None)
                        else:
                            threads[coro] = _SUSPENDED  # Suspend.
                            joiners[event.child].append(coro)
                        have_ready = True

                    elif isinstance(event, KillEvent):
                        threads[coro] = ValueEvent(None)
                        kill_thread(event.child)
                        have_ready = True

                # Only start the select when nothing else is ready.
                if not have_ready:
                    break

            # Wait and fire.
            event2coro = {v: k for k, v in threads.items()}
            for event in _event_select(threads.values()):
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
                    threads[event2coro[event]] = ReturnEvent(None)
                else:
                    advance_thread(event2coro[event], value)

        except ThreadException as te:
            # Exception raised from inside a thread.
            event = ExceptionEvent(te.exc_info)
            if te.coro in delegators:
                # The thread is a delegate. Raise exception in its delegator.
                threads[delegators[te.coro]] = event
                del delegators[te.coro]
            else:
                # The thread is root-level. Raise in client code.
                exit_te = te
                break

        except:  # noqa
            # For instance, KeyboardInterrupt during select(). Raise into root thread and terminate others.
            threads = {root_coro: ExceptionEvent(_exc_info())}

    # If any threads still remain, kill them.
    for coro in threads:
        coro.close()

    # If we're exiting with an exception, raise it in the client.
    if exit_te:
        exit_te.reraise()
