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

        head = self._parse_head(ByteStreamBuffers.to_bytes(head_view))
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
