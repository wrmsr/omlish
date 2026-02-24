# ruff: noqa: UP045
# @omlish-lite
"""
time bash -c 'cat ~/Downloads/ghidra_11.4.2_PUBLIC_20250826.zip | curl -X POST --data-binary @- http://localhost:8087/sha1'
time sha1 ~/Downloads/ghidra_11.4.2_PUBLIC_20250826.zip
"""  # noqa
import asyncio
import hashlib
import typing as ta

from ....core import ChannelPipelineHandler
from ....core import ChannelPipelineHandlerContext
from ....core import PipelineChannel
from ....drivers.asyncio import SimpleAsyncioStreamPipelineChannelDriver
from ....flow.stub import StubChannelPipelineFlow
from ....flow.types import ChannelPipelineFlowMessages
from ....handlers.flatmap import FlatMapChannelPipelineHandlers
from ...requests import PipelineHttpRequestAborted
from ...requests import PipelineHttpRequestContentChunk
from ...requests import PipelineHttpRequestEnd
from ...requests import PipelineHttpRequestHead
from ...responses import FullPipelineHttpResponse
from ...server.requests import PipelineHttpRequestBodyStreamDecoder
from ...server.requests import PipelineHttpRequestHeadDecoder
from ...server.responses import PipelineHttpResponseEncoder


##


class Sha1Handler(ChannelPipelineHandler):
    """
    Handles:
      POST /sha1

    Reads the request body as a stream of HttpContentChunk and computes SHA1 incrementally. On DecodedHttpRequestEnd,
    responds with hex digest and closes.

    If the peer disconnects partway through upload (HttpRequestAborted), it closes quietly.
    """

    def __init__(self) -> None:
        super().__init__()

        self._active = False
        self._h: ta.Any = None  # hashlib object

    def inbound(self, ctx: ChannelPipelineHandlerContext, msg: ta.Any) -> None:
        if isinstance(msg, PipelineHttpRequestHead):
            if msg.method.upper() == 'POST' and msg.target.split('?', 1)[0] == '/sha1':
                self._active = True
                self._h = hashlib.sha1()  # noqa

            else:
                # Not our endpoint; reply 404 and close.
                ctx.feed_out(FullPipelineHttpResponse.simple(
                    status=404,
                    body=b'not found',
                ))

                ctx.feed_final_output()

            return

        if isinstance(msg, PipelineHttpRequestContentChunk):
            if self._active and self._h is not None:
                self._h.update(msg.data)

            return

        if isinstance(msg, PipelineHttpRequestEnd):
            if self._active and self._h is not None:
                hexd = self._h.hexdigest().encode('ascii')

                ctx.feed_out(FullPipelineHttpResponse.simple(
                    body=hexd,
                ))

                ctx.feed_final_output()

                self._active = False
                self._h = None

            return

        if isinstance(msg, PipelineHttpRequestAborted):
            # Graceful: nothing to do, just close and drop state.
            self._active = False
            self._h = None

            ctx.feed_final_output()

            return

        ctx.feed_in(msg)


def build_http_sha1_channel() -> PipelineChannel:
    return PipelineChannel(
        [

            PipelineHttpRequestHeadDecoder(),

            PipelineHttpRequestBodyStreamDecoder(),

            PipelineHttpResponseEncoder(),

            Sha1Handler(),

            FlatMapChannelPipelineHandlers.drop('inbound', filter_type=ChannelPipelineFlowMessages.FlushInput),

        ],

        services=[
            StubChannelPipelineFlow(auto_read=True),
        ],
    )


async def serve_sha1(
        *,
        host: str = '127.0.0.1',
        port: int = 8087,
) -> None:
    """
    Minimal HTTP/1 server:
      POST /sha1

    Supports:
      - Content-Length bodies (streamed)
      - Transfer-Encoding: chunked bodies (streamed)
      - bodies with no length info (stream until EOF; supports infinite streams)

    Gracefully handles disconnects mid-upload and supports concurrent connections.
    """

    async def _handle_client(
            reader: asyncio.StreamReader,
            writer: asyncio.StreamWriter,
    ) -> None:
        ch = build_http_sha1_channel(

        )

        drv = SimpleAsyncioStreamPipelineChannelDriver(
            ch,
            reader,
            writer,
        )

        await drv.run()

    srv = await asyncio.start_server(_handle_client, host, port)

    async with srv:
        await srv.serve_forever()


def main() -> None:
    asyncio.run(serve_sha1())


if __name__ == '__main__':
    main()
