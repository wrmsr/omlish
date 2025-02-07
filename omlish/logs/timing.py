# ruff: noqa: UP006 UP007
# @omlish-lite
import logging
import time
import typing as ta


##


class LogTimingContext:
    DEFAULT_LOG: ta.ClassVar[ta.Optional[logging.Logger]] = None

    class _NOT_SPECIFIED:  # noqa
        def __new__(cls, *args, **kwargs):  # noqa
            raise TypeError

    def __init__(
            self,
            description: str,
            *,
            log: ta.Union[logging.Logger, ta.Type[_NOT_SPECIFIED], None] = _NOT_SPECIFIED,  # noqa
            level: int = logging.DEBUG,
    ) -> None:
        super().__init__()

        self._description = description
        if log is self._NOT_SPECIFIED:
            log = self.DEFAULT_LOG  # noqa
        self._log: ta.Optional[logging.Logger] = log  # type: ignore
        self._level = level

    def set_description(self, description: str) -> 'LogTimingContext':
        self._description = description
        return self

    _begin_time: float
    _end_time: float

    def __enter__(self) -> 'LogTimingContext':
        self._begin_time = time.time()

        if self._log is not None:
            self._log.log(self._level, f'Begin : {self._description}')  # noqa

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._end_time = time.time()

        if self._log is not None:
            self._log.log(
                self._level,
                f'End : {self._description} - {self._end_time - self._begin_time:0.2f} s elapsed',
            )


log_timing_context = LogTimingContext
