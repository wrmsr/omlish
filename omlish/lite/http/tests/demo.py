import functools
import socket
import socketserver
import sys

from ...socket import get_best_socket_family
from ...socketserver import SocketHandlerSocketServerStreamRequestHandler
from ..coroserver import CoroHttpServer
from ..coroserver import CoroHttpServerSocketHandler
from ..coroserver import UnsupportedMethodHttpHandlerError
from ..handlers import HttpHandlerRequest
from ..handlers import HttpHandlerResponse
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

    return HttpHandlerResponse(
        200,
        data=resp.encode('utf-8'),
    )


##


class HTTPServer(socketserver.TCPServer):

    allow_reuse_address = True  # Seems to make sense in testing environment

    def server_bind(self):
        super().server_bind()
        host, port = self.server_address[:2]
        self.server_name = socket.getfqdn(host)  # type: ignore
        self.server_port = port


class ThreadingHTTPServer(socketserver.ThreadingMixIn, HTTPServer):
    daemon_threads = True


##


def _main() -> None:
    port = 8000
    bind = None

    server_class = ThreadingHTTPServer
    server_class.address_family, addr = get_best_socket_family(bind, port)
    # server_class.address_family = socket.AF_UNIX

    with server_class(
            addr,
            functools.partial(
                SocketHandlerSocketServerStreamRequestHandler,
                socket_handler_factory=functools.partial(
                    CoroHttpServerSocketHandler,
                    server_factory=functools.partial(
                        CoroHttpServer,
                        handler=say_hi_handler,
                        parser=HttpRequestParser(
                            server_version=HttpProtocolVersions.HTTP_1_1,
                        ),
                    ),
                    log_handler=lambda s, l: print(repr((s.client_address, l)), file=sys.stderr),
                ),
            ),
    ) as httpd:
        host, port = httpd.socket.getsockname()[:2]
        url_host = f'[{host}]' if ':' in host else host
        print(f'Serving HTTP on {host} port {port} (http://{url_host}:{port}/) ...')  # noqa

        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print('\nKeyboard interrupt received, exiting.')
            sys.exit(0)


if __name__ == '__main__':
    _main()
