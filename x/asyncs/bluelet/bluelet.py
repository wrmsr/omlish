# THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
# WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
# COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
# OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
# https://github.com/sampsyo/bluelet
"""
Extremely simple pure-Python implementation of coroutine-style asynchronous socket I/O. Inspired by, but inferior to,
Eventlet. Bluelet can also be thought of as a less-terrible replacement for asyncore.

Bluelet: easy concurrency without all the messy parallelism.
"""
import abc
import collections
import dataclasses as dc
import errno
import select
import socket
import sys
import time
import traceback
import types
import typing as ta
import weakref


ExcInfo: ta.TypeAlias = tuple[type[BaseException], BaseException, types.TracebackType]

Coro: ta.TypeAlias = ta.Generator['Event', ta.Any, None]


class HasFileno(ta.Protocol):
    def fileno(self) -> int: ...


Waitable: ta.TypeAlias = int | HasFileno
Waitables: ta.TypeAlias = tuple[
    ta.Sequence[Waitable],
    ta.Sequence[Waitable],
    ta.Sequence[Waitable],
]


##


class Event(abc.ABC):  # noqa
    """
    Just a base class identifying Bluelet events. An event is an object yielded from a Bluelet thread coroutine to
    suspend operation and communicate with the scheduler.
    """


class WaitableEvent(Event):
    """
    A waitable event is one encapsulating an action that can be waited for using a select() call. That is, it's an event
    with an associated file descriptor.
    """

    def waitables(self) -> Waitables:
        """
        Return "waitable" objects to pass to select(). Should return three iterables for input readiness, output
        readiness, and exceptional conditions (i.e., the three lists passed to select()).
        """
        return (), (), ()

    def fire(self) -> ta.Any:
        """Called when an associated file descriptor becomes ready (i.e., is returned from a select() call)."""


@dc.dataclass(frozen=True)
class ValueEvent(Event):
    """An event that does nothing but return a fixed value."""

    value: ta.Any


@dc.dataclass(frozen=True)
class ExceptionEvent(Event):
    """Raise an exception at the yield point. Used internally."""

    exc_info: ExcInfo


@dc.dataclass(frozen=True)
class SpawnEvent(Event):
    """Add a new coroutine thread to the scheduler."""

    spawned: Coro


@dc.dataclass(frozen=True)
class JoinEvent(Event):
    """Suspend the thread until the specified child thread has completed."""

    child: Coro


@dc.dataclass(frozen=True)
class KillEvent(Event):
    """Unschedule a child thread."""

    child: Coro


@dc.dataclass(frozen=True)
class DelegationEvent(Event):
    """
    Suspend execution of the current thread, start a new thread and, once the child thread finished, return control to
    the parent thread.
    """

    spawned: Coro


@dc.dataclass(frozen=True)
class ReturnEvent(Event):
    """Return a value the current thread's delegator at the point of delegation. Ends the current (delegate) thread."""

    value: ta.Any


class SleepEvent(WaitableEvent):
    """Suspend the thread for a given duration."""

    def __init__(self, duration: float) -> None:
        super().__init__()
        self.wakeup_time = time.time() + duration

    def time_left(self) -> float:
        return max(self.wakeup_time - time.time(), 0.0)


class ReadEvent(WaitableEvent):
    """Reads from a file-like object."""

    def __init__(self, fd: ta.IO, bufsize: int) -> None:
        super().__init__()
        self.fd = fd
        self.bufsize = bufsize

    def waitables(self) -> Waitables:
        return (self.fd,), (), ()

    def fire(self):
        return self.fd.read(self.bufsize)


class WriteEvent(WaitableEvent):
    """Writes to a file-like object."""

    def __init__(self, fd: ta.IO, data) -> None:
        super().__init__()
        self.fd = fd
        self.data = data

    def waitable(self):
        return (), (self.fd,), ()

    def fire(self) -> None:
        self.fd.write(self.data)


# Core logic for executing and scheduling threads.


def _event_select(events):
    """
    Perform a select() over all the Events provided, returning the ones ready to be fired. Only WaitableEvents
    (including SleepEvents) matter here; all other events are ignored (and thus postponed).
    """

    # Gather waitables and wakeup times.
    waitable_to_event: dict[tuple[str, Waitable], Event] = {}
    rlist: list[Waitable] = []
    wlist: list[Waitable] = []
    xlist: list[Waitable] = []
    earliest_wakeup = None
    for event in events:
        if isinstance(event, SleepEvent):
            if not earliest_wakeup:
                earliest_wakeup = event.wakeup_time
            else:
                earliest_wakeup = min(earliest_wakeup, event.wakeup_time)

        elif isinstance(event, WaitableEvent):
            r, w, x = event.waitables()
            rlist.extend(r)
            wlist.extend(w)
            xlist.extend(x)
            for waitable in r:
                waitable_to_event[('r', waitable)] = event
            for waitable in w:
                waitable_to_event[('w', waitable)] = event
            for waitable in x:
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
        rready, wready, xready = (), (), ()
        if timeout:
            time.sleep(timeout)

    # Gather ready events corresponding to the ready waitables.
    ready_events = set()
    for ready in rready:
        ready_events.add(waitable_to_event[('r', ready)])
    for ready in wready:
        ready_events.add(waitable_to_event[('w', ready)])
    for ready in xready:
        ready_events.add(waitable_to_event[('x', ready)])

    # Gather any finished sleeps.
    for event in events:
        if isinstance(event, SleepEvent) and event.time_left() == 0.0:
            ready_events.add(event)

    return ready_events


