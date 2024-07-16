import abc
import binascii
import collections
import errno
import fcntl
import heapq
import logging
import os
import select
import socket
import struct
import sys
import threading
import time
import typing as ta


log = logging.getLogger(__name__)


T = ta.TypeVar('T')


##


def _check(cond: bool, msg: str) -> None:
    if not cond:
        raise Exception(msg)


def _check_eq(l: T, r: T, msg: ta.Optional[str] = None) -> T:
    if l != r:
        raise Exception(msg or f'must be equal: {l}, {r}')
    return l


def _check_not_none(o: ta.Optional[T], msg: ta.Optional[str] = None) -> T:
    if o is None:
        raise Exception(msg or 'must not be none')
    return o


##


def _callbacks(obj: ta.Any, name: str) -> ta.List[ta.Callable]:
    return obj.__dict__.setdefault('_callbacks', {}).setdefault(name, [])


def callback_add(obj: ta.Any, name: str, fn) -> None:
    _callbacks(obj, name).append(fn)


def callback_remove(obj: ta.Any, name: str, fn: ta.Callable) -> None:
    _callbacks(obj, name).remove(fn)


def callback(obj: ta.Any, name: str, *args: ta.Any, **kwargs: ta.Any) -> None:
    for fn in _callbacks(obj, name):
        fn(*args, **kwargs)


##


def set_cloexec(fd: int) -> None:
    flags = fcntl.fcntl(fd, fcntl.F_GETFD)
    _check(fd > 2, f'fd {fd!r} <= 2')
    fcntl.fcntl(fd, fcntl.F_SETFD, flags | fcntl.FD_CLOEXEC)


def set_nonblock(fd: int) -> None:
    flags = fcntl.fcntl(fd, fcntl.F_GETFL)
    fcntl.fcntl(fd, fcntl.F_SETFL, flags | os.O_NONBLOCK)


def set_block(fd: int) -> None:
    flags = fcntl.fcntl(fd, fcntl.F_GETFL)
    fcntl.fcntl(fd, fcntl.F_SETFL, flags & ~os.O_NONBLOCK)


def pipe() -> ta.Tuple[ta.BinaryIO, ta.BinaryIO]:
    rfd, wfd = os.pipe()
    return (
        os.fdopen(rfd, 'rb', 0),
        os.fdopen(wfd, 'wb', 0)
    )


def io_op(fn, *args):
    while True:
        try:
            return fn(*args), None
        except (select.error, OSError, IOError):
            e = sys.exc_info()[1]
            log.debug('io_op(%r) -> OSError: %s', fn, e)
            if e.args[0] == errno.EINTR:
                continue
            if e.args[0] in (errno.EIO, errno.ECONNRESET, errno.EPIPE):
                return None, e
            raise


##


IoObj = ta.Union[ta.BinaryIO, socket.socket]


CHUNK_SIZE = 131072


class Side:

    def __init__(
            self,
            stream: 'Stream',
            fp: IoObj,
            *,
            cloexec: bool = True,
            keep_alive: bool = True,
            blocking: bool = False,
    ) -> None:
        super().__init__()

        self._stream = stream
        self._fp = fp
        self._keep_alive = keep_alive

        self._fd = fp.fileno()
        self._closed = False

        if cloexec:
            set_cloexec(self._fd)
        if not blocking:
            set_nonblock(self._fd)

    @property
    def stream(self) -> 'Stream':
        return self._stream

    @property
    def fd(self) -> int:
        return self._fd

    @property
    def closed(self) -> bool:
        return self._closed

    def __repr__(self) -> str:
        return f'<Side of {self._stream.name or repr(self._stream)} fd {self._fd}>'

    def close(self) -> None:
        log.debug('%r.close()', self)
        if not self._closed:
            self._closed = True
            self._fp.close()

    def read(self, n: int = CHUNK_SIZE) -> bytes:
        if self._closed:
            return b''

        c, dc = io_op(os.read, self._fd, n)
        if dc:
            log.debug('%r: disconnected during read: %s', self, dc)
            return b''

        return c

    def write(self, s: bytes) -> ta.Optional[int]:
        if self._closed:
            return None

        c, dc = io_op(os.write, self._fd, s)
        if dc:
            log.debug('%r: disconnected during write: %s', self, dc)
            return None

        return c


