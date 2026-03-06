# ruff: noqa: UP006 UP045
# @omlish-lite
import abc
import collections
import dataclasses as dc
import typing as ta
import zlib

from omlish.io.streams.types import BytesLikeOrMemoryview
from omlish.io.streams.utils import ByteStreamBuffers
from omlish.lite.abstract import Abstract

from ..bytes.buffering import InboundBytesBufferingChannelPipelineHandler
from ..core import ChannelPipelineHandlerContext
from ..core import ChannelPipelineMessages
from ..flow.types import ChannelPipelineFlow
from ..flow.types import ChannelPipelineFlowMessages
from .objects import PipelineHttpMessageObjects
from .objects import PipelineHttpMessageHead
from .objects import PipelineHttpMessageEnd
from .objects import PipelineHttpMessageContentChunkData


##


@dc.dataclass(frozen=True)
class PipelineHttpDecompressionConfig:
    DEFAULT: ta.ClassVar['PipelineHttpDecompressionConfig']

    max_decomp_chunk: int = 64 * 1024  # max bytes emitted per inflate step

    max_decomp_total: ta.Optional[int] = None    # max total decompressed bytes per object
    max_expansion_ratio: ta.Optional[int] = 200  # max_out <= max(1, in_total) * ratio (+ small slack)

    max_out_pending: ta.Optional[int] = 256 * 1024  # cap decompressed bytes retained by this stage (if you buffer)

    # CPU Bounding: how many decompress steps to perform before yielding to the driver
    max_steps_per_call: ta.Optional[int] = 10


PipelineHttpDecompressionConfig.DEFAULT = PipelineHttpDecompressionConfig()


#


