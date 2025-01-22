# ruff: noqa: UP006 UP007
import hashlib
import logging
import time
import typing as ta

from omlish.lite.logs import log


##


def read_yaml_file(yaml_file: str) -> ta.Any:
    yaml = __import__('yaml')

    with open(yaml_file) as f:
        return yaml.safe_load(f)


##


def sha256_str(s: str) -> str:
    return hashlib.sha256(s.encode('utf-8')).hexdigest()


##


class LogTimingContext:
    DEFAULT_LOG: ta.ClassVar[logging.Logger] = log

    def __init__(
            self,
            description: str,
            *,
            log: ta.Optional[logging.Logger] = None,  # noqa
            level: int = logging.DEBUG,
    ) -> None:
        super().__init__()

        self._description = description
        self._log = log if log is not None else self.DEFAULT_LOG
        self._level = level

    def set_description(self, description: str) -> 'LogTimingContext':
        self._description = description
        return self

    _begin_time: float
    _end_time: float

    def __enter__(self) -> 'LogTimingContext':
        self._begin_time = time.time()

        self._log.log(self._level, f'Begin : {self._description}')  # noqa

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._end_time = time.time()

        self._log.log(
            self._level,
            f'End : {self._description} - {self._end_time - self._begin_time:0.2f} s elapsed',
        )


log_timing_context = LogTimingContext
