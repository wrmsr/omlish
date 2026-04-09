# ruff: noqa: UP006 UP037 UP045
# @omlish-lite
import dataclasses as dc
import typing as ta

from ....io.pipelines.core import IoPipelineHandler
from ....io.pipelines.core import IoPipelineHandlerContext
from ....io.pipelines.core import IoPipelineMessages
from ....io.pipelines.flow.types import IoPipelineFlowMessages
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


IoPipelineHttpCompressionConfig.DEFAULT = IoPipelineHttpCompressionConfig()


#


class IoPipelineHttpObjectCompressor(
    IoPipelineHttpMessageObjects,
    IoPipelineHandler,
    Abstract,
):
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

    #

    def _reset(self) -> None:
        self._compressor = None

    #

    def _on_outbound_final_output(self, ctx: IoPipelineHandlerContext, msg: IoPipelineMessages.FinalOutput) -> None:
        if self._compressor is None:
            ctx.feed_out(msg)
            return

        self._reset()

        ctx.feed_out(self._make_aborted('eof before end of message'))
        ctx.feed_out(msg)

    def _on_outbound_head(self, ctx: IoPipelineHandlerContext, msg: IoPipelineHttpMessageHead) -> None:
        if self._compressor is not None:
            ctx.feed_out(self._make_aborted('unexpected message sequence'))
            return

        enc = msg.headers.lower.get('content-encoding', ())

        for coding_name, coding in self._codings.items():
            if coding_name.lower() in enc:
                self._compressor = coding()
                break

        ctx.feed_out(msg)

    def _on_outbound_body_data(self, ctx: IoPipelineHandlerContext, msg: IoPipelineHttpMessageBodyData) -> None:
        if (z := self._compressor) is None:
            ctx.feed_out(msg)
            return

        for mv in ByteStreamBuffers.iter_segments(msg.data):
            out = z.compress(mv)
            if out:
                ctx.feed_out(self._make_body_data(out))

    def _on_outbound_flush_output(self, ctx: IoPipelineHandlerContext, msg: IoPipelineFlowMessages.FlushOutput) -> None:
        if (z := self._compressor) is None:
            ctx.feed_out(msg)
            return

        if chunk := z.flush():
            ctx.feed_out(self._make_body_data(chunk))

        ctx.feed_out(msg)

    def _on_outbound_end(self, ctx: IoPipelineHandlerContext, msg: IoPipelineHttpMessageEnd) -> None:
        if (z := self._compressor) is None:
            ctx.feed_out(msg)
            return

        out = z.finish()
        if out:
            ctx.feed_out(self._make_body_data(out))

        self._reset()
        ctx.feed_out(msg)

    def outbound(self, ctx: IoPipelineHandlerContext, msg: ta.Any) -> None:
        if isinstance(msg, IoPipelineMessages.FinalOutput):
            self._on_outbound_final_output(ctx, msg)

        elif isinstance(msg, self._head_type):
            self._on_outbound_head(ctx, msg)

        elif isinstance(msg, self._body_data_type):
            self._on_outbound_body_data(ctx, msg)

        elif isinstance(msg, IoPipelineFlowMessages.FlushOutput):
            self._on_outbound_flush_output(ctx, msg)

        elif isinstance(msg, self._end_type):
            self._on_outbound_end(ctx, msg)

        else:
            ctx.feed_out(msg)
