import socket
import typing as ta

from ....http.coro.server.fdio import CoroHttpServerConnectionFdioHandler
from ....http.coro.server.server import UnsupportedMethodSimpleHttpHandlerError
from ....http.simple.handlers import SimpleHttpHandlerRequest
from ....http.simple.handlers import SimpleHttpHandlerResponse
from ....http.simple.handlers import SimpleHttpHandlerResponseStreamedData
from ....sockets.addresses import SocketAddress
from ..handlers import ServerSocketFdioHandler
from ..kqueue import KqueueFdioPoller  # noqa
from ..manager import FdioManager
from ..pollers import FdioPoller
from ..pollers import PollFdioPoller  # noqa
from ..pollers import SelectFdioPoller


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
                addr,
                sock,
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
