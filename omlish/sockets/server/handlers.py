# ruff: noqa: UP006 UP007
# @omlish-lite
import abc
import concurrent.futures as cf
import dataclasses as dc
import socket
import typing as ta

from ..addresses import SocketAndAddress
from ..handlers import SocketHandler
from ..io import SocketIoPair
from ..io import close_socket_immediately


SocketServerHandler = ta.Callable[[SocketAndAddress], None]  # ta.TypeAlias


##


class SocketServerHandler_(abc.ABC):  # noqa
    @abc.abstractmethod
    def __call__(self, conn: SocketAndAddress) -> None:
        raise NotImplementedError


##


@dc.dataclass(frozen=True)
class StandardSocketServerHandler(SocketServerHandler_):
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


#


@dc.dataclass(frozen=True)
class CallbackWrappedSocketServerHandler(SocketServerHandler_):
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


#


@dc.dataclass(frozen=True)
class SocketHandlerSocketServerHandler(SocketServerHandler_):
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


#


@dc.dataclass(frozen=True)
class SocketWrappingSocketServerHandler(SocketServerHandler_):
    handler: SocketServerHandler
    wrapper: ta.Callable[[SocketAndAddress], SocketAndAddress]

    def __call__(self, conn: SocketAndAddress) -> None:
        wrapped_conn = self.wrapper(conn)
        self.handler(wrapped_conn)


#

@dc.dataclass(frozen=True)
class ExecutorSocketServerHandler(SocketServerHandler_):
    handler: SocketServerHandler
    executor: cf.Executor

    def __call__(self, conn: SocketAndAddress) -> None:
        self.executor.submit(self.handler, conn)
