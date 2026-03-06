# ruff: noqa: UP006 UP045
# @omlish-lite
import dataclasses as dc
import typing as ta

from omlish.io.streams.utils import ByteStreamBuffers

from ....core import ChannelPipelineHandler
from ....core import ChannelPipelineHandlerContext
from ....core import ChannelPipelineMessages
from ....core import PipelineChannel
from ....flow.stub import StubChannelPipelineFlow
from ....flow.types import ChannelPipelineFlow
from ....flow.types import ChannelPipelineFlowMessages
from ....handlers.flatmap import FlatMapChannelPipelineHandlers
from ....handlers.logs import LoggingChannelPipelineHandler
from ....ssl.handlers import SslChannelPipelineHandler
from ...client.requests import PipelineHttpRequestEncoder
from ...client.responses import PipelineHttpResponseChunkedDecoder
from ...client.responses import PipelineHttpResponseDecompressor
from ...client.responses import PipelineHttpResponseHeadDecoder
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
        if isinstance(msg, FullPipelineHttpRequest):
            ctx.feed_out(msg)

            if (fc := ctx.services.find(ChannelPipelineFlow)) is not None and not fc.is_auto_read():
                ctx.feed_out(ChannelPipelineFlowMessages.ReadyForInput())

            return

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

        if isinstance(msg, ChannelPipelineFlowMessages.FlushInput):
            if (fc := ctx.services.find(ChannelPipelineFlow)) is not None and not fc.is_auto_read():
                ctx.feed_out(ChannelPipelineFlowMessages.ReadyForInput())

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


##


def build_http_client(
        *,
        with_logging: bool = False,

        with_ssl: bool = False,
        ssl_kwargs: ta.Optional[ta.Mapping[str, ta.Any]] = None,

        with_gzip: bool = False,

        with_flow: bool = False,
        flow_auto_read: bool = False,
) -> PipelineChannel.Spec:
    return PipelineChannel.Spec(
        [
            *([LoggingChannelPipelineHandler()] if with_logging else []),

            *([SslChannelPipelineHandler(**(ssl_kwargs or {}))] if with_ssl else []),

            PipelineHttpResponseHeadDecoder(),

            *([PipelineHttpResponseDecompressor()] if with_gzip else []),

            PipelineHttpResponseChunkedDecoder(),

            PipelineHttpRequestEncoder(),

            HttpClientHandler(),

            *([FlatMapChannelPipelineHandlers.drop('inbound', filter_type=ChannelPipelineFlowMessages.FlushInput)] if with_flow else []),  # noqa
        ],

        services=[
            *([StubChannelPipelineFlow(auto_read=flow_auto_read)] if with_flow else []),
        ],
    )


##


@dc.dataclass(frozen=True)
class ParsedUrl:
    host: str
    port: int
    path: str


def parse_url(url: str) -> ParsedUrl:
    # Parse URL (very simple - just extract host and path)
    if url.startswith('http://'):
        ssl = False
        url_without_scheme = url[7:]
    elif url.startswith('https://'):
        ssl = True
        url_without_scheme = url[8:]
    else:
        raise ValueError(url)

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
        if ssl:
            port = 443
        else:
            port = 80

    return ParsedUrl(
        host,
        port,
        path,
    )
