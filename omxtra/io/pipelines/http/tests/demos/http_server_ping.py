# ruff: noqa: UP045
# @omlish-lite
import asyncio
import typing as ta

from ....core import ChannelPipelineHandler
from ....core import ChannelPipelineHandlerContext
from ....core import PipelineChannel
from ....drivers.asyncio import AsyncioStreamChannelPipelineDriver
from ...requests import PipelineHttpRequestHead
from ...responses import FullPipelineHttpResponse
from ...server.requests import PipelineHttpRequestHeadDecoder
from ...server.responses import PipelineHttpResponseEncoder


##


class PingHandler(ChannelPipelineHandler):
    """
    Responds to GET /ping with plaintext "pong" and closes the channel.

    This is intentionally minimal and not a full HTTP server implementation.
    """

    def inbound(self, ctx: ChannelPipelineHandlerContext, msg: ta.Any) -> None:
        if not isinstance(msg, PipelineHttpRequestHead):
            ctx.feed_in(msg)
            return

        if msg.method == 'GET' and msg.target == '/ping':
            resp = FullPipelineHttpResponse.simple(
                status=200,
                body=b'pong',
            )

        else:
            resp = FullPipelineHttpResponse.simple(
                status=404,
                body=b'not found',
            )

        # Write response object; encoder will convert to bytes.
        ctx.feed_out(resp)

        # Request logical close; driver will close transport after flushing outbound.
        ctx.feed_final_output()


def build_http_ping_channel() -> PipelineChannel:
    return PipelineChannel(
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
    """
    Start a minimal HTTP/1 server with one endpoint:
      GET /ping  -> 200 'pong'
      otherwise -> 404

    Each connection gets its own Channel and AsyncioStreamDriver.
    """

    async def _handle_client(reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
        drv = AsyncioStreamChannelPipelineDriver(
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
