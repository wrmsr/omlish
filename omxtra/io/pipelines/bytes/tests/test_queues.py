# @omlish-lite
import unittest

from ...core import PipelineChannel
from ...handlers.flatmap import FlatMapChannelPipelineHandlers
from ...handlers.fns import FnChannelPipelineHandler
from ..queues import InboundBytesBufferingQueueChannelPipelineHandler


class TestQueues(unittest.TestCase):
    def test_inbound_queue(self):
        ch = PipelineChannel([
            FnChannelPipelineHandler.of(inbound=lambda ctx, msg: ctx.feed_in(msg + b'!')),
            h := InboundBytesBufferingQueueChannelPipelineHandler(),
        ])

        ch.feed_in(b'abc')
        assert not ch.poll()
        assert h.inbound_buffered_bytes() == 4
        assert h.drain() == [b'abc!']
        assert h.inbound_buffered_bytes() == 0

    def test_inbound_queue_filter(self):
        ch = PipelineChannel([
            FnChannelPipelineHandler.of(inbound=lambda ctx, msg: ctx.feed_in(msg + b'!' if isinstance(msg, bytes) else msg)),  # noqa
            h := InboundBytesBufferingQueueChannelPipelineHandler(filter=True),
            FlatMapChannelPipelineHandlers.emit_and_drop('inbound'),
        ])

        ch.feed_in(b'abc')
        assert not ch.poll()
        assert h.inbound_buffered_bytes() == 4
        assert h.drain() == [b'abc!']
        assert h.inbound_buffered_bytes() == 0

        ch.feed_in(420)
        assert h.inbound_buffered_bytes() == 0
        assert ch.drain() == [420]
        assert h.inbound_buffered_bytes() == 0
