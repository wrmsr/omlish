# noinspection DuplicatedCode
# @omdev-amalg-output httpd_amalg.py
"""A simple Web server built with Bluelet to support concurrent requests in a single OS thread."""
import abc
import collections
import dataclasses as dc
import errno
import logging
import mimetypes
import os
import select
import socket
import sys
import time
import traceback
import types
import typing as ta
import weakref


BlueletWaitable = ta.Union[int, 'BlueletHasFileno']  # ta.TypeAlias
T = ta.TypeVar('T')
BlueletExcInfo = ta.Tuple[ta.Type[BaseException], BaseException, types.TracebackType]  # ta.TypeAlias
BlueletCoro = ta.Generator[ta.Union['BlueletEvent', 'BlueletCoro'], ta.Any, None]  # ta.TypeAlias


########################################
# ../../../../../omlish/lite/logs.py
"""
TODO:
 - debug
"""
# ruff: noqa: UP007


log = logging.getLogger(__name__)


def configure_standard_logging(level: ta.Union[int, str] = logging.INFO) -> None:
    logging.root.addHandler(logging.StreamHandler())
    logging.root.setLevel(level)


########################################
# ../../bluelet/events.py
# Based on bluelet ( https://github.com/sampsyo/bluelet ) by Adrian Sampson, original license:
# THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
# WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
# COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
# OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
# ruff: noqa: UP007


##


class BlueletEvent(abc.ABC):  # noqa
    """
    Just a base class identifying Bluelet events. An event is an object yielded from a Bluelet coro coroutine to
    suspend operation and communicate with the scheduler.
    """


##


class BlueletHasFileno(ta.Protocol):
    def fileno(self) -> int: ...




@dc.dataclass(frozen=True)
class BlueletWaitables:
    r: ta.Sequence[BlueletWaitable] = ()
    w: ta.Sequence[BlueletWaitable] = ()
    x: ta.Sequence[BlueletWaitable] = ()


class WaitableBlueletEvent(BlueletEvent, abc.ABC):  # noqa
    """
    A waitable event is one encapsulating an action that can be waited for using a select() call. That is, it's an event
    with an associated file descriptor.
    """

    def waitables(self) -> BlueletWaitables:
        """
        Return "waitable" objects to pass to select(). Should return three iterables for input readiness, output
        readiness, and exceptional conditions (i.e., the three lists passed to select()).
        """
        return BlueletWaitables()

    def fire(self) -> ta.Any:
        """Called when an associated file descriptor becomes ready (i.e., is returned from a select() call)."""


########################################
# ../../bluelet/core.py
# Based on bluelet ( https://github.com/sampsyo/bluelet ) by Adrian Sampson, original license:
# THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
# WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
# COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
# OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
# ruff: noqa: UP006 UP007


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


########################################
# ../../bluelet/runner.py
"""
TODO:
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
 - https://github.com/python/cpython/issues/120804 - GH-120804: Remove get_child_watcher and set_child_watcher from asyncio 
 - https://github.com/python/cpython/pull/17063/files bpo-38692: Add os.pidfd_open
 - clone PidfdChildWatcher + ThreadedChildWatcher
"""  # noqa
# Based on bluelet ( https://github.com/sampsyo/bluelet ) by Adrian Sampson, original license:
# THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
# WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
# COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
# OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
# ruff: noqa: UP006 UP007


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


def _bluelet_event_select(events: ta.Iterable[BlueletEvent]) -> ta.Set[WaitableBlueletEvent]:
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
        log.debug('_bluelet_event_select: +select: %r %r %r %r', rlist, wlist, xlist, timeout)
        rready, wready, xready = select.select(rlist, wlist, xlist, timeout)
        log.debug('_bluelet_event_select: -select: %r %r %r', rready, wready, xready)

    else:
        rready, wready, xready = [], [], []
        if timeout:
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

    def __init__(self, root_coro: BlueletCoro) -> None:
        super().__init__()

        self._root_coro = root_coro

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
        self._history: ta.MutableMapping[BlueletCoro, ta.Optional[BlueletEvent]] = weakref.WeakKeyDictionary({self._root_coro: None})  # noqa

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
            raise BlueletCoroException(coro, BlueletCoroException._exc_info())  # noqa

        else:
            if isinstance(next_event, ta.Generator):
                # Automatically invoke sub-coroutines. (Shorthand for explicit bluelet.call().)
                next_event = DelegationBlueletEvent(next_event)
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
        log.debug(f'{__class__.__name__}._handle_core_event: %r %r', coro, event)

        if isinstance(event, SpawnBlueletEvent):
            self._coros[event.spawned] = ValueBlueletEvent(None)  # Spawn.
            self._history[event.spawned] = None  # Record in history.
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
        log.debug(f'{__class__.__name__}._step')

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
                        raise TypeError(f'Unknown event type: {event}')

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
            # Exception raised from inside a coro.
            event = ExceptionBlueletEvent(te.exc_info)
            if te.coro in self._delegators:
                # The coro is a delegate. Raise exception in its delegator.
                self._coros[self._delegators[te.coro]] = event
                del self._delegators[te.coro]
            else:
                # The coro is root-level. Raise in client code.
                return te

        except:  # noqa
            # For instance, KeyboardInterrupt during select(). Raise into root coro and terminate others.
            self._coros = {self._root_coro: ExceptionBlueletEvent(BlueletCoroException._exc_info())}  # noqa

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


