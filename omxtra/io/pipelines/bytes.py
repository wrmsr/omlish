# ruff: noqa: UP045
# @omlish-lite
import typing as ta

from omlish.io.streams.utils import ByteStreamBuffers

from .flow import ChannelPipelineFlowControlAdapter


##


class BytesChannelPipelineFlowControlAdapter(ChannelPipelineFlowControlAdapter):
    def get_cost(self, msg: ta.Any) -> ta.Optional[int]:
        return ByteStreamBuffers.bytes_len(msg)
