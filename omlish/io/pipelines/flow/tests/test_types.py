import unittest

from ..stub import StubIoPipelineFlowService
from ..types import IoPipelineFlow


class TestFlow(unittest.TestCase):
    def test_flow(self):
        self.assertEqual(IoPipelineFlow.is_auto_read(None), False)
        self.assertEqual(IoPipelineFlow.is_auto_read(StubIoPipelineFlowService(auto_read=False)), False)
        self.assertEqual(IoPipelineFlow.is_auto_read(StubIoPipelineFlowService(auto_read=True)), True)
        self.assertEqual(StubIoPipelineFlowService(auto_read=False).is_auto_read(), False)
        self.assertEqual(StubIoPipelineFlowService(auto_read=True).is_auto_read(), True)
