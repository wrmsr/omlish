# ruff: noqa: FURB188 UP045
# @omlish-lite
import typing as ta

from ...streams.utils import ByteStreamBuffers
from ..core import IoPipelineHandlerFn
from ..handlers.fns import IoPipelineHandlerFns
from ..handlers.queues import InboundQueueIoPipelineHandler
from .buffering import InboundBytesBufferingIoPipelineHandler


##


class InboundBytesBufferingQueueIoPipelineHandler(
    InboundBytesBufferingIoPipelineHandler,
    InboundQueueIoPipelineHandler,
):
    def __init__(
            self,
            *,
            filter: ta.Union[IoPipelineHandlerFn[ta.Any, bool], ta.Literal[True], None] = None,  # noqa
            passthrough: bool = False,
    ) -> None:
        if filter is True:
            filter = IoPipelineHandlerFns.no_context(ByteStreamBuffers.can_bytes)  # noqa

        super().__init__(
            filter=filter,  # noqa
            passthrough=passthrough,
        )

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
