# ruff: noqa: UP045
# @omlish-lite
import asyncio
import typing as ta

from ......io.pipelines.bytes.buffers import OutboundBytesBufferIoPipelineHandler
from ......io.pipelines.core import IoPipeline
from ......io.pipelines.core import IoPipelineHandler
from ......io.pipelines.core import IoPipelineHandlerContext
from ......io.pipelines.core import IoPipelineMessages
from ......io.pipelines.drivers.asyncio import SimpleAsyncioStreamIoPipelineDriver
from ......io.pipelines.flow.stub import StubIoPipelineFlowService
from ......io.pipelines.flow.types import IoPipelineFlow
from ......io.pipelines.flow.types import IoPipelineFlowMessages
from ....requests import IoPipelineHttpRequestHead
from ....requests import IoPipelineHttpRequestObject
from ....responses import FullIoPipelineHttpResponse
from ...requests import IoPipelineHttpRequestDecoder
from ...responses import IoPipelineHttpResponseEncoder


##


class PingHandler(IoPipelineHandler):
    """
    Responds to GET /ping with plaintext "pong" and closes the channel.

    This is intentionally minimal and not a full HTTP server implementation.
    """

    def inbound(self, ctx: IoPipelineHandlerContext, msg: ta.Any) -> None:
        if isinstance(msg, IoPipelineMessages.InitialInput):
            ctx.feed_in(msg)

            if not IoPipelineFlow.is_auto_read(ctx):
                ctx.feed_out(IoPipelineFlowMessages.ReadyForInput())

            return

        if not isinstance(msg, IoPipelineHttpRequestHead):
            if not isinstance(msg, IoPipelineHttpRequestObject):
                ctx.feed_in(msg)
            return

        if msg.method == 'GET' and msg.target == '/ping':
            resp = FullIoPipelineHttpResponse.simple(body=b'pong')

        else:
            resp = FullIoPipelineHttpResponse.simple(status=404, body=b'not found')

        # Write response bytes immediately.
        ctx.feed_out(resp)

        # Request logical close; driver will close transport after flushing outbound.
        ctx.feed_final_output()


def build_http_ping_spec(
        # *,
        # outbound_capacity: ta.Optional[int] = 1 << 22,
        # outbound_overflow_policy: ta.Literal['allow', 'close', 'raise', 'drop'] = 'close',
) -> IoPipeline.Spec:
    return IoPipeline.Spec(
        [
            OutboundBytesBufferIoPipelineHandler(),
            IoPipelineHttpResponseEncoder(),
            IoPipelineHttpRequestDecoder(),
            PingHandler(),
        ],
        services=[
            StubIoPipelineFlowService(auto_read=False),
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
        drv = SimpleAsyncioStreamIoPipelineDriver(
            build_http_ping_spec(),
            reader,
            writer,
            # backpressure_sleep=0.0,
        )

        await drv.run()

    srv = await asyncio.start_server(_handle_client, host, port)
    async with srv:
        await srv.serve_forever()


def main() -> None:
    asyncio.run(serve_ping())


if __name__ == '__main__':
    main()
