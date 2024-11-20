import functools
import http.server
import sys

from .adapter import SocketRequestHandlerSocketServerAdapter
from .http import HttpServerRequest
from .http import HttpServerResponse
from .http import HttpSocketRequestHandler
from .http import UnsupportedMethodServerHandlerError
from .sockets import get_best_socket_family


##


def say_hi_handler(req: HttpServerRequest) -> HttpServerResponse:
    if req.method not in ('GET', 'POST'):
        raise UnsupportedMethodServerHandlerError

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
                SocketRequestHandlerSocketServerAdapter,
                adapter_target_factory=functools.partial(
                    HttpSocketRequestHandler,
                    handler=say_hi_handler,
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
