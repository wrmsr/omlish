import socket
import typing as ta

from omlish.lite.check import check_not_none
from omlish.lite.fdio.corohttp import CoroHttpServerConnectionFdIoHandler
from omlish.lite.fdio.handlers import SocketFdIoHandler
from omlish.lite.http.handlers import HttpHandler
from omlish.lite.http.handlers import HttpHandlerRequest
from omlish.lite.http.handlers import HttpHandlerResponse
from omlish.lite.socket import SocketAddress

from .dispatchers import Dispatchers
from .types import HasDispatchers


##


class SocketServerFdIoHandler(SocketFdIoHandler):
    def __init__(
            self,
            addr: SocketAddress,
            on_connect: ta.Callable[[socket.socket, SocketAddress], None],
    ) -> None:
        sock = socket.create_server(addr)
        sock.setblocking(False)

        super().__init__(addr, sock)

        self._on_connect = on_connect

        sock.listen(1)

    def readable(self) -> bool:
        return True

    def on_readable(self) -> None:
        cli_sock, cli_addr = check_not_none(self._sock).accept()
        cli_sock.setblocking(False)

        self._on_connect(cli_sock, cli_addr)


##


def say_hi_handler(req: HttpHandlerRequest) -> HttpHandlerResponse:
    resp = '\n'.join([
        f'method: {req.method}',
        f'path: {req.path}',
        f'data: {len(req.data or b"")}',
        '',
    ])

    return HttpHandlerResponse(
        200,
        data=resp.encode('utf-8'),
    )


##


class HttpServer(HasDispatchers):
    def __init__(
            self,
            addr: SocketAddress = ('localhost', 8000),
            handler: HttpHandler = say_hi_handler,
    ) -> None:
        super().__init__()

        self._addr = addr
        self._handler = handler

        self._server = SocketServerFdIoHandler(self._addr, self._on_connect)

    def get_dispatchers(self) -> Dispatchers:
        return Dispatchers([self._server])

    def _on_connect(self, sock: socket.socket, addr: SocketAddress) -> None:
        conn = CoroHttpServerConnectionFdIoHandler(  # noqa
            addr,
            sock,
            self._handler,
        )

        raise NotImplementedError
