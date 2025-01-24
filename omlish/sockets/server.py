# @omlish-lite
# ruff: noqa: UP006 UP007
import abc
import contextlib
import dataclasses as dc
import selectors
import socket
import threading
import time
import typing as ta

from ..lite.check import check
from .addresses import SocketAndAddress
from .bind import SocketBinder
from .handlers import SocketHandler
from .io import SocketIoPair
from .io import close_socket_immediately


SocketServerHandler = ta.Callable[[SocketAndAddress], None]  # ta.TypeAlias


##


class SocketServer(abc.ABC):
    def __init__(
            self,
            binder: SocketBinder,
            handler: SocketServerHandler,
            *,
            on_error: ta.Optional[ta.Callable[[BaseException], None]] = None,
            poll_interval: float = .5,
            shutdown_timeout: ta.Optional[float] = None,
    ) -> None:
        super().__init__()

        self._binder = binder
        self._handler = handler
        self._on_error = on_error
        self._poll_interval = poll_interval
        self._shutdown_timeout = shutdown_timeout

        self._lock = threading.RLock()
        self._is_shutdown = threading.Event()
        self._should_shutdown = False

    @property
    def binder(self) -> SocketBinder:
        return self._binder

    @property
    def handler(self) -> SocketServerHandler:
        return self._handler

    #

    class SelectorProtocol(ta.Protocol):
        def register(self, *args, **kwargs) -> None:
            raise NotImplementedError

        def select(self, *args, **kwargs) -> bool:
            raise NotImplementedError

    Selector: ta.ClassVar[ta.Any]
    if hasattr(selectors, 'PollSelector'):
        Selector = selectors.PollSelector
    else:
        Selector = selectors.SelectSelector

    #

    @contextlib.contextmanager
    def _listen_context(self) -> ta.Iterator[SelectorProtocol]:
        with contextlib.ExitStack() as es:
            es.enter_context(self._lock)
            es.enter_context(self._binder)

            self._binder.listen()

            self._is_shutdown.clear()
            try:
                # XXX: Consider using another file descriptor or connecting to the socket to wake this up instead of
                # polling. Polling reduces our responsiveness to a shutdown request and wastes cpu at all other times.
                with self.Selector() as selector:
                    selector.register(self._binder.fileno(), selectors.EVENT_READ)

                    yield selector

            finally:
                self._is_shutdown.set()

    @contextlib.contextmanager
    def loop_context(self, poll_interval: ta.Optional[float] = None) -> ta.Iterator[ta.Iterator[bool]]:
        if poll_interval is None:
            poll_interval = self._poll_interval

        with self._listen_context() as selector:
            def loop():
                while not self._should_shutdown:
                    ready = selector.select(poll_interval)

                    # bpo-35017: shutdown() called during select(), exit immediately.
                    if self._should_shutdown:
                        break  # type: ignore[unreachable]

                    if ready:
                        try:
                            conn = self._binder.accept()

                        except OSError as exc:
                            if (on_error := self._on_error) is not None:
                                on_error(exc)

                            return

                        self._handler(conn)

                    yield bool(ready)

            yield loop()

    def run(self, poll_interval: ta.Optional[float] = None) -> None:
        with self.loop_context(poll_interval=poll_interval) as loop:
            for _ in loop:
                pass

    #

    class _NOT_SET:  # noqa
        def __new__(cls, *args, **kwargs):  # noqa
            raise TypeError

    def shutdown(
            self,
            block: bool = False,
            timeout: ta.Union[float, None, ta.Type[_NOT_SET]] = _NOT_SET,
    ) -> None:
        self._should_shutdown = True

        if block:
            if timeout is self._NOT_SET:
                timeout = self._shutdown_timeout

            if not self._is_shutdown.wait(timeout=timeout):  # type: ignore
                raise TimeoutError

    #

    def __enter__(self) -> 'SocketServer':
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.shutdown()


##


