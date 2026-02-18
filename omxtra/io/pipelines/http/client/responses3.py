# ruff: noqa: UP006 UP045
# @omlish-lite
import typing as ta
import zlib

from omlish.io.streams.utils import ByteStreamBuffers

from ...core import ChannelPipelineHandler
from ...core import ChannelPipelineHandlerContext
from ...core import ChannelPipelineMessages
from ..responses import PipelineHttpResponseHead


##


class PipelineHttpResponseConditionalGzipDecoder3(ChannelPipelineHandler):
    MAX_DECOMP_CHUNK = 64 * 1024
    MAX_DECOMP_TOTAL = 256 * 1024 * 1024
    MAX_EXPANSION_RATIO = 200

    MAX_IN_PENDING = 256 * 1024        # cap compressed bytes retained by this stage
    MAX_OUT_PENDING = 256 * 1024       # cap decompressed bytes retained by this stage (if you buffer)

    def __init__(self) -> None:
        super().__init__()
        self._enabled = False
        self._z: ta.Optional[ta.Any] = None

        self._in_total = 0
        self._out_total = 0

        self._in_pending = bytearray()
        self._out_pending = bytearray()  # optional; you can skip if you always emit immediately

    def inbound_buffered_bytes(self) -> int:
        # Now flow-control accounting is fully under your control.
        return len(self._in_pending) + len(self._out_pending)

    def _reset(self) -> None:
        self._in_total = 0
        self._out_total = 0
        self._in_pending.clear()
        self._out_pending.clear()

    def _check_budgets(self) -> None:
        if self._out_total > self.MAX_DECOMP_TOTAL:
            raise ValueError('gzip output exceeds limit (possible zip bomb)')

        slack = self.MAX_DECOMP_CHUNK
        if self._out_total > (max(1, self._in_total) * self.MAX_EXPANSION_RATIO + slack):
            raise ValueError('gzip expansion ratio exceeds limit (possible zip bomb)')

        if len(self._in_pending) > self.MAX_IN_PENDING:
            raise ValueError('gzip compressed pending exceeds limit (flow control)')

        if len(self._out_pending) > self.MAX_OUT_PENDING:
            raise ValueError('gzip output pending exceeds limit (flow control)')

    def _emit_out_pending(self, ctx: ChannelPipelineHandlerContext) -> None:
        # If you don't yet have downstream backpressure, just flush immediately.
        if self._out_pending:
            ctx.feed_in(bytes(self._out_pending))
            self._out_pending.clear()

    def _pump(self, ctx: ChannelPipelineHandlerContext) -> None:
        """
        Drain pending compressed input through zlib into output, under strict bounds.
        Stops when it can't make progress or would exceed pending caps.
        """
        z = self._z
        if z is None:
            return

        # First, flush any already buffered output if you buffer at all.
        self._emit_out_pending(ctx)

        # Pump while we have input and output headroom.
        while self._in_pending:
            # If we're buffering output, enforce some headroom;
            # if you emit immediately, MAX_OUT_PENDING can be 0 and this stays trivial.
            out_headroom = self.MAX_OUT_PENDING - len(self._out_pending)
            if out_headroom <= 0:
                break

            # Always bound per-call production.
            cap = min(self.MAX_DECOMP_CHUNK, out_headroom)

            # Feed *some* input. You can choose a slice size to avoid huge mv creation.
            # This also makes MAX_IN_PENDING meaningful.
            chunk = memoryview(self._in_pending)

            out = z.decompress(chunk, cap)
            if out:
                self._out_total += len(out)
                self._out_pending += out
                self._check_budgets()
                self._emit_out_pending(ctx)

            # Now: advance input by how much zlib actually consumed.
            #
            # CPython doesn't directly expose "bytes consumed" from the arg, but you can infer it using unconsumed_tail:
            # it's the portion of the provided input zlib didn't consume.
            ut = z.unconsumed_tail
            if ut:
                consumed = len(chunk) - len(ut)
                if consumed <= 0:
                    # No input consumed; if also no output produced, we're stuck.
                    if not out:
                        break
                    # If we produced output but consumed nothing, loop continues bounded by cap.
                else:
                    del self._in_pending[:consumed]
                    # Keep remainder as pending (ut is a view into the provided bytes, but we've preserved it by keeping
                    # _in_pending).
            else:
                # All consumed
                del self._in_pending[:]

            # Budget check also covers in/out pending sizes
            self._check_budgets()

            # If neither output nor input consumption happened, stop.
            if not out and ut and len(ut) == len(chunk):
                break

    def inbound(self, ctx: ChannelPipelineHandlerContext, msg: ta.Any) -> None:
        if isinstance(msg, ChannelPipelineMessages.Eof):
            if self._enabled and self._z is not None:
                # Drain any remaining pending input first
                self._pump(ctx)

                # Then flush zlib incrementally under cap
                while True:
                    out = self._z.flush(self.MAX_DECOMP_CHUNK)
                    if not out:
                        break
                    self._out_total += len(out)
                    self._out_pending += out
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

        # Append bytes to our own pending buffer.
        for mv in ByteStreamBuffers.iter_segments(msg):
            self._in_total += len(mv)
            self._in_pending += mv
            self._check_budgets()
            self._pump(ctx)
