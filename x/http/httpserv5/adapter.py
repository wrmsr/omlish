import socket
import socketserver
import typing as ta

from omlish.lite.check import check_not_none

from .sockets import SocketAddress
from .sockets import SocketHandlerFactory


##


class SocketServerBaseRequestHandler_:  # noqa
    request: socket.socket
    client_address: SocketAddress
    server: socketserver.TCPServer


class SocketServerStreamRequestHandler_(SocketServerBaseRequestHandler_):  # noqa
    rbufsize: int
    wbufsize: int

    timeout: float | None

    disable_nagle_algorithm: bool

    connection: socket.socket
    rfile: ta.BinaryIO
    wfile: ta.BinaryIO


#


class SocketHandlerSocketServerAdapter(  # type: ignore[misc]
    socketserver.StreamRequestHandler,
    SocketServerStreamRequestHandler_,
):
    adapter_target_factory: SocketHandlerFactory | None = None

    def __init__(
            self,
            request: socket.socket,
            client_address: SocketAddress,
            server: socketserver.TCPServer,
            *,
            adapter_target_factory: SocketHandlerFactory | None = None,
    ) -> None:
        if adapter_target_factory is not None:
            self.adapter_target_factory = adapter_target_factory

        super().__init__(
            request,
            client_address,
            server,
        )

    def handle(self) -> None:
        target = check_not_none(self.adapter_target_factory)(
            self.client_address,
            self.rfile,  # type: ignore[arg-type]
            self.wfile,  # type: ignore[arg-type]
        )
        target.handle()
