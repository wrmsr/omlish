# ruff: noqa: ANN201 N802
import logging
import typing as ta

from .. import term
from ..lite.logs import JsonLogFormatter  # noqa
from ..lite.logs import StandardLogFormatter


class ColorLogFormatter(StandardLogFormatter):

    LEVEL_COLORS: ta.Mapping[int, term.SGRs.FG] = {
        logging.WARNING: term.SGRs.FG.BRIGHT_YELLOW,
        logging.ERROR: term.SGRs.FG.BRIGHT_RED,
        logging.CRITICAL: term.SGRs.FG.BRIGHT_RED,
    }

    def formatMessage(self, record):
        buf = super().formatMessage(record)
        try:
            c = self.LEVEL_COLORS[record.levelno]
        except KeyError:
            pass
        else:
            buf = term.SGR(c) + buf + term.SGR(term.SGRs.RESET)
        return buf