def _reraise(typ: type[BaseException], exc: BaseException, tb: types.TracebackType) -> ta.NoReturn:
    raise exc.with_traceback(tb)


class ThreadException(Exception):
    def __init__(self, coro: Coro, exc_info: ExcInfo) -> None:
        super().__init__()
        self.coro = coro
        self.exc_info = exc_info

    def reraise(self):
        _reraise(self.exc_info[0], self.exc_info[1], self.exc_info[2])


SUSPENDED = Event()  # Special sentinel placeholder for suspended threads.


class Delegated(Event):
    """Placeholder indicating that a thread has delegated execution to a different thread."""

    def __init__(self, child) -> None:
        super().__init__()
        self.child = child


def run(root_coro: Coro) -> None:
    """
    Schedules a coroutine, running it to completion. This encapsulates the Bluelet scheduler, which the root coroutine
    can add to by spawning new coroutines.
    """

    # The "threads" dictionary keeps track of all the currently- executing and suspended coroutines. It maps coroutines
    # to their currently "blocking" event. The event value may be SUSPENDED if the coroutine is waiting on some other
    # condition: namely, a delegated coroutine or a joined coroutine. In this case, the coroutine should *also* appear
    # as a value in one of the below dictionaries `delegators` or `joiners`.
    threads = {root_coro: ValueEvent(None)}

    # Maps child coroutines to delegating parents.
    delegators = {}

    # Maps child coroutines to joining (exit-waiting) parents.
    joiners: ta.MutableMapping[Coro, list[Coro]] = collections.defaultdict(list)

    # History of spawned coroutines for joining of already completed
    # coroutines.
    history = weakref.WeakKeyDictionary({root_coro: None})

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

        except:
            # Thread raised some other exception.
            del threads[coro]
            raise ThreadException(coro, sys.exc_info())

        else:
            if isinstance(next_event, types.GeneratorType):
                # Automatically invoke sub-coroutines. (Shorthand for explicit bluelet.call().)
                next_event = DelegationEvent(next_event)
            threads[coro] = next_event

    def kill_thread(coro):
        """Unschedule this thread and its (recursive) delegates."""

        # Collect all coroutines in the delegation stack.
        coros = [coro]
        while isinstance(threads[coro], Delegated):
            coro = threads[coro].child
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
                        threads[coro] = Delegated(event.spawned)  # Suspend.
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
                            threads[coro] = SUSPENDED  # Suspend.
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
            event2coro = dict((v, k) for k, v in threads.items())
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

        except:
            # For instance, KeyboardInterrupt during select(). Raise into root thread and terminate others.
            threads = {root_coro: ExceptionEvent(sys.exc_info())}

    # If any threads still remain, kill them.
    for coro in threads:
        coro.close()

    # If we're exiting with an exception, raise it in the client.
    if exit_te:
        exit_te.reraise()


# Sockets and their associated events.

class SocketClosedError(Exception):
    pass


class Listener:
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

    def accept(self) -> Event:
        """
        An event that waits for a connection on the listening socket. When a connection is made, the event returns a
        Connection object.
        """

        if self._closed:
            raise SocketClosedError
        return AcceptEvent(self)

    def close(self) -> None:
        """Immediately close the listening socket. (Not an event.)"""

        self._closed = True
        self.sock.close()


