import asyncio

from omcore.http.pipelines.servers.apps.asgi import AsgiIoPipelineHandler
from omcore.http.pipelines.servers.apps.asgi import IoPipelineAsgiSpec
from omcore.http.pipelines.servers.requests import IoPipelineHttpRequestAggregatorDecoder
from omcore.http.pipelines.servers.requests import IoPipelineHttpRequestDecoder
from omcore.http.pipelines.servers.responses import IoPipelineHttpResponseEncoder
from omcore.io.pipelines.core import IoPipeline
from omcore.io.pipelines.drivers.asyncio import PollAsyncioStreamIoPipelineDriver


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
