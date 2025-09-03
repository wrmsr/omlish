# ruff: noqa: UP006 UP007 UP045
# @omlish-lite
import abc
import logging
import sys
import typing as ta

from .callers import LoggingCaller
from .levels import LogLevel


T = ta.TypeVar('T')
T_co = ta.TypeVar('T_co', covariant=True)


##


class AnyLogging(ta.Protocol[T_co]):
    def isEnabledFor(self, level: LogLevel) -> bool: ...  # noqa

    def getEffectiveLevel(self) -> LogLevel: ...  # noqa

    #

    def debug(self, msg: str, *args: ta.Any, **kwargs: ta.Any) -> T_co: ...

    def info(self, msg: str, *args: ta.Any, **kwargs: ta.Any) -> T_co: ...

    def warning(self, msg: str, *args: ta.Any, **kwargs: ta.Any) -> T_co: ...

    def error(self, msg: str, *args: ta.Any, **kwargs: ta.Any) -> T_co: ...

    def exception(self, msg: str, *args: ta.Any, exc_info: bool = True, **kwargs: ta.Any) -> T_co: ...

    def critical(self, msg: str, *args: ta.Any, **kwargs: ta.Any) -> T_co: ...

    def log(self, level: LogLevel, msg: str, *args: ta.Any, **kwargs: ta.Any) -> T_co: ...


class Logging(AnyLogging[None], ta.Protocol):
    pass


class AsyncLogging(AnyLogging[ta.Awaitable[None]], ta.Protocol):
    pass


##


class AnyAbstractLogging(abc.ABC, ta.Generic[T]):
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

    def debug(self, msg: str, *args: ta.Any, _logging_stack_offset: int = 0, **kwargs: ta.Any) -> T:
        return self.log(logging.DEBUG, msg, *args, _logging_stack_offset=_logging_stack_offset + 1, **kwargs)

    def info(self, msg: str, *args: ta.Any, _logging_stack_offset: int = 0, **kwargs: ta.Any) -> T:
        return self.log(logging.INFO, msg, *args, _logging_stack_offset=_logging_stack_offset + 1, **kwargs)

    def warning(self, msg: str, *args: ta.Any, _logging_stack_offset: int = 0, **kwargs: ta.Any) -> T:
        return self.log(logging.WARNING, msg, *args, _logging_stack_offset=_logging_stack_offset + 1, **kwargs)

    def error(self, msg: str, *args: ta.Any, _logging_stack_offset: int = 0, **kwargs: ta.Any) -> T:
        return self.log(logging.ERROR, msg, *args, _logging_stack_offset=_logging_stack_offset + 1, **kwargs)

    def exception(self, msg: str, *args: ta.Any, exc_info: bool = True, _logging_stack_offset: int = 0, **kwargs: ta.Any) -> T:  # noqa
        return self.error(msg, *args, exc_info=exc_info, _logging_stack_offset=_logging_stack_offset + 1, **kwargs)  # noqa

    def critical(self, msg: str, *args: ta.Any, _logging_stack_offset: int = 0, **kwargs: ta.Any) -> T:
        return self.log(logging.CRITICAL, msg, *args, _logging_stack_offset=_logging_stack_offset + 1, **kwargs)

    @abc.abstractmethod
    def log(
            self,
            level: int,
            msg: str,
            *args: ta.Any,
            exc_info: ta.Any = None,
            extra: ta.Any = None,
            stack_info: bool = False,
            _logging_stack_offset: int = 0,
    ) -> T:
        raise NotImplementedError


class AbstractLogging(AnyAbstractLogging[None], abc.ABC):
    def log(self, level: LogLevel, msg: str, *args: ta.Any, _logging_stack_offset: int = 0, **kwargs: ta.Any) -> None:
        if not isinstance(level, int):
            raise TypeError('Level must be an integer.')
        if self.is_enabled_for(level):
            self._log(level, msg, args, _logging_stack_offset=_logging_stack_offset + 1, **kwargs)

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
            _logging_stack_offset: int = 0,
    ) -> None:
        raise NotImplementedError


class AbstractAsyncLogging(AnyAbstractLogging[ta.Awaitable[None]], abc.ABC):
    async def log(self, level: LogLevel, msg: str, *args: ta.Any, _logging_stack_offset: int = 0, **kwargs: ta.Any) -> None:  # noqa
        if not isinstance(level, int):
            raise TypeError('Level must be an integer.')
        if self.is_enabled_for(level):
            await self._log(level, msg, args, _logging_stack_offset=_logging_stack_offset + 1, **kwargs)

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
            _logging_stack_offset: int = 0,
    ) -> ta.Awaitable[None]:
        raise NotImplementedError


##


class AnyNopLogging(AnyAbstractLogging[T], abc.ABC):
    def get_effective_level(self) -> LogLevel:
        return logging.CRITICAL + 1


class NopLogging(AnyNopLogging[None], AbstractLogging):
    def _log(self, *args: ta.Any, **kwargs: ta.Any) -> None:
        pass


class NopAsyncLogging(AnyNopLogging[ta.Awaitable[None]], AbstractAsyncLogging):
    async def _log(self, *args: ta.Any, **kwargs: ta.Any) -> None:
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
            _logging_stack_offset: int = 0,
    ) -> None:
        caller = LoggingCaller.find(_logging_stack_offset, stack_info=stack_info)

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
