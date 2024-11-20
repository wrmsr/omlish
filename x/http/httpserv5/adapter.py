import socket
import socketserver
import typing as ta

from omlish import check

from .sockets import SocketAddress
from .sockets import SocketRequestHandlerFactory


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
    rfile: ta.IO
    wfile: ta.IO


#


class SocketRequestHandlerSocketServerAdapter(
    socketserver.StreamRequestHandler,
    SocketServerBaseRequestHandler_,
):
    adapter_target_factory: SocketRequestHandlerFactory | None = None

    def __init__(
            self,
            request: socket.socket,
            client_address: SocketAddress,
            server: socketserver.TCPServer,
            *,
            adapter_target_factory: SocketRequestHandlerFactory | None = None,
    ) -> None:
        if adapter_target_factory is not None:
            self.adapter_target_factory = adapter_target_factory

        super().__init__(
            request,
            client_address,
            server,
        )

    def handle(self) -> None:
        target = check.not_none(self.adapter_target_factory)(
            self.client_address,
            self.rfile,
            self.wfile,
        )
        target.handle()
