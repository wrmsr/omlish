import asyncio

from omlish.http.pipelines.servers.apps.asgi import AsgiIoPipelineHandler
from omlish.http.pipelines.servers.apps.asgi import IoPipelineAsgiSpec
from omlish.http.pipelines.servers.requests import IoPipelineHttpRequestAggregatorDecoder
from omlish.http.pipelines.servers.requests import IoPipelineHttpRequestDecoder
from omlish.http.pipelines.servers.responses import IoPipelineHttpResponseEncoder
from omlish.io.pipelines.core import IoPipeline
from omlish.io.pipelines.drivers.asyncio2 import PollAsyncioStreamIoPipelineDriver


##


async def serve_asgi_pipeline(spec: IoPipelineAsgiSpec) -> None:
    async def _handle_client(reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
        drv = PollAsyncioStreamIoPipelineDriver(
            IoPipeline.Spec(
                [
                    IoPipelineHttpRequestDecoder(),
                    IoPipelineHttpRequestAggregatorDecoder(),
                    IoPipelineHttpResponseEncoder(),
                    AsgiIoPipelineHandler(spec.app),
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
