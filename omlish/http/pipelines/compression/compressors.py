# ruff: noqa: UP006 UP045
# @omlish-lite
import collections
import dataclasses as dc
import typing as ta

from ....io.pipelines.core import IoPipelineHandlerContext
from ....io.pipelines.core import IoPipelineMessages
from ....io.streams.types import BytesLike
from ....io.streams.utils import ByteStreamBuffers
from ....lite.abstract import Abstract
from ..objects import IoPipelineHttpMessageBodyData
from ..objects import IoPipelineHttpMessageEnd
from ..objects import IoPipelineHttpMessageHead
from ..objects import IoPipelineHttpMessageObjects
from .codings import DefaultIoPiplineHttpCompressionCodings
from .codings import IoPiplineHttpCompressorCoding
from .codings import IoPiplineHttpCompressorCodings


##


@dc.dataclass(frozen=True)
class IoPipelineHttpCompressionConfig:
    DEFAULT: ta.ClassVar['IoPipelineHttpCompressionConfig']

    max_comp_chunk: int = 64 * 1024  # max bytes emitted per compress step

    # CPU Bounding: how many compress steps to perform before yielding to the driver
    max_steps_per_call: ta.Optional[int] = None


IoPipelineHttpCompressionConfig.DEFAULT = IoPipelineHttpCompressionConfig()


#


class IoPipelineHttpObjectCompressor(
    IoPipelineHttpMessageObjects,
    Abstract,
):
    """Conditional streaming gzip compression with CPU-bounding."""

    def __init__(
            self,
            codings: ta.Optional[IoPiplineHttpCompressorCodings] = None,
            config: IoPipelineHttpCompressionConfig = IoPipelineHttpCompressionConfig.DEFAULT,
    ) -> None:
        super().__init__()

        self._config = config
        if codings is None:
            codings = DefaultIoPiplineHttpCompressionCodings.COMPRESSOR
        self._codings = codings

        self._compressor: ta.Optional[IoPiplineHttpCompressorCoding] = None

        # Internal buffering
        self._in_pending: collections.deque[BytesLike] = collections.deque()
        self._in_pending_bytes = 0

        # Deferral State
        self._pending_end: ta.Optional[IoPipelineHttpMessageEnd] = None

    #

    def _reset(self) -> None:
        self._compressor = None

        self._in_pending.clear()
        self._in_pending_bytes = 0

        self._pending_end = None

    def _pump(self, ctx: IoPipelineHandlerContext) -> None:
        z = self._compressor
        if z is None:
            return

        steps = 0
        max_steps = self._config.max_steps_per_call

        # Compression Loop
        while self._in_pending:
            # Check for CPU step limit
            if max_steps is not None and steps >= max_steps:
                self._defer_resume(ctx)
                return

            steps += 1
            chunk = self._in_pending.popleft()
            cl = len(chunk)
            self._in_pending_bytes -= cl

            out = z.compress(chunk)
            if out:
                ctx.feed_in(self._make_body_data(out))

        # Handle EOF
        if not self._in_pending and self._pending_end is not None:
            if max_steps is not None and steps >= max_steps:
                self._defer_resume(ctx)
                return

            out = z.flush()
            if out:
                ctx.feed_in(self._make_body_data(out))

            msg = self._pending_end
            self._pending_end = None
            ctx.feed_in(msg)

    def _defer_resume(self, ctx: IoPipelineHandlerContext) -> None:
        def resume(c: IoPipelineHandlerContext) -> None:
            self._pump(c)

        ctx.defer(resume)

    #

    def _on_inbound_final_input(self, ctx: IoPipelineHandlerContext, msg: IoPipelineMessages.FinalInput) -> None:  # noqa
        if self._compressor is None:
            ctx.feed_in(msg)
            return

        self._reset()

        ctx.feed_in(self._make_aborted('eof before end of message'))
        ctx.feed_in(msg)

    def _on_inbound_head(self, ctx: IoPipelineHandlerContext, msg: IoPipelineHttpMessageHead) -> None:  # noqa
        if self._compressor is not None:
            ctx.feed_in(self._make_aborted('unexpected message sequence'))
            return

        enc = msg.headers.lower.get('content-encoding', ())

        for coding_name, coding in self._codings.items():
            if coding_name.lower() in enc:
                self._compressor = coding()
                break

        ctx.feed_in(msg)

    def _on_inbound_body_data(self, ctx: IoPipelineHandlerContext, msg: IoPipelineHttpMessageBodyData) -> None:  # noqa
        if self._compressor is None:
            ctx.feed_in(msg)
            return

        for mv in ByteStreamBuffers.iter_segments(msg.data):
            mvl = len(mv)
            self._in_pending.append(mv)
            self._in_pending_bytes += mvl

        self._pump(ctx)

    def _on_inbound_end(self, ctx: IoPipelineHandlerContext, msg: IoPipelineHttpMessageEnd) -> None:
        if self._compressor is None:
            ctx.feed_in(msg)
            return

        self._pending_end = msg
        self._pump(ctx)

    def inbound(self, ctx: IoPipelineHandlerContext, msg: ta.Any) -> None:
        if isinstance(msg, IoPipelineMessages.FinalInput):
            self._on_inbound_final_input(ctx, msg)

        elif isinstance(msg, self._head_type):
            self._on_inbound_head(ctx, msg)

        elif isinstance(msg, self._body_data_type):
            self._on_inbound_body_data(ctx, msg)

        elif isinstance(msg, self._end_type):
            self._on_inbound_end(ctx, msg)

        else:
            ctx.feed_in(msg)
