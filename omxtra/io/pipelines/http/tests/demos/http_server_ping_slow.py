# ruff: noqa: UP045
# @omlish-lite
import asyncio
import typing as ta

from omlish.http.headers import HttpHeaders
from omlish.http.versions import HttpVersions

from ....core import ChannelPipelineHandler
from ....core import ChannelPipelineHandlerContext
from ....core import PipelineChannel
from ....drivers.asyncio import SimpleAsyncioStreamPipelineChannelDriver
from ...requests import PipelineHttpRequestHead
from ...responses import FullPipelineHttpResponse
from ...responses import PipelineHttpResponseHead
from ...server.requests import PipelineHttpRequestHeadDecoder
from ...server.responses import PipelineHttpResponseEncoder


##


class PingHandler(ChannelPipelineHandler):
    def inbound(self, ctx: ChannelPipelineHandlerContext, msg: ta.Any) -> None:
        if not isinstance(msg, PipelineHttpRequestHead):
            ctx.feed_in(msg)
            return

        if msg.method == 'GET' and msg.target == '/ping':
            ctx.feed_out(PipelineHttpResponseHead(
                status=200,
                reason='OK',
                version=HttpVersions.HTTP_1_1,
                headers=HttpHeaders([
                    ('Content-Type', 'text/plain; charset=utf-8'),
                    ('Content-Length', '4'),
                    ('Connection', 'close'),
                ]),
            ))

        else:
            ctx.feed_out(FullPipelineHttpResponse.simple(
                status=404,
                body=b'not found',
            ))
            ctx.feed_final_output()


def build_http_ping_channel() -> PipelineChannel.Spec:
    return PipelineChannel.Spec(
        [
            PipelineHttpRequestHeadDecoder(),
            PipelineHttpResponseEncoder(),
            PingHandler(),
        ],
    )


async def serve_ping(
        *,
        host: str = '127.0.0.1',
        port: int = 8087,
) -> None:
    async def _handle_client(reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
        drv = SimpleAsyncioStreamPipelineChannelDriver(
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
