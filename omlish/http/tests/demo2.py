# ruff: noqa: UP006 UP007 UP045
"""
Todo:
 - x/http/htt/omni/socketbinding.py

socat TCP-LISTEN:8000,fork UNIX-CONNECT:foo.sock
"""
import concurrent.futures as cf
import contextlib
import dataclasses as dc
import errno
import functools
import socket
import typing as ta

from ... import check
from ...io.pipelines.core import IoPipeline
from ...io.pipelines.core import IoPipelineHandler
from ...io.pipelines.core import IoPipelineHandlerContext
from ...io.pipelines.core import IoPipelineMessages
from ...io.pipelines.core import IoPipelineMetadata
from ...io.pipelines.drivers.sync import SyncSocketIoPipelineDriver
from ...io.pipelines.flow.types import IoPipelineFlow
from ...io.pipelines.flow.types import IoPipelineFlowMessages
from ...io.streams.utils import ByteStreamBuffers
from ...sockets.addresses import SocketAndAddress
from ...sockets.bind import CanSocketBinder
from ...sockets.bind import SocketBinder
from ...sockets.handlers.server import SocketServer
from ...sockets.handlers.simple import ExecutorSocketHandler
from ...sockets.handlers.simple import SocketHandler
from ...sockets.handlers.simple import SocketWrappingSocketHandler
from ...sockets.handlers.simple import StandardSocketHandler
from ...sockets.handlers.ssl import SslErrorHandlingSocketHandler
from ...sockets.handlers.threading import ThreadingSocketHandler
from ..coro.server.server import UnsupportedMethodHttpHandlerError
from ..handlers import HttpHandler
from ..handlers import HttpHandlerRequest
from ..handlers import HttpHandlerResponse
from ..handlers import HttpHandlerResponseStreamedData
from ..headers import HttpHeaders
from ..pipelines.requests import FullIoPipelineHttpRequest
from ..pipelines.responses import FullIoPipelineHttpResponse
from ..pipelines.responses import IoPipelineHttpResponseHead
from ..pipelines.servers.requests import IoPipelineHttpRequestAggregatorDecoder
from ..pipelines.servers.requests import IoPipelineHttpRequestDecoder
from ..pipelines.servers.responses import IoPipelineHttpResponseEncoder


if ta.TYPE_CHECKING:
    import ssl


##


@dc.dataclass(frozen=True)
class SocketAndAddressIoPipelineMetadata(IoPipelineMetadata):
    v: SocketAndAddress


class HttpHandlerHandler(IoPipelineHandler):
    def __init__(self, handler: HttpHandler) -> None:
        super().__init__()

        self._handler = handler

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

        handler_req = HttpHandlerRequest(
            client_address=ctx.pipeline.metadata[SocketAndAddressIoPipelineMetadata],
            method=msg.head.method,
            path=msg.head.target,
            headers=check.not_none(msg.head.parsed).headers,
            data=ByteStreamBuffers.to_bytes(msg.body),
        )

        handler_resp = self._handler(handler_req)

        # TODO: handler_resp.close_connection

        resp = FullIoPipelineHttpResponse(
            head=IoPipelineHttpResponseHead(
                status=handler_resp.status,
                reason=IoPipelineHttpResponseHead.get_reason_phrase(handler_resp.status),
                headers=HttpHeaders(handler_resp.headers or {}),
            ),
            body=check.isinstance(handler_resp.data or b'', bytes),
        )

        #

        ctx.feed_out(resp)
        ctx.feed_out(IoPipelineMessages.FinalOutput())


def pipeline_serve(
        conn: SocketAndAddress,
        *,
        handler: HttpHandler,
) -> None:
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
                HttpHandlerHandler(handler),
            ],
            metadata=[
                SocketAndAddressIoPipelineMetadata(conn),
            ],
        ),
        conn.socket,
    )

    drv.loop_until_done()


@contextlib.contextmanager
def make_simple_http_server(
        bind: CanSocketBinder,
        handler: HttpHandler,
        *,
        # keep_alive: bool = False,
        ssl_context: ta.Optional['ssl.SSLContext'] = None,
        ignore_ssl_errors: bool = False,
        executor: ta.Optional[cf.Executor] = None,
        use_threads: bool = False,
        **kwargs: ta.Any,
) -> ta.Iterator[SocketServer]:
    check.arg(not (executor is not None and use_threads))

    #

    with contextlib.ExitStack() as es:
        socket_handler: SocketHandler = functools.partial(
            pipeline_serve,
            handler=handler,
            # keep_alive=keep_alive,
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

        server = es.enter_context(SocketServer(
            SocketBinder.of(bind),
            socket_handler,
            **kwargs,
        ))

        yield server


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
    data = resp.encode('utf-8')

    resp_data: ta.Any
    if 'stream' in req.headers:
        def stream_data():
            for b in data:
                yield bytes([b])

        resp_data = HttpHandlerResponseStreamedData(
            stream_data(),
            len(data),
        )

    else:
        resp_data = data

    return HttpHandlerResponse(
        200,
        data=resp_data,
    )


##


def _main() -> None:
    default_port = 8000

    #

    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('port_or_unix_socket', default=str(default_port), nargs='?')
    args = parser.parse_args()

    #

    port_or_unix_socket = check.non_empty_str(args.port_or_unix_socket)
    bind: ta.Any
    try:
        port = int(port_or_unix_socket)
    except ValueError:
        bind = check.non_empty_str(port_or_unix_socket)
    else:
        bind = port

    #

    with make_simple_http_server(
        bind,
        say_hi_handler,
        use_threads=True,
    ) as server:
        server.run()


if __name__ == '__main__':
    _main()
