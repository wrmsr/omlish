# ruff: noqa: UP006 UP045
# @omlish-lite
import asyncio
import typing as ta

from ......io.pipelines.asyncs import AsyncIoPipelineMessages  # noqa
from ......io.pipelines.core import IoPipeline
from ......io.pipelines.drivers.asyncio import LoopAsyncioStreamIoPipelineDriver
from ....responses import FullIoPipelineHttpResponse  # noqa
from ....responses import IoPipelineHttpResponseHead  # noqa
from ...apps.asgi import AsgiHandler
from ...apps.asgi import AsgiSpec
from ...requests import IoPipelineHttpRequestAggregatorDecoder
from ...requests import IoPipelineHttpRequestDecoder
from ...responses import IoPipelineHttpResponseEncoder


##


def build_asgi_spec(app: ta.Any) -> IoPipeline.Spec:
    return IoPipeline.Spec(
        [
            IoPipelineHttpRequestDecoder(),
            IoPipelineHttpRequestAggregatorDecoder(),
            IoPipelineHttpResponseEncoder(),
            AsgiHandler(app),
        ],
    ).update_config(
        # raise_immediately=True,
    )


async def a_serve_asgi_pipeline(spec: AsgiSpec) -> None:
    async def _handle_client(reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
        drv = LoopAsyncioStreamIoPipelineDriver(
            build_asgi_spec(spec.app),
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
