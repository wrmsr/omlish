# @omlish-lite
# ruff: noqa: UP006 UP007 UP045
import concurrent.futures as cf
import contextlib
import errno
import functools
import socket
import typing as ta

from ....io.pipelines.core import IoPipeline
from ....io.pipelines.drivers.sync import SyncSocketIoPipelineDriver
from ....lite.check import check
from ....sockets.addresses import SocketAndAddress
from ....sockets.bind import CanSocketBinder
from ....sockets.bind import SocketBinder
from ....sockets.handlers.server import SocketHandlerServer
from ....sockets.handlers.simple import ExecutorSocketHandler
from ....sockets.handlers.simple import SocketHandler
from ....sockets.handlers.simple import SocketWrappingSocketHandler
from ....sockets.handlers.simple import StandardSocketHandler
from ....sockets.handlers.ssl import SslErrorHandlingSocketHandler
from ....sockets.handlers.threading import ThreadingSocketHandler
from ...pipelines.servers.requests import IoPipelineHttpRequestAggregatorDecoder
from ...pipelines.servers.requests import IoPipelineHttpRequestDecoder
from ...pipelines.servers.responses import IoPipelineHttpResponseEncoder
from ..handlers import SimpleHttpHandler
from .handlers import SimpleHttpHandlerServerIoPipelineHandler


if ta.TYPE_CHECKING:
    import ssl


##


@contextlib.contextmanager
def make_simple_http_server(
        bind: CanSocketBinder,
        handler: SimpleHttpHandler,
        *,
        # keep_alive: bool = False,  # TODO
        ssl_context: ta.Optional['ssl.SSLContext'] = None,
        ignore_ssl_errors: bool = False,
        executor: ta.Optional[cf.Executor] = None,
        use_threads: bool = False,
        **kwargs: ta.Any,
) -> ta.Iterator[SocketHandlerServer]:
    check.arg(not (executor is not None and use_threads))

    #

    def pipeline_serve(conn: SocketAndAddress) -> None:
        try:
            conn.socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        except OSError as e:
            if e.errno != errno.ENOPROTOOPT:
                raise

        drv = SyncSocketIoPipelineDriver(
            IoPipeline.Spec(
                [
                    IoPipelineHttpRequestDecoder(),
                    IoPipelineHttpRequestAggregatorDecoder(),
                    IoPipelineHttpResponseEncoder(),
                    SimpleHttpHandlerServerIoPipelineHandler(handler),
                ],
                metadata=[
                    SimpleHttpHandlerServerIoPipelineHandler.SocketAndAddressMetadata.of(conn),
                ],
            ),
            conn.socket,
        )

        drv.loop_until_done()

    #

    with contextlib.ExitStack() as es:
        socket_handler: SocketHandler = pipeline_serve

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
