# @omlish-lite
import unittest

from ...core import ChannelPipelineMessages
from ...core import PipelineChannel
from ...handlers.flatmap import FlatMapChannelPipelineHandlers
from ...handlers.fns import ChannelPipelineHandlerFns
from ..decoders import DelimiterFramePipelineDecoder
from ..decoders import UnicodePipelineDecoder


INBOUND_EMIT_TERMINAL = FlatMapChannelPipelineHandlers.emit_and_drop(
    'inbound',
    filter=ChannelPipelineHandlerFns.not_isinstance(ChannelPipelineMessages.MustPropagate),
)


class TestDecoders(unittest.TestCase):
    def test_decoders(self):
        ch = PipelineChannel([
            UnicodePipelineDecoder(),
            INBOUND_EMIT_TERMINAL,
        ])

        ch.feed_in(b'abcd')
        assert ch.drain() == ['abcd']

        ch.feed_in(b'hi \xe2\x98\x83 there')
        assert ch.drain() == ['hi ☃ there']

    def test_delim(self):
        ch = PipelineChannel([
            DelimiterFramePipelineDecoder([b'\n']),
            UnicodePipelineDecoder(),
            INBOUND_EMIT_TERMINAL,
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
        assert ch.drain() == ['k']
