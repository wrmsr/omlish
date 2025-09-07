# @omlish-lite
import typing as ta

from .levels import LogLevel


##


@ta.runtime_checkable
class LoggerLike(ta.Protocol):
    """Satisfied by both our Logger and stdlib logging.Logger."""

    def isEnabledFor(self, level: LogLevel) -> bool: ...  # noqa

    def getEffectiveLevel(self) -> LogLevel: ...  # noqa

    #

    def log(self, level: LogLevel, msg: str, /, *args: ta.Any, **kwargs: ta.Any) -> None: ...  # noqa

    def debug(self, msg: str, /, *args: ta.Any, **kwargs: ta.Any) -> None: ...  # noqa

    def info(self, msg: str, /, *args: ta.Any, **kwargs: ta.Any) -> None: ...  # noqa

    def warning(self, msg: str, /, *args: ta.Any, **kwargs: ta.Any) -> None: ...  # noqa

    def error(self, msg: str, /, *args: ta.Any, **kwargs: ta.Any) -> None: ...  # noqa

    def exception(self, msg: str, /, *args: ta.Any, **kwargs: ta.Any) -> None: ...  # noqa

    def critical(self, msg: str, /, *args: ta.Any, **kwargs: ta.Any) -> None: ...  # noqa
