# ruff: noqa: ANN201
# ruff: noqa: N802

import datetime
import logging
import typing as ta

from .. import json
from .. import term


class StandardLogFormatter(logging.Formatter):

    converter = datetime.datetime.fromtimestamp  # type: ignore

    def formatTime(self, record, datefmt=None):
        ct = self.converter(record.created)  # type: ignore
        if datefmt:
            return ct.strftime(datefmt)  # noqa
        else:
            t = ct.strftime("%Y-%m-%d %H:%M:%S")  # noqa
            return '%s.%03d' % (t, record.msecs)


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


class JsonLogFormatter(logging.Formatter):

    KEYS: ta.Mapping[str, bool] = {
        'name': False,
        'msg': False,
        'args': False,
        'levelname': False,
        'levelno': False,
        'pathname': False,
        'filename': False,
        'module': False,
        'exc_info': True,
        'exc_text': True,
        'stack_info': True,
        'lineno': False,
        'funcName': False,
        'created': False,
        'msecs': False,
        'relativeCreated': False,
        'thread': False,
        'threadName': False,
        'processName': False,
        'process': False,
    }

    def format(self, record: logging.LogRecord) -> str:
        dct = {k: v for k, o in self.KEYS.items() for v in [getattr(record, k)] if not (o and v is None)}
        return json.dumps_compact(dct)
