# ruff: noqa: UP045
# @omlish-lite
import asyncio
import typing as ta

from .....io.pipelines.core import IoPipeline
from .....io.pipelines.core import IoPipelineHandler
from .....io.pipelines.core import IoPipelineHandlerContext
from .....io.pipelines.core import IoPipelineMessages
from .....io.pipelines.drivers.asyncio import SimpleAsyncioStreamIoPipelineDriver
from .....io.pipelines.flow.stub import StubIoPipelineFlow
from .....io.pipelines.flow.types import IoPipelineFlow
from .....io.pipelines.flow.types import IoPipelineFlowMessages
from ...requests import IoPipelineHttpRequestHead
from ...requests import IoPipelineHttpRequestObject
from ...server.requests import IoPipelineHttpRequestDecoder


##


class PingHandler(IoPipelineHandler):
    """
    Responds to GET /ping with plaintext "pong" and closes the channel.

    This is intentionally minimal and not a full HTTP server implementation.
    """

    def inbound(self, ctx: IoPipelineHandlerContext, msg: ta.Any) -> None:
        if isinstance(msg, IoPipelineMessages.InitialInput):
            ctx.feed_in(msg)

            if not IoPipelineFlow.is_auto_read_context(ctx):
                ctx.feed_out(IoPipelineFlowMessages.ReadyForInput())

            return

        if not isinstance(msg, IoPipelineHttpRequestHead):
            if not isinstance(msg, IoPipelineHttpRequestObject):
                ctx.feed_in(msg)
            return

        if msg.method == 'GET' and msg.target == '/ping':
            body = b'pong'
            resp = (
                b'HTTP/1.1 200 OK\r\n'
                b'Content-Type: text/plain; charset=utf-8\r\n'
                b'Content-Length: ' + str(len(body)).encode('ascii') + b'\r\n'
                b'Connection: close\r\n'
                b'\r\n' +
                body
            )

        else:
            body = b'not found'
            resp = (
                b'HTTP/1.1 404 Not Found\r\n'
                b'Content-Type: text/plain; charset=utf-8\r\n'
                b'Content-Length: ' + str(len(body)).encode('ascii') + b'\r\n'
                b'Connection: close\r\n'
                b'\r\n' +
                body
            )

        # Write response bytes immediately.
        ctx.feed_out(resp)

        # Request logical close; driver will close transport after flushing outbound.
        ctx.feed_final_output()


def build_http_ping_channel(
        # *,
        # outbound_capacity: ta.Optional[int] = 1 << 22,
        # outbound_overflow_policy: ta.Literal['allow', 'close', 'raise', 'drop'] = 'close',
) -> IoPipeline.Spec:
    return IoPipeline.Spec(
        [
            IoPipelineHttpRequestDecoder(),
            PingHandler(),
        ],
        services=[
            StubIoPipelineFlow(auto_read=False),
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
            build_http_ping_channel(),
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
