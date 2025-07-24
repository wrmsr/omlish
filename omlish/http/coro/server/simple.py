# ruff: noqa: UP006 UP007 UP045
# @omlish-lite
"""
TODO:
 - logging
"""
import concurrent.futures as cf
import contextlib
import functools
import typing as ta

from ....lite.check import check
from ....sockets.addresses import SocketAndAddress
from ....sockets.bind import CanSocketBinder
from ....sockets.bind import SocketBinder
from ....sockets.server.handlers import ExecutorSocketServerHandler
from ....sockets.server.handlers import SocketHandlerSocketServerHandler
from ....sockets.server.handlers import SocketServerHandler
from ....sockets.server.handlers import SocketWrappingSocketServerHandler
from ....sockets.server.handlers import StandardSocketServerHandler
from ....sockets.server.server import SocketServer
from ....sockets.server.ssl import SslErrorHandlingSocketServerHandler
from ....sockets.server.threading import ThreadingSocketServerHandler
from ...handlers import HttpHandler
from ...parsing import HttpRequestParser
from ...versions import HttpProtocolVersion
from ...versions import HttpProtocolVersions
from .server import CoroHttpServer
from .sockets import CoroHttpServerSocketHandler


if ta.TYPE_CHECKING:
    import ssl


##


@contextlib.contextmanager
def make_simple_http_server(
        bind: CanSocketBinder,
        handler: HttpHandler,
        *,
        server_version: HttpProtocolVersion = HttpProtocolVersions.HTTP_1_1,
        keep_alive: bool = False,
        ssl_context: ta.Optional['ssl.SSLContext'] = None,
        ignore_ssl_errors: bool = False,
        executor: ta.Optional[cf.Executor] = None,
        use_threads: bool = False,
        **kwargs: ta.Any,
) -> ta.Iterator[SocketServer]:
    check.arg(not (executor is not None and use_threads))

    #

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
            keep_alive=keep_alive,
        )

        #

        server_handler: SocketServerHandler = SocketHandlerSocketServerHandler(
            socket_handler,
        )

        #

        if ssl_context is not None:
            server_handler = SocketWrappingSocketServerHandler(
                server_handler,
                SocketAndAddress.socket_wrapper(functools.partial(
                    ssl_context.wrap_socket,
                    server_side=True,
                )),
            )

        if ignore_ssl_errors:
            server_handler = SslErrorHandlingSocketServerHandler(
                server_handler,
            )

        #

        server_handler = StandardSocketServerHandler(
            server_handler,
        )

        #

        if executor is not None:
            server_handler = ExecutorSocketServerHandler(
                server_handler,
                executor,
            )

        elif use_threads:
            server_handler = es.enter_context(ThreadingSocketServerHandler(
                server_handler,
            ))

        #

        server = es.enter_context(SocketServer(
            SocketBinder.of(bind),
            server_handler,
            **kwargs,
        ))

        yield server