class Stream:

    def __init__(
            self,
            protocol: 'Protocol',
            rfp: IoObj,
            wfp: IoObj,
            name: str = 'default',
    ) -> None:
        super().__init__()

        self._protocol = protocol
        self._rs = Side(self, rfp)
        self._ws = Side(self, wfp)
        self._name = name

    @property
    def protocol(self) -> 'Protocol':
        return self._protocol

    @property
    def rs(self) -> Side:
        return self._rs

    @property
    def ws(self) -> Side:
        return self._ws

    @property
    def name(self) -> str:
        return self._name

    def __repr__(self) -> str:
        return f'<Stream {self._name} {id(self) & 0xffff:04x}>'

    def set_protocol(self, protocol: 'Protocol') -> None:
        _check_eq(self._protocol._stream, self)  # noqa
        self._protocol._stream = None
        self._protocol = protocol
        self._protocol._stream = self  # noqa

    ##

    def on_receive(self, broker):
        buf = self._rs.read(self._protocol.read_size)
        if not buf:
            log.debug('%r: empty read, disconnecting', self._rs)
            return self.on_disconnect(broker)

        self._protocol.on_receive(broker, buf)

    def on_transmit(self, broker):
        self._protocol.on_transmit(broker)

    def on_shutdown(self, broker):
        callback(self, 'shutdown')
        self._protocol.on_shutdown(broker)

    def on_disconnect(self, broker):
        callback(self, 'disconnect')
        self._protocol.on_disconnect(broker)


##


class Protocol(abc.ABC):
    read_size = CHUNK_SIZE

    def __init__(self) -> None:
        super().__init__()

        self._stream: ta.Optional[Stream] = None

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({self._stream!r})'

    ##

    @abc.abstractmethod
    def on_receive(self, broker, buf):
        raise NotImplementedError

    @abc.abstractmethod
    def on_transmit(self, broker):
        raise NotImplementedError

    def on_shutdown(self, broker):
        log.debug('%r: shutting down', self)
        self._stream.on_disconnect(broker)

    def on_disconnect(self, broker):
        log.debug('%r: disconnecting', self)
        broker.stop_receive(self._stream)
        if self._stream.ws:
            broker._stop_transmit(self._stream)
        self._stream.rs.close()
        if self._stream.ws:
            self._stream.ws.close()


##


class SocketPair(ta.Tuple):
    rsock: socket.socket
    wsock: socket.socket


class LatchError(Exception):
    pass


