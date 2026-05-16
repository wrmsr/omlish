# ruff: noqa: UP006 UP007 UP037 UP045
# @omlish-lite
"""
TODO:
 - logging
"""
import concurrent.futures as cf
import contextlib
import functools
import typing as ta

from omlish.http.simple.handlers import SimpleHttpHandler
from omlish.lite.check import check
from omlish.sockets.addresses import SocketAndAddress
from omlish.sockets.bind import CanSocketBinder
from omlish.sockets.bind import SocketBinder
from omlish.sockets.handlers.server import SocketHandlerServer
from omlish.sockets.handlers.simple import ExecutorSocketHandler
from omlish.sockets.handlers.simple import SocketHandler
from omlish.sockets.handlers.simple import SocketWrappingSocketHandler
from omlish.sockets.handlers.simple import StandardSocketHandler
from omlish.sockets.handlers.ssl import SslErrorHandlingSocketHandler
from omlish.sockets.handlers.threading import ThreadingSocketHandler

from .server import CoroHttpServer
from .sockets import CoroHttpServerSocketHandler


if ta.TYPE_CHECKING:
    import ssl


##


@contextlib.contextmanager
def make_simple_http_server(
        bind: CanSocketBinder,
        handler: SimpleHttpHandler,
        *,
        keep_alive: bool = False,
        ssl_context: ta.Optional['ssl.SSLContext'] = None,
        ignore_ssl_errors: bool = False,
        executor: ta.Optional[cf.Executor] = None,
        use_threads: bool = False,
        **kwargs: ta.Any,
) -> ta.Iterator[SocketHandlerServer]:
    check.arg(not (executor is not None and use_threads))

    #

    with contextlib.ExitStack() as es:
        server_factory = functools.partial(
            CoroHttpServer,
            handler=handler,
        )

        socket_handler: SocketHandler = CoroHttpServerSocketHandler(
            server_factory,
            keep_alive=keep_alive,
        )

        #

        if ssl_context is not None:
            socket_handler = SocketWrappingSocketHandler(
                socket_handler,
                SocketAndAddress.socket_wrapper(functools.partial(
                    ssl_context.wrap_socket,
                    server_side=True,
                )),
            )

        if ignore_ssl_errors:
            socket_handler = SslErrorHandlingSocketHandler(
                socket_handler,
            )

        #

        socket_handler = StandardSocketHandler(
            socket_handler,
        )

        #

        if executor is not None:
            socket_handler = ExecutorSocketHandler(
                socket_handler,
                executor,
            )

        elif use_threads:
            socket_handler = es.enter_context(ThreadingSocketHandler(
                socket_handler,
            ))

        #

        server = es.enter_context(SocketHandlerServer(
            SocketBinder.of(bind),
            socket_handler,
            **kwargs,
        ))

        yield server
