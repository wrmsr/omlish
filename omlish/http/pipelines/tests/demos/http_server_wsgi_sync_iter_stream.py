# ruff: noqa: UP006 UP045
# @omlish-lite
import errno
import hashlib
import socket
import typing as ta

from .....io.pipelines.core import IoPipeline
from .....io.pipelines.core import IoPipelineHandler
from .....io.pipelines.core import IoPipelineHandlerContext
from .....io.pipelines.core import IoPipelineMessages
from .....io.pipelines.drivers.sync import IterSyncSocketIoPipelineDriver
from .....io.streams.types import BytesLike
from .....lite.abstract import Abstract
from .....lite.check import check
from ....headers import HttpHeaders
from ...requests import FullIoPipelineHttpRequest
from ...requests import IoPipelineHttpRequestBodyData
from ...requests import IoPipelineHttpRequestEnd
from ...requests import IoPipelineHttpRequestHead
from ...requests import IoPipelineHttpRequestObject
from ...responses import FullIoPipelineHttpResponse
from ...responses import IoPipelineHttpResponseHead
from ...server.apps.wsgi import WsgiSpec
from ...server.requests import IoPipelineHttpRequestAggregatorDecoder
from ...server.requests import IoPipelineHttpRequestDecoder
from ...server.responses import IoPipelineHttpResponseEncoder


##


class WsgiFeedbackHandler(IoPipelineHandler):
    class Envelope(ta.NamedTuple):
        msg: ta.Any

    def inbound(self, ctx: IoPipelineHandlerContext, msg: ta.Any) -> None:
        if isinstance(msg, IoPipelineHttpRequestObject):
            ctx.feed_out(WsgiFeedbackHandler.Envelope(msg))
            return

        if isinstance(msg, WsgiFeedbackHandler.Envelope):
            ctx.feed_out(msg.msg)
            return

        ctx.feed_in(msg)


def build_wsgi_spec() -> IoPipeline.Spec:
    return IoPipeline.Spec(
        [
            IoPipelineHttpRequestDecoder(),
            IoPipelineHttpRequestAggregatorDecoder(enabled='unless_chunked'),
            IoPipelineHttpResponseEncoder(),
            WsgiFeedbackHandler(),
        ],
    )


class WsgiConnHandler:
    def __init__(
            self,
            spec: WsgiSpec,
            conn: socket.socket,
            addr: ta.Any,
    ) -> None:
        super().__init__()

        self._spec = spec
        self._conn = conn
        self._addr = addr

    _drv: IterSyncSocketIoPipelineDriver

    #

    class _RequestHandler(Abstract):
        def __init__(self, o: 'WsgiConnHandler', head: 'IoPipelineHttpRequestHead') -> None:
            super().__init__()

            self._o = o
            self._head = head

        #

        def _make_environ(self) -> ta.Dict[str, ta.Any]:
            return {
                'REQUEST_METHOD': self._head.method,
                'PATH_INFO': self._head.target,
            }

        #

        def _send_response_full(self, head: IoPipelineHttpResponseHead, body: BytesLike) -> None:
            resp = FullIoPipelineHttpResponse(
                head=head,
                body=body,
            )

            self._o._drv.enqueue(WsgiFeedbackHandler.Envelope(resp))  # noqa

        def _send_response_stream(self, head: IoPipelineHttpResponseHead, body: ta.Iterable[BytesLike]) -> None:
            self._o._drv.enqueue(WsgiFeedbackHandler.Envelope(head))  # noqa

            # for d in body:
            #     if not d:
            #         # FIXME: early break??
            #         continue
            #
            #     self._o._drv.enqueue(WsgiFeedbackHandler.Envelope(IoPipelineHttpResponseBodyData(d)))

            raise NotImplementedError

        #

        def run(self) -> None:
            environ = self._make_environ()

            #

            started_response: ta.Optional[ta.Tuple[ta.Any, ta.Any]] = None

            def start_response(status, headers):  # noqa
                nonlocal started_response
                check.none(started_response)
                started_response = (status, headers)

            #

            ret = self._o._spec.app(environ, start_response)  # noqa

            #

            status, headers = check.not_none(started_response)
            status_code_str, _, status_reason = status.partition(' ')
            status_code = int(status_code_str)
            head = IoPipelineHttpResponseHead(
                status=status_code,
                reason=status_reason,
                headers=HttpHeaders(headers),
            )

            #

            if isinstance(ret, list):
                ret = b''.join(ret)
            if isinstance(ret, bytes):
                self._send_response_full(head, ret)
            elif isinstance(ret, ta.Iterable):
                self._send_response_stream(head, ret)
            else:
                raise TypeError(ret)

            #

            self._o._drv.enqueue(WsgiFeedbackHandler.Envelope(IoPipelineMessages.FinalOutput()))  # noqa

    class _FullRequestHandler(_RequestHandler):
        def __init__(self, o: 'WsgiConnHandler', req: 'FullIoPipelineHttpRequest') -> None:
            super().__init__(o, req.head)

            self._req = req

    class _StreamRequestHandler(_RequestHandler):
        class _RequestInput:
            def __init__(self, o: 'WsgiConnHandler._StreamRequestHandler') -> None:
                super().__init__()

                self._o = o

            def read(self, n: int = 0) -> bytes:
                while (out := self._o._o._drv.next()) is not None:  # noqa
                    if isinstance(out, WsgiFeedbackHandler.Envelope):
                        out = out.msg

                        if isinstance(out, IoPipelineHttpRequestBodyData):
                            return out.data

                        elif isinstance(out, IoPipelineHttpRequestEnd):
                            return b''

                        else:
                            raise TypeError(out)

                    else:
                        raise TypeError(out)

                raise RuntimeError('Pipeline stalled')

        def _make_environ(self) -> ta.Dict[str, ta.Any]:
            return {
                **super()._make_environ(),
                'wsgi.input': self._RequestInput(self),
            }

    #

    def run(self) -> None:
        try:
            self._conn.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        except OSError as e:
            if e.errno != errno.ENOPROTOOPT:
                raise

        self._drv = IterSyncSocketIoPipelineDriver(
            build_wsgi_spec(),
            self._conn,
        )

        while (out := self._drv.next()) is not None:
            if isinstance(out, WsgiFeedbackHandler.Envelope):
                out = out.msg

                if isinstance(out, FullIoPipelineHttpRequest):
                    self._FullRequestHandler(self, out).run()

                elif isinstance(out, IoPipelineHttpRequestHead):
                    self._StreamRequestHandler(self, out).run()

                else:
                    raise TypeError(out)


def serve_wsgi_pipeline(spec: WsgiSpec) -> None:
    def _handle_client(conn: socket.socket, addr: ta.Any) -> None:  # noqa
        WsgiConnHandler(spec, conn, addr).run()

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


def ping_and_sha1_app(environ, start_response):
    method = environ.get('REQUEST_METHOD', '')
    path = environ.get('PATH_INFO', '')

    if method == 'GET' and path == '/ping':
        body = b'pong'
        start_response('200 OK', [
            ('Content-Type', 'text/plain'),
            ('Content-Length', str(len(body))),
        ])
        return [body]

    elif method == 'POST' and path == '/sha1':
        h = hashlib.sha1()  # noqa
        while b := environ['wsgi.input'].read():
            h.update(b)

        body = h.hexdigest().encode('ascii')
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
    wsgi_spec = WsgiSpec(ping_and_sha1_app)

    # serve_wsgi_wsgiref(ping_spec)
    serve_wsgi_pipeline(wsgi_spec)


if __name__ == '__main__':
    _main()
