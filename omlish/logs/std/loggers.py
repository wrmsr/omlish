# ruff: noqa: UP007
# @omlish-lite
import logging
import typing as ta

from ..base import Logger
from ..base import LoggingMsgFn
from ..contexts import CaptureLoggingContext
from ..levels import LogLevel
from .records import LoggingContextLogRecord


##


class StdLogger(Logger):
    def __init__(self, std: logging.Logger) -> None:
        super().__init__()

        self._std = std

    @property
    def std(self) -> logging.Logger:
        return self._std

    def is_enabled_for(self, level: LogLevel) -> bool:
        return self._std.isEnabledFor(level)

    def get_effective_level(self) -> LogLevel:
        return self._std.getEffectiveLevel()

    def _log(self, ctx: CaptureLoggingContext, msg: ta.Union[str, tuple, LoggingMsgFn], *args: ta.Any) -> None:
        if not self.is_enabled_for(ctx.level):
            return

        ctx.capture()

        ms, args = self._prepare_msg_args(msg, *args)

        rec = LoggingContextLogRecord(
            name=self._std.name,
            msg=ms,
            args=args,

            _logging_context=ctx,
        )

        self._std.handle(rec)
