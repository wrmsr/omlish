# @omlish-lite
import unittest

from ...core import ChannelPipelineMessages
from ...core import PipelineChannel
from ...handlers.queues import InboundQueueChannelPipelineHandler
from ..decoders import DelimiterFramePipelineDecoder
from ..decoders import UnicodePipelineDecoder


class TestDecoders(unittest.TestCase):
    def test_decoders(self):
        ch = PipelineChannel([
            UnicodePipelineDecoder(),
            ibq := InboundQueueChannelPipelineHandler(),
        ])

        ch.feed_in(b'abcd')
        assert ibq.drain() == ['abcd']

        ch.feed_in(b'hi \xe2\x98\x83 there')
        assert ibq.drain() == ['hi ☃ there']

    def test_delim(self):
        ch = PipelineChannel([
            DelimiterFramePipelineDecoder([b'\n']),
            UnicodePipelineDecoder(),
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
