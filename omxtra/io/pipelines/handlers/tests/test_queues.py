# @omlish-lite
import unittest

from ..queues import DuplexQueueChannelPipelineHandler


class TestQueues(unittest.TestCase):
    def test_queues(self):
        h = DuplexQueueChannelPipelineHandler()
        print(repr(h))
