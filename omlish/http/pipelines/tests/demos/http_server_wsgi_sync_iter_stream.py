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
from .....lite.check import check
from ....headers import HttpHeaders
from ...requests import FullIoPipelineHttpRequest
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
            IoPipelineHttpRequestAggregatorDecoder(),
            IoPipelineHttpResponseEncoder(),
            WsgiFeedbackHandler(),
        ],
    )


def serve_wsgi_pipeline(spec: WsgiSpec) -> None:
    def _handle_client(conn: socket.socket, addr: ta.Any) -> None:  # noqa
        try:
            conn.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        except OSError as e:
            if e.errno != errno.ENOPROTOOPT:
                raise

        drv = IterSyncSocketIoPipelineDriver(
            build_wsgi_spec(),
            conn,
        )

        req: ta.Optional[FullIoPipelineHttpRequest] = None

        started_response: ta.Optional[ta.Tuple[ta.Any, ta.Any]] = None

        def start_response(status, headers):  # noqa
            nonlocal started_response
            check.none(started_response)
            started_response = (status, headers)

        while (out := drv.next()) is not None:
            if isinstance(out, WsgiFeedbackHandler.Envelope):
                out = out.msg

                if isinstance(out, FullIoPipelineHttpRequest):
                    check.none(req)
                    req = out

                    environ = {
                        'REQUEST_METHOD': req.head.method,
                        'PATH_INFO': req.head.target,
                    }

                    #

                    ret = spec.app(environ, start_response)

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

                    resp = FullIoPipelineHttpResponse(
                        head=IoPipelineHttpResponseHead(
                            status=status_code,
                            reason=status_reason,
                            headers=HttpHeaders(headers),
                        ),
                        body=body,
                    )

                    #

                    drv.enqueue(
                        WsgiFeedbackHandler.Envelope(resp),
                        WsgiFeedbackHandler.Envelope(IoPipelineMessages.FinalOutput()),
                    )

                else:
                    raise TypeError(out)

            else:
                raise TypeError(out)

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
