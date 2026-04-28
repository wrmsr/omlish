import asyncio

from omlish.http.pipelines.servers.apps.asgi import AsgiHandler
from omlish.http.pipelines.servers.apps.asgi import AsgiSpec
from omlish.http.pipelines.servers.requests import IoPipelineHttpRequestAggregatorDecoder
from omlish.http.pipelines.servers.requests import IoPipelineHttpRequestDecoder
from omlish.http.pipelines.servers.responses import IoPipelineHttpResponseEncoder
from omlish.io.pipelines.core import IoPipeline
from omlish.io.pipelines.drivers.asyncio2 import PollAsyncioStreamIoPipelineDriver


##


async def a_serve_asgi_pipeline(spec: AsgiSpec) -> None:
    async def _handle_client(reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
        drv = PollAsyncioStreamIoPipelineDriver(
            IoPipeline.Spec(
                [
                    IoPipelineHttpRequestDecoder(),
                    IoPipelineHttpRequestAggregatorDecoder(),
                    IoPipelineHttpResponseEncoder(),
                    AsgiHandler(spec.app),
                ],
            ).update_config(
                raise_immediately=True,
            ),
            reader,
            writer,
        )

        await drv.loop_until_done()

    srv = await asyncio.start_server(_handle_client, spec.host, spec.port)
    async with srv:
        await srv.serve_forever()


def serve_asgi_pipeline(spec: AsgiSpec) -> None:
    asyncio.run(a_serve_asgi_pipeline(spec))
