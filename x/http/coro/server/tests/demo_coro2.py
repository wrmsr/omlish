import socket
import typing as ta

from omlish.http.simple.handlers import SimpleHttpHandlerRequest
from omlish.http.simple.handlers import SimpleHttpHandlerResponse
from omlish.http.simple.handlers import SimpleHttpHandlerResponseStreamedData
from omlish.io.fdio.handlers import ServerSocketFdioHandler
from omlish.io.fdio.kqueue import KqueueFdioPoller  # noqa
from omlish.io.fdio.manager import FdioManager
from omlish.io.fdio.pollers import FdioPoller
from omlish.io.fdio.pollers import PollFdioPoller  # noqa
from omlish.io.fdio.pollers import SelectFdioPoller
from omlish.sockets.addresses import SocketAddress

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
        200,
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
