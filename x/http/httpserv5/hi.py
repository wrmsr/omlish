import functools
import http.server
import sys

from omlish.lite.http.parsing import HttpRequestParser
from omlish.lite.http.versions import HttpProtocolVersions
from omlish.lite.socket import get_best_socket_family
from omlish.lite.socketserver import SocketHandlerSocketServerStreamRequestHandler

from .server import CoroHttpServer
from .server import CoroHttpServerSocketHandler
from .server import HttpHandlerRequest
from .server import HttpHandlerResponse
from .server import UnsupportedMethodHttpHandlerError


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

    return HttpHandlerResponse(
        200,
        data=resp.encode('utf-8'),
    )


##


def _main() -> None:
    port = 8000
    bind = None

    server_class = http.server.ThreadingHTTPServer
    server_class.address_family, addr = get_best_socket_family(bind, port)

    with server_class(
            addr,
            functools.partial(
                SocketHandlerSocketServerStreamRequestHandler,
                socket_handler_factory=functools.partial(
                    CoroHttpServerSocketHandler,
                    coro_http_server_factory=functools.partial(
                        CoroHttpServer,
                        handler=say_hi_handler,
                        parser=HttpRequestParser(
                            server_version=HttpProtocolVersions.HTTP_1_1,
                        ),
                    ),
                ),
            ),
    ) as httpd:
        host, port = httpd.socket.getsockname()[:2]
        url_host = f'[{host}]' if ':' in host else host
        print(f'Serving HTTP on {host} port {port} (http://{url_host}:{port}/) ...')

        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print('\nKeyboard interrupt received, exiting.')
            sys.exit(0)


if __name__ == '__main__':
    _main()
