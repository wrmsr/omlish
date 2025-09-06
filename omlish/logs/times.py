# ruff: noqa: UP045
# @omlish-lite
import logging
import time
import typing as ta

from .infos import logging_context_info
from .warnings import LoggingSetupWarning


##


@logging_context_info
@ta.final
class LoggingTimeFields(ta.NamedTuple):
    """Maps directly to stdlib `logging.LogRecord` fields, and must be kept in sync with it."""

    created: float
    msecs: float
    relative_created: float

    @classmethod
    def get_std_start_time_ns(cls) -> int:
        x: ta.Any = logging._startTime  # type: ignore[attr-defined]  # noqa

        # Before 3.13.0b1 this will be `time.time()`, a float of seconds. After that, it will be `time.time_ns()`, an
        # int.
        #
        # See:
        #  - https://github.com/python/cpython/commit/1316692e8c7c1e1f3b6639e51804f9db5ed892ea
        #
        if isinstance(x, float):
            return int(x * 1e9)
        else:
            return x

    @classmethod
    def build(
            cls,
            time_ns: int,
            *,
            start_time_ns: ta.Optional[int] = None,
    ) -> 'LoggingTimeFields':
        # https://github.com/python/cpython/commit/1316692e8c7c1e1f3b6639e51804f9db5ed892ea
        created = time_ns / 1e9  # ns to float seconds

        # Get the number of whole milliseconds (0-999) in the fractional part of seconds.
        # Eg: 1_677_903_920_999_998_503 ns --> 999_998_503 ns--> 999 ms
        # Convert to float by adding 0.0 for historical reasons. See gh-89047
        msecs = (time_ns % 1_000_000_000) // 1_000_000 + 0.0

        # https://github.com/python/cpython/commit/1500a23f33f5a6d052ff1ef6383d9839928b8ff1
        if msecs == 999.0 and int(created) != time_ns // 1_000_000_000:
            # ns -> sec conversion can round up, e.g:
            # 1_677_903_920_999_999_900 ns --> 1_677_903_921.0 sec
            msecs = 0.0

        if start_time_ns is None:
            start_time_ns = cls.get_std_start_time_ns()
        relative_created = (time_ns - start_time_ns) / 1e6

        return cls(
            created=created,
            msecs=msecs,
            relative_created=relative_created,
        )


##


class UnexpectedLoggingStartTimeWarning(LoggingSetupWarning):
    pass


def _check_logging_start_time() -> None:
    if (x := LoggingTimeFields.get_std_start_time_ns()) < (t := time.time()):
        import warnings  # noqa

        warnings.warn(
            f'Unexpected logging start time detected: '
            f'get_std_start_time_ns={x}, '
            f'time.time()={t}',
            UnexpectedLoggingStartTimeWarning,
        )


_check_logging_start_time()
