# @omlish-lite
import unittest

from ..base import LoggerMetric
from ..base import LoggerMetricCollector
from ..standard import TimeoutLoggerMetric


##


class PrintingLoggerMetricCollector(LoggerMetricCollector):
    def _metric(self, m: LoggerMetric) -> None:
        print(f'{type(m).__name__}: {m.value}')


class TestMetrics(unittest.TestCase):
    def test_metrics(self):
        pml = PrintingLoggerMetricCollector()
        pml.metric(TimeoutLoggerMetric())