class Latch:

    _idle_socketpairs: ta.ClassVar[ta.List[SocketPair]] = []

    def __init__(
            self,
            *,
            notify: ta.Optional[ta.Callable[['Latch'], None]] = None,
    ) -> None:
        super().__init__()
        self._notify = notify

        self._closed = False
        self._lock = threading.Lock()
        self._queue: ta.List[ta.Any] = []
        self._sleeping: ta.List[ta.Tuple[socket.socket, bytes]] = []
        self._waking = 0

    def __repr__(self) -> str:
        return 'Latch(%#x, size=%d, t=%r)' % (id(self), len(self._queue), threading.current_thread().name)

    def close(self) -> None:
        self._lock.acquire()
        try:
            self._closed = True
            while self._waking < len(self._sleeping):
                wsock, cookie = self._sleeping[self._waking]
                self._wake(wsock, cookie)
                self._waking += 1
        finally:
            self._lock.release()

    def size(self) -> int:
        self._lock.acquire()
        try:
            if self._closed:
                raise LatchError
            return len(self._queue)
        finally:
            self._lock.release()

    def _get_socketpair(self) -> SocketPair:
        try:
            return Latch._idle_socketpairs.pop()
        except IndexError:
            rsock, wsock = socket.socketpair()
            rsock.setblocking(False)
            set_cloexec(rsock.fileno())
            set_cloexec(wsock.fileno())
            return SocketPair(rsock, wsock)

    COOKIE_MAGIC, = struct.unpack('L', b'LTCH' * (struct.calcsize('L')//4))
    COOKIE_FMT = '>Qqqq'
    COOKIE_SIZE = struct.calcsize(COOKIE_FMT)

    def _make_cookie(self) -> bytes:
        return struct.pack(
            self.COOKIE_FMT,
            self.COOKIE_MAGIC,
            os.getpid(),
            id(self),
            threading.get_ident(),
        )

    def get(self, timeout: ta.Optional[float] = None, block: bool = True) -> ta.Any:
        log.debug('%r.get(timeout=%r, block=%r)', self, timeout, block)
        self._lock.acquire()
        try:
            if self._closed:
                raise LatchError
            i = len(self._sleeping)
            if len(self._queue) > i:
                log.debug('%r.get() -> %r', self, self._queue[i])
                return self._queue.pop(i)
            if not block:
                raise TimeoutError
            rsock, wsock = self._get_socketpair()
            cookie = self._make_cookie()
            self._sleeping.append((wsock, cookie))
        finally:
            self._lock.release()

        poller = Poller()
        poller.start_receive(rsock.fileno())
        try:
            return self._get_sleep(
                poller,
                timeout,
                block,
                rsock,
                wsock,
                cookie,
            )
        finally:
            poller.close()

    def _get_sleep(
            self,
            poller: 'Poller',
            timeout: ta.Optional[float],
            block: bool,
            rsock: socket.socket,
            wsock: socket.socket,
            cookie: bytes,
    ) -> ta.Any:
        log.debug(
            '%r._get_sleep(timeout=%r, block=%r, fd=%d/%d)',
            self,
            timeout,
            block,
            rsock.fileno(),
            wsock.fileno(),
        )

        e = None
        try:
            list(poller.poll(timeout))
        except Exception:
            e = sys.exc_info()[1]

        self._lock.acquire()
        try:
            i = self._sleeping.index((wsock, cookie))
            del self._sleeping[i]

            try:
                got_cookie = rsock.recv(self.COOKIE_SIZE)
            except socket.error:
                e2 = sys.exc_info()[1]
                if e2.args[0] == errno.EAGAIN:
                    e = TimeoutError()
                else:
                    e = e2

            Latch._idle_socketpairs.append(SocketPair(rsock, wsock))
            if e:
                raise e

            _check_eq(cookie, got_cookie, f'Cookie incorrect; got {binascii.hexlify(got_cookie)!r}, expected {binascii.hexlify(cookie)!r}')  # noqa
            _check(i < self._waking, 'Cookie correct, but no queue element assigned.')
            self._waking -= 1
            if self._closed:
                raise LatchError
            log.debug('%r.get() wake -> %r', self, self._queue[i])
            return self._queue.pop(i)
        finally:
            self._lock.release()

    def put(self, obj: ta.Any = None) -> None:
        log.debug('%r.put(%r)', self, obj)
        self._lock.acquire()
        try:
            if self._closed:
                raise LatchError
            self._queue.append(obj)

            wsock = None
            if self._waking < len(self._sleeping):
                wsock, cookie = self._sleeping[self._waking]
                self._waking += 1
                log.debug('%r.put() -> waking wfd=%r', self, wsock.fileno())
            elif self._notify:
                self._notify(self)
        finally:
            self._lock.release()

        if wsock:
            self._wake(wsock, cookie)  # noqa

    def _wake(self, wsock: socket.socket, cookie: bytes) -> None:
        c, dc = io_op(os.write, wsock.fileno(), cookie)
        _check(c == len(cookie) and not dc)


##


class Timer:

    def __init__(self, when: float, fn: ta.Callable) -> None:
        super().__init__()
        self._when = when
        self._fn = fn
        self._active = True

    @property
    def when(self) -> float:
        return self._when

    @property
    def fn(self) -> ta.Callable:
        return self._fn

    @property
    def active(self) -> bool:
        return self._active

    def __repr__(self) -> str:
        return f'Timer({self._when!r}, {self._fn!r})'

    def __eq__(self, other):
        return self._when == other._when  # noqa

    def __lt__(self, other):
        return self._when < other._when  # noqa

    def __le__(self, other):
        return self._when <= other._when  # noqa

    def cancel(self) -> None:
        self._active = False


class TimerList:

    def __init__(self) -> None:
        super().__init__()
        self._lst: ta.List[Timer] = []

    def get_timeout(self) -> ta.Optional[float]:
        while self._lst and not self._lst[0].active:
            heapq.heappop(self._lst)
        if self._lst:
            return max(0., self._lst[0].when - time.monotonic())
        return None

    def schedule(self, when: float, fn: ta.Callable) -> Timer:
        timer = Timer(when, fn)
        heapq.heappush(self._lst, timer)
        return timer

    def expire(self) -> None:
        now = time.monotonic()
        while self._lst and self._lst[0].when <= now:
            timer = heapq.heappop(self._lst)
            if timer.active:
                timer.active = False
                timer.fn()


##


class Poller:

    class Entry(ta.NamedTuple):
        data: ta.Any
        gen: int

    def __init__(self) -> None:
        super().__init__()
        self._rfds: ta.Dict[int, Poller.Entry] = {}
        self._wfds: ta.Dict[int, Poller.Entry] = {}
        self._gen = 1

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}@{id(self):x}'

    @property
    def readers(self) -> ta.List[ta.Tuple[ta.Any, int]]:
        return list((fd, data) for fd, (data, gen) in self._rfds.items())

    @property
    def writers(self) -> ta.List[ta.Tuple[ta.Any, int]]:
        return list((fd, data) for fd, (data, gen) in self._wfds.items())

    def close(self) -> None:
        pass

    def start_receive(self, fd: int, data: ta.Any = None) -> None:
        self._rfds[fd] = Poller.Entry(data or fd, self._gen)

    def stop_receive(self, fd: int) -> None:
        self._rfds.pop(fd, None)

    def start_transmit(self, fd: int, data: ta.Any = None) -> None:
        self._wfds[fd] = Poller.Entry(data or fd, self._gen)

    def stop_transmit(self, fd: int) -> None:
        self._wfds.pop(fd, None)

    def _poll(self, timeout: ta.Optional[float]) -> ta.Iterable[ta.Any]:
        (rfds, wfds, _), _ = io_op(
            select.select,
            self._rfds,
            self._wfds,
            (),
            timeout,
        )

        for fd in rfds:
            log.debug('%r: read for %r', self, fd)
            e = self._rfds.get(fd, (None, None))
            if e.gen and e.gen < self._gen:
                yield e.data

        for fd in wfds:
            log.debug('%r: write for %r', self, fd)
            e = self._wfds.get(fd, (None, None))
            if e.gen and e.gen < self._gen:
                yield e.data

    def poll(self, timeout: ta.Optional[float] = None) -> ta.Iterable[ta.Any]:
        log.debug('%r: poll(%r)', self, timeout)
        self._gen += 1
        return self._poll(timeout)


##


class Waker(Protocol):
    read_size = 1

    @classmethod
    def build_stream(cls, broker: 'Broker') -> Stream:
        return Stream(
            cls(broker),
            *pipe(),
        )

    def __init__(self, broker: 'Broker') -> None:
        super().__init__()

        self._broker = broker
        self._deferred = collections.deque()

    def __repr__(self):
        return 'Waker(fd=%r/%r)' % (
            self._stream.rs and self._stream.rs.fd,
            self._stream.ws and self._stream.ws.fd,
        )

    @property
    def keep_alive(self) -> bool:
        return bool(self._deferred)

    def on_transmit(self, broker):
        raise TypeError

    def on_receive(self, broker, buf):
        log.debug('%r.on_receive()', self)

        while True:
            try:
                func, args, kwargs = self._deferred.popleft()
            except IndexError:
                return

            try:
                func(*args, **kwargs)
            except Exception:
                log.exception('%r.defer() crashed: %r(*%r, **%r)', self, func, args, kwargs)
                broker.shutdown()

    def _wake(self):
        try:
            self._stream.ws.write(b' ')
        except OSError:
            e = sys.exc_info()[1]
            if e.args[0] not in (errno.EBADF, errno.EWOULDBLOCK):
                raise

    broker_shutdown_msg = (
        "An attempt was made to enqueue a message with a Broker that has already exited. It is likely your program "
        "called Broker.shutdown() too early."
    )

    def defer(self, func, *args, **kwargs):
        if threading.get_ident() == self._broker.thread_ident:
            log.debug('%r.defer() [immediate]', self)
            return func(*args, **kwargs)

        if self._broker._exited:  # noqa
            raise Exception(self.broker_shutdown_msg)

        log.debug('%r.defer() [fd=%r]', self, self._stream.ws.fd)
        self._deferred.append((func, args, kwargs))
        self._wake()


class Broker:

    def __init__(self) -> None:
        super().__init__()

        self._alive = True
        self._exited = False

        self._shutdown_timeout = 3.0

        self._poller = Poller()
        self._timers = TimerList()

        self._thread = threading.Thread(
            target=self._broker_main,
            name=f'{repr(self)}._broker_main',
        )
        self._thread.start()

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}@{id(self):x}'

    @property
    def thread_ident(self) -> ta.Optional[int]:
        return self._thread.ident

    def keep_alive(self) -> bool:
        # it = (side.keep_alive for (_, (side, _)) in self._poller.readers)
        # return sum(it, 0) > 0 or self._timers.get_timeout() is not None
        raise NotImplementedError

    def _call(self, stream: Stream, fn: ta.Callable) -> None:
        try:
            fn(self)
        except Exception:  # noqa
            log.exception('%r crashed', stream)
            stream.on_disconnect(self)

    def _loop_once(self, timeout: ta.Optional[float] = None) -> None:
        timer_to = self._timers.get_timeout()
        if timeout is None:
            timeout = timer_to
        elif timer_to is not None and timer_to < timeout:
            timeout = timer_to

        for side, fn in self._poller.poll(timeout):
            self._call(side.stream, fn)
        if timer_to is not None:
            self._timers.expire()

    def _broker_exit(self):
        for _, (side, _) in self._poller.readers + self._poller.writers:
            log.debug('%r: force disconnecting %r', self, side)
            side.stream.on_disconnect(self)

        self._poller.close()

    def _broker_shutdown(self):
        for _, (side, _) in self._poller.readers + self._poller.writers:
            self._call(side.stream, side.stream.on_shutdown)

        deadline = time.monotonic() + self._shutdown_timeout
        while self.keep_alive() and time.monotonic() < deadline:
            self._loop_once(max(0., deadline - time.monotonic()))

        if self.keep_alive():
            log.error(
                '%r: pending work still existed %d seconds after shutdown began. This may be due to a timer that is '
                'yet to expire, or a child connection that did not fully shut down.',
                self,
                self._shutdown_timeout,
            )

    def _do_broker_main(self) -> None:
        try:
            while self._alive:
                self._loop_once()

            callback(self, 'before_shutdown')
            callback(self, 'shutdown')
            self._broker_shutdown()

        except Exception:  # noqa
            log.exception('%r: broker crashed', self)

        self._alive = False
        self._exited = True
        self._broker_exit()

    def _broker_main(self) -> None:
        try:
            self._do_broker_main()
        finally:
            callback(self, 'exit')

    def shutdown(self) -> None:
        log.debug('%r: shutting down', self)

        def _shutdown():
            self._alive = False

        if self._alive and not self._exited:
            self.defer(_shutdown)

    def join(self) -> None:
        self._thread.join()


##


def _main() -> None:
    pass


if __name__ == '__main__':
    _main()
