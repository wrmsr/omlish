import socket
import typing as ta

from omcore.http.simple.handlers import SimpleHttpHandlerRequest
from omcore.http.simple.handlers import SimpleHttpHandlerResponse
from omcore.http.simple.handlers import SimpleHttpHandlerResponseStreamedData
from omcore.io.fdio.handlers import ServerSocketFdioHandler
from omcore.io.fdio.kqueue import KqueueFdioPoller  # noqa
from omcore.io.fdio.manager import FdioManager
from omcore.io.fdio.pollers import FdioPoller
from omcore.io.fdio.pollers import PollFdioPoller  # noqa
from omcore.io.fdio.pollers import SelectFdioPoller
from omcore.sockets.addresses import SocketAddress

from ...server.fdio import CoroHttpServerConnectionFdioHandler
from ...server.server import UnsupportedMethodSimpleHttpHandlerError


##


def say_hi_handler(req: SimpleHttpHandlerRequest) -> SimpleHttpHandlerResponse:
    if req.method not in ('GET', 'POST'):
        raise UnsupportedMethodSimpleHttpHandlerError

    resp = '\n'.join([
        f'method: {req.method}',
        f'path: {req.path}',
        f'data: {len(req.data or b"")}',
        '',
    ])
    data = resp.encode('utf-8')

    resp_data: ta.Any
    if 'stream' in req.headers:
        def stream_data():
            for b in data:
                yield bytes([b])

        resp_data = SimpleHttpHandlerResponseStreamedData(
            stream_data(),
            len(data),
        )

    else:
        resp_data = data

    return SimpleHttpHandlerResponse(
        status=200,
        data=resp_data,
    )


##


def _main() -> None:
    poller: FdioPoller = next(filter(None, [
        KqueueFdioPoller,
        PollFdioPoller,
        SelectFdioPoller,
    ]))()

    man = FdioManager(poller)

    def on_connect(sock: socket.socket, addr: SocketAddress) -> None:
        try:
            conn = CoroHttpServerConnectionFdioHandler(
                sock,
                addr,
                say_hi_handler,
            )

            man.register(conn)

        except BaseException:  # noqa
            sock.close()

            raise

    server = ServerSocketFdioHandler(('127.0.0.1', 8080), on_connect)

    man.register(server)

    while True:
        man.poll()


if __name__ == '__main__':
    _main()
