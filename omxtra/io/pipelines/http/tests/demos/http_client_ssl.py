# ruff: noqa: UP006 UP045
# @omlish-lite
import asyncio
import typing as ta

from omlish.io.streams.utils import ByteStreamBuffers

from ....core import ChannelPipelineHandler
from ....core import ChannelPipelineHandlerContext
from ....core import ChannelPipelineMessages
from ....core import PipelineChannel
from ....drivers.asyncio import SimpleAsyncioStreamPipelineChannelDriver
from ....handlers.flatmap import FlatMapChannelPipelineHandlers
from ....ssl.handlers import SslChannelPipelineHandler
from ...client.requests import PipelineHttpRequestEncoder
from ...client.responses import PipelineHttpResponseChunkedDecoder
from ...client.responses import PipelineHttpResponseDecoder
from ...requests import FullPipelineHttpRequest
from ...responses import PipelineHttpResponseContentChunkData
from ...responses import PipelineHttpResponseEnd
from ...responses import PipelineHttpResponseHead


##


class HttpClientHandler(ChannelPipelineHandler):
    """
    Simple HTTP client handler that sends a request and prints the response.

    Accumulates response head and body, then prints on EOF.
    """

    def __init__(self) -> None:
        super().__init__()

        self._response_head: ta.Optional[PipelineHttpResponseHead] = None
        self._body_chunks: ta.List[bytes] = []

    def inbound(self, ctx: ChannelPipelineHandlerContext, msg: ta.Any) -> None:
        if isinstance(msg, PipelineHttpResponseHead):
            self._response_head = msg
            return

        if isinstance(msg, PipelineHttpResponseEnd):
            return

        if isinstance(msg, ChannelPipelineMessages.FinalInput):
            self._print_response()
            ctx.feed_in(msg)
            ctx.feed_out(ChannelPipelineMessages.FinalOutput())
            return

        # Handle wrapped chunks
        if isinstance(msg, PipelineHttpResponseContentChunkData):
            self._body_chunks.append(msg.data)
            return

        # Body bytes (for non-chunked responses)
        if ByteStreamBuffers.can_bytes(msg):
            for mv in ByteStreamBuffers.iter_segments(msg):
                if mv:
                    self._body_chunks.append(ByteStreamBuffers.memoryview_to_bytes(mv))
            return

        # Pass through other messages
        ctx.feed_in(msg)

    def _print_response(self) -> None:
        """Print the accumulated response."""

        if self._response_head is None:
            print('No response received')
            return

        head = self._response_head
        body = b''.join(self._body_chunks)

        print(f'HTTP/{head.version.major}.{head.version.minor} {head.status} {head.reason}')
        print()

        # Print headers
        for name, value in head.headers.raw:
            print(f'{name}: {value}')

        print()

        # Print body (decoded if text)
        try:
            print(body.decode('utf-8'))
        except UnicodeDecodeError:
            print(f'<binary body: {len(body)} bytes>')


def build_ssl_http_client_channel(**ssl_kwargs: ta.Any) -> PipelineChannel.Spec:
    """Build a client channel with encoder, decoder, and handler."""

    return PipelineChannel.Spec([
        SslChannelPipelineHandler(**ssl_kwargs),
        PipelineHttpResponseDecoder(),
        PipelineHttpResponseChunkedDecoder(),
        PipelineHttpRequestEncoder(),
        HttpClientHandler(),
        FlatMapChannelPipelineHandlers.feed_out_and_drop(filter_type=FullPipelineHttpRequest),
    ])


async def fetch_url(url: str = 'https://example.com/') -> None:
    # Parse URL (very simple - just extract host and path)
    if not url.startswith('https://'):
        raise ValueError('Only https:// URLs supported')

    url_without_scheme = url[8:]  # Remove 'https://'
    if '/' in url_without_scheme:
        host, path = url_without_scheme.split('/', 1)
        path = '/' + path
    else:
        host = url_without_scheme
        path = '/'

    # Extract port if present
    if ':' in host:
        host, port_str = host.split(':', 1)
        port = int(port_str)
    else:
        port = 443

    # Connect
    reader, writer = await asyncio.open_connection(host, port)

    try:
        # Send request
        request = FullPipelineHttpRequest.simple(
            host,
            path,
            headers={
                'User-Agent': 'omlish-http-client/0.1',
            },
        )

        # Run driver to process request/response
        drv = SimpleAsyncioStreamPipelineChannelDriver(
            build_ssl_http_client_channel(
                server_side=False,
                server_hostname=host,
            ),
            reader,
            writer,
        )

        drv_run_task = asyncio.create_task(drv.run())

        await drv.feed_in(request)

        await drv_run_task

    finally:
        writer.close()
        await writer.wait_closed()


def main() -> None:
    asyncio.run(fetch_url(
        # 'https://127.0.0.1:8443/',
    ))


if __name__ == '__main__':
    # try:
    #     __import__('omlish.check')
    # except ImportError:
    #     pass

    main()
