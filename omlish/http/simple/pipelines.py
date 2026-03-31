# @omlish-lite
# ruff: noqa: UP006 UP007 UP045
import concurrent.futures as cf
import contextlib
import dataclasses as dc
import errno
import functools
import socket
import typing as ta

from ...io.pipelines.core import IoPipeline
from ...io.pipelines.core import IoPipelineHandler
from ...io.pipelines.core import IoPipelineHandlerContext
from ...io.pipelines.core import IoPipelineMessages
from ...io.pipelines.core import IoPipelineMetadata
from ...io.pipelines.drivers.sync import SyncSocketIoPipelineDriver
from ...io.pipelines.flow.types import IoPipelineFlow
from ...io.pipelines.flow.types import IoPipelineFlowMessages
from ...io.streams.utils import ByteStreamBuffers
from ...lite.check import check
from ...sockets.addresses import SocketAndAddress
from ...sockets.bind import CanSocketBinder
from ...sockets.bind import SocketBinder
from ...sockets.handlers.server import SocketHandlerServer
from ...sockets.handlers.simple import ExecutorSocketHandler
from ...sockets.handlers.simple import SocketHandler
from ...sockets.handlers.simple import SocketWrappingSocketHandler
from ...sockets.handlers.simple import StandardSocketHandler
from ...sockets.handlers.ssl import SslErrorHandlingSocketHandler
from ...sockets.handlers.threading import ThreadingSocketHandler
from ..headers import HttpHeaders
from ..pipelines.requests import FullIoPipelineHttpRequest
from ..pipelines.responses import FullIoPipelineHttpResponse
from ..pipelines.responses import IoPipelineHttpResponseBodyData
from ..pipelines.responses import IoPipelineHttpResponseEnd
from ..pipelines.servers.requests import IoPipelineHttpRequestAggregatorDecoder
from ..pipelines.servers.requests import IoPipelineHttpRequestDecoder
from ..pipelines.servers.responses import IoPipelineHttpResponseEncoder
from ..pipelines.servers.responses import IoPipelineHttpResponseHead
from .handlers import SimpleHttpHandler
from .handlers import SimpleHttpHandlerRequest
from .handlers import SimpleHttpHandlerResponseStreamedData


if ta.TYPE_CHECKING:
    import ssl


##


class SimpleHttpHandlerServerIoPipelineHandler(IoPipelineHandler):
    def __init__(self, handler: SimpleHttpHandler) -> None:
        super().__init__()

        self._handler = handler

    @dc.dataclass(frozen=True)
    class SocketAndAddressMetadata(IoPipelineMetadata):
        v: SocketAndAddress

    def inbound(self, ctx: IoPipelineHandlerContext, msg: ta.Any) -> None:
        if isinstance(msg, IoPipelineMessages.InitialInput):
            ctx.feed_in(msg)

            if not IoPipelineFlow.is_auto_read(ctx):
                ctx.feed_out(IoPipelineFlowMessages.ReadyForInput())

            return

        if not isinstance(msg, FullIoPipelineHttpRequest):
            ctx.feed_in(msg)
            return

        #

        handler_req = SimpleHttpHandlerRequest(
            client_address=ctx.pipeline.metadata[SimpleHttpHandlerServerIoPipelineHandler.SocketAndAddressMetadata],
            method=msg.head.method,
            path=msg.head.target,
            headers=check.not_none(msg.head.parsed).headers,
            data=ByteStreamBuffers.to_bytes(msg.body),
        )

        handler_resp = self._handler(handler_req)

        try:
            headers = HttpHeaders(handler_resp.headers or {})
            new_headers: ta.Dict[str, str] = {}

            data = handler_resp.data

            if data is not None and headers.lower.get('content-length') is None:
                cl: ta.Optional[int]
                if isinstance(data, bytes):
                    cl = len(data)
                elif isinstance(data, SimpleHttpHandlerResponseStreamedData):
                    cl = data.length
                else:
                    raise TypeError(data)
                if cl is not None:
                    new_headers['Content-Length'] = str(cl)

            # if headers.lower.get('connect') is None:
            #     if h.key.lower() != 'connection':
            #         return None
            #     elif h.value.lower() == 'close':
            #         return True
            #     elif h.value.lower() == 'keep-alive':
            #         return False
            #     else:
            #         return None
            new_headers['Connection'] = 'close'  # TODO: handler_resp.close_connection

            if new_headers:
                headers = HttpHeaders({**headers, **new_headers})

            head = IoPipelineHttpResponseHead(
                status=handler_resp.status,
                reason=IoPipelineHttpResponseHead.get_reason_phrase(handler_resp.status),
                headers=headers,
            )

            if isinstance(data, (bytes, type(None))):
                resp = FullIoPipelineHttpResponse(
                    head=head,
                    body=data or b'',
                )

                ctx.feed_out(resp)

            elif isinstance(data, SimpleHttpHandlerResponseStreamedData):
                ctx.feed_out(head)

                for b in data.iter:
                    ctx.feed_out(IoPipelineHttpResponseBodyData(b))

                ctx.feed_out(IoPipelineHttpResponseEnd())

            else:
                raise TypeError(data)

            ctx.feed_out(IoPipelineMessages.FinalOutput())

        finally:
            handler_resp.close()


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
                    SimpleHttpHandlerServerIoPipelineHandler.SocketAndAddressMetadata(conn),
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
