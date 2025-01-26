# ruff: noqa: UP006 UP007
"""
Todo:
 - x/http/htt/omni/socketbinding.py

socat TCP-LISTEN:8000,fork UNIX-CONNECT:foo.sock
"""
import contextlib
import functools
import ssl
import typing as ta

from ... import check
from ...sockets.bind import CanSocketBinder
from ...sockets.bind import SocketBinder
from ...sockets.server.handlers import SocketHandlerSocketServerHandler
from ...sockets.server.handlers import SocketServerHandler
from ...sockets.server.handlers import SocketWrappingSocketServerHandler
from ...sockets.server.handlers import StandardSocketServerHandler
from ...sockets.server.server import SocketServer
from ...sockets.server.threading import ThreadingSocketServerHandler
from ..coro.server import CoroHttpServer
from ..coro.server import CoroHttpServerSocketHandler
from ..coro.server import UnsupportedMethodHttpHandlerError
from ..handlers import HttpHandler
from ..handlers import HttpHandlerRequest
from ..handlers import HttpHandlerResponse
from ..handlers import HttpHandlerResponseStreamedData
from ..parsing import HttpRequestParser
from ..versions import HttpProtocolVersion
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


@contextlib.contextmanager
def make_simple_http_server(
        bind: CanSocketBinder,
        handler: HttpHandler,
        *,
        server_version: HttpProtocolVersion = HttpProtocolVersions.HTTP_1_1,
        ssl_context: ta.Optional[ssl.SSLContext] = None,
        use_threads: bool = False,
) -> ta.Iterator[SocketServer]:
    with contextlib.ExitStack() as es:
        server_factory = functools.partial(
            CoroHttpServer,
            handler=handler,
            parser=HttpRequestParser(
                server_version=server_version,
            ),
        )

        socket_handler = CoroHttpServerSocketHandler(
            server_factory,
        )

        server_handler: SocketServerHandler = SocketHandlerSocketServerHandler(
            socket_handler,
        )

        if ssl_context is not None:
            server_handler = SocketWrappingSocketServerHandler(
                functools.partial(
                    ssl_context.wrap_socket,
                    server_side=True,
                ),
            )

        server_handler = StandardSocketServerHandler(
            server_handler,
        )

        if use_threads:
            server_handler = es.enter_context(ThreadingSocketServerHandler(
                server_handler,
            ))

        server = es.enter_context(SocketServer(
            SocketBinder.of(bind),
            server_handler,
        ))

        yield server


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

    with make_simple_http_server(
        bind,
        say_hi_handler,
        use_threads=True,
    ) as server:
        server.run()


if __name__ == '__main__':
    _main()