def bluelet_run(root_coro: BlueletCoro) -> None:
    _BlueletRunner(root_coro).run()


########################################
# ../../bluelet/sockets.py
# Based on bluelet ( https://github.com/sampsyo/bluelet ) by Adrian Sampson, original license:
# THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
# WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
# COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
# OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
# ruff: noqa: UP006 UP007


##


class SocketClosedBlueletError(Exception):
    pass


class BlueletListener:
    """A socket wrapper object for listening sockets."""

    def __init__(self, host: str, port: int) -> None:
        """Create a listening socket on the given hostname and port."""

        super().__init__()
        self._closed = False
        self.host = host
        self.port = port

        self.sock = sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((host, port))
        sock.listen(5)

    def accept(self) -> 'AcceptBlueletEvent':
        """
        An event that waits for a connection on the listening socket. When a connection is made, the event returns a
        Connection object.
        """

        if self._closed:
            raise SocketClosedBlueletError
        return AcceptBlueletEvent(self)

    def close(self) -> None:
        """Immediately close the listening socket. (Not an event.)"""

        self._closed = True
        self.sock.close()


class BlueletConnection:
    """A socket wrapper object for connected sockets."""

    def __init__(self, sock: socket.socket, addr: ta.Tuple[str, int]) -> None:
        super().__init__()
        self.sock = sock
        self.addr = addr
        self._buf = bytearray()
        self._closed: bool = False

    def close(self) -> None:
        """Close the connection."""

        self._closed = True
        self.sock.close()

    def recv(self, size: int) -> BlueletEvent:
        """Read at most size bytes of data from the socket."""

        if self._closed:
            raise SocketClosedBlueletError

        if self._buf:
            # We already have data read previously.
            out = self._buf[:size]
            self._buf = self._buf[size:]
            return ValueBlueletEvent(bytes(out))
        else:
            return ReceiveBlueletEvent(self, size)

    def send(self, data: bytes) -> BlueletEvent:
        """Sends data on the socket, returning the number of bytes successfully sent."""

        if self._closed:
            raise SocketClosedBlueletError
        return SendBlueletEvent(self, data)

    def sendall(self, data: bytes) -> BlueletEvent:
        """Send all of data on the socket."""

        if self._closed:
            raise SocketClosedBlueletError
        return SendBlueletEvent(self, data, True)

    def readline(self, terminator: bytes = b'\n', bufsize: int = 1024) -> BlueletCoro:
        """Reads a line (delimited by terminator) from the socket."""

        if self._closed:
            raise SocketClosedBlueletError

        while True:
            if terminator in self._buf:
                line, self._buf = self._buf.split(terminator, 1)
                line += terminator
                yield ReturnBlueletEvent(bytes(line))
                break

            if (data := (yield ReceiveBlueletEvent(self, bufsize))):
                self._buf += data
            else:
                line = self._buf
                self._buf = bytearray()
                yield ReturnBlueletEvent(bytes(line))
                break


##


class SocketBlueletEvent(BlueletEvent, abc.ABC):  # noqa
    pass


#


@dc.dataclass(frozen=True, eq=False)
class AcceptBlueletEvent(WaitableBlueletEvent, SocketBlueletEvent):
    """An event for Listener objects (listening sockets) that suspends execution until the socket gets a connection."""

    listener: BlueletListener

    def waitables(self) -> BlueletWaitables:
        return BlueletWaitables(r=[self.listener.sock])

    def fire(self) -> BlueletConnection:
        sock, addr = self.listener.sock.accept()
        return BlueletConnection(sock, addr)


#


@dc.dataclass(frozen=True, eq=False)
class ReceiveBlueletEvent(WaitableBlueletEvent, SocketBlueletEvent):
    """An event for Connection objects (connected sockets) for asynchronously reading data."""

    conn: BlueletConnection
    bufsize: int

    def waitables(self) -> BlueletWaitables:
        return BlueletWaitables(r=[self.conn.sock])

    def fire(self) -> bytes:
        return self.conn.sock.recv(self.bufsize)


#


@dc.dataclass(frozen=True, eq=False)
class SendBlueletEvent(WaitableBlueletEvent, SocketBlueletEvent):
    """An event for Connection objects (connected sockets) for asynchronously writing data."""

    conn: BlueletConnection
    data: bytes
    sendall: bool = False

    def waitables(self) -> BlueletWaitables:
        return BlueletWaitables(w=[self.conn.sock])

    def fire(self) -> ta.Optional[int]:
        if self.sendall:
            self.conn.sock.sendall(self.data)
            return None
        else:
            return self.conn.sock.send(self.data)


