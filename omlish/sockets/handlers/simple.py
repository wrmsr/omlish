# ruff: noqa: UP006 UP007 UP045
# @omlish-lite
import concurrent.futures as cf
import dataclasses as dc
import socket
import typing as ta

from ...logs.protocols import LoggerLike
from ..addresses import SocketAndAddress
from ..io import close_socket_immediately
from .types import SocketHandler
from .types import SocketHandler_


##


@dc.dataclass(frozen=True)
class StandardSocketHandler(SocketHandler_):
    handler: SocketHandler

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


##


@dc.dataclass(frozen=True)
class CallbackWrappedSocketHandler(SocketHandler_):
    handler: SocketHandler

    before_handle: ta.Optional[SocketHandler] = None
    after_handle: ta.Optional[SocketHandler] = None

    # Return True if suppress like __exit__
    on_error: ta.Optional[ta.Callable[[SocketAndAddress, Exception], bool]] = None

    finally_: ta.Optional[SocketHandler] = None

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


##


@dc.dataclass(frozen=True)
class SocketWrappingSocketHandler(SocketHandler_):
    handler: SocketHandler
    wrapper: ta.Callable[[SocketAndAddress], SocketAndAddress]

    def __call__(self, conn: SocketAndAddress) -> None:
        wrapped_conn = self.wrapper(conn)
        self.handler(wrapped_conn)


##


@dc.dataclass(frozen=True)
class ExecutorSocketHandler(SocketHandler_):
    handler: SocketHandler
    executor: cf.Executor

    def __call__(self, conn: SocketAndAddress) -> None:
        self.executor.submit(self.handler, conn)


##


@dc.dataclass(frozen=True)
class ExceptionLoggingSocketHandler(SocketHandler_):
    handler: SocketHandler
    log: LoggerLike

    ignored: ta.Optional[ta.Container[ta.Type[Exception]]] = None

    def __call__(self, conn: SocketAndAddress) -> None:
        try:
            return self.handler(conn)

        except Exception as e:  # noqa
            if (ignored := self.ignored) is None or type(e) not in ignored:
                self.log.exception('Error in handler %r for conn %r', self.handler, conn)

            raise
