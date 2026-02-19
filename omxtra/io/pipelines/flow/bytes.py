# ruff: noqa: UP045
# @omlish-lite
import typing as ta

from omlish.io.streams.utils import ByteStreamBuffers
from omlish.lite.abstract import Abstract

from .flow import ChannelPipelineFlowControl
from .flow import ChannelPipelineFlowControlAdapter
from .flow import FlowControlChannelPipelineHandler


##


class BytesChannelPipelineFlowControlAdapter(ChannelPipelineFlowControlAdapter):
    def get_cost(self, msg: ta.Any) -> ta.Optional[int]:
        return ByteStreamBuffers.bytes_len(msg, True)


##


class BytesChannelPipelineFlowControl(ChannelPipelineFlowControl, Abstract):
    """
    Special cased flow control specifically for 'external' bytes streams. Many of the decoders will talk to the instance
    of this (if present) to report the bytes they've consumed as they consume them. If present in a pipeline it must be
    unique, and should generally be at the outermost position.
    """


##


class BytesFlowControlChannelPipelineHandler(FlowControlChannelPipelineHandler, BytesChannelPipelineFlowControl):
    def __init__(
            self,
            config: FlowControlChannelPipelineHandler.Config = FlowControlChannelPipelineHandler.Config(),
            *,
            adapter: ChannelPipelineFlowControlAdapter = BytesChannelPipelineFlowControlAdapter(),
            **kwargs: ta.Any,
    ) -> None:
        super().__init__(
            adapter,
            config,
            **kwargs,
        )
