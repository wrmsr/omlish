# ruff: noqa: UP045
# @omlish-lite
import typing as ta

from omlish.io.streams.utils import ByteStreamBuffers

from .core import BytesChannelPipelineFlowControl
from .flow import ChannelPipelineFlowControlAdapter
from .flow import FlowControlChannelPipelineHandler


##


class BytesChannelPipelineFlowControlAdapter(ChannelPipelineFlowControlAdapter):
    def get_cost(self, msg: ta.Any) -> ta.Optional[int]:
        return ByteStreamBuffers.bytes_len(msg)


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
