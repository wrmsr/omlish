# ruff: noqa: UP006 UP045
# @omlish-lite
import asyncio
import typing as ta

from omlish.http.pipelines.servers.apps.asgi import AsgiHandler
from omlish.http.pipelines.servers.apps.asgi import AsgiSpec
from omlish.http.pipelines.servers.requests import IoPipelineHttpRequestAggregatorDecoder
from omlish.http.pipelines.servers.requests import IoPipelineHttpRequestDecoder
from omlish.http.pipelines.servers.responses import IoPipelineHttpResponseEncoder
from omlish.io.pipelines.asyncs import AsyncIoPipelineMessages  # noqa
from omlish.io.pipelines.core import IoPipeline
from omlish.io.pipelines.drivers.asyncio import SimpleAsyncioStreamIoPipelineDriver


##


async def a_serve_asgi_pipeline(spec: AsgiSpec) -> None:
    async def _handle_client(reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
        drv = SimpleAsyncioStreamIoPipelineDriver(
            IoPipeline.Spec(
                [
                    IoPipelineHttpRequestDecoder(),
                    IoPipelineHttpRequestAggregatorDecoder(),
                    IoPipelineHttpResponseEncoder(),
                    AsgiHandler(spec.app),
                ],
            ).update_config(
                # raise_immediately=True,
            ),
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


async def app(scope, receive, send):
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
    app_spec = AsgiSpec(app)

    serve_asgi_pipeline(app_spec)


if __name__ == '__main__':
    _main()
