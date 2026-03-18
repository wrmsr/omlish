# ruff: noqa: UP006 UP045
# @omlish-lite
import collections
import dataclasses as dc
import typing as ta

from ....io.pipelines.bytes.buffering import InboundBytesBufferingIoPipelineHandler
from ....io.pipelines.core import IoPipelineHandlerContext
from ....io.pipelines.core import IoPipelineMessages
from ....io.pipelines.flow.types import IoPipelineFlow
from ....io.pipelines.flow.types import IoPipelineFlowMessages
from ....io.streams.utils import ByteStreamBuffers
from ....io.types import BytesLike
from ....lite.abstract import Abstract
from ..objects import IoPipelineHttpMessageBodyData
from ..objects import IoPipelineHttpMessageEnd
from ..objects import IoPipelineHttpMessageHead
from ..objects import IoPipelineHttpMessageObjects
from .codings import DefaultIoPiplineHttpCompressionCodings
from .codings import IoPiplineHttpDecompressorCoding
from .codings import IoPiplineHttpDecompressorCodings


##


@dc.dataclass(frozen=True)
class IoPipelineHttpDecompressionConfig:
    DEFAULT: ta.ClassVar['IoPipelineHttpDecompressionConfig']

    max_decomp_chunk: int = 64 * 1024  # max bytes emitted per inflate step

    max_decomp_total: ta.Optional[int] = None    # max total decompressed bytes per object
    max_expansion_ratio: ta.Optional[int] = 200  # max_out <= max(1, in_total) * ratio (+ small slack)

    max_out_pending: ta.Optional[int] = 256 * 1024  # cap decompressed bytes retained by this stage (if you buffer)

    # CPU Bounding: how many decompress steps to perform before yielding to the driver
    max_steps_per_call: ta.Optional[int] = None


IoPipelineHttpDecompressionConfig.DEFAULT = IoPipelineHttpDecompressionConfig()


#


