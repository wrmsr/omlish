import unittest

from ..core import ChannelPipelineEvents
from ..core import PipelineChannel
from ..decoders import DelimiterFrameDecoder
from ..decoders import Utf8Decode


class TestDecoders(unittest.TestCase):
    def test_decoders(self):
        ch = PipelineChannel([
            Utf8Decode(),
        ])

        ch.feed_in(b'abcd')
        assert ch.drain_out() == ['abcd']

        ch.feed_in(b'hi \xe2\x98\x83 there')
        assert ch.drain_out() == ['hi ☃ there']

    def test_delim(self):
        ch = PipelineChannel([
            DelimiterFrameDecoder([b'\n']),
            Utf8Decode(),
        ])

        ch.feed_in(b'abc')
        assert ch.drain_out() == []
        ch.feed_in(b'de\nf')
        assert ch.drain_out() == ['abcde']
        ch.feed_in(b'g\nh\nij\n')
        assert ch.drain_out() == ['fg', 'h', 'ij']
        ch.feed_in(b'\nk')
        assert ch.drain_out() == ['']
        ch.feed_eof()
        assert ch.drain_out() == ['k', ChannelPipelineEvents.Eof()]
