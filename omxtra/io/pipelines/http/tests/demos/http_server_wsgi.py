# ruff: noqa: UP006 UP045
# @omlish-lite
import asyncio
import typing as ta

from ....core import ChannelPipelineMessages
from ....core import PipelineChannel
from ....drivers.asyncio import SimpleAsyncioStreamPipelineChannelDriver
from ....flow.types import ChannelPipelineFlowMessages
from ....handlers.flatmap import FlatMapChannelPipelineHandlers
from ...server.apps.wsgi import WsgiHandler
from ...server.apps.wsgi import WsgiSpec
from ...server.requests import PipelineHttpRequestAggregatorDecoder
from ...server.requests import PipelineHttpRequestDecoder
from ...server.responses import PipelineHttpResponseEncoder


##


def build_wsgi_channel(app: ta.Any) -> PipelineChannel.Spec:
    return PipelineChannel.Spec([
        PipelineHttpRequestDecoder(),
        PipelineHttpRequestAggregatorDecoder(),
        PipelineHttpResponseEncoder(),
        WsgiHandler(app),
        FlatMapChannelPipelineHandlers.drop(
            'inbound',
            filter_type=(
                ChannelPipelineMessages.FinalInput,
                ChannelPipelineFlowMessages.FlushInput,
            ),
        ),
    ])


async def a_serve_wsgi_pipeline(spec: WsgiSpec) -> None:
    async def _handle_client(reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
        drv = SimpleAsyncioStreamPipelineChannelDriver(
            build_wsgi_channel(spec.app),
            reader,
            writer,
        )

        await drv.run()

    srv = await asyncio.start_server(_handle_client, spec.host, spec.port)
    async with srv:
        await srv.serve_forever()


def serve_wsgi_pipeline(spec: WsgiSpec) -> None:
    asyncio.run(a_serve_wsgi_pipeline(spec))


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
