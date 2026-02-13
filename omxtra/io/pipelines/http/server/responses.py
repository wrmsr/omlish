# ruff: noqa: UP006 UP045
# @omlish-lite
import typing as ta
import zlib

from omlish.io.streams.segmented import SegmentedByteStreamBuffer
from omlish.io.streams.utils import ByteStreamBuffers

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

    def buffered_bytes(self) -> int:
        return len(self._buf)

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

        before = len(self._buf)

        for mv in ByteStreamBuffers.iter_segments(msg):
            if mv:
                self._buf.write(mv)

        i = self._buf.find(b'\r\n\r\n')
        if i < 0:
            return

        head_view = self._buf.split_to(i + 4)
        head = self._parse_head(ByteStreamBuffers.to_bytes(head_view))
        self._got_head = True

        after = len(self._buf)
        if (bfc := ctx.bytes_flow_control) is not None:
            bfc.on_consumed(before - after + (i + 4))

        ctx.feed_in(head)

        if len(self._buf):
            before2 = len(self._buf)
            body_view = self._buf.split_to(before2)
            if (bfc := ctx.bytes_flow_control) is not None:
                bfc.on_consumed(before2)
            ctx.feed_in(body_view)

    def _parse_head(self, raw: bytes) -> PipelineHttpResponseHead:
        text = raw.decode('iso-8859-1', errors='replace')
        lines = text.split('\r\n')
        while lines and lines[-1] == '':
            lines.pop()
        if not lines:
            raise ValueError('bad http response head')

        status_line = lines[0]
        parts = status_line.split(' ', 2)
        if len(parts) < 2:
            raise ValueError('bad http status line')

        version = parts[0].strip()
        try:
            status = int(parts[1])
        except ValueError:
            raise ValueError('bad http status code') from None
        reason = parts[2].strip() if len(parts) > 2 else ''

        headers: ta.Dict[str, str] = {}
        for ln in lines[1:]:
            if not ln or ':' not in ln:
                continue
            k, v = ln.split(':', 1)
            headers[k.strip().casefold()] = v.lstrip(' \t').strip()

        return PipelineHttpResponseHead(
            version=version,
            status=status,
            reason=reason,
            headers=headers,
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
            enc = (msg.header('content-encoding') or '').lower()
            self._enabled = ('gzip' in enc)
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
