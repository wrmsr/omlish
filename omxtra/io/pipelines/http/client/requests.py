# ruff: noqa: UP006 UP007 UP045
# @omlish-lite
import io
import typing as ta

from omlish.http.headers import HttpHeaders
from omlish.http.versions import HttpVersion

from ...core import ChannelPipelineHandler
from ...core import ChannelPipelineHandlerContext
from ..requests import FullPipelineHttpRequest
from ..requests import PipelineHttpRequestContentChunkData
from ..requests import PipelineHttpRequestEnd
from ..requests import PipelineHttpRequestHead


##


class PipelineHttpRequestEncoder(ChannelPipelineHandler):
    """
    Encodes HTTP/1.x requests into wire format bytes.

    Supports both aggregated and streaming requests:

    Aggregated (single message):
      - FullPipelineHttpRequest -> bytes (request line + headers + body)

    Streaming (multi-message):
      - PipelineHttpRequestHead -> request line + headers + blank line
      - PipelineHttpRequestContentChunk* -> body chunks (raw or chunked-encoded)
      - PipelineHttpRequestEnd -> terminator (for chunked encoding)

    Transfer-Encoding:
      - If 'chunked' in Transfer-Encoding header: wraps chunks in chunked encoding
      - Otherwise: writes raw bytes (handler must set Content-Length correctly)

    All other messages pass through unchanged.
    """

    def __init__(self) -> None:
        super().__init__()

        self._streaming = False
        self._chunked = False

    def outbound(self, ctx: ChannelPipelineHandlerContext, msg: ta.Any) -> None:
        if isinstance(msg, PipelineHttpRequestHead):
            self._handle_request_head(ctx, msg)
            return

        if isinstance(msg, PipelineHttpRequestContentChunkData):
            self._handle_content_chunk_data(ctx, msg)
            return

        if isinstance(msg, PipelineHttpRequestEnd):
            self._handle_request_end(ctx)
            return

        if isinstance(msg, FullPipelineHttpRequest):
            self._handle_full_request(ctx, msg)
            return

        # Pass through
        ctx.feed_out(msg)

    def _handle_request_head(self, ctx: ChannelPipelineHandlerContext, msg: PipelineHttpRequestHead) -> None:
        """Emit request line + headers, enter streaming mode."""

        self._streaming = True
        self._chunked = self._is_chunked(msg.headers)

        buf = io.BytesIO()

        buf.write(self._encode_request_line(msg.method, msg.target, msg.version))

        for hl in self._encode_headers(msg.headers):
            buf.write(hl)

        buf.write(b'\r\n')

        ctx.feed_out(buf.getvalue())

    def _handle_content_chunk_data(self, ctx: ChannelPipelineHandlerContext, msg: PipelineHttpRequestContentChunkData) -> None:  # noqa
        """Emit body chunk (raw or chunked-encoded)."""

        if not self._streaming:
            # Not in streaming mode - pass through unchanged
            ctx.feed_out(msg)
            return

        if self._chunked:
            # Chunked encoding: <size-hex>\r\n<data>\r\n
            if msg.data:
                size_hex = f'{len(msg.data):x}\r\n'.encode('ascii')
                ctx.feed_out(size_hex)
                ctx.feed_out(msg.data)
                ctx.feed_out(b'\r\n')
        else:
            # Raw data
            if msg.data:
                ctx.feed_out(msg.data)

    def _handle_request_end(self, ctx: ChannelPipelineHandlerContext) -> None:
        """Emit terminator if chunked, reset state."""

        if not self._streaming:
            # Not in streaming mode - pass through
            ctx.feed_out(PipelineHttpRequestEnd())
            return

        if self._chunked:
            # Emit final chunk: 0\r\n\r\n
            ctx.feed_out(b'0\r\n\r\n')

        # Reset state
        self._streaming = False
        self._chunked = False

    def _handle_full_request(self, ctx: ChannelPipelineHandlerContext, msg: FullPipelineHttpRequest) -> None:
        """Emit complete request in one shot."""

        head = msg.head
        body = msg.body

        buf = io.BytesIO()

        buf.write(self._encode_request_line(head.method, head.target, head.version))

        for hl in self._encode_headers(head.headers):
            buf.write(hl)

        buf.write(b'\r\n')
        buf.write(body)

        ctx.feed_out(buf.getvalue())

    def _encode_request_line(self, method: str, target: str, version: HttpVersion) -> bytes:
        """Encode HTTP request line: 'GET /path HTTP/1.1\r\n'."""

        version_str = f'HTTP/{version.major}.{version.minor}'
        return f'{method} {target} {version_str}\r\n'.encode('ascii')

    def _encode_headers(self, headers: HttpHeaders) -> ta.List[bytes]:
        """Encode headers as 'Name: value\r\n' lines."""

        lines: ta.List[bytes] = []

        # HttpHeaders stores entries as list of (name, value) tuples
        for name, value in headers.raw:
            # Header names and values should be ASCII-safe in practice
            line = f'{name}: {value}\r\n'.encode('ascii')
            lines.append(line)

        return lines

    def _is_chunked(self, headers: HttpHeaders) -> bool:
        """Check if Transfer-Encoding includes 'chunked'."""

        te = headers.lower.get('transfer-encoding', ())
        return 'chunked' in te
