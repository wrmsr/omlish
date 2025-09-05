# ruff: noqa: UP007
# @omlish-lite
import logging
import typing as ta

from ..base import Logger
from ..base import LoggingContext
from ..base import LoggingMsgFn
from ..base import LogLevel
from .records import LoggingContextLogRecord


##


class StdLogger(Logger):
    def __init__(self, std: logging.Logger) -> None:
        super().__init__()

        self._std = std

    @property
    def std(self) -> logging.Logger:
        return self._std

    def get_effective_level(self) -> LogLevel:
        return self._std.getEffectiveLevel()

    def _log(self, ctx: LoggingContext, msg: ta.Union[str, LoggingMsgFn], *args: ta.Any) -> None:
        if not self.is_enabled_for(ctx.level):
            return

        ctx.build_caller()

        if callable(msg):
            if args:
                raise TypeError(f'Must not provide both a message function and args: {msg=} {args=}')
            x = msg()
            if isinstance(x, str):
                msg, args = x, ()
            elif isinstance(x, tuple):
                if x:
                    msg, args = x[0], x[1:]
                else:
                    msg, args = '', ()
            elif x is None:
                msg, args = '', ()
            else:
                raise TypeError(x)

        rec = LoggingContextLogRecord(
            name=self._std.name,
            msg=msg,  # type: ignore[arg-type]
            args=args,

            _logging_context=ctx,
        )

        self._std.handle(rec)
