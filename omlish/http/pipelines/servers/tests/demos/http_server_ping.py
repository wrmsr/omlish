# ruff: noqa: UP045
# @omlish-lite
import asyncio
import typing as ta

from ......io.pipelines.core import IoPipeline
from ......io.pipelines.core import IoPipelineHandler
from ......io.pipelines.core import IoPipelineHandlerContext
from ......io.pipelines.drivers.asyncio import LoopAsyncioStreamIoPipelineDriver
from ....requests import IoPipelineHttpRequestHead
from ....requests import IoPipelineHttpRequestObject
from ....responses import FullIoPipelineHttpResponse
from ...requests import IoPipelineHttpRequestDecoder
from ...responses import IoPipelineHttpResponseEncoder


##


class PingHandler(IoPipelineHandler):
    def inbound(self, ctx: IoPipelineHandlerContext, msg: ta.Any) -> None:
        if not isinstance(msg, IoPipelineHttpRequestHead):
            if not isinstance(msg, IoPipelineHttpRequestObject):
                ctx.feed_in(msg)
            return

        if msg.method == 'GET' and msg.target == '/ping':
            ctx.feed_out(FullIoPipelineHttpResponse.simple(
                status=200,
                body=b'pong',
            ))

        else:
            ctx.feed_out(FullIoPipelineHttpResponse.simple(
                status=404,
                body=b'not found',
            ))

        ctx.feed_final_output()


def build_http_ping_spec() -> IoPipeline.Spec:
    return IoPipeline.Spec([
        IoPipelineHttpRequestDecoder(),
        IoPipelineHttpResponseEncoder(),
        PingHandler(),
    ])


async def serve_ping(
        *,
        host: str = '127.0.0.1',
        port: int = 8087,
) -> None:
    async def _handle_client(reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
        drv = LoopAsyncioStreamIoPipelineDriver(
            build_http_ping_spec(),
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
