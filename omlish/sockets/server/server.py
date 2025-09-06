# ruff: noqa: UP006 UP007 UP045
# @omlish-lite
import abc
import contextlib
import enum
import logging
import selectors
import threading
import typing as ta

from ...lite.abstract import Abstract
from ...lite.contextmanagers import ExitStacked
from ...lite.contextmanagers import defer
from ...logs.protocols import LoggerLike
from ..addresses import SocketAndAddress
from ..bind import SocketBinder
from ..io import close_socket_immediately
from .handlers import SocketServerHandler


##


class SocketServer:
    _DEFAULT_LOGGER: LoggerLike = logging.getLogger('.'.join([__name__, 'SocketServer']))  # FIXME

    def __init__(
            self,
            binder: SocketBinder,
            handler: SocketServerHandler,
            *,
            on_error: ta.Optional[ta.Callable[[BaseException, ta.Optional[SocketAndAddress]], None]] = None,
            error_logger: ta.Optional[LoggerLike] = _DEFAULT_LOGGER,
            poll_interval: float = .5,
            shutdown_timeout: ta.Optional[float] = None,
    ) -> None:
        super().__init__()

        self._binder = binder
        self._handler = handler
        self._on_error = on_error
        self._error_logger = error_logger
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

    def _handle_error(self, exc: BaseException, conn: ta.Optional[SocketAndAddress] = None) -> None:
        if (error_logger := self._error_logger) is not None:
            error_logger.exception('Error in socket server: %r', conn)

        if (on_error := self._on_error) is not None:
            on_error(exc, conn)

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

    class PollResult(enum.Enum):
        TIMEOUT = enum.auto()
        CONNECTION = enum.auto()
        ERROR = enum.auto()
        SHUTDOWN = enum.auto()

    class PollContext(ExitStacked, Abstract):
        @abc.abstractmethod
        def poll(self, timeout: ta.Optional[float] = None) -> 'SocketServer.PollResult':
            raise NotImplementedError

    class _PollContext(PollContext):
        def __init__(self, server: 'SocketServer') -> None:
            super().__init__()

            self._server = server

        _selector: ta.Any = None

        def _enter_contexts(self) -> None:
            self._enter_context(self._server._lock)  # noqa: SLF001
            self._enter_context(self._server._binder)  # noqa: SLF001

            self._server._binder.listen()  # noqa: SLF001

            self._server._is_shutdown.clear()  # noqa: SLF001
            self._enter_context(defer(self._server._is_shutdown.set))  # noqa

            # XXX: Consider using another file descriptor or connecting to the socket to wake this up instead of
            # polling. Polling reduces our responsiveness to a shutdown request and wastes cpu at all other times.
            self._selector = self._enter_context(self._server.Selector())
            self._selector.register(self._server._binder.fileno(), selectors.EVENT_READ)  # noqa: SLF001

        def poll(self, timeout: ta.Optional[float] = None) -> 'SocketServer.PollResult':
            if self._server._should_shutdown:  # noqa: SLF001
                return SocketServer.PollResult.SHUTDOWN

            ready = self._selector.select(timeout)

            # bpo-35017: shutdown() called during select(), exit immediately.
            if self._server._should_shutdown:  # noqa: SLF001
                return SocketServer.PollResult.SHUTDOWN  # type: ignore[unreachable]

            if not ready:
                return SocketServer.PollResult.TIMEOUT

            try:
                conn = self._server._binder.accept()  # noqa: SLF001

            except OSError as exc:
                self._server._handle_error(exc)  # noqa: SLF001

                return SocketServer.PollResult.ERROR

            try:
                self._server._handler(conn)  # noqa: SLF001

            except Exception as exc:  # noqa
                self._server._handle_error(exc, conn)  # noqa: SLF001

                close_socket_immediately(conn.socket)

            return SocketServer.PollResult.CONNECTION

    def poll_context(self) -> PollContext:
        return self._PollContext(self)

    #

    @contextlib.contextmanager
    def loop_context(self, poll_interval: ta.Optional[float] = None) -> ta.Iterator[ta.Iterator[bool]]:
        if poll_interval is None:
            poll_interval = self._poll_interval

        with self.poll_context() as pc:
            def loop():
                while True:
                    res = pc.poll(poll_interval)
                    if res in (SocketServer.PollResult.ERROR, SocketServer.PollResult.SHUTDOWN):
                        return
                    else:
                        yield res == SocketServer.PollResult.CONNECTION

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
