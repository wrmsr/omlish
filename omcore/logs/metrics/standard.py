from ...lite.abstract import Abstract
from .base import CounterLoggerMetric
from .base import HistogramLoggerMetric
from .base import SecondsLoggerMetricUnit


##


class TimeoutLoggerMetric(CounterLoggerMetric):
    pass


class LatencyLoggerMetric(SecondsLoggerMetricUnit, HistogramLoggerMetric, Abstract):
    pass
