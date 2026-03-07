# ruff: noqa: UP045
# @omlish-lite
import asyncio
import typing as ta

from .....io.pipelines.core import ChannelPipeline
from .....io.pipelines.core import ChannelPipelineHandler
from .....io.pipelines.core import ChannelPipelineHandlerContext
from .....io.pipelines.drivers.asyncio import SimpleAsyncioStreamChannelPipelineDriver
from ...requests import PipelineHttpRequestHead
from ...requests import PipelineHttpRequestObject
from ...responses import FullPipelineHttpResponse
from ...server.requests import PipelineHttpRequestDecoder
from ...server.responses import PipelineHttpResponseEncoder


##


class PingHandler(ChannelPipelineHandler):
    def inbound(self, ctx: ChannelPipelineHandlerContext, msg: ta.Any) -> None:
        if not isinstance(msg, PipelineHttpRequestHead):
            if not isinstance(msg, PipelineHttpRequestObject):
                ctx.feed_in(msg)
            return

        if msg.method == 'GET' and msg.target == '/ping':
            ctx.feed_out(FullPipelineHttpResponse.simple(
                status=200,
                body=b'pong',
            ))

        else:
            ctx.feed_out(FullPipelineHttpResponse.simple(
                status=404,
                body=b'not found',
            ))

        ctx.feed_final_output()


def build_http_ping_channel() -> ChannelPipeline.Spec:
    return ChannelPipeline.Spec([
        PipelineHttpRequestDecoder(),
        PipelineHttpResponseEncoder(),
        PingHandler(),
    ])


async def serve_ping(
        *,
        host: str = '127.0.0.1',
        port: int = 8087,
) -> None:
    async def _handle_client(reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
        drv = SimpleAsyncioStreamChannelPipelineDriver(
            build_http_ping_channel(),
            reader,
            writer,
        )

        await drv.run()

    srv = await asyncio.start_server(_handle_client, host, port)
    async with srv:
        await srv.serve_forever()


def main() -> None:
    asyncio.run(serve_ping())


if __name__ == '__main__':
    main()
