# ruff: noqa: UP006 UP007
# @omlish-lite
import abc
import logging
import sys
import typing as ta

from .callers import LoggingCaller


LogLevel = int  # ta.TypeAlias


##


class Logging(ta.Protocol):
    def isEnabledFor(self, level: LogLevel) -> bool:  # noqa
        ...

    def getEffectiveLevel(self) -> LogLevel:  # noqa
        ...

    #

    def debug(self, msg: str, *args: ta.Any, **kwargs: ta.Any) -> None:
        ...

    def info(self, msg: str, *args: ta.Any, **kwargs: ta.Any) -> None:
        ...

    def warning(self, msg: str, *args: ta.Any, **kwargs: ta.Any) -> None:
        ...

    def error(self, msg: str, *args: ta.Any, **kwargs: ta.Any) -> None:
        ...

    def exception(self, msg: str, *args: ta.Any, exc_info: bool = True, **kwargs) -> None:
        ...

    def critical(self, msg: str, *args: ta.Any, **kwargs: ta.Any) -> None:
        ...

    def log(self, level: LogLevel, msg: str, *args: ta.Any, **kwargs: ta.Any) -> None:
        ...


##


class AbstractLogging(abc.ABC):
    @ta.final
    def isEnabledFor(self, level: LogLevel) -> bool:  # noqa
        return self.is_enabled_for(level)

    def is_enabled_for(self, level: LogLevel) -> bool:  # noqa
        return level >= self.getEffectiveLevel()

    @ta.final
    def getEffectiveLevel(self) -> LogLevel:  # noqa
        return self.get_effective_level()

    @abc.abstractmethod
    def get_effective_level(self) -> LogLevel:  # noqa
        raise NotImplementedError

    #

    def debug(self, msg: str, *args: ta.Any, **kwargs: ta.Any) -> None:
        if self.is_enabled_for(logging.DEBUG):
            self.log(logging.DEBUG, msg, args, **kwargs)

    def info(self, msg: str, *args: ta.Any, **kwargs: ta.Any) -> None:
        if self.is_enabled_for(logging.INFO):
            self.log(logging.INFO, msg, args, **kwargs)

    def warning(self, msg: str, *args: ta.Any, **kwargs: ta.Any) -> None:
        if self.is_enabled_for(logging.WARNING):
            self.log(logging.WARNING, msg, args, **kwargs)

    def error(self, msg: str, *args: ta.Any, **kwargs: ta.Any) -> None:
        if self.is_enabled_for(logging.ERROR):
            self.log(logging.ERROR, msg, args, **kwargs)

    def exception(self, msg: str, *args: ta.Any, exc_info: bool = True, **kwargs: ta.Any) -> None:
        self.error(msg, *args, exc_info=exc_info, **kwargs)

    def critical(self, msg: str, *args: ta.Any, **kwargs: ta.Any) -> None:
        if self.is_enabled_for(logging.CRITICAL):
            self.log(logging.CRITICAL, msg, args, **kwargs)

    def log(self, level: LogLevel, msg: str, *args: ta.Any, **kwargs: ta.Any) -> None:
        if not isinstance(level, int):
            raise TypeError('Level must be an integer.')
        if self.is_enabled_for(level):
            self._log(level, msg, args, **kwargs)

    @abc.abstractmethod
    def _log(
            self,
            level: int,
            msg: str,
            args: ta.Any,
            *,
            exc_info: ta.Any = None,
            extra: ta.Any = None,
            stack_info: bool = False,
    ) -> None:
        raise NotImplementedError


##


class NopLogging(AbstractLogging):
    def get_effective_level(self) -> LogLevel:
        return logging.CRITICAL + 1

    def _log(self, *args: ta.Any, **kwargs: ta.Any) -> None:
        pass


##


class StdlibLogging(AbstractLogging):
    def __init__(self, underlying: logging.Logger) -> None:
        super().__init__()

        if not isinstance(underlying, logging.Logger):
            raise TypeError(underlying)

        self._underlying = underlying

    #

    def is_enabled_for(self, level: int) -> bool:  # noqa
        return self._underlying.isEnabledFor(level)

    def get_effective_level(self) -> int:  # noqa
        return self._underlying.getEffectiveLevel()

    #

    def _log(
            self,
            level: int,
            msg: str,
            args: ta.Any,
            *,
            exc_info: ta.Any = None,
            extra: ta.Any = None,
            stack_info: bool = False,
    ) -> None:
        caller = LoggingCaller.find(stack_info)

        if exc_info:
            if isinstance(exc_info, BaseException):
                exc_info = (type(exc_info), exc_info, exc_info.__traceback__)
            elif not isinstance(exc_info, tuple):
                exc_info = sys.exc_info()

        record = self._underlying.makeRecord(
            name=self._underlying.name,
            level=level,
            fn=caller.filename,
            lno=caller.lineno,
            msg=msg,
            args=args,
            exc_info=exc_info,
            func=caller.func,
            extra=extra,
            sinfo=caller.sinfo,
        )

        self._underlying.handle(record)
