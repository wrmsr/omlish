# ruff: noqa: UP006 UP045
# @omlish-lite
import collections
import dataclasses as dc
import typing as ta
import zlib

from omlish.http.headers import HttpHeaders
from omlish.http.parsing import HttpParser
from omlish.http.parsing import ParsedHttpMessage
from omlish.io.streams.types import BytesLikeOrMemoryview
from omlish.io.streams.utils import ByteStreamBuffers
from omlish.lite.check import check

from ...bytes.buffering import InboundBytesBufferingChannelPipelineHandler
from ...core import ChannelPipelineHandlerContext
from ...core import ChannelPipelineMessages
from ...flow.types import ChannelPipelineFlow
from ...flow.types import ChannelPipelineFlowMessages
from ..decoders import ChunkedPipelineHttpContentChunkDecoder
from ..decoders import PipelineHttpDecodingConfig
from ..decoders import PipelineHttpDecodingMessageAdapter
from ..decoders import PipelineHttpHeadDecoder
from ..responses import PipelineHttpResponseAborted
from ..responses import PipelineHttpResponseContentChunkData
from ..responses import PipelineHttpResponseEnd
from ..responses import PipelineHttpResponseHead


##


class ResponsePipelineHttpDecodingMessageAdapter(PipelineHttpDecodingMessageAdapter):
    def make_head(self, parsed: ParsedHttpMessage) -> ta.Any:
        status = check.not_none(parsed.status_line)

        return PipelineHttpResponseHead(
            version=status.http_version,
            status=status.status_code,
            reason=status.reason_phrase,
            headers=HttpHeaders(parsed.headers.entries),
            parsed=parsed,
        )

    def make_aborted(self, reason: str) -> ta.Any:
        return PipelineHttpResponseAborted(reason)

    def make_content_chunk_data(self, data: BytesLikeOrMemoryview) -> ta.Any:
        return PipelineHttpResponseContentChunkData(data)

    def make_end(self) -> ta.Any:
        return PipelineHttpResponseEnd()


##


class PipelineHttpResponseDecoder(InboundBytesBufferingChannelPipelineHandler):
    """HTTP/1.x response head decoder."""

    def __init__(
            self,
            *,
            config: PipelineHttpDecodingConfig = PipelineHttpDecodingConfig.DEFAULT,
    ) -> None:
        super().__init__()

        self._decoder = PipelineHttpHeadDecoder(
            ResponsePipelineHttpDecodingMessageAdapter(),
            HttpParser.Mode.RESPONSE,
            config=config,
        )

    def inbound_buffered_bytes(self) -> int:
        return self._decoder.inbound_buffered_bytes()

    def inbound(self, ctx: ChannelPipelineHandlerContext, msg: ta.Any) -> None:
        if self._decoder.done:
            ctx.feed_in(msg)
            return

        if isinstance(msg, ChannelPipelineFlowMessages.FlushInput):
            if not ctx.services[ChannelPipelineFlow].is_auto_read():
                ctx.feed_out(ChannelPipelineFlowMessages.ReadyForInput())

            ctx.feed_in(msg)
            return

        for dec_msg in self._decoder.inbound(msg):
            ctx.feed_in(dec_msg)


##


@dc.dataclass(frozen=True)
class PipelineHttpCompressionDecodingConfig:
    DEFAULT: ta.ClassVar['PipelineHttpCompressionDecodingConfig']

    max_decomp_chunk: int = 64 * 1024  # max bytes emitted per inflate step

    max_decomp_total: ta.Optional[int] = None    # max total decompressed bytes per response
    max_expansion_ratio: ta.Optional[int] = 200  # max_out <= max(1, in_total) * ratio (+ small slack)

    max_out_pending: ta.Optional[int] = 256 * 1024  # cap decompressed bytes retained by this stage (if you buffer)


PipelineHttpCompressionDecodingConfig.DEFAULT = PipelineHttpCompressionDecodingConfig()


#


