# ruff: noqa: UP006 UP007
# @omlish-lite
import contextlib
import functools
import ssl
import typing as ta

from ..sockets.bind import CanSocketBinder
from ..sockets.bind import SocketBinder
from ..sockets.server.handlers import SocketHandlerSocketServerHandler
from ..sockets.server.handlers import SocketServerHandler
from ..sockets.server.handlers import SocketWrappingSocketServerHandler
from ..sockets.server.handlers import StandardSocketServerHandler
from ..sockets.server.server import SocketServer
from ..sockets.server.threading import ThreadingSocketServerHandler
from .coro.server import CoroHttpServer
from .coro.server import CoroHttpServerSocketHandler
from .handlers import HttpHandler
from .parsing import HttpRequestParser
from .versions import HttpProtocolVersion
from .versions import HttpProtocolVersions


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
