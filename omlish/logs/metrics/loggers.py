# # @omlish-lite
# import typing as ta
#
# from ..lite.check import check
# from .base import AsyncLogger
# from .base import Logger
# from .base import LoggingMsgFn
# from .contexts import CaptureLoggingContext
# from .contexts import CaptureLoggingContextImpl
# from .metrics import Metric
# from .metrics import Metrics
#
#
# ##
#
#
# class MetricsLogger(Metrics, Logger):
#     def __init__(self, m: Metrics, l: Logger) -> None:
#         super().__init__()
#
#         self._m = m
#         self._l = l
#
#     def _metric(self, metric: ta.Type[Metric], value: ta.Optional[float] = None) -> None:
#         self._m.metric(metric, value)
#
#     def _log(
#             self,
#             ctx: CaptureLoggingContext,
#             msg: ta.Union[str, tuple, LoggingMsgFn],  # noqa
#             *args: ta.Any,
#             **kwargs: ta.Any,
#     ) -> None:
#         self._l._log(  # noqa
#             check.isinstance(ctx, CaptureLoggingContextImpl).inc_stack_offset(),
#             msg,
#             *args,
#             **kwargs,
#         )
#
#
# class AsyncMetricsLogger(AsyncMetrics, AsyncLogger):
#     def __init__(self, m: AsyncMetrics, l: AsyncLogger) -> None:
#         super().__init__()
#
#         self._m = m
#         self._l = l
#
#     def _metric(self, metric: ta.Type[Metric], value: ta.Optional[float] = None) -> ta.Awaitable[None]:
#         return self._m.metric(metric, value)
#
#     async def _log(
#             self,
#             ctx: CaptureLoggingContext,
#             msg: ta.Union[str, tuple, LoggingMsgFn],  # noqa
#             *args: ta.Any,
#             **kwargs: ta.Any,
#     ) -> None:
#         await self._l._log(  # noqa
#             check.isinstance(ctx, CaptureLoggingContextImpl).inc_stack_offset(),
#             msg,
#             *args,
#             **kwargs,
#         )
