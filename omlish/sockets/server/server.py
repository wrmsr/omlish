# @omlish-lite
# ruff: noqa: UP006 UP007
import abc
import contextlib
import logging
import selectors
import threading
import typing as ta

from ..addresses import SocketAndAddress
from ..bind import SocketBinder
from ..io import close_socket_immediately
from .handlers import SocketServerHandler


##


class SocketServer(abc.ABC):
    _DEFAULT_LOGGER = logging.getLogger('.'.join([__name__, 'SocketServer']))

    def __init__(
            self,
            binder: SocketBinder,
            handler: SocketServerHandler,
            *,
            on_error: ta.Optional[ta.Callable[[BaseException, ta.Optional[SocketAndAddress]], None]] = None,
            error_logger: ta.Optional[logging.Logger] = _DEFAULT_LOGGER,
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
                            self._handle_error(exc)

                            return

                        try:
                            self._handler(conn)

                        except Exception as exc:  # noqa
                            self._handle_error(exc, conn)

                            close_socket_immediately(conn.socket)

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
