"""
time bash -c 'cat ~/Downloads/ghidra_11.4.2_PUBLIC_20250826.zip | curl -X POST --data-binary @- http://localhost:8087/sha1'
time sha1 ~/Downloads/ghidra_11.4.2_PUBLIC_20250826.zip
"""  # noqa
import asyncio
import hashlib
import typing as ta

from ...asyncio import BytesFlowControlAsyncioStreamChannelPipelineDriver
from ...bytes import BytesFlowControlChannelPipelineHandler
from ...core import ChannelPipelineHandler
from ...core import ChannelPipelineHandlerContext
from ...core import PipelineChannel
from ...http.requests import PipelineHttpRequestAborted
from ...http.requests import PipelineHttpRequestContentChunk
from ...http.requests import PipelineHttpRequestEnd
from ...http.requests import PipelineHttpRequestHead
from ...http.server.requests import PipelineHttpRequestBodyStreamDecoder
from ...http.server.requests import PipelineHttpRequestHeadDecoder


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
                body = b'not found'
                resp = (
                    b'HTTP/1.1 404 Not Found\r\n'
                    b'Content-Type: text/plain; charset=utf-8\r\n'
                    b'Content-Length: ' + str(len(body)).encode('ascii') + b'\r\n'
                    b'Connection: close\r\n'
                    b'\r\n' + body
                )

                ctx.feed_out(resp)
                ctx.channel.feed_close()

            return

        if isinstance(msg, PipelineHttpRequestContentChunk):
            if self._active and self._h is not None:
                self._h.update(msg.data)

            return

        if isinstance(msg, PipelineHttpRequestEnd):
            if self._active and self._h is not None:
                hexd = self._h.hexdigest().encode('ascii')
                resp = (
                    b'HTTP/1.1 200 OK\r\n'
                    b'Content-Type: text/plain; charset=utf-8\r\n'
                    b'Content-Length: ' + str(len(hexd)).encode('ascii') + b'\r\n'
                    b'Connection: close\r\n'
                    b'\r\n' + hexd
                )

                ctx.feed_out(resp)
                ctx.channel.feed_close()

                self._active = False
                self._h = None

            return

        if isinstance(msg, PipelineHttpRequestAborted):
            # Graceful: nothing to do, just close and drop state.
            self._active = False
            self._h = None

            ctx.channel.feed_close()

            return

        ctx.feed_in(msg)


def build_http_sha1_channel(
        *,
        outbound_capacity: int | None = 1 << 22,
        outbound_overflow_policy: ta.Literal['allow', 'close', 'raise', 'drop'] = 'close',

        max_head: int = 64 << 10,

        max_chunk: int = 1 << 20,
        max_body_buf: int | None = 1 << 22,
) -> PipelineChannel:
    return PipelineChannel([

        BytesFlowControlChannelPipelineHandler(
            BytesFlowControlChannelPipelineHandler.Config(
                outbound_capacity=outbound_capacity,
                outbound_overflow_policy=outbound_overflow_policy,
            ),
        ),

        PipelineHttpRequestHeadDecoder(
            max_head=max_head,
        ),

        PipelineHttpRequestBodyStreamDecoder(
            max_chunk=max_chunk,
            max_buf=max_body_buf,
        ),

        Sha1Handler(),

    ])


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

        drv = BytesFlowControlAsyncioStreamChannelPipelineDriver(
            ch,
            reader,
            writer,
            backpressure_sleep=0.001,
        )

        await drv.run()

    srv = await asyncio.start_server(_handle_client, host, port)

    async with srv:
        await srv.serve_forever()


def main() -> None:
    asyncio.run(serve_sha1())


if __name__ == '__main__':
    main()
