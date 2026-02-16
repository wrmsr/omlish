# ruff: noqa: UP006 UP045
# @omlish-lite
import typing as ta
import zlib

from omlish.http.headers import HttpHeaders
from omlish.http.parsing import HttpParser
from omlish.http.parsing import parse_http_message
from omlish.io.streams.segmented import SegmentedByteStreamBuffer
from omlish.io.streams.utils import ByteStreamBuffers
from omlish.lite.check import check

from ...core import ChannelPipelineEvents
from ...core import ChannelPipelineHandler
from ...core import ChannelPipelineHandlerContext
from ..responses import PipelineHttpResponseEnd
from ..responses import PipelineHttpResponseHead


##


class PipelineHttpResponseDecoder(ChannelPipelineHandler):
    """
    Minimal HTTP/1.x response head decoder (demo-grade).

    Uses an internal SegmentedByteStreamBuffer with max_bytes to prevent runaway header buffering.

    On successful parse:
      - emits DecodedHttpResponseHead
      - forwards any remaining buffered bytes as body bytes/views
    """

    def __init__(
            self,
            *,
            max_head: int = 0x10000,
            chunk_size: int = 0x10000,
    ) -> None:
        super().__init__()

        self._buf = SegmentedByteStreamBuffer(
            max_bytes=max_head,
            chunk_size=chunk_size,
        )
        self._got_head = False
        self._max_head = int(max_head)

    # def buffered_bytes(self) -> int:
    #     return len(self._buf)

    def inbound(self, ctx: ChannelPipelineHandlerContext, msg: ta.Any) -> None:
        if isinstance(msg, ChannelPipelineEvents.Eof):
            # If EOF arrives before head parsed, treat as protocol error.
            if not self._got_head and len(self._buf):
                raise ValueError('EOF before HTTP head complete')
            ctx.feed_in(msg)
            return

        if (
                self._got_head or
                not ByteStreamBuffers.can_bytes(msg)
        ):
            ctx.feed_in(msg)
            return

        for mv in ByteStreamBuffers.iter_segments(msg):
            if mv:
                self._buf.write(mv)

        i = self._buf.find(b'\r\n\r\n')
        if i < 0:
            return

        before = len(self._buf)
        head_view = self._buf.split_to(i + 4)
        after = len(self._buf)

        head = self._parse_head(ByteStreamBuffers.any_to_bytes(head_view))
        self._got_head = True

        if (bfc := ctx.bytes_flow_control) is not None:
            bfc.on_consumed(self, before - after)

        ctx.feed_in(head)

        if len(self._buf):
            before2 = len(self._buf)
            body_view = self._buf.split_to(before2)

            ctx.feed_in(body_view)

    def _parse_head(self, raw: bytes) -> PipelineHttpResponseHead:
        parsed = parse_http_message(raw, mode=HttpParser.Mode.RESPONSE)
        status = check.not_none(parsed.status_line)

        return PipelineHttpResponseHead(
            version=status.http_version,
            status=status.status_code,
            reason=status.reason_phrase,
            headers=HttpHeaders(parsed.headers.entries),
            parsed=parsed,
        )


##


class PipelineHttpResponseConditionalGzipDecoder(ChannelPipelineHandler):
    """
    Conditional streaming gzip decompression.

    Watches for DecodedHttpResponseHead; if Content-Encoding includes 'gzip', enable zlib decompressor for body bytes.
    Flushes on EOF.
    """

    def __init__(self) -> None:
        super().__init__()

        self._enabled = False
        self._z: ta.Optional[ta.Any] = None

    def inbound(self, ctx: ChannelPipelineHandlerContext, msg: ta.Any) -> None:
        if isinstance(msg, ChannelPipelineEvents.Eof):
            if self._enabled and self._z is not None:
                tail = self._z.flush()
                if tail:
                    ctx.feed_in(tail)
            ctx.feed_in(msg)
            return

        if isinstance(msg, PipelineHttpResponseHead):
            enc = msg.headers.lower.get('content-encoding', ())
            self._enabled = 'gzip' in enc
            self._z = zlib.decompressobj(16 + zlib.MAX_WBITS) if self._enabled else None
            ctx.feed_in(msg)
            return

        if (
                not self._enabled or
                self._z is None or
                not ByteStreamBuffers.can_bytes(msg)
        ):
            ctx.feed_in(msg)
            return

        for mv in ByteStreamBuffers.iter_segments(msg):
            out = self._z.decompress(mv)
            if out:
                ctx.feed_in(out)