@dc.dataclass(frozen=True)
class StandardSocketServerHandler:
    handler: SocketServerHandler

    timeout: ta.Optional[float] = None

    # http://bugs.python.org/issue6192
    # TODO: https://eklitzke.org/the-caveats-of-tcp-nodelay
    disable_nagle_algorithm: bool = False

    no_close: bool = False

    def __call__(self, conn: SocketAndAddress) -> None:
        try:
            if self.timeout is not None:
                conn.socket.settimeout(self.timeout)

            if self.disable_nagle_algorithm:
                conn.socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, True)

            self.handler(conn)

        finally:
            close_socket_immediately(conn.socket)


@dc.dataclass(frozen=True)
class CallbackWrappedSocketServerHandler:
    handler: SocketServerHandler

    before_handle: ta.Optional[SocketServerHandler] = None
    after_handle: ta.Optional[SocketServerHandler] = None

    # Return True if suppress like __exit__
    on_error: ta.Optional[ta.Callable[[SocketAndAddress, Exception], bool]] = None

    finally_: ta.Optional[SocketServerHandler] = None

    def __call__(self, conn: SocketAndAddress) -> None:
        try:
            if (before_handle := self.before_handle) is not None:
                before_handle(conn)

            self.handler(conn)

        except Exception as e:
            if (on_error := self.on_error) is not None and on_error(conn, e):
                pass
            else:
                raise

        else:
            if (after_handle := self.after_handle) is not None:
                after_handle(conn)

        finally:
            if (finally_ := self.finally_) is not None:
                finally_(conn)


@dc.dataclass(frozen=True)
class SocketHandlerServerSocketHandler:
    handler: SocketHandler

    r_buf_size: int = -1
    w_buf_size: int = 0

    def __call__(self, conn: SocketAndAddress) -> None:
        fp = SocketIoPair.from_socket(
            conn.socket,
            r_buf_size=self.r_buf_size,
            w_buf_size=self.w_buf_size,
        )

        self.handler(conn.address, fp)


##


class ThreadingSocketServerHandler:
    def __init__(
            self,
            handler: SocketServerHandler,
            *,
            shutdown_timeout: ta.Optional[float] = None,
    ) -> None:
        super().__init__()

        self._handler = handler
        self._shutdown_timeout = shutdown_timeout

        self._lock = threading.RLock()
        self._threads: ta.List[threading.Thread] = []
        self._is_shutdown = False

    @property
    def handler(self) -> SocketServerHandler:
        return self._handler

    #

    def __call__(self, conn: SocketAndAddress) -> None:
        self.handle(conn)

    def handle(self, conn: SocketAndAddress) -> None:
        with self._lock:
            check.state(not self._is_shutdown)

            self._reap()

            t = threading.Thread(
                target=self._handler,
                args=(conn,),
            )

            self._threads.append(t)

            t.start()

    #

    def _reap(self) -> None:
        with self._lock:
            self._threads[:] = (thread for thread in self._threads if thread.is_alive())

    def is_alive(self) -> bool:
        with self._lock:
            self._reap()

            return bool(self._threads)

    def join(self, timeout: ta.Optional[float] = None) -> None:
        if timeout is not None:
            deadline: ta.Optional[float] = time.time() + timeout
        else:
            deadline = None

        def calc_timeout() -> ta.Optional[float]:
            if deadline is None:
                return None

            tt = deadline - time.time()
            if tt <= 0:
                raise TimeoutError

            return tt

        if not (self._lock.acquire(timeout=calc_timeout() or -1)):
            raise TimeoutError

        try:
            self._reap()

            for t in self._threads:
                t.join(timeout=calc_timeout())

                if t.is_alive():
                    raise TimeoutError

        finally:
            self._lock.release()

    #

    class _NOT_SET:  # noqa
        def __new__(cls, *args, **kwargs):  # noqa
            raise TypeError

    def shutdown(
            self,
            block: bool = False,
            timeout: ta.Union[float, None, ta.Type[_NOT_SET]] = _NOT_SET,
    ) -> None:
        self._is_shutdown = True

        if block:
            if timeout is self._NOT_SET:
                timeout = self._shutdown_timeout

            self.join(timeout=timeout)  # type: ignore

    #

    def __enter__(self) -> 'ThreadingSocketServerHandler':
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.shutdown()
