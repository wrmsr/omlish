# ruff: noqa: FURB188 UP045
# @omlish-lite
import typing as ta

from omlish.io.streams.utils import ByteStreamBuffers

from ..handlers.queues import InboundQueueChannelPipelineHandler
from .buffering import InboundBytesBufferingChannelPipelineHandler


##


class InboundBytesBufferingQueueChannelPipelineHandler(
    InboundBytesBufferingChannelPipelineHandler,
    InboundQueueChannelPipelineHandler,
):
    _buffered_bytes: int = 0

    # @ta.override
    def inbound_buffered_bytes(self) -> ta.Optional[int]:
        return self._buffered_bytes

    # @ta.override
    def _append(self, msg: ta.Any) -> None:
        bl = ByteStreamBuffers.bytes_len(msg, True)

        super()._append((msg, bl))

        if bl is not None:
            self._buffered_bytes += bl

    # @ta.override
    def _popleft(self) -> ta.Any:
        msg, bl = self._q.popleft()

        if bl is not None:
            self._buffered_bytes -= bl

        return msg
