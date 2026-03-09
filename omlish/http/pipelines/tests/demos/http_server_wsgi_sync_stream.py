# ruff: noqa: UP006 UP045
# @omlish-lite
import collections
import errno
import hashlib
import socket
import typing as ta

from .....io.pipelines.core import IoPipeline
from .....io.pipelines.core import IoPipelineHandler
from .....io.pipelines.core import IoPipelineHandlerContext
from .....io.pipelines.core import IoPipelineMessages
from .....io.pipelines.drivers.metadata import DriverIoPipelineMetadata
from .....io.pipelines.drivers.sync import LoopSyncSocketIoPipelineDriver
from .....io.pipelines.flow.stub import StubIoPipelineFlow
from .....io.pipelines.flow.types import IoPipelineFlow
from .....io.pipelines.flow.types import IoPipelineFlowMessages
from .....lite.check import check
from ....headers import HttpHeaders
from ...requests import IoPipelineHttpRequestContentChunkData
from ...requests import IoPipelineHttpRequestEnd
from ...requests import IoPipelineHttpRequestHead
from ...responses import IoFullPipelineHttpResponse
from ...responses import IoPipelineHttpResponseHead
from ...server.apps.wsgi import WsgiSpec
from ...server.requests import IoPipelineHttpRequestDecoder
from ...server.responses import IoPipelineHttpResponseEncoder


##


class StreamWsgiOuterHandler(IoPipelineHandler):
    def outbound(self, ctx: IoPipelineHandlerContext, msg: ta.Any) -> None:
        if isinstance(msg, IoPipelineFlowMessages.ReadyForInput):
            driver = check.isinstance(ctx.pipeline.metadata[DriverIoPipelineMetadata].driver, LoopSyncSocketIoPipelineDriver)  # noqa
            b = driver._sock.recv(driver._config.read_chunk_size)  # noqa
            driver._pipeline_.feed_in(b, IoPipelineFlowMessages.FlushInput())  # noqa
            return

        ctx.feed_out(msg)


class StreamWsgiInnerHandler(IoPipelineHandler):
    def __init__(self, app: ta.Any) -> None:
        super().__init__()

        self._app = app

        self._inbound_queue: ta.Optional['collections.deque[ta.Any]'] = None  # noqa

    class _Input:
        def __init__(self, h: 'StreamWsgiInnerHandler', ctx: IoPipelineHandlerContext) -> None:
            self._h = h
            self._ctx = ctx

        def read(self, n: int = 0) -> bytes:
            if (iq := self._h._inbound_queue) is not None:  # noqa
                if len(iq) > 0:
                    msg = iq.popleft()

                    if isinstance(msg, IoPipelineHttpRequestContentChunkData):
                        return msg.data
                    elif isinstance(msg, IoPipelineHttpRequestEnd):
                        return b''
                    else:
                        raise TypeError(msg)

            else:
                self._h._inbound_queue = iq = collections.deque()  # noqa

            self._ctx.feed_out(IoPipelineFlowMessages.ReadyForInput())

            msg = iq.popleft()

            if isinstance(msg, IoPipelineHttpRequestContentChunkData):
                return msg.data
            elif isinstance(msg, IoPipelineHttpRequestEnd):
                return b''
            else:
                raise TypeError(msg)

    def _on_inbound_request_head(self, ctx: IoPipelineHandlerContext, msg: IoPipelineHttpRequestHead) -> None:
        environ = {
            'REQUEST_METHOD': msg.method,
            'PATH_INFO': msg.target,
            'wsgi.input': self._Input(self, ctx),
        }

        #

        started_response: ta.Optional[ta.Tuple[ta.Any, ta.Any]] = None

        def start_response(status, headers):  # noqa
            nonlocal started_response
            check.none(started_response)
            started_response = (status, headers)

        #

        ret = self._app(environ, start_response)

        #

        status, headers = check.not_none(started_response)
        status_code_str, _, status_reason = status.partition(' ')
        status_code = int(status_code_str)

        #

        body: bytes
        if isinstance(ret, bytes):
            body = ret
        elif isinstance(ret, list):
            body = b''.join(ret)
        else:
            raise TypeError(ret)

        #

        resp = IoFullPipelineHttpResponse(
            head=IoPipelineHttpResponseHead(
                status=status_code,
                reason=status_reason,
                headers=HttpHeaders(headers),
            ),
            body=body,
        )

        #

        ctx.feed_out(resp)
        ctx.feed_out(IoPipelineMessages.FinalOutput())

    def inbound(self, ctx: IoPipelineHandlerContext, msg: ta.Any) -> None:
        if isinstance(msg, IoPipelineMessages.InitialInput):
            ctx.feed_in(msg)

            if not IoPipelineFlow.is_auto_read_context(ctx):
                ctx.feed_out(IoPipelineFlowMessages.ReadyForInput())

            return

        if isinstance(msg, (IoPipelineHttpRequestContentChunkData, IoPipelineHttpRequestEnd)):
            check.not_none(self._inbound_queue).append(msg)
            return

        if isinstance(msg, IoPipelineHttpRequestHead):
            check.none(self._inbound_queue)
            self._on_inbound_request_head(ctx, msg)
            return

        ctx.feed_in(msg)


##


def build_wsgi_spec(app: ta.Any) -> IoPipeline.Spec:
    return IoPipeline.Spec(
        [
            StreamWsgiOuterHandler(),
            IoPipelineHttpRequestDecoder(),
            IoPipelineHttpResponseEncoder(),
            StreamWsgiInnerHandler(app),
        ],
        services=[
            StubIoPipelineFlow(auto_read=False),
        ],
    )


def serve_wsgi_pipeline(spec: WsgiSpec) -> None:
    def _handle_client(conn: socket.socket, addr: ta.Any) -> None:  # noqa
        try:
            conn.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        except OSError as e:
            if e.errno != errno.ENOPROTOOPT:
                raise

        drv = LoopSyncSocketIoPipelineDriver(
            build_wsgi_spec(spec.app),
            conn,
        )

        drv.run()

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((spec.host, spec.port))
        server.listen()

        while True:
            conn, addr = server.accept()
            _handle_client(conn, addr)


##


def serve_wsgi_wsgiref(spec: WsgiSpec) -> None:
    from wsgiref.simple_server import make_server  # noqa

    httpd = make_server(spec.host, spec.port, spec.app)
    httpd.serve_forever()


##


def sha1_app(environ, start_response):
    method = environ.get('REQUEST_METHOD', '')
    path = environ.get('PATH_INFO', '')

    if not (method.upper() == 'POST' and path.split('?', 1)[0] == '/sha1'):
        body = b'not found'
        start_response('404 Not Found', [
            ('Content-Type', 'text/plain'),
            ('Content-Length', str(len(body))),
        ])
        return [body]

    h = hashlib.sha1()  # noqa
    while b := environ['wsgi.input'].read():
        h.update(b)

    body = h.hexdigest().encode('ascii')
    start_response('200 OK', [
        ('Content-Type', 'text/plain'),
        ('Content-Length', str(len(body))),
    ])
    return [body]


##


def _main() -> None:
    ping_spec = WsgiSpec(sha1_app)

    # serve_wsgi_wsgiref(ping_spec)
    serve_wsgi_pipeline(ping_spec)


if __name__ == '__main__':
    _main()
