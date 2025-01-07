# ruff: noqa: UP006 UP007
# @omlish-lite
import socket
import socketserver
import typing as ta

from ..lite.check import check
from .addresses import SocketAddress
from .handlers import SocketHandlerFactory


##


class SocketServerBaseRequestHandler_:  # noqa
    request: socket.socket
    client_address: SocketAddress
    server: socketserver.TCPServer


class SocketServerStreamRequestHandler_(SocketServerBaseRequestHandler_):  # noqa
    rbufsize: int
    wbufsize: int

    timeout: ta.Optional[float]

    disable_nagle_algorithm: bool

    connection: socket.socket
    rfile: ta.BinaryIO
    wfile: ta.BinaryIO


##


class SocketHandlerSocketServerStreamRequestHandler(  # type: ignore[misc]
    socketserver.StreamRequestHandler,
    SocketServerStreamRequestHandler_,
):
    socket_handler_factory: ta.Optional[SocketHandlerFactory] = None

    def __init__(
            self,
            request: socket.socket,
            client_address: SocketAddress,
            server: socketserver.TCPServer,
            *,
            socket_handler_factory: ta.Optional[SocketHandlerFactory] = None,
    ) -> None:
        if socket_handler_factory is not None:
            self.socket_handler_factory = socket_handler_factory

        super().__init__(
            request,
            client_address,
            server,
        )

    def handle(self) -> None:
        target = check.not_none(self.socket_handler_factory)(
            self.client_address,
            self.rfile,  # type: ignore[arg-type]
            self.wfile,  # type: ignore[arg-type]
        )
        target.handle()
