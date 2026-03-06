# ruff: noqa: UP006 UP045
# @omlish-lite
import asyncio
import typing as ta

from omlish.http.headers import HttpHeaders  # noqa
from omlish.lite.check import check  # noqa

from ....asyncs import AsyncChannelPipelineMessages  # noqa
from ....core import ChannelPipelineMessages
from ....core import PipelineChannel
from ....drivers.asyncio import SimpleAsyncioStreamPipelineChannelDriver
from ....flow.types import ChannelPipelineFlowMessages
from ....handlers.flatmap import FlatMapChannelPipelineHandlers
from ...responses import FullPipelineHttpResponse  # noqa
from ...responses import PipelineHttpResponseHead  # noqa
from ...server.apps.asgi import AsgiHandler
from ...server.apps.asgi import AsgiSpec
from ...server.requests import PipelineHttpRequestAggregator
from ...server.requests import PipelineHttpRequestHeadDecoder
from ...server.responses import PipelineHttpResponseEncoder


##


def build_asgi_channel(app: ta.Any) -> PipelineChannel.Spec:
    return PipelineChannel.Spec(
        [
            PipelineHttpRequestHeadDecoder(),
            PipelineHttpRequestAggregator(),
            PipelineHttpResponseEncoder(),
            AsgiHandler(app),
            FlatMapChannelPipelineHandlers.drop(
                'inbound',
                filter_type=(
                    ChannelPipelineMessages.FinalInput,
                    ChannelPipelineFlowMessages.FlushInput,
                ),
            ),
        ],
    ).update_pipeline_config(
        # raise_immediately=True,
    )


async def a_serve_asgi_pipeline(spec: AsgiSpec) -> None:
    async def _handle_client(reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
        drv = SimpleAsyncioStreamPipelineChannelDriver(
            build_asgi_channel(spec.app),
            reader,
            writer,
        )

        await drv.run()

    srv = await asyncio.start_server(_handle_client, spec.host, spec.port)
    async with srv:
        await srv.serve_forever()


def serve_asgi_pipeline(spec: AsgiSpec) -> None:
    asyncio.run(a_serve_asgi_pipeline(spec))


##


def serve_asgi_uvicorn(spec: AsgiSpec) -> None:
    import uvicorn  # noqa

    server = uvicorn.Server(uvicorn.Config(
        spec.app,
        host=spec.host,
        port=spec.port,
    ))

    asyncio.run(server.serve())


##


async def ping_app(scope, receive, send):
    if scope['type'] != 'http':
        return

    method = scope.get('method')
    path = scope.get('path')

    if (method, path) != ('GET', '/ping'):
        body = b'not found'

        await send({
            'type': 'http.response.start',
            'status': 404,
            'headers': [
                (b'content-type', b'text/plain'),
                (b'content-length', str(len(body)).encode('ascii')),
            ],
        })

        await send({
            'type': 'http.response.body',
            'body': body,
        })

        return

    body = b'pong'

    await send({
        'type': 'http.response.start',
        'status': 200,
        'headers': [
            (b'content-type', b'text/plain'),
            (b'content-length', str(len(body)).encode('ascii')),
        ],
    })

    for i in range(len(body)):
        await send({
            'type': 'http.response.body',
            'body': bytes([body[i]]),
            'more_body': i < len(body) - 1,
        })

        await asyncio.sleep(.2)


##


def _main() -> None:
    ping_spec = AsgiSpec(ping_app)

    # serve_asgi_uvicorn(ping_spec)
    serve_asgi_pipeline(ping_spec)


if __name__ == '__main__':
    _main()
