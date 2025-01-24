"""
Todo:
 - x/http/htt/omni/socketbinding.py

socat TCP-LISTEN:8000,fork UNIX-CONNECT:foo.sock
"""
import functools
import typing as ta

from ... import check
from ...sockets.bind import SocketBinder
from ...sockets.server.handlers import SocketHandlerSocketServerHandler
from ...sockets.server.handlers import StandardSocketServerHandler
from ...sockets.server.server import SocketServer
from ..coro.server import CoroHttpServer
from ..coro.server import CoroHttpServerSocketHandler
from ..coro.server import UnsupportedMethodHttpHandlerError
from ..handlers import HttpHandlerRequest
from ..handlers import HttpHandlerResponse
from ..handlers import HttpHandlerResponseStreamedData
from ..parsing import HttpRequestParser
from ..versions import HttpProtocolVersions


##


def say_hi_handler(req: HttpHandlerRequest) -> HttpHandlerResponse:
    if req.method not in ('GET', 'POST'):
        raise UnsupportedMethodHttpHandlerError

    resp = '\n'.join([
        f'method: {req.method}',
        f'path: {req.path}',
        f'data: {len(req.data or b"")}',
        '',
    ])
    data = resp.encode('utf-8')

    return HttpHandlerResponse(
        200,
        data=HttpHandlerResponseStreamedData(
            (bytes([b]) for b in data),
            len(data),
        ),
    )


##


def _main() -> None:
    default_port = 8000

    #

    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('port_or_unix_socket', default=str(default_port), nargs='?')
    args = parser.parse_args()

    #

    port_or_unix_socket = check.non_empty_str(args.port_or_unix_socket)
    bind: ta.Any
    try:
        port = int(port_or_unix_socket)
    except ValueError:
        bind = check.non_empty_str(port_or_unix_socket)
    else:
        bind = port

    #

    http_server_factory = functools.partial(
        CoroHttpServer,
        handler=say_hi_handler,
        parser=HttpRequestParser(
            server_version=HttpProtocolVersions.HTTP_1_1,
        ),
    )

    with SocketServer(
            SocketBinder.new(bind),
            StandardSocketServerHandler(
                SocketHandlerSocketServerHandler(
                    CoroHttpServerSocketHandler(
                        http_server_factory,
                    ),
                ),
            ),
    ) as server:
        server.run()


if __name__ == '__main__':
    _main()
