import functools
import http.server
import sys

from omlish.lite.http.parsing import HttpRequestParser
from omlish.lite.http.versions import HttpProtocolVersions
from omlish.lite.socket import get_best_socket_family
from omlish.lite.socketserver import SocketHandlerSocketServerStreamRequestHandler

from .server import HttpServer
from .server import HttpServerRequest
from .server import HttpServerResponse
from .server import HttpServerSocketHandler
from .server import UnsupportedMethodHttpServerHandlerError


##


def say_hi_handler(req: HttpServerRequest) -> HttpServerResponse:
    if req.method not in ('GET', 'POST'):
        raise UnsupportedMethodHttpServerHandlerError

    resp = '\n'.join([
        f'method: {req.method}',
        f'path: {req.path}',
        f'data: {len(req.data or b"")}',
        '',
    ])

    return HttpServerResponse(
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
                handler_factory=functools.partial(
                    HttpServerSocketHandler,
                    http_server=HttpServer(
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
