# ruff: noqa: UP006 UP007 UP043 UP045
# @omlish-lite
import enum
import typing as ta

from omlish.io.streams.utils import CanByteStreamBuffer

from ...bytes.decoders2 import BytesToMessageDecoderChannelPipelineHandler
from ...core import ChannelPipelineHandlerContext
from ..objects import PipelineHttpMessageHead


##


class PipelineHttpObjectDecoder(BytesToMessageDecoderChannelPipelineHandler):
    def __init__(
            self,
    ) -> None:
        super().__init__()

    #

    class State(enum.Enum):
        HEAD = 'head'

    _state = State.HEAD

    @property
    def state(self) -> State:
        return self._state

    #

    _head: PipelineHttpMessageHead

    def _decode(
            self,
            ctx: ChannelPipelineHandlerContext,
            data: CanByteStreamBuffer,
            out: ta.List[ta.Any],
            *,
            final: bool = False,
    ) -> None:
        raise NotImplementedError
