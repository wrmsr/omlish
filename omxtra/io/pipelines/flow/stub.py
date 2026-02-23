import typing as ta

from .types import ChannelPipelineFlow


##


@ta.final
class StubChannelPipelineFlow(ChannelPipelineFlow):
    def is_auto_read(self) -> bool:
        return True
