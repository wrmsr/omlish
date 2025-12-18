# ruff: noqa: UP006 UP007 UP045 UP046
# @omlish-lite
import typing as ta

from ..lite.asyncs import sync_await
from .base import AsyncLogger
from .base import CaptureLoggingContext
from .base import Logger
from .base import LoggingMsgFn
from .levels import LogLevel


##


class AsyncLoggerToLogger(Logger):
    def __init__(self, u: AsyncLogger) -> None:
        super().__init__()

        self._u = u

    def get_effective_level(self) -> LogLevel:
        return self._u.get_effective_level()

    def _log(
            self,
            ctx: CaptureLoggingContext,
            msg: ta.Union[str, tuple, LoggingMsgFn],
            *args: ta.Any,
            **kwargs: ta.Any,
    ) -> None:
        sync_await(
            self._u._log(  # noqa
                ctx,
                msg,
                *args,
                **kwargs,
            ),
        )


class LoggerToAsyncLogger(AsyncLogger):
    def __init__(self, u: Logger) -> None:
        super().__init__()

        self._u = u

    def get_effective_level(self) -> LogLevel:
        return self._u.get_effective_level()

    async def _log(
            self,
            ctx: CaptureLoggingContext,
            msg: ta.Union[str, tuple, LoggingMsgFn],
            *args: ta.Any,
            **kwargs: ta.Any,
    ) -> None:
        return self._u._log(  # noqa
            ctx,
            msg,
            *args,
            **kwargs,
        )
