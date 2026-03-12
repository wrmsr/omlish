# ruff: noqa: UP006 UP045
# @omlish-lite
import dataclasses as dc
import typing as ta

from ....lite.check import check
from ...streams.segmented import SegmentedByteStreamBuffer
from ...streams.types import MutableByteStreamBuffer
from ...streams.utils import ByteStreamBuffers
from ..core import IoPipelineHandlerContext
from ..core import IoPipelineHandlerNotification
from ..core import IoPipelineHandlerNotifications
from ..core import IoPipelineMessages
from ..flow.types import IoPipelineFlow
from ..flow.types import IoPipelineFlowMessages
from .buffering import OutboundBytesBufferingIoPipelineHandler


##


@ta.final
class OutboundBytesBufferIoPipelineHandler(OutboundBytesBufferingIoPipelineHandler):
    @ta.final
    @dc.dataclass(frozen=True)
    class Config:
        flush_threshold: ta.Optional[int] = 8 * 1024
        max_buffer_size: ta.Optional[int] = None
        buffer_chunk_size: int = 64 * 1024

        DEFAULT: ta.ClassVar['OutboundBytesBufferIoPipelineHandler.Config']

    Config.DEFAULT = Config()

    def __init__(self, config: ta.Optional[Config] = None) -> None:
        super().__init__()

        if config is None:
            config = self.Config.DEFAULT
        self._config = config

    #

    _buf: ta.Optional[MutableByteStreamBuffer] = None

    def _new_buf(self) -> MutableByteStreamBuffer:
        return SegmentedByteStreamBuffer(
            max_size=self._config.max_buffer_size,
            chunk_size=self._config.buffer_chunk_size,
        )

    def outbound_buffered_bytes(self) -> ta.Optional[int]:
        if (buf := self._buf) is None:
            return 0
        return len(buf)

    #

    def notify(self, ctx: IoPipelineHandlerContext, no: IoPipelineHandlerNotification) -> None:
        if isinstance(no, IoPipelineHandlerNotifications.Added):
            # This handler *requires* flow
            check.not_none(no.ctx.services.find(IoPipelineFlow))

    #

    def _flush(self, ctx: IoPipelineHandlerContext) -> None:
        if (buf := self._buf) is None or len(buf) == 0:
            return

        # Collect all buffered segments and feed them out
        for seg in buf.segments():
            ctx.feed_out(seg)

        # Reset buffer
        self._buf = None

    _FLUSH_AND_FEED_OUT_TYPES: ta.ClassVar[ta.Tuple[type, ...]] = (
        IoPipelineFlowMessages.FlushOutput,
        IoPipelineMessages.FinalOutput,
    )

    def outbound(self, ctx: IoPipelineHandlerContext, msg: ta.Any) -> None:
        if isinstance(msg, self._FLUSH_AND_FEED_OUT_TYPES):
            self._flush(ctx)
            ctx.feed_out(msg)

        elif ByteStreamBuffers.can_bytes(msg):
            # Buffer the bytes
            if (buf := self._buf) is None:
                buf = self._buf = self._new_buf()

            for seg in ByteStreamBuffers.iter_segments(msg):
                if seg:
                    buf.write(seg)

            # Check if we should flush based on threshold
            if (
                (threshold := self._config.flush_threshold) is not None and
                len(buf) >= threshold
            ):
                self._flush(ctx)

        else:
            ctx.feed_out(msg)
