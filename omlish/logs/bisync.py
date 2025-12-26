import abc
import typing as ta

from .. import check
from .. import lang
from .base import AsyncLogger
from .base import Logger
from .base import LoggingMsgFn
from .contexts import CaptureLoggingContext
from .contexts import CaptureLoggingContextImpl
from .levels import LogLevel


##


class BisyncLogger(Logger, lang.Abstract):
    @property
    @abc.abstractmethod
    def a(self) -> 'BisyncAsyncLogger':
        raise NotImplementedError


class BisyncAsyncLogger(AsyncLogger, lang.Abstract):
    @property
    @abc.abstractmethod
    def s(self) -> BisyncLogger:
        raise NotImplementedError


##


class _BisyncLoggerImpl(BisyncLogger, lang.Final):
    def __init__(self, u: 'Logger') -> None:
        super().__init__()

        self._u = u

    _a: 'BisyncAsyncLogger'

    @property
    def a(self) -> BisyncAsyncLogger:
        return self._a

    def get_effective_level(self) -> LogLevel:
        return self._u.get_effective_level()

    def _log(
            self,
            ctx: CaptureLoggingContext,
            msg: ta.Union[str, tuple, LoggingMsgFn],  # noqa
            *args: ta.Any,
            **kwargs: ta.Any,
    ) -> None:
        return self._u._log(  # noqa
            check.isinstance(ctx, CaptureLoggingContextImpl).inc_stack_offset(),
            msg,
            *args,
            **kwargs,
        )


class _BisyncAsyncLoggerImpl(BisyncAsyncLogger, lang.Final):
    def __init__(self, u: 'AsyncLogger') -> None:
        super().__init__()

        self._u = u

    _s: BisyncLogger

    @property
    def s(self) -> BisyncLogger:
        return self._s

    def get_effective_level(self) -> LogLevel:
        return self._u.get_effective_level()

    async def _log(
            self,
            ctx: CaptureLoggingContext,
            msg: ta.Union[str, tuple, LoggingMsgFn],  # noqa
            *args: ta.Any,
            **kwargs: ta.Any,
    ) -> None:
        return await self._u._log(  # noqa
            check.isinstance(ctx, CaptureLoggingContextImpl).inc_stack_offset(),
            msg,
            *args,
            **kwargs,
        )


def make_bisync_logger(log: Logger, alog: AsyncLogger) -> BisyncLogger:
    s = _BisyncLoggerImpl(log)
    a = _BisyncAsyncLoggerImpl(alog)
    s._a = a  # noqa
    a._s = s  # noqa
    return s