class Connection:
    """A socket wrapper object for connected sockets."""

    def __init__(self, sock: socket.socket, addr: tuple[str, int]) -> None:
        super().__init__()
        self.sock = sock
        self.addr = addr
        self._buf: bytes = b''
        self._closed: bool = False

    def close(self) -> None:
        """Close the connection."""

        self._closed = True
        self.sock.close()

    def recv(self, size: int) -> Event:
        """Read at most size bytes of data from the socket."""

        if self._closed:
            raise SocketClosedError

        if self._buf:
            # We already have data read previously.
            out = self._buf[:size]
            self._buf = self._buf[size:]
            return ValueEvent(out)
        else:
            return ReceiveEvent(self, size)

    def send(self, data: bytes) -> Event:
        """Sends data on the socket, returning the number of bytes successfully sent."""

        if self._closed:
            raise SocketClosedError
        return SendEvent(self, data)

    def sendall(self, data: bytes) -> Event:
        """Send all of data on the socket."""

        if self._closed:
            raise SocketClosedError
        return SendEvent(self, data, True)

    def readline(self, terminator: bytes = b'\n', bufsize: int = 1024) -> ta.Iterator[Event]:
        """Reads a line (delimited by terminator) from the socket."""

        if self._closed:
            raise SocketClosedError

        while True:
            if terminator in self._buf:
                line, self._buf = self._buf.split(terminator, 1)
                line += terminator
                yield ReturnEvent(line)
                break
            data = yield ReceiveEvent(self, bufsize)
            if data:
                self._buf += data
            else:
                line = self._buf
                self._buf = b''
                yield ReturnEvent(line)
                break


class AcceptEvent(WaitableEvent):
    """An event for Listener objects (listening sockets) that suspends execution until the socket gets a connection."""

    def __init__(self, listener: Listener) -> None:
        super().__init__()
        self.listener = listener

    def waitables(self) -> Waitables:
        return (self.listener.sock,), (), ()

    def fire(self) -> Connection:
        sock, addr = self.listener.sock.accept()
        return Connection(sock, addr)


class ReceiveEvent(WaitableEvent):
    """An event for Connection objects (connected sockets) for asynchronously reading data."""

    def __init__(self, conn: Connection, bufsize: int) -> None:
        super().__init__()
        self.conn = conn
        self.bufsize = bufsize

    def waitables(self) -> Waitables:
        return (self.conn.sock,), (), ()

    def fire(self) -> bytes:
        return self.conn.sock.recv(self.bufsize)


class SendEvent(WaitableEvent):
    """An event for Connection objects (connected sockets) for asynchronously writing data."""

    def __init__(self, conn: Connection, data: bytes, sendall: bool = False) -> None:
        super().__init__()
        self.conn = conn
        self.data = data
        self.sendall = sendall

    def waitables(self) -> Waitables:
        return (), (self.conn.sock,), ()

    def fire(self) -> int | None:
        if self.sendall:
            return self.conn.sock.sendall(self.data)
        else:
            return self.conn.sock.send(self.data)


# Public interface for threads; each returns an event object that can immediately be "yield"ed.

def null() -> Event:
    """Event: yield to the scheduler without doing anything special."""

    return ValueEvent(None)


def spawn(coro) -> Event:
    """Event: add another coroutine to the scheduler. Both the parent and child coroutines run concurrently."""

    if not isinstance(coro, types.GeneratorType):
        raise ValueError('%s is not a coroutine' % str(coro))
    return SpawnEvent(coro)


def call(coro) -> Event:
    """
    Event: delegate to another coroutine. The current coroutine is resumed once the sub-coroutine finishes. If the
    sub-coroutine returns a value using end(), then this event returns that value.
    """

    if not isinstance(coro, types.GeneratorType):
        raise ValueError('%s is not a coroutine' % str(coro))
    return DelegationEvent(coro)


def end(value=None) -> Event:
    """Event: ends the coroutine and returns a value to its delegator."""

    return ReturnEvent(value)


def read(fd: ta.IO, bufsize: int | None = None) -> Event:
    """Event: read from a file descriptor asynchronously."""

    if bufsize is None:
        # Read all.
        def reader():
            buf = []
            while True:
                data = yield read(fd, 1024)
                if not data:
                    break
                buf.append(data)
            yield ReturnEvent(''.join(buf))

        return DelegationEvent(reader())

    else:
        return ReadEvent(fd, bufsize)


def write(fd: ta.IO, data: bytes) -> Event:
    """Event: write to a file descriptor asynchronously."""

    return WriteEvent(fd, data)


def connect(host: str, port: int) -> Event:
    """Event: connect to a network address and return a Connection object for communicating on the socket."""

    addr = (host, port)
    sock = socket.create_connection(addr)
    return ValueEvent(Connection(sock, addr))


def sleep(duration: float) -> Event:
    """Event: suspend the thread for ``duration`` seconds."""

    return SleepEvent(duration)


def join(coro) -> Event:
    """Suspend the thread until another, previously `spawn`ed thread completes."""

    return JoinEvent(coro)


def kill(coro) -> Event:
    """Halt the execution of a different `spawn`ed thread."""

    return KillEvent(coro)


# Convenience function for running socket servers.


def server(host: str, port: int, func) -> ta.Iterator[Event]:
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

    listener = Listener(host, port)
    try:
        while True:
            conn = yield listener.accept()
            yield spawn(handler(conn))
    except KeyboardInterrupt:
        pass
    finally:
        listener.close()
