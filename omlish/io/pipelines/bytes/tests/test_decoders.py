# ruff: noqa: UP006
# @omlish-lite
import dataclasses as dc
import typing as ta
import unittest

from .....lite.check import check
from ....streams.types import ByteStreamBuffer
from ...core import IoPipeline
from ...core import IoPipelineMessages
from ...core import IoPipelineService
from ...flow.types import IoPipelineFlow
from ...flow.types import IoPipelineFlowMessages
from ...handlers.queues import InboundQueueIoPipelineHandler
from ..decoders import BufferedBytesToMessageDecoderIoPipelineHandler
from ..decoders import DelimiterFrameDecoderIoPipelineHandler
from ..decoders import IoPipelineHandlerContext
from ..decoders import UnicodeDecoderIoPipelineHandler


##


class TestDecoders(unittest.TestCase):
    def test_decoders(self):
        ch = IoPipeline.new([
            UnicodeDecoderIoPipelineHandler(),
            ibq := InboundQueueIoPipelineHandler(),
        ])

        ch.feed_in(b'abcd')
        assert ibq.drain() == ['abcd']

        ch.feed_in(b'hi \xe2\x98\x83 there')
        assert ibq.drain() == ['hi ☃ there']

    def test_delim(self):
        ch = IoPipeline.new([
            DelimiterFrameDecoderIoPipelineHandler([b'\n']),
            UnicodeDecoderIoPipelineHandler(),
            ibq := InboundQueueIoPipelineHandler(),
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
        assert isinstance(eof, IoPipelineMessages.FinalInput)


##


class MyFlow(IoPipelineFlow, IoPipelineService):
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


class ByteTripletsToMessageDecoder(BufferedBytesToMessageDecoderIoPipelineHandler):
    def _decode_buffer(
            self,
            ctx: IoPipelineHandlerContext,
            inb: ByteStreamBuffer,
            out: ta.List[ta.Any],
            *,
            final: bool = False,
    ) -> None:
        if final:
            check.state(len(inb) == 0)
            return

        check.state(len(inb) > 0)
        while len(inb) >= 3:
            out.append(DumbBytesMessage(inb.split_to(3).tobytes()))


def test_b2md_ar():
    ch = IoPipeline.new(
        [
            ByteTripletsToMessageDecoder(),
            ibq := InboundQueueIoPipelineHandler(),
        ],
        services=[mf := MyFlow(auto_read=True)],  # noqa
    )

    print()

    ch.feed_in(b'abcd', IoPipelineFlowMessages.FlushInput())
    print(f'{ch.output.drain()=} {ibq.drain()=}')

    ch.feed_in(IoPipelineMessages.FinalInput())
    print(f'{ch.output.drain()=} {ibq.drain()=}')


def test_b2md_nar():
    ch = IoPipeline.new(
        [
            ByteTripletsToMessageDecoder(),
            ibq := InboundQueueIoPipelineHandler(),
        ],
        services=[mf := MyFlow(auto_read=False)],  # noqa
    )

    print()

    ch.feed_in(b'abcd', IoPipelineFlowMessages.FlushInput())
    print(f'{ch.output.drain()=} {ibq.drain()=}')

    ch.feed_in(IoPipelineMessages.FinalInput())
    print(f'{ch.output.drain()=} {ibq.drain()=}')
