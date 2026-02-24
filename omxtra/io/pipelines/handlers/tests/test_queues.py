# @omlish-lite
import unittest

from ...core import PipelineChannel
from ..fns import FnChannelPipelineHandler
from ..queues import InboundQueueChannelPipelineHandler


class TestQueues(unittest.TestCase):
    def test_queues(self):
        ch = PipelineChannel([
            FnChannelPipelineHandler.of(inbound=lambda ctx, msg: ctx.feed_in(msg + '!')),
            h := InboundQueueChannelPipelineHandler(),
        ])

        ch.feed_in('abc')
        assert not ch.output.poll()
        assert h.drain() == ['abc!']
