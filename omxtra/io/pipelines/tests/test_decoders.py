import unittest

from ..core import ChannelPipelineMessages
from ..core import PipelineChannel
from ..decoders import DelimiterFramePipelineDecoder
from ..decoders import UnicodePipelineDecoder


class TestDecoders(unittest.TestCase):
    def test_decoders(self):
        ch = PipelineChannel([
            UnicodePipelineDecoder(),
        ])

        ch.feed_in(b'abcd')
        assert ch.drain() == ['abcd']

        ch.feed_in(b'hi \xe2\x98\x83 there')
        assert ch.drain() == ['hi ☃ there']

    def test_delim(self):
        ch = PipelineChannel([
            DelimiterFramePipelineDecoder([b'\n']),
            UnicodePipelineDecoder(),
        ])

        ch.feed_in(b'abc')
        assert ch.drain() == []
        ch.feed_in(b'de\nf')
        assert ch.drain() == ['abcde']
        ch.feed_in(b'g\nh\nij\n')
        assert ch.drain() == ['fg', 'h', 'ij']
        ch.feed_in(b'\nk')
        assert ch.drain() == ['']
        ch.feed_eof()
        assert ch.drain() == ['k', ChannelPipelineMessages.Eof()]
