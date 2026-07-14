# ruff: noqa: UP006 UP045
# @om-lite
import asyncio
import typing as ta

from ......io.pipelines.core import IoPipeline
from ......io.pipelines.drivers.asyncio import PollAsyncioStreamIoPipelineDriver
from ...apps.wsgi import IoPipelineWsgiSpec
from ...apps.wsgi import WsgiIoPipelineHandler
from ...requests import IoPipelineHttpRequestAggregatorDecoder
from ...requests import IoPipelineHttpRequestDecoder
from ...responses import IoPipelineHttpResponseEncoder


##


def build_wsgi_spec(app: ta.Any) -> IoPipeline.Spec:
    return IoPipeline.Spec([
        IoPipelineHttpRequestDecoder(),
        IoPipelineHttpRequestAggregatorDecoder(),
        IoPipelineHttpResponseEncoder(),
        WsgiIoPipelineHandler(app),
    ])


async def a_serve_wsgi_pipeline(spec: IoPipelineWsgiSpec) -> None:
    async def _handle_client(reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
        drv = PollAsyncioStreamIoPipelineDriver(
            build_wsgi_spec(spec.app),
            reader,
            writer,
        )

        await drv.loop_until_done()

    srv = await asyncio.start_server(_handle_client, spec.host, spec.port)
    async with srv:
        await srv.serve_forever()


def serve_wsgi_pipeline(spec: IoPipelineWsgiSpec) -> None:
    asyncio.run(a_serve_wsgi_pipeline(spec))


##


def serve_wsgi_wsgiref(spec: IoPipelineWsgiSpec) -> None:
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
    ping_spec = IoPipelineWsgiSpec(ping_app)

    # serve_wsgi_wsgiref(ping_spec)
    serve_wsgi_pipeline(ping_spec)


if __name__ == '__main__':
    _main()
