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

    max_in_pending: ta.Optional[int] = 256 * 1024   # cap compressed bytes retained by this stage
    max_out_pending: ta.Optional[int] = 256 * 1024  # cap decompressed bytes retained by this stage (if you buffer)


PipelineHttpCompressionDecodingConfig.DEFAULT = PipelineHttpCompressionDecodingConfig()


#


class PipelineHttpResponseConditionalGzipDecoder(InboundBytesBufferingChannelPipelineHandler):
    """
    Conditional streaming gzip decompression.

    Watches for DecodedHttpResponseHead; if Content-Encoding includes 'gzip', enable zlib decompressor for body bytes.
    Flushes on EOF.

    FIXME:
     - flow control messages lol
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

        self._in_total_bytes = 0
        self._out_total_bytes = 0

        self._in_pending: collections.deque[BytesLikeOrMemoryview] = collections.deque()
        self._in_pending_bytes = 0

        self._out_pending: collections.deque[BytesLikeOrMemoryview] = collections.deque()
        self._out_pending_bytes = 0

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

        if (mip := self._config.max_in_pending) is not None and self._in_pending_bytes > mip:
            raise ValueError('gzip compressed pending exceeds limit (flow control)')

        if (mop := self._config.max_out_pending) is not None and self._out_pending_bytes > mop:
            raise ValueError('gzip output pending exceeds limit (flow control)')

    def _emit_out_pending(self, ctx: ChannelPipelineHandlerContext) -> None:
        while self._out_pending:
            o = self._out_pending.popleft()
            self._out_pending_bytes -= len(o)
            ctx.feed_in(o)
        check.state(self._out_pending_bytes == 0)

    def _pump(self, ctx: ChannelPipelineHandlerContext) -> None:
        """
        Drain pending compressed input through zlib into output, under strict bounds. Stops when it can't make progress
        or would exceed pending caps.
        """

        z = self._z
        if z is None:
            return

        # First, flush any already buffered output if you buffer at all.
        self._emit_out_pending(ctx)

        # Pump while we have input and output headroom.
        while self._in_pending:
            # If we're buffering output, enforce some headroom; if you emit immediately, max_out_pending can be 0 and
            # this stays trivial.
            if (mop := self._config.max_out_pending) is not None:
                out_headroom = mop - self._out_pending_bytes
                if out_headroom <= 0:
                    break

                # Always bound per-call production.
                cap = min(self._config.max_decomp_chunk, out_headroom)

            else:
                cap = self._config.max_decomp_chunk

            # Feed *some* input. You can choose a slice size to avoid huge mv creation. This also makes max_in_pending
            # meaningful.
            chunk = self._in_pending.popleft()
            cl = len(chunk)
            self._in_pending_bytes -= cl

            out = z.decompress(chunk, cap)
            if out:
                ol = len(out)
                self._out_total_bytes += ol
                self._out_pending.append(out)
                self._out_pending_bytes += ol
                self._check_budgets()
                self._emit_out_pending(ctx)

            # Now: advance input by how much zlib actually consumed.
            #
            # CPython doesn't directly expose "bytes consumed" from the arg, but you can infer it using unconsumed_tail:
            # it's the portion of the provided input zlib didn't consume.
            ut = z.unconsumed_tail
            utl = len(ut)
            if ut:
                consumed = cl - utl
                if consumed <= 0:
                    # No input consumed; if also no output produced, we're stuck.
                    if not out:
                        # break
                        raise NotImplementedError

                    # If we produced output but consumed nothing, loop continues bounded by cap.
                    self._in_pending.appendleft(b'')

                else:
                    # Keep remainder as pending
                    self._in_pending.appendleft(ut)
                    self._in_pending_bytes += utl

            # Budget check also covers in/out pending sizes
            self._check_budgets()

            # If neither output nor input consumption happened, stop.
            if not out and ut and utl == cl:
                break

    def inbound(self, ctx: ChannelPipelineHandlerContext, msg: ta.Any) -> None:
        if isinstance(msg, ChannelPipelineMessages.FinalInput):
            if self._enabled and self._z is not None:
                # Drain any remaining pending input first
                self._pump(ctx)

                while True:
                    out = self._z.flush(self._config.max_decomp_chunk)
                    if not out:
                        break
                    ol = len(out)
                    self._out_total_bytes += ol
                    self._out_pending.append(out)
                    self._out_pending_bytes += ol
                    self._check_budgets()
                    self._emit_out_pending(ctx)

            ctx.feed_in(msg)
            return

        if isinstance(msg, PipelineHttpResponseHead):
            enc = msg.headers.lower.get('content-encoding', ())
            self._enabled = 'gzip' in enc
            self._z = zlib.decompressobj(16 + zlib.MAX_WBITS) if self._enabled else None
            self._reset()
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
            mvl = len(mv)
            self._in_total_bytes += mvl
            self._in_pending.append(mv)
            self._in_pending_bytes += mvl
            self._check_budgets()
            self._pump(ctx)


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
