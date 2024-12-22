# ruff: noqa: ANN201 N802
import logging
import typing as ta

from ..term import codes as tc
from .standard import StandardLogFormatter


class ColorLogFormatter(StandardLogFormatter):
    LEVEL_COLORS: ta.Mapping[int, tc.SGRs.FG] = {
        logging.WARNING: tc.SGRs.FG.BRIGHT_YELLOW,
        logging.ERROR: tc.SGRs.FG.BRIGHT_RED,
        logging.CRITICAL: tc.SGRs.FG.BRIGHT_RED,
    }

    def formatMessage(self, record):
        buf = super().formatMessage(record)
        try:
            c = self.LEVEL_COLORS[record.levelno]
        except KeyError:
            pass
        else:
            buf = tc.SGR(c) + buf + tc.SGR(tc.SGRs.RESET)
        return buf
