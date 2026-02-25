# ruff: noqa: UP006 UP045
# @omlish-lite
import asyncio
import dataclasses as dc
import typing as ta

from omlish.http.headers import HttpHeaders
from omlish.lite.check import check

from ....core import ChannelPipelineHandler
from ....core import ChannelPipelineHandlerContext
from ....core import ChannelPipelineMessages
from ....core import PipelineChannel
from ....drivers.asyncio import SimpleAsyncioStreamPipelineChannelDriver
from ....flow.types import ChannelPipelineFlowMessages
from ....handlers.flatmap import FlatMapChannelPipelineHandlers
from ...requests import FullPipelineHttpRequest
from ...responses import FullPipelineHttpResponse
from ...responses import PipelineHttpResponseHead
from ...server.requests import PipelineHttpRequestBodyAggregator
from ...server.requests import PipelineHttpRequestHeadDecoder
from ...server.responses import PipelineHttpResponseEncoder


##


@dc.dataclass(frozen=True)
class WsgiSpec:
    app: ta.Any
    host: str = '127.0.0.1'
    port: int = 8087


##


class WsgiHandler(ChannelPipelineHandler):
    def __init__(self, app: ta.Any) -> None:
        super().__init__()

        self._app = app

    def inbound(self, ctx: ChannelPipelineHandlerContext, msg: ta.Any) -> None:
        if not isinstance(msg, FullPipelineHttpRequest):
            ctx.feed_in(msg)
            return

        #

        environ = {
            'REQUEST_METHOD': msg.head.method,
            'PATH_INFO': msg.head.target,
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

        resp = FullPipelineHttpResponse(
            head=PipelineHttpResponseHead(
                status=status_code,
                reason=status_reason,
                headers=HttpHeaders(headers),
            ),
            body=body,
        )

        #

        ctx.feed_out(resp)
        ctx.feed_out(ChannelPipelineMessages.FinalOutput())


def build_wsgi_channel(app: ta.Any) -> PipelineChannel.Spec:
    return PipelineChannel.Spec([
        PipelineHttpRequestHeadDecoder(),
        PipelineHttpRequestBodyAggregator(),
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


async def a_serve_wsgi_pipeline(spec: 'WsgiSpec') -> None:
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


def serve_wsgi_pipeline(spec: 'WsgiSpec') -> None:
    asyncio.run(a_serve_wsgi_pipeline(spec))


##


def serve_wsgi_wsgiref(spec: 'WsgiSpec') -> None:
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
