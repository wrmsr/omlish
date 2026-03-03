# ruff: noqa: UP006 UP007 UP043 UP045
# @omlish-lite
import enum
import typing as ta

from omlish.io.streams.types import ByteStreamBuffer

from ...bytes.decoders import BytesToMessageDecoderChannelPipelineHandler
from ...core import ChannelPipelineHandlerContext


##


class PipelineHttpObjectDecoder(BytesToMessageDecoderChannelPipelineHandler):
    class State(enum.Enum):
        HEAD = 'head'

    _state = State.HEAD

    @property
    def state(self) -> State:
        return self._state

    #

    def _decode(
            self,
            ctx: ChannelPipelineHandlerContext,
            buf: ByteStreamBuffer,
            *,
            final: bool = False,
    ) -> ta.Sequence[ta.Any]:
        raise NotImplementedError
