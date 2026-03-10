# ruff: noqa: UP006 UP045
# @omlish-lite
import errno
import socket
import typing as ta

from .....io.pipelines.core import IoPipeline
from .....io.pipelines.drivers.sync import SyncSocketIoPipelineDriver
from ...server.apps.wsgi import WsgiHandler
from ...server.apps.wsgi import WsgiSpec
from ...server.requests import IoPipelineHttpRequestAggregatorDecoder
from ...server.requests import IoPipelineHttpRequestDecoder
from ...server.responses import IoPipelineHttpResponseEncoder


##


def build_wsgi_spec(app: ta.Any) -> IoPipeline.Spec:
    return IoPipeline.Spec(
        [
            IoPipelineHttpRequestDecoder(),
            IoPipelineHttpRequestAggregatorDecoder(),
            IoPipelineHttpResponseEncoder(),
            WsgiHandler(app),
        ],
    )


def serve_wsgi_pipeline(spec: WsgiSpec) -> None:
    def _handle_client(conn: socket.socket, addr: ta.Any) -> None:  # noqa
        try:
            conn.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        except OSError as e:
            if e.errno != errno.ENOPROTOOPT:
                raise

        drv = SyncSocketIoPipelineDriver(
            build_wsgi_spec(spec.app),
            conn,
        )

        drv.loop_until_done()

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

    # serve_wsgi_wsgiref(ping_spec)
    serve_wsgi_pipeline(ping_spec)


if __name__ == '__main__':
    _main()
