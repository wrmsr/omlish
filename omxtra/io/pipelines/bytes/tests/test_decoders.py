# @omlish-lite
import dataclasses as dc
import typing as ta
import unittest

from omlish.io.streams.types import ByteStreamBuffer
from omlish.lite.check import check

from ...core import ChannelPipelineMessages
from ...core import PipelineChannel
from ...flow.types import ChannelPipelineFlow
from ...flow.types import ChannelPipelineFlowMessages
from ...handlers.queues import InboundQueueChannelPipelineHandler
from ..decoders import BytesToMessageDecoderChannelPipelineHandler
from ..decoders import ChannelPipelineHandlerContext
from ..decoders import DelimiterFrameDecoderChannelPipelineHandler
from ..decoders import UnicodeDecoderChannelPipelineHandler


##


class TestDecoders(unittest.TestCase):
    def test_decoders(self):
        ch = PipelineChannel.new([
            UnicodeDecoderChannelPipelineHandler(),
            ibq := InboundQueueChannelPipelineHandler(),
        ])

        ch.feed_in(b'abcd')
        assert ibq.drain() == ['abcd']

        ch.feed_in(b'hi \xe2\x98\x83 there')
        assert ibq.drain() == ['hi ☃ there']

    def test_delim(self):
        ch = PipelineChannel.new([
            DelimiterFrameDecoderChannelPipelineHandler([b'\n']),
            UnicodeDecoderChannelPipelineHandler(),
            ibq := InboundQueueChannelPipelineHandler(),
        ])

        ch.feed_in(b'abc')
        assert ibq.drain() == []
        ch.feed_in(b'de\nf')
        assert ibq.drain() == ['abcde']
        ch.feed_in(b'g\nh\nij\n')
        assert ibq.drain() == ['fg', 'h', 'ij']
        ch.feed_in(b'\nk')
        assert ibq.drain() == ['']
        ch.feed_final_input()
        om, eof = ibq.drain()
        assert om == 'k'
        assert isinstance(eof, ChannelPipelineMessages.FinalInput)


##


class MyFlow(ChannelPipelineFlow):
    def __init__(self, *, auto_read: bool) -> None:
        super().__init__()

        self._auto_read = auto_read

    def is_auto_read(self) -> bool:
        return self._auto_read

    def set_auto_read(self, auto_read: bool) -> None:
        self._auto_read = auto_read


@dc.dataclass()
class DumbBytesMessage:
    b: bytes


class ByteTripletsToMessageDecoder(BytesToMessageDecoderChannelPipelineHandler):
    def _decode(
            self,
            ctx: ChannelPipelineHandlerContext,
            inb: ByteStreamBuffer,
            *,
            final: bool = False,
    ) -> ta.Iterable[ta.Any]:
        check.state(len(inb) > 0)
        while len(inb) >= 3:
            yield DumbBytesMessage(inb.split_to(3).tobytes())


def test_b2md_ar():
    ch = PipelineChannel.new(
        [
            ByteTripletsToMessageDecoder(),
            ibq := InboundQueueChannelPipelineHandler(),
        ],
        services=[mf := MyFlow(auto_read=True)],  # noqa
    )

    print()

    ch.feed_in(b'abcd', ChannelPipelineFlowMessages.FlushInput())
    print(f'{ch.output.drain()=} {ibq.drain()=}')

    ch.feed_in(ChannelPipelineMessages.FinalInput())
    print(f'{ch.output.drain()=} {ibq.drain()=}')


def test_b2md_nar():
    ch = PipelineChannel.new(
        [
            ByteTripletsToMessageDecoder(),
            ibq := InboundQueueChannelPipelineHandler(),
        ],
        services=[mf := MyFlow(auto_read=False)],  # noqa
    )

    print()

    ch.feed_in(b'abcd', ChannelPipelineFlowMessages.FlushInput())
    print(f'{ch.output.drain()=} {ibq.drain()=}')

    ch.feed_in(ChannelPipelineMessages.FinalInput())
    print(f'{ch.output.drain()=} {ibq.drain()=}')