class PipelineHttpObjectDecompressor(
    PipelineHttpMessageObjects,
    InboundBytesBufferingChannelPipelineHandler,
    Abstract,
):
    """Conditional streaming gzip decompression with CPU-bounding and flow control."""

    def __init__(
            self,
            *,
            config: PipelineHttpDecompressionConfig = PipelineHttpDecompressionConfig.DEFAULT,
    ) -> None:
        super().__init__()

        self._config = config

        self._decompressor: ta.Optional[PipelineHttpObjectDecompressor.Decompressor] = None

        # Statistics for budget checks
        self._in_total_bytes = 0
        self._out_total_bytes = 0

        # Internal buffering
        self._in_pending: collections.deque[BytesLikeOrMemoryview] = collections.deque()
        self._in_pending_bytes = 0
        self._out_pending: collections.deque[BytesLikeOrMemoryview] = collections.deque()
        self._out_pending_bytes = 0

        # Flow Control and Deferral State
        self._read_requested = False
        self._pending_end: ta.Optional[PipelineHttpMessageEnd] = None

    #

    def inbound_buffered_bytes(self) -> int:
        return self._in_pending_bytes + self._out_pending_bytes

    #

    class Decompressor(Abstract):
        @abc.abstractmethod
        def decompress(
                self,
                data: BytesLikeOrMemoryview,
                max_bytes: ta.Optional[int] = None,
                /,
        ) -> ta.Optional[BytesLikeOrMemoryview]:
            raise NotImplementedError

        @abc.abstractmethod
        def unconsumed_tail(self) -> ta.Optional[BytesLikeOrMemoryview]:
            raise NotImplementedError

        @abc.abstractmethod
        def flush(self) -> ta.Optional[BytesLikeOrMemoryview]:
            raise NotImplementedError

    #

    class ZlibDecompressor(Decompressor):
        def __init__(self, wbits: int = 16 + zlib.MAX_WBITS) -> None:
            self._z = zlib.decompressobj(wbits)

        def decompress(
                self,
                data: BytesLikeOrMemoryview,
                max_bytes: ta.Optional[int] = None,
                /,
        ) -> ta.Optional[BytesLikeOrMemoryview]:
            return self._z.decompress(data, max_bytes or 0)

        def unconsumed_tail(self) -> ta.Optional[BytesLikeOrMemoryview]:
            return self._z.unconsumed_tail

        def flush(self) -> ta.Optional[BytesLikeOrMemoryview]:
            return self._z.flush()

    #

    def _reset(self) -> None:
        self._decompressor = None

        self._in_total_bytes = 0
        self._out_total_bytes = 0

        self._in_pending.clear()
        self._in_pending_bytes = 0
        self._out_pending.clear()
        self._out_pending_bytes = 0

        self._pending_end = None

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

    def _emit_out_pending(self, ctx: ChannelPipelineHandlerContext) -> bool:
        """Returns True if at least one message was emitted."""

        emitted = False

        while self._out_pending and (self._is_auto_read(ctx) or self._read_requested):
            o = self._out_pending.popleft()
            self._out_pending_bytes -= len(o)

            if not self._is_auto_read(ctx):
                self._read_requested = False

            ctx.feed_in(self._make_content_chunk_data(o))
            emitted = True

            # In manual mode, we satisfy one 'read' at a time.
            if not self._is_auto_read(ctx):
                break

        return emitted

    def _pump(self, ctx: ChannelPipelineHandlerContext) -> bool:
        """Returns True if it effectively satisfied a read request."""

        z = self._decompressor
        if z is None:
            return False

        steps = 0
        max_steps = self._config.max_steps_per_call

        # 1. Try to clear existing output.
        if self._emit_out_pending(ctx):
            if not self._is_auto_read(ctx):
                return True

        # 2. If blocked by downstream, we can't satisfy anything.
        if self._out_pending:
            return False

        # 3. Decompression Loop
        while self._in_pending:
            # Enforce output buffer budget
            if (mop := self._config.max_out_pending) is not None:
                if self._out_pending_bytes >= mop:
                    break

            # Check for CPU step limit
            if max_steps is not None and steps >= max_steps:
                self._defer_resume(ctx)
                return False  # We haven't satisfied it yet, we deferred.

            steps += 1
            chunk = self._in_pending.popleft()
            cl = len(chunk)
            self._in_pending_bytes -= cl

            out = z.decompress(chunk, self._config.max_decomp_chunk)
            if out:
                ol = len(out)
                self._out_total_bytes += ol
                self._out_pending.append(out)
                self._out_pending_bytes += ol
                self._check_budgets()

                if self._emit_out_pending(ctx):
                    if not self._is_auto_read(ctx):
                        return True  # Satisfied!

            ut = z.unconsumed_tail()
            if ut:
                self._in_pending.appendleft(ut)
                self._in_pending_bytes += len(ut)
                if not out:
                    break

        # 4. Handle EOF
        if not self._in_pending and self._pending_end is not None:
            if max_steps is not None and steps >= max_steps:
                self._defer_resume(ctx)
                return False

            out = z.flush()
            if out:
                ol = len(out)
                self._out_total_bytes += ol
                self._out_pending.append(out)
                self._out_pending_bytes += ol
                self._check_budgets()
                self._emit_out_pending(ctx)

            msg = self._pending_end
            self._pending_end = None
            self._read_requested = False
            ctx.feed_in(msg)
            return True  # FinalInput counts as satisfying the last read

        return False

    def _defer_resume(self, ctx: ChannelPipelineHandlerContext) -> None:
        def resume(c: ChannelPipelineHandlerContext) -> None:
            # If a deferred pump satisfies a read, it must provide the FlushInput
            if self._pump(c) and not self._is_auto_read(c):
                c.feed_in(ChannelPipelineFlowMessages.FlushInput())

        ctx.defer(resume)

    #

    def _on_inbound_final_input(self, ctx: ChannelPipelineHandlerContext, msg: ChannelPipelineMessages.FinalInput) -> None:  # noqa
        if self._decompressor is None:
            ctx.feed_in(msg)
            return

        self._reset()

        ctx.feed_in(self._make_aborted('eof before end of message'))
        ctx.feed_in(msg)

    def _on_inbound_flush_input(self, ctx: ChannelPipelineHandlerContext, msg: ChannelPipelineFlowMessages.FlushInput) -> None:  # noqa
        self._pump(ctx)
        ctx.feed_in(msg)

    def _on_inbound_head(self, ctx: ChannelPipelineHandlerContext, msg: PipelineHttpMessageHead) -> None:  # noqa
        if self._decompressor is not None:
            ctx.feed_in(self._make_aborted('unexpected message sequence'))
            return

        enc = msg.headers.lower.get('content-encoding', ())

        if 'gzip' in enc:
            self._decompressor = self.ZlibDecompressor()

        ctx.feed_in(msg)

    def _on_inbound_content_chunk_data(self, ctx: ChannelPipelineHandlerContext, msg: PipelineHttpMessageContentChunkData) -> None:  # noqa
        if self._decompressor is None:
            ctx.feed_in(msg)
            return

        for mv in ByteStreamBuffers.iter_segments(msg.data):
            mvl = len(mv)
            self._in_total_bytes += mvl
            self._in_pending.append(mv)
            self._in_pending_bytes += mvl
            self._check_budgets()

        self._pump(ctx)

    def _on_inbound_end(self, ctx: ChannelPipelineHandlerContext, msg: PipelineHttpMessageEnd) -> None:
        if self._decompressor is None:
            ctx.feed_in(msg)
            return

        self._pending_end = msg
        self._pump(ctx)

    def inbound(self, ctx: ChannelPipelineHandlerContext, msg: ta.Any) -> None:
        if isinstance(msg, ChannelPipelineMessages.FinalInput):
            self._on_inbound_final_input(ctx, msg)

        elif isinstance(msg, ChannelPipelineFlowMessages.FlushInput):
            self._on_inbound_flush_input(ctx, msg)

        elif isinstance(msg, self._head_type):
            self._on_inbound_head(ctx, msg)

        elif isinstance(msg, self._content_chunk_data_type):
            self._on_inbound_content_chunk_data(ctx, msg)

        elif isinstance(msg, self._end_type):
            self._on_inbound_end(ctx, msg)

        else:
            ctx.feed_in(msg)

    #

    def _on_outbound_ready_for_input(self, ctx: ChannelPipelineHandlerContext, msg: ChannelPipelineFlowMessages.ReadyForInput) -> None:  # Noqa
        self._read_requested = True

        if self._out_pending or (self._decompressor is not None and self._in_pending):
            if self._pump(ctx):
                if not self._is_auto_read(ctx):
                    ctx.feed_in(ChannelPipelineFlowMessages.FlushInput())

                return  # Swallow since we satisfied it

        ctx.feed_out(msg)

    def outbound(self, ctx: ChannelPipelineHandlerContext, msg: ta.Any) -> None:
        if isinstance(msg, ChannelPipelineFlowMessages.ReadyForInput):
            self._on_outbound_ready_for_input(ctx, msg)

        else:
            ctx.feed_out(msg)
