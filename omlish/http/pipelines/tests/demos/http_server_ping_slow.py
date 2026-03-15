# ruff: noqa: UP045
# @omlish-lite
import asyncio
import typing as ta

from .....io.pipelines.core import IoPipeline
from .....io.pipelines.core import IoPipelineHandler
from .....io.pipelines.core import IoPipelineHandlerContext
from .....io.pipelines.drivers.asyncio import SimpleAsyncioStreamIoPipelineDriver
from .....io.pipelines.flow.stub import StubIoPipelineFlowService
from .....io.pipelines.flow.types import IoPipelineFlowMessages
from .....io.pipelines.sched.types import IoPipelineScheduling
from ....headers import HttpHeaders
from ....versions import HttpVersions
from ...requests import IoPipelineHttpRequestHead
from ...responses import FullIoPipelineHttpResponse
from ...responses import IoPipelineHttpResponseHead
from ...servers.requests import IoPipelineHttpRequestDecoder
from ...servers.responses import IoPipelineHttpResponseEncoder


##


class PingHandler(IoPipelineHandler):
    def inbound(self, ctx: IoPipelineHandlerContext, msg: ta.Any) -> None:
        if not isinstance(msg, IoPipelineHttpRequestHead):
            ctx.feed_in(msg)
            return

        if msg.method == 'GET' and msg.target == '/ping':
            ctx.feed_out(IoPipelineHttpResponseHead(
                status=200,
                reason='OK',
                version=HttpVersions.HTTP_1_1,
                headers=HttpHeaders([
                    ('Content-Type', 'text/plain; charset=utf-8'),
                    ('Content-Length', '4'),
                    ('Connection', 'close'),
                ]),
            ))
            ctx.feed_out(IoPipelineFlowMessages.FlushOutput())

            def write_pong(n: int) -> None:
                ctx.feed_out(b'pong'[n:n + 1])
                ctx.feed_out(IoPipelineFlowMessages.FlushOutput())

                if n < 4:
                    ctx.services[IoPipelineScheduling].schedule(ctx.ref, 1, lambda: write_pong(n + 1))
                else:
                    ctx.feed_final_output()

            ctx.services[IoPipelineScheduling].schedule(ctx.ref, 1, lambda: write_pong(0))

        else:
            ctx.feed_out(FullIoPipelineHttpResponse.simple(
                status=404,
                body=b'not found',
            ))
            ctx.feed_final_output()


def build_http_ping_spec() -> IoPipeline.Spec:
    return IoPipeline.Spec(
        [
            IoPipelineHttpRequestDecoder(),
            IoPipelineHttpResponseEncoder(),
            PingHandler(),
        ],
        services=[
            StubIoPipelineFlowService(auto_read=True),
        ],
    )


async def serve_ping(
        *,
        host: str = '127.0.0.1',
        port: int = 8087,
) -> None:
    async def _handle_client(reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
        drv = SimpleAsyncioStreamIoPipelineDriver(
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