class IoPipelineHttpObjectDecompressor(
    IoPipelineHttpMessageObjects,
    InboundBytesBufferingIoPipelineHandler,
    Abstract,
):
    def __init__(
            self,
            codings: ta.Optional[IoPiplineHttpDecompressorCodings] = None,
            config: IoPipelineHttpDecompressionConfig = IoPipelineHttpDecompressionConfig.DEFAULT,
    ) -> None:
        super().__init__()

        self._config = config
        if codings is None:
            codings = DefaultIoPiplineHttpCompressionCodings.DECOMPRESSOR
        self._codings = codings

        self._decompressor: ta.Optional[IoPiplineHttpDecompressorCoding] = None

        # Statistics for budget checks
        self._in_total_bytes = 0
        self._out_total_bytes = 0

        # Internal buffering
        self._in_pending: collections.deque[BytesLike] = collections.deque()
        self._in_pending_bytes = 0
        self._out_pending: collections.deque[BytesLike] = collections.deque()
        self._out_pending_bytes = 0

        # Flow Control and Deferral State
        self._read_requested = False
        self._pending_end: ta.Optional[IoPipelineHttpMessageEnd] = None

    #

    def inbound_buffered_bytes(self) -> int:
        return self._in_pending_bytes + self._out_pending_bytes

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
            raise ValueError('decompressor output exceeds limit (possible zip bomb)')

        if (mer := self._config.max_expansion_ratio) is not None:
            slack = self._config.max_decomp_chunk
            if self._out_total_bytes > (max(1, self._in_total_bytes) * mer + slack):
                raise ValueError('decompressor expansion ratio exceeds limit (possible zip bomb)')

    def _is_auto_read(self, ctx: IoPipelineHandlerContext) -> bool:
        if (flow := ctx.services.find(IoPipelineFlow)) is None:
            return True
        return flow.is_auto_read()

    def _emit_out_pending(self, ctx: IoPipelineHandlerContext) -> bool:
        """Returns True if at least one message was emitted."""

        emitted = False

        while self._out_pending and (self._is_auto_read(ctx) or self._read_requested):
            o = self._out_pending.popleft()
            self._out_pending_bytes -= len(o)

            if not self._is_auto_read(ctx):
                self._read_requested = False

            ctx.feed_in(self._make_body_data(o))
            emitted = True

            # In manual mode, we satisfy one 'read' at a time.
            if not self._is_auto_read(ctx):
                break

        return emitted

    def _pump(self, ctx: IoPipelineHandlerContext) -> bool:
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

            out = z.finish()
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

    def _defer_resume(self, ctx: IoPipelineHandlerContext) -> None:
        def resume(c: IoPipelineHandlerContext) -> None:
            # If a deferred pump satisfies a read, it must provide the FlushInput
            if self._pump(c) and not self._is_auto_read(c):
                c.feed_in(IoPipelineFlowMessages.FlushInput())

        ctx.defer(resume)

    #

    def _on_inbound_final_input(self, ctx: IoPipelineHandlerContext, msg: IoPipelineMessages.FinalInput) -> None:
        if self._decompressor is None:
            ctx.feed_in(msg)
            return

        self._reset()

        ctx.feed_in(self._make_aborted('eof before end of message'))
        ctx.feed_in(msg)

    def _on_inbound_flush_input(self, ctx: IoPipelineHandlerContext, msg: IoPipelineFlowMessages.FlushInput) -> None:
        self._pump(ctx)
        ctx.feed_in(msg)

    def _on_inbound_head(self, ctx: IoPipelineHandlerContext, msg: IoPipelineHttpMessageHead) -> None:
        if self._decompressor is not None:
            ctx.feed_in(self._make_aborted('unexpected message sequence'))
            return

        enc = msg.headers.lower.get('content-encoding', ())

        # TODO: spec is actually an ordered stack lol
        for coding_name, coding in self._codings.items():
            if coding_name.lower() in enc:
                self._decompressor = coding()
                break

        ctx.feed_in(msg)

    def _on_inbound_body_data(self, ctx: IoPipelineHandlerContext, msg: IoPipelineHttpMessageBodyData) -> None:
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

    def _on_inbound_end(self, ctx: IoPipelineHandlerContext, msg: IoPipelineHttpMessageEnd) -> None:
        if self._decompressor is None:
            ctx.feed_in(msg)
            return

        self._pending_end = msg
        self._pump(ctx)

    def inbound(self, ctx: IoPipelineHandlerContext, msg: ta.Any) -> None:
        if isinstance(msg, IoPipelineMessages.FinalInput):
            self._on_inbound_final_input(ctx, msg)

        elif isinstance(msg, IoPipelineFlowMessages.FlushInput):
            self._on_inbound_flush_input(ctx, msg)

        elif isinstance(msg, self._head_type):
            self._on_inbound_head(ctx, msg)

        elif isinstance(msg, self._body_data_type):
            self._on_inbound_body_data(ctx, msg)

        elif isinstance(msg, self._end_type):
            self._on_inbound_end(ctx, msg)

        else:
            ctx.feed_in(msg)

    #

    def _on_outbound_ready_for_input(self, ctx: IoPipelineHandlerContext, msg: IoPipelineFlowMessages.ReadyForInput) -> None:  # Noqa
        self._read_requested = True

        if self._out_pending or (self._decompressor is not None and self._in_pending):
            if self._pump(ctx):
                if not self._is_auto_read(ctx):
                    ctx.feed_in(IoPipelineFlowMessages.FlushInput())

                return  # Swallow since we satisfied it

        ctx.feed_out(msg)

    def outbound(self, ctx: IoPipelineHandlerContext, msg: ta.Any) -> None:
        if isinstance(msg, IoPipelineFlowMessages.ReadyForInput):
            self._on_outbound_ready_for_input(ctx, msg)

        else:
            ctx.feed_out(msg)
