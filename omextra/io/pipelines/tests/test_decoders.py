import unittest

from ..core import PipelineChannel
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
