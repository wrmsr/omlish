import logging
import typing as ta

from ..formatters import LoggingContextFormatter
from .records import LoggingContextLogRecord
from .records import LogRecordLoggingContext


##


@ta.final
class StdLoggingFormatter(logging.Formatter):
    def __init__(self, ctx_formatter: LoggingContextFormatter) -> None:
        super().__init__()

        self._ctx_formatter = ctx_formatter

    def format(self, rec: logging.LogRecord) -> str:
        if isinstance(rec, LoggingContextLogRecord):
            ctx = rec._logging_context  # noqa
        else:
            ctx = LogRecordLoggingContext(rec)

        return self._ctx_formatter.format(ctx)
