# ruff: noqa: UP006 UP007
# @omlish-lite
"""
TODO:
 - translate json keys
"""
import logging
import typing as ta

from ..lite.json import json_dumps_compact


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

    def __init__(
            self,
            *args: ta.Any,
            json_dumps: ta.Optional[ta.Callable[[ta.Any], str]] = None,
            **kwargs: ta.Any,
    ) -> None:
        super().__init__(*args, **kwargs)

        if json_dumps is None:
            json_dumps = json_dumps_compact
        self._json_dumps = json_dumps

    def format(self, record: logging.LogRecord) -> str:
        dct = {
            k: v
            for k, o in self.KEYS.items()
            for v in [getattr(record, k)]
            if not (o and v is None)
        }
        return self._json_dumps(dct)
