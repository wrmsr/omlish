# @omlish-lite
import typing as ta

from ...lite.check import check
from ..base import AsyncLogger
from ..base import Logger
from ..base import LoggingMsgFn
from ..contexts import CaptureLoggingContext
from ..contexts import CaptureLoggingContextImpl
from ..levels import LogLevel
from .base import AsyncLoggerMetricCollector
from .base import LoggerMetric
from .base import LoggerMetricCollector


##


class MetricCollectingLogger(Logger):
    def __init__(self, u: Logger, c: LoggerMetricCollector) -> None:
        super().__init__()

        self._u = u
        self._c = c

    def get_effective_level(self) -> LogLevel:
        return self._u.get_effective_level()

    def _log(
            self,
            ctx: CaptureLoggingContext,
            msg: ta.Union[str, tuple, LoggingMsgFn],  # noqa
            *args: ta.Any,
            **kwargs: ta.Any,
    ) -> None:
        self._u._log(  # noqa
            check.isinstance(ctx, CaptureLoggingContextImpl).inc_stack_offset(),
            msg,
            *args,
            **kwargs,
        )

    def _metric(self, m: LoggerMetric) -> None:
        self._u.metric(m)
        self._c.metric(m)


class AsyncMetricCollectingLogger(AsyncLogger):
    def __init__(self, u: AsyncLogger, c: AsyncLoggerMetricCollector) -> None:
        super().__init__()

        self._u = u
        self._c = c

    def get_effective_level(self) -> LogLevel:
        return self._u.get_effective_level()

    async def _log(
            self,
            ctx: CaptureLoggingContext,
            msg: ta.Union[str, tuple, LoggingMsgFn],  # noqa
            *args: ta.Any,
            **kwargs: ta.Any,
    ) -> None:
        await self._u._log(  # noqa
            check.isinstance(ctx, CaptureLoggingContextImpl).inc_stack_offset(),
            msg,
            *args,
            **kwargs,
        )

    async def _metric(self, m: LoggerMetric) -> None:
        await self._u.metric(m)
        await self._c.metric(m)