class PipelineHttpResponseConditionalGzipDecoder(InboundBytesBufferingChannelPipelineHandler):
    """
    Conditional streaming gzip decompression.

    Watches for DecodedHttpResponseHead; if Content-Encoding includes 'gzip', enable zlib decompressor for body bytes.
    Flushes on EOF.
    """

    def __init__(
            self,
            *,
            config: PipelineHttpCompressionDecodingConfig = PipelineHttpCompressionDecodingConfig.DEFAULT,
    ) -> None:
        super().__init__()

        self._config = config
        self._enabled = False
        self._z: ta.Optional[ta.Any] = None

        # Internal buffering
        self._in_pending: collections.deque[BytesLikeOrMemoryview] = collections.deque()
        self._in_pending_bytes = 0
        self._out_pending: collections.deque[BytesLikeOrMemoryview] = collections.deque()
        self._out_pending_bytes = 0

        # Flow Control State
        self._read_requested = False

    def inbound_buffered_bytes(self) -> int:
        return self._in_pending_bytes + self._out_pending_bytes

    def _reset(self) -> None:
        self._in_total_bytes = 0
        self._out_total_bytes = 0

        self._in_pending.clear()
        self._in_pending_bytes = 0

        self._out_pending.clear()
        self._out_pending_bytes = 0

    def _check_budgets(self) -> None:
        if (mdt := self._config.max_decomp_total) is not None and self._out_total_bytes > mdt:
            raise ValueError('gzip output exceeds limit (possible zip bomb)')

        if (mer := self._config.max_expansion_ratio) is not None:
            slack = self._config.max_decomp_chunk
            if self._out_total_bytes > (max(1, self._in_total_bytes) * mer + slack):
                raise ValueError('gzip expansion ratio exceeds limit (possible zip bomb)')

    def _is_auto_read(self, ctx: ChannelPipelineHandlerContext) -> bool:
        if (flow := ctx.services.find(ChannelPipelineFlow)) is None:
            return True
        return flow.is_auto_read()

    def _emit_out_pending(self, ctx: ChannelPipelineHandlerContext) -> None:
        # We emit if:
        # 1. We have data AND
        # 2. (Auto-read is on OR downstream specifically asked via ReadyForInput)
        while self._out_pending and (self._is_auto_read(ctx) or self._read_requested):
            o = self._out_pending.popleft()
            self._out_pending_bytes -= len(o)

            # In manual mode, we've now satisfied the specific request that was pending
            if not self._is_auto_read(ctx):
                self._read_requested = False

            ctx.feed_in(o)

    def _pump(self, ctx: ChannelPipelineHandlerContext) -> None:
        z = self._z
        if z is None:
            return

        # 1. Try to clear existing output buffer first
        self._emit_out_pending(ctx)

        # 2. If we still have output pending, we are "blocked" by downstream
        if self._out_pending:
            return

        # 3. Decompress input into output pending
        while self._in_pending:
            # Enforce output budget
            if (mop := self._config.max_out_pending) is not None:
                if self._out_pending_bytes >= mop:
                    break

            chunk = self._in_pending.popleft()
            cl = len(chunk)
            self._in_pending_bytes -= cl

            # Note: Using max_decomp_chunk as a limit to prevent CPU pinning
            out = z.decompress(chunk, self._config.max_decomp_chunk)

            if out:
                self._out_pending.append(out)
                self._out_pending_bytes += len(out)
                self._check_budgets()

                # Try to emit immediately if allowed
                self._emit_out_pending(ctx)

                # If we filled the output buffer or consumed a read request, stop pumping
                if self._out_pending:
                    break

            # Handle unconsumed tail (same as your previous logic)
            ut = z.unconsumed_tail
            if ut:
                self._in_pending.appendleft(ut)
                self._in_pending_bytes += len(ut)
                if not out:  # Stuck
                    break

    def inbound(self, ctx: ChannelPipelineHandlerContext, msg: ta.Any) -> None:
        if isinstance(msg, ChannelPipelineMessages.FinalInput):
            if self._enabled and self._z is not None:
                # 1. Final pump of any remaining pending input
                self._pump(ctx)
                # 2. Extract trailing bytes from zlib (footer/checksum)
                # We don't use _pump here because flush() doesn't take input
                try:
                    out = self._z.flush()
                    if out:
                        self._out_pending.append(out)
                        self._out_pending_bytes += len(out)
                        self._emit_out_pending(ctx)
                except Exception:  # noqa
                    raise  # or handle decompression error  # noqa

            ctx.feed_in(msg)
            return

        if isinstance(msg, ChannelPipelineFlowMessages.FlushInput):
            self._pump(ctx)
            ctx.feed_in(msg)
            return

        if isinstance(msg, PipelineHttpResponseHead):
            enc = msg.headers.lower.get('content-encoding', ())
            self._enabled = 'gzip' in enc
            self._z = zlib.decompressobj(16 + zlib.MAX_WBITS) if self._enabled else None
            self._reset()
            ctx.feed_in(msg)
            return

        if not self._enabled or self._z is None or not ByteStreamBuffers.can_bytes(msg):
            ctx.feed_in(msg)
            return

        # Buffer new compressed data
        for mv in ByteStreamBuffers.iter_segments(msg):
            self._in_pending.append(mv)
            self._in_pending_bytes += len(mv)
            self._check_budgets()

        self._pump(ctx)

    def outbound(self, ctx: ChannelPipelineHandlerContext, msg: ta.Any) -> None:
        if isinstance(msg, ChannelPipelineFlowMessages.ReadyForInput):
            # Mark that downstream is hungry
            self._read_requested = True

            # Try to satisfy from internal buffers (both pending out and pending in)
            if self._out_pending or (self._enabled and self._in_pending):
                self._pump(ctx)

                # If we successfully emitted data, we consumed the 'ReadyForInput'. We return early so the message
                # doesn't go upstream.
                if not self._read_requested:
                    return

        # Otherwise, pass it up (including FlushOutput or unsatisfied ReadyForInput)
        ctx.feed_out(msg)


##


class PipelineHttpResponseChunkedDecoder(InboundBytesBufferingChannelPipelineHandler):
    def __init__(
            self,
            *,
            config: PipelineHttpDecodingConfig = PipelineHttpDecodingConfig.DEFAULT,
    ) -> None:
        super().__init__()

        self._config = config

        self._decoder: ta.Optional[ChunkedPipelineHttpContentChunkDecoder] = None

    def inbound_buffered_bytes(self) -> ta.Optional[int]:
        if (dec := self._decoder) is None:
            return 0
        return dec.inbound_buffered_bytes()

    def inbound(self, ctx: ChannelPipelineHandlerContext, msg: ta.Any) -> None:
        if isinstance(msg, PipelineHttpResponseHead):
            check.none(self._decoder)

            if msg.headers.contains_value('transfer-encoding', 'chunked', ignore_case=True):
                self._decoder = ChunkedPipelineHttpContentChunkDecoder(
                    ResponsePipelineHttpDecodingMessageAdapter(),
                    config=self._config,
                )

            ctx.feed_in(msg)
            return

        if (dec := self._decoder) is None:
            ctx.feed_in(msg)
            return

        if isinstance(msg, ChannelPipelineFlowMessages.FlushInput):
            if not ctx.services[ChannelPipelineFlow].is_auto_read():
                ctx.feed_out(ChannelPipelineFlowMessages.ReadyForInput())

            ctx.feed_in(msg)
            return

        for dec_msg in dec.inbound(msg):
            ctx.feed_in(dec_msg)

        if dec.done:
            self._decoder = None