##


class PipelineHttpResponseChunkedDecoder(ChannelPipelineHandler):
    """
    Decodes HTTP/1.x chunked transfer encoding.

    Watches for PipelineHttpResponseHead; if Transfer-Encoding includes 'chunked',
    decodes chunked body format:

      <chunk-size-hex>\r\n
      <chunk-data>
      \r\n
      ...
      0\r\n
      \r\n

    Emits decoded body bytes and PipelineHttpResponseEnd when complete.
    """

    def __init__(
            self,
            *,
            max_chunk_header: int = 1024,
            chunk_size: int = 0x10000,
    ) -> None:
        super().__init__()

        self._buf = SegmentedByteStreamBuffer(
            max_bytes=max_chunk_header,
            chunk_size=chunk_size,
        )
        self._enabled = False
        self._chunk_remaining = 0
        self._state: ta.Literal['size', 'data', 'trailer', 'done'] = 'size'

    def inbound(self, ctx: ChannelPipelineHandlerContext, msg: ta.Any) -> None:
        if isinstance(msg, ChannelPipelineEvents.Eof):
            if self._enabled and self._state != 'done':
                raise ValueError('EOF before chunked encoding complete')
            ctx.feed_in(msg)
            return

        if isinstance(msg, PipelineHttpResponseHead):
            te = msg.headers.lower.get('transfer-encoding', ())
            self._enabled = 'chunked' in te
            ctx.feed_in(msg)
            return

        if not self._enabled or not ByteStreamBuffers.can_bytes(msg):
            ctx.feed_in(msg)
            return

        # Process chunked encoding
        for mv in ByteStreamBuffers.iter_segments(msg):
            if mv:
                self._buf.write(mv)

        self._decode_chunks(ctx)

    def _decode_chunks(self, ctx: ChannelPipelineHandlerContext) -> None:
        """Decode as many complete chunks as possible from buffer."""

        while True:
            if self._state == 'size':
                # Parse chunk size line: <hex-size>\r\n
                i = self._buf.find(b'\r\n')
                if i < 0:
                    return  # Need more data

                before = len(self._buf)
                size_line = self._buf.split_to(i + 2)
                after = len(self._buf)

                size_bytes = ByteStreamBuffers.any_to_bytes(size_line)[:-2]  # Strip \r\n
                try:
                    self._chunk_remaining = int(size_bytes, 16)
                except ValueError as e:
                    raise ValueError(f'Invalid chunk size: {size_bytes!r}') from e

                if (bfc := ctx.bytes_flow_control) is not None:
                    bfc.on_consumed(self, before - after)

                if self._chunk_remaining == 0:
                    # Final chunk
                    self._state = 'trailer'
                else:
                    self._state = 'data'

            elif self._state == 'data':
                # Read chunk data + trailing \r\n
                needed = self._chunk_remaining + 2
                if len(self._buf) < needed:
                    return  # Need more data

                before = len(self._buf)

                # Extract chunk data
                chunk_data = self._buf.split_to(self._chunk_remaining)

                # Extract trailing \r\n
                trailing = self._buf.split_to(2)
                trailing_bytes = ByteStreamBuffers.any_to_bytes(trailing)

                after = len(self._buf)

                if trailing_bytes != b'\r\n':
                    raise ValueError(f'Expected \\r\\n after chunk data, got {trailing_bytes!r}')

                # Emit chunk data
                ctx.feed_in(chunk_data)

                if (bfc := ctx.bytes_flow_control) is not None:
                    bfc.on_consumed(self, before - after)

                self._chunk_remaining = 0
                self._state = 'size'

            elif self._state == 'trailer':
                # Final \r\n after 0-size chunk
                if len(self._buf) < 2:
                    return  # Need more data

                before = len(self._buf)
                trailing = self._buf.split_to(2)
                after = len(self._buf)

                trailing_bytes = ByteStreamBuffers.any_to_bytes(trailing)

                if trailing_bytes != b'\r\n':
                    raise ValueError(f'Expected \\r\\n after final chunk, got {trailing_bytes!r}')

                if (bfc := ctx.bytes_flow_control) is not None:
                    bfc.on_consumed(self, before - after)

                # Emit end marker
                ctx.feed_in(PipelineHttpResponseEnd())

                self._state = 'done'
                return

            elif self._state == 'done':
                # Should not receive more data after completion
                if len(self._buf) > 0:
                    raise ValueError('Unexpected data after chunked encoding complete')
                return
