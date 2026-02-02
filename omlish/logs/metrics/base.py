# ruff: noqa: UP006 UP007 UP045
# @omlish-lite
import abc
import typing as ta

from ...lite.abstract import Abstract


T = ta.TypeVar('T')


##


class LoggerMetricUnit(Abstract):
    def __init_subclass__(cls, **kwargs: ta.Any) -> None:
        super().__init_subclass__(**kwargs)

        try:
            mut = LOGGER_METRIC_UNIT_TYPES
        except NameError:
            pass
        else:
            bcs = [bc for bc in mut if issubclass(cls, bc)]
            if len(bcs) != 1:
                raise TypeError(f'{cls.__name__} must be a subclass of exactly one of {mut}, got {bcs}.')

        try:
            mtc = LoggerMetric
        except NameError:
            pass
        else:
            if issubclass(cls, mtc):
                mp = cls.__mro__.index(mtc)
                mup = cls.__mro__.index(LoggerMetricUnit)
                if mup > mp:
                    raise TypeError(f'{cls.__name__} must have Metric before MetricUnit in its MRO.')


class CountLoggerMetricUnit(LoggerMetricUnit):
    @classmethod
    def default_value(cls) -> ta.Optional[float]:
        return 1


class RatioLoggerMetricUnit(LoggerMetricUnit):
    pass


class SecondsLoggerMetricUnit(LoggerMetricUnit):
    pass


class BytesLoggerMetricUnit(LoggerMetricUnit):
    pass


LOGGER_METRIC_UNIT_TYPES: ta.Tuple[ta.Type[LoggerMetricUnit], ...] = (
    CountLoggerMetricUnit,
    RatioLoggerMetricUnit,
    SecondsLoggerMetricUnit,
    BytesLoggerMetricUnit,
)


##


class LoggerMetric(Abstract):
    @ta.final
    def __init__(self, value: ta.Optional[float] = None) -> None:
        if value is None:
            value = self.default_value()
        if value is None:
            raise ValueError(f'{type(self).__name__} has no default value.')

        self.__value = value

    @property
    def value(self) -> float:
        return self.__value

    @classmethod
    def default_value(cls) -> ta.Optional[float]:
        return None

    def __init_subclass__(cls, **kwargs: ta.Any) -> None:
        super().__init_subclass__(**kwargs)

        try:
            mtt = LOGGER_METRIC_TYPES
        except NameError:
            pass
        else:
            bcs = [bc for bc in mtt if issubclass(cls, bc)]
            if Abstract in cls.__bases__:
                if len(bcs) > 1:
                    raise TypeError(f'{cls.__name__} must be a subclass of at most one of {mtt}, got {bcs}.')
            else:
                if len(bcs) != 1:
                    raise TypeError(f'{cls.__name__} must be a subclass of exactly one of {mtt}, got {bcs}.')

        # if Abstract not in cls.__bases__ and not issubclass(cls, LoggerMetricUnit):
        #     raise TypeError(f'{cls.__name__} must be a subclass of LoggerMetricUnit.')


class CounterLoggerMetric(CountLoggerMetricUnit, LoggerMetric, Abstract):
    pass


class GaugeLoggerMetric(LoggerMetric, Abstract):
    pass


class HistogramLoggerMetric(LoggerMetric, Abstract):
    pass


LOGGER_METRIC_TYPES: ta.Tuple[ta.Type[LoggerMetric], ...] = (
    CounterLoggerMetric,
    GaugeLoggerMetric,
    HistogramLoggerMetric,
)


##


class AnyLoggerMetricCollector(Abstract, ta.Generic[T]):
    @ta.final
    def metric(self, m: LoggerMetric) -> T:
        return self._metric(m)

    @abc.abstractmethod
    def _metric(self, m: LoggerMetric) -> T:
        raise NotImplementedError


class LoggerMetricCollector(AnyLoggerMetricCollector[None], Abstract):
    @abc.abstractmethod
    def _metric(self, m: LoggerMetric) -> None:
        raise NotImplementedError


class AsyncLoggerMetricCollector(AnyLoggerMetricCollector[ta.Awaitable[None]], Abstract):
    @abc.abstractmethod
    def _metric(self, m: LoggerMetric) -> ta.Awaitable[None]:
        raise NotImplementedError


##


class AnyNopLoggerMetricCollector(AnyLoggerMetricCollector[T], Abstract):
    pass


class NopLoggerMetricCollector(AnyNopLoggerMetricCollector[None], LoggerMetricCollector):
    @ta.final
    def _metric(self, m: LoggerMetric) -> None:
        pass


class AsyncNopLoggerMetricCollector(AnyNopLoggerMetricCollector[ta.Awaitable[None]], AsyncLoggerMetricCollector):
    @ta.final
    async def _metric(self, m: LoggerMetric) -> None:
        pass
