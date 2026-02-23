import dataclasses as dc
import typing as ta

from omlish.io.streams.types import ByteStreamBuffer
from omlish.lite.check import check

from ...core import ChannelPipelineHandlerContext
from ...core import ChannelPipelineMessages
from ...core import PipelineChannel
from ...flow.types import ChannelPipelineFlow
from ...flow.types import ChannelPipelineFlowMessages
from ...handlers.queues import InboundQueueChannelPipelineHandler
from ..b2md import BytesToMessageDecoder


class MyFlow(ChannelPipelineFlow):
    def __init__(self, *, auto_read: bool) -> None:
        super().__init__()

        self._auto_read = auto_read

    @property
    def is_auto_read(self) -> bool:
        return self._auto_read

    def set_auto_read(self, auto_read: bool) -> None:
        self._auto_read = auto_read


@dc.dataclass()
class DumbBytesMessage:
    b: bytes


class ByteTripletsToMessageDecoder(BytesToMessageDecoder):
    def _decode(
            self,
            ctx: ChannelPipelineHandlerContext,
            inb: ByteStreamBuffer,
            *,
            final: bool = False,
    ) -> ta.Iterable[ta.Any]:
        check.state(len(inb))
        while len(inb) >= 3:
            yield DumbBytesMessage(inb.split_to(3).tobytes())


def test_b2md_ar():
    ch = PipelineChannel(
        [
            ByteTripletsToMessageDecoder(),
            ibq := InboundQueueChannelPipelineHandler(),
        ],
        services=[mf := MyFlow(auto_read=True)],  # noqa
    )

    print()

    ch.feed_in(b'abcd', ChannelPipelineFlowMessages.FlushInput())
    print(f'{ch.drain()=} {ibq.drain()=}')

    ch.feed_in(ChannelPipelineMessages.FinalInput())
    print(f'{ch.drain()=} {ibq.drain()=}')


def test_b2md_nar():
    ch = PipelineChannel(
        [
            ByteTripletsToMessageDecoder(),
            ibq := InboundQueueChannelPipelineHandler(),
        ],
        services=[mf := MyFlow(auto_read=False)],  # noqa
    )

    print()

    ch.feed_in(b'abcd', ChannelPipelineFlowMessages.FlushInput())
    print(f'{ch.drain()=} {ibq.drain()=}')

    ch.feed_in(ChannelPipelineMessages.FinalInput())
    print(f'{ch.drain()=} {ibq.drain()=}')
