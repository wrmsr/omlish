"""
Todo:
 - x/http/htt/omni/socketbinding.py

socat TCP-LISTEN:8000,fork UNIX-CONNECT:foo.sock
"""
import functools
import os
import socket
import socketserver
import sys
import typing as ta

from ... import check
from ...sockets.addresses import get_best_socket_family
from ...sockets.server import SocketHandlerSocketServerStreamRequestHandler
from ..coro.server import CoroHttpServer
from ..coro.server import CoroHttpServerSocketHandler
from ..coro.server import UnsupportedMethodHttpHandlerError
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


class HttpServer(socketserver.TCPServer):
    allow_reuse_address = True  # Seems to make sense in testing environment

    def __init__(
            self,
            server_address: ta.Any,
            RequestHandlerClass: ta.Callable,  # noqa
            bind_and_activate: bool = True,
            *,
            address_family: int = socket.AF_INET,
            socket_type: int = socket.SOCK_STREAM,
            request_queue_size: int = 5,
            allow_reuse_address: bool = False,
            allow_reuse_port: bool = False,
    ) -> None:
        self.address_family = address_family
        self.socket_type = socket_type
        self.request_queue_size = request_queue_size
        self.allow_reuse_address = allow_reuse_address
        self.allow_reuse_port = allow_reuse_port

        super().__init__(
            server_address,
            RequestHandlerClass,
            bind_and_activate=bind_and_activate,
        )

    def server_bind(self):
        super().server_bind()

        host, port = self.server_address[:2]

        self.server_name = socket.getfqdn(host)  # type: ignore  # noqa
        self.server_port = port  # noqa


class ThreadingHttpServer(socketserver.ThreadingMixIn, HttpServer):
    daemon_threads = True


##


def _main() -> None:
    default_port = 8000

    #

    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('port_or_unix_socket', default=str(default_port), nargs='?')
    args = parser.parse_args()

    #

    unix_socket: str | None = None
    port: int | None = None
    bind: str | None = None

    port_or_unix_socket = check.non_empty_str(args.port_or_unix_socket)
    try:
        port = int(port_or_unix_socket)
    except ValueError:
        unix_socket = check.non_empty_str(port_or_unix_socket)

    #

    server_class = ThreadingHttpServer

    if unix_socket is not None:
        check.arg(unix_socket.endswith('.sock'))
        if os.path.exists(unix_socket):
            os.unlink(unix_socket)
        addr = unix_socket
        address_family = socket.AF_UNIX
    elif port is not None:
        address_family, addr = get_best_socket_family(bind, port)
    else:
        raise RuntimeError

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
            address_family=address_family,
    ) as httpd:
        if unix_socket:
            print(f'Serving HTTP on unix socket {httpd.socket.getsockname()} ...')  # noqa
        else:
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
