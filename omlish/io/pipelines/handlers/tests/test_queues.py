# @omlish-lite
import unittest

from ...core import IoPipeline
from ..fns import FnIoPipelineHandler
from ..queues import InboundQueueIoPipelineHandler


class TestQueues(unittest.TestCase):
    def test_queues(self):
        ch = IoPipeline.new([
            FnIoPipelineHandler.of(inbound=lambda ctx, msg: ctx.feed_in(msg + '!')),
            h := InboundQueueIoPipelineHandler(),
        ])

        ch.feed_in('abc')
        assert not ch.output.poll()
        assert h.drain() == ['abc!']
