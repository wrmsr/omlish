# ruff: noqa: UP006 UP045
# @omlish-lite
import concurrent.futures as cf
import contextlib
import errno
import socket
import typing as ta

from ......io.pipelines.bytes.buffers import OutboundBytesBufferIoPipelineHandler
from ......io.pipelines.core import IoPipeline
from ......io.pipelines.core import IoPipelineHandler
from ......io.pipelines.drivers.sync import SyncSocketIoPipelineDriver
from ......io.pipelines.flow.stub import StubIoPipelineFlowService
from ......io.pipelines.handlers.logs import LoggingIoPipelineHandler
from ......io.pipelines.ssl.handlers import SslIoPipelineHandler
from ......lite.check import check
from ......sockets.addresses import SocketAndAddress
from ......sockets.bind import SocketBinder
from ......sockets.handlers.server import SocketHandlerServer
from ......sockets.handlers.simple import ExecutorSocketHandler
from ......sockets.handlers.simple import SocketHandler
from ......sockets.handlers.simple import StandardSocketHandler
from ......sockets.handlers.threading import ThreadingSocketHandler
from ......sockets.handlers.types import SocketHandler_
from ...apps.wsgi import WsgiHandler
from ...apps.wsgi import WsgiSpec
from ...requests import IoPipelineHttpRequestAggregatorDecoder
from ...requests import IoPipelineHttpRequestDecoder
from ...responses import IoPipelineHttpResponseEncoder


##


def build_wsgi_spec(
        app: ta.Any,
        *,
        outermost_handlers: ta.Optional[ta.Sequence[IoPipelineHandler]] = None,
        innermost_handlers: ta.Optional[ta.Sequence[IoPipelineHandler]] = None,

        with_logging: bool = False,

        with_ssl: bool = False,
        ssl_kwargs: ta.Optional[ta.Mapping[str, ta.Any]] = None,

        with_flow: bool = False,
        flow_auto_read: bool = False,

        raise_immediately: bool = False,
) -> IoPipeline.Spec:
    return IoPipeline.Spec(
        [
            *(outermost_handlers or []),

            *([LoggingIoPipelineHandler()] if with_logging else []),

            *([OutboundBytesBufferIoPipelineHandler()] if with_flow else []),

            *([SslIoPipelineHandler(**(ssl_kwargs or {}))] if with_ssl else []),

            IoPipelineHttpRequestDecoder(),
            IoPipelineHttpRequestAggregatorDecoder(),

            IoPipelineHttpResponseEncoder(),

            WsgiHandler(app),

            *(innermost_handlers or []),
        ],

        config=IoPipeline.Config.DEFAULT.update(
            raise_immediately=raise_immediately,
        ),

        services=[
            *([StubIoPipelineFlowService(auto_read=flow_auto_read)] if with_flow else []),
        ],
    )


class PipelineHttpServerSocketHandler(SocketHandler_):
    def __init__(self, spec: WsgiSpec) -> None:
        super().__init__()

        self._spec = spec

    def __call__(self, conn: SocketAndAddress) -> None:
        try:
            conn.socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        except OSError as e:
            if e.errno != errno.ENOPROTOOPT:
                raise

        drv = SyncSocketIoPipelineDriver(
            build_wsgi_spec(
                self._spec.app,
                with_flow=True,
            ),
            conn.socket,
        )

        drv.loop_until_done()


##


@contextlib.contextmanager
def make_simple_http_server(
        spec: WsgiSpec,
        *,
        executor: ta.Optional[cf.Executor] = None,
        use_threads: bool = False,
        **kwargs: ta.Any,
) -> ta.Iterator[SocketHandlerServer]:
    check.arg(not (executor is not None and use_threads))

    #

    with contextlib.ExitStack() as es:
        socket_handler: SocketHandler = PipelineHttpServerSocketHandler(
            spec,
        )

        #

        socket_handler = StandardSocketHandler(
            socket_handler,
            enable_nodelay=True,
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
            SocketBinder.of((spec.host, spec.port)),
            socket_handler,
            **kwargs,
        ))

        yield server


def serve_wsgi_pipeline(spec: WsgiSpec) -> None:
    with make_simple_http_server(
            spec,
            use_threads=True,
    ) as server:
        server.run()


##


def ping_app(environ, start_response):
    method = environ.get('REQUEST_METHOD', '')
    path = environ.get('PATH_INFO', '')

    if method == 'GET' and path == '/ping':
        body = b'pong'
        start_response('200 OK', [
            ('Content-Type', 'text/plain'),
            ('Content-Length', str(len(body))),
        ])
        return [body]
    else:
        body = b'not found'
        start_response('404 Not Found', [
            ('Content-Type', 'text/plain'),
            ('Content-Length', str(len(body))),
        ])
        return [body]


##


def _main() -> None:
    ping_spec = WsgiSpec(ping_app)

    serve_wsgi_pipeline(ping_spec)


if __name__ == '__main__':
    _main()
