# ruff: noqa: FURB188 UP045
# @omlish-lite
import typing as ta

from omlish.io.streams.utils import ByteStreamBuffers

from .buffering import InboundBytesBufferingChannelPipelineHandler
from ..handlers.queues import InboundQueueChannelPipelineHandler


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
        # FIXME: use 'or_none'
        if ByteStreamBuffers.can_bytes(msg):
            bl = ByteStreamBuffers.bytes_len(msg)
        else:
            bl = None

        super()._append((msg, bl))

        self._buffered_bytes += bl

    # @ta.override
    def _popleft(self) -> ta.Any:
        msg, bl = self._q.popleft()

        if bl is not None:
            self._buffered_bytes -= bl

        return msg
