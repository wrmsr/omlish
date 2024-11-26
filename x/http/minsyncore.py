import socket

from omlish.lite.check import check_not_none
from omlish.lite.fdio.corohttp import CoroHttpServerConnectionFdIoHandler
from omlish.lite.fdio.handlers import SocketFdIoHandler
from omlish.lite.fdio.manager import FdIoManager
from omlish.lite.fdio.pollers import FdIoPoller
from omlish.lite.fdio.pollers import PollFdIoPoller
from omlish.lite.http.handlers import HttpHandler
from omlish.lite.http.handlers import HttpHandlerRequest
from omlish.lite.http.handlers import HttpHandlerResponse
from omlish.lite.logs import configure_standard_logging
from omlish.lite.socket import SocketAddress


##


class CoroHttpServerFdIoHandler(SocketFdIoHandler):
    def __init__(
            self,
            addr: SocketAddress,
            handler: HttpHandler,
            io: FdIoManager,
    ) -> None:
        super().__init__(addr, socket.create_server(addr))

        self._handler = handler
        self._io = io

        sock = check_not_none(self._sock)
        sock.setblocking(False)
        sock.listen(1)

    def readable(self) -> bool:
        return True

    def on_readable(self) -> None:
        cli_sock, cli_addr = self._sock.accept()
        cli_sock.setblocking(False)

        conn = CoroHttpServerConnectionFdIoHandler(
            cli_addr,
            cli_sock,
            self._handler,
        )

        self._io.register(conn)


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


def _main() -> None:
    configure_standard_logging('INFO')

    io_poller_impl: type[FdIoPoller] = next(filter(None, [
        # KqueueFdIoPoller,
        PollFdIoPoller,
        # SelectFdIoPoller,
    ]))
    io_poller = io_poller_impl()

    io_manager = FdIoManager(io_poller)

    srv_addr = ('localhost', 8000)
    srv = CoroHttpServerFdIoHandler(
        srv_addr,
        say_hi_handler,
        io_manager,
    )
    io_manager.register(srv)

    while True:
        io_manager.poll()


if __name__ == '__main__':
    _main()