##


def bluelet_connect(host: str, port: int) -> BlueletEvent:
    """Event: connect to a network address and return a Connection object for communicating on the socket."""

    addr = (host, port)
    sock = socket.create_connection(addr)
    return ValueBlueletEvent(BlueletConnection(sock, addr))


def bluelet_server(host: str, port: int, func) -> BlueletCoro:
    """
    A coroutine that runs a network server. Host and port specify the listening address. func should be a coroutine that
    takes a single parameter, a Connection object. The coroutine is invoked for every incoming connection on the
    listening socket.
    """

    def handler(conn):
        try:
            yield func(conn)
        finally:
            conn.close()

    listener = BlueletListener(host, port)
    try:
        while True:
            conn = yield listener.accept()
            yield bluelet_spawn(handler(conn))
    except KeyboardInterrupt:
        pass
    finally:
        listener.close()


########################################
# httpd_amalg.py


ROOT = '.'
INDEX_FILENAME = 'index.html'


@dc.dataclass(frozen=True)
class Request:
    method: bytes
    path: bytes
    headers: ta.Mapping[bytes, bytes]


def parse_request(lines: ta.Sequence[bytes]) -> Request:
    """Parse an HTTP request."""

    method, path, version = lines[0].split(None, 2)
    headers: dict[bytes, bytes] = {}
    for line in lines[1:]:
        if not line:
            continue
        key, value = line.split(b': ', 1)
        headers[key] = value
    return Request(method, path, headers)


def mime_type(filename: str) -> str:
    """Return a reasonable MIME type for the file or text/plain as a fallback."""

    mt, _ = mimetypes.guess_type(filename)
    if mt:
        return mt
    else:
        return 'text/plain'


@dc.dataclass(frozen=True)
class Response:
    status: str
    headers: ta.Mapping[str, str]
    content: bytes


def respond(req: Request) -> Response:
    """Generate an HTTP response for a parsed request."""

    # Remove query string, if any.
    pathb = req.path
    if b'?' in pathb:
        pathb, query = pathb.split(b'?', 1)
    path = pathb.decode('utf8')

    # Strip leading / and add prefix.
    if path.startswith('/') and len(path) > 0:
        filename = path[1:]
    else:
        filename = path
    filename = os.path.join(ROOT, filename)

    # Expand to index file if possible.
    index_fn = os.path.join(filename, INDEX_FILENAME)
    if os.path.isdir(filename) and os.path.exists(index_fn):
        filename = index_fn

    if os.path.isdir(filename):
        # Directory listing.
        pfx = (path[1:] + '/') if len(path) > 1 else ''
        files = []
        for name in sorted(os.listdir(filename), key=lambda n: (not os.path.isdir(n), n)):
            files.append(f'<li><a href="{pfx}{name}">{"/" if os.path.isdir(name) else ""}{name}</a></li>')
        html = f'<html><head><title>{path}</title></head><body><h1>{path}</h1><ul>{"".join(files)}</ul></body></html>'
        return Response(
            '200 OK',
            {'Content-Type': 'text/html'},
            html.encode('utf8'),
        )

    elif os.path.exists(filename):
        # Send file contents.
        with open(filename, 'rb') as f:
            return Response(
                '200 OK',
                {'Content-Type': mime_type(filename)},
                f.read(),
            )

    else:
        # Not found.
        print('Not found.')
        return Response(
            '404 Not Found',
            {'Content-Type': 'text/html'},
            b'<html><head><title>404 Not Found</title></head><body><h1>Not found.</h1></body></html>',
        )


def webrequest(conn: BlueletConnection) -> BlueletCoro:
    """A Bluelet coroutine implementing an HTTP server."""

    # Get the HTTP request.
    req_lines: list[bytes] = []
    while True:
        line = (yield conn.readline(b'\r\n')).strip()
        if not line:
            # End of headers.
            break
        req_lines.append(line)

    # Make sure a request was sent.
    if not req_lines:
        return

    # Parse and log the request and get the response values.
    req = parse_request(req_lines)
    print('%r %r' % (req.method, req.path))
    resp = respond(req)

    # Send response.
    yield conn.sendall(f'HTTP/1.1 {resp.status}\r\n'.encode('utf8'))
    for key, value in resp.headers.items():
        yield conn.sendall(f'{key}: {value}\r\n'.encode('utf8'))
    yield conn.sendall(b'\r\n')
    yield conn.sendall(resp.content)


if __name__ == '__main__':
    def ticker(delay: float = 3.) -> BlueletCoro:
        i = 0
        while True:
            yield bluelet_sleep(delay)
            print(f'tick {i}')
            i += 1

    def _main() -> BlueletCoro:
        yield bluelet_spawn(bluelet_server('', 8000, webrequest))
        yield bluelet_spawn(ticker())

    if len(sys.argv) > 1:
        ROOT = os.path.expanduser(sys.argv[1])

    print('http://127.0.0.1:8000/')
    bluelet_run(_main())
