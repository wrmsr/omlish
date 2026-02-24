# ruff: noqa: UP006 UP007 UP045
# @omlish-lite
import io
import typing as ta

from omlish.http.headers import HttpHeaders
from omlish.http.versions import HttpVersion

from ...core import ChannelPipelineHandler
from ...core import ChannelPipelineHandlerContext
from ..responses import FullPipelineHttpResponse
from ..responses import PipelineHttpResponseContentChunkData
from ..responses import PipelineHttpResponseEnd
from ..responses import PipelineHttpResponseHead


##


class PipelineHttpResponseEncoder(ChannelPipelineHandler):
    """
    Encodes HTTP/1.x responses into wire format bytes.

    Supports both aggregated and streaming responses:

    Aggregated (single message):
      - FullPipelineHttpResponse -> bytes (status line + headers + body)

    Streaming (multi-message):
      - PipelineHttpResponseHead -> status line + headers + blank line
      - PipelineHttpContentChunk* -> body chunks (raw or chunked-encoded)
      - PipelineHttpResponseEnd -> terminator (for chunked encoding)

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
        if isinstance(msg, PipelineHttpResponseHead):
            self._handle_response_head(ctx, msg)
            return

        if isinstance(msg, PipelineHttpResponseContentChunkData):
            self._handle_content_chunk_data(ctx, msg)
            return

        if isinstance(msg, PipelineHttpResponseEnd):
            self._handle_response_end(ctx)
            return

        if isinstance(msg, FullPipelineHttpResponse):
            self._handle_full_response(ctx, msg)
            return

        # Pass through
        ctx.feed_out(msg)

    def _handle_response_head(self, ctx: ChannelPipelineHandlerContext, msg: PipelineHttpResponseHead) -> None:
        """Emit status line + headers, enter streaming mode."""

        self._streaming = True
        self._chunked = self._is_chunked(msg.headers)

        buf = io.BytesIO()

        buf.write(self._encode_status_line(msg.version, msg.status, msg.reason))

        for hl in self._encode_headers(msg.headers):
            buf.write(hl)

        buf.write(b'\r\n')

        ctx.feed_out(buf.getvalue())

    def _handle_content_chunk_data(self, ctx: ChannelPipelineHandlerContext, msg: PipelineHttpResponseContentChunkData) -> None:  # noqa
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

    def _handle_response_end(self, ctx: ChannelPipelineHandlerContext) -> None:
        """Emit terminator if chunked, reset state."""

        if not self._streaming:
            # Not in streaming mode - pass through
            ctx.feed_out(PipelineHttpResponseEnd())
            return

        if self._chunked:
            # Emit final chunk: 0\r\n\r\n
            ctx.feed_out(b'0\r\n\r\n')

        # Reset state
        self._streaming = False
        self._chunked = False

    def _handle_full_response(self, ctx: ChannelPipelineHandlerContext, msg: FullPipelineHttpResponse) -> None:
        """Emit complete response in one shot."""

        head = msg.head
        body = msg.body

        buf = io.BytesIO()

        buf.write(self._encode_status_line(head.version, head.status, head.reason))

        for hl in self._encode_headers(head.headers):
            buf.write(hl)

        buf.write(b'\r\n')
        buf.write(body)

        ctx.feed_out(buf.getvalue())

    def _encode_status_line(self, version: HttpVersion, status: int, reason: str) -> bytes:
        """Encode HTTP status line: 'HTTP/1.1 200 OK\r\n'."""

        version_str = f'HTTP/{version.major}.{version.minor}'
        return f'{version_str} {status} {reason}\r\n'.encode('ascii')

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
