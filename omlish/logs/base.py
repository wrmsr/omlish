# ruff: noqa: UP006 UP007 UP045 UP046
# @omlish-lite
import abc
import sys
import time
import types
import typing as ta

from ..lite.abstract import Abstract
from .callers import LoggingCaller
from .infos import LoggingAsyncioTaskInfo
from .infos import LoggingMultiprocessingInfo
from .infos import LoggingProcessInfo
from .infos import LoggingSourceFileInfo
from .infos import LoggingThreadInfo
from .levels import NamedLogLevel
from .times import LoggingTimeFields


T = ta.TypeVar('T')


LogLevel = int  # ta.TypeAlias

LoggingMsgFn = ta.Callable[[], ta.Union[str, tuple, None]]  # ta.TypeAlias

LoggingExcInfoTuple = ta.Tuple[ta.Type[BaseException], BaseException, ta.Optional[types.TracebackType]]  # ta.TypeAlias
LoggingExcInfo = ta.Union[BaseException, LoggingExcInfoTuple]  # ta.TypeAlias
LoggingExcInfoArg = ta.Union[LoggingExcInfo, bool, None]  # ta.TypeAlias


##


@ta.final
class LoggingContext:
    level: NamedLogLevel

    time_ns: int

    exc_info: ta.Optional[LoggingExcInfo] = None
    exc_info_tuple: ta.Optional[LoggingExcInfoTuple] = None

    @ta.final
    class NOT_SET:  # noqa
        def __new__(cls, *args, **kwargs):  # noqa
            raise TypeError

    #

    def __init__(
            self,
            level: LogLevel,
            *,
            time_ns: ta.Optional[int] = None,

            exc_info: LoggingExcInfoArg = False,

            caller: ta.Union[LoggingCaller, ta.Type[NOT_SET], None] = NOT_SET,
            stack_offset: int = 0,
            stack_info: bool = False,
    ) -> None:
        self.level = level if level.__class__ is NamedLogLevel else NamedLogLevel(level)  # type: ignore[assignment]

        #

        if time_ns is None:
            time_ns = time.time_ns()
        self.time_ns: int = time_ns

        #

        if exc_info is True:
            sys_exc_info = sys.exc_info()
            if sys_exc_info[0] is not None:
                exc_info = sys_exc_info
            else:
                exc_info = None
        elif exc_info is False:
            exc_info = None

        if exc_info is not None:
            self.exc_info = exc_info
            if isinstance(exc_info, BaseException):
                self.exc_info_tuple = (type(exc_info), exc_info, exc_info.__traceback__)
            else:
                self.exc_info_tuple = exc_info

        #

        if caller is not LoggingContext.NOT_SET:
            self._caller = caller  # type: ignore[assignment]
        else:
            self._stack_offset = stack_offset
            self._stack_info = stack_info

        #

        self.thread = LoggingThreadInfo.build()
        self.process = LoggingProcessInfo.build()
        self.multiprocessing = LoggingMultiprocessingInfo.build()
        self.asyncio_task = LoggingAsyncioTaskInfo.build()

    #

    _times: LoggingTimeFields

    @property
    def times(self) -> LoggingTimeFields:
        try:
            return self._times
        except AttributeError:
            pass

        times = self._times = LoggingTimeFields.build(self.time_ns)
        return times

    #

    def inc_stack_offset(self, ofs: int = 1) -> 'LoggingContext':
        if hasattr(self, '_stack_offset'):
            self._stack_offset += ofs
        return self

    _caller: ta.Optional[LoggingCaller]

    def build_caller(self) -> ta.Optional[LoggingCaller]:
        """Must be cooperatively called only from the exact configured _stack_offset."""

        try:
            return self._caller
        except AttributeError:
            pass

        caller = self._caller = LoggingCaller.find(
            self._stack_offset + 1,
            stack_info=self._stack_info,
        )
        return caller

    def caller(self) -> ta.Optional[LoggingCaller]:
        try:
            return self._caller
        except AttributeError:
            return None

    _source_file: ta.Optional[LoggingSourceFileInfo]

    def source_file(self) -> ta.Optional[LoggingSourceFileInfo]:
        try:
            return self._source_file
        except AttributeError:
            pass

        if (caller := self.caller()) is None:
            return None

        src_file = self._source_file = LoggingSourceFileInfo.build(caller.file_path)
        return src_file


##


class AnyLogger(Abstract, ta.Generic[T]):
    def is_enabled_for(self, level: LogLevel) -> bool:
        return self.get_effective_level() >= level

    @abc.abstractmethod
    def get_effective_level(self) -> LogLevel:
        raise NotImplementedError

    #

    @ta.final
    def isEnabledFor(self, level: LogLevel) -> bool:  # noqa
        return self.is_enabled_for(level)

    @ta.final
    def getEffectiveLevel(self) -> LogLevel:  # noqa
        return self.get_effective_level()

    ##

    @ta.overload
    def log(self, level: LogLevel, msg: str, *args: ta.Any, **kwargs: ta.Any) -> T:
        ...

    @ta.overload
    def log(self, level: LogLevel, msg: ta.Tuple[ta.Any, ...], **kwargs: ta.Any) -> T:
        ...

    @ta.overload
    def log(self, level: LogLevel, msg_fn: LoggingMsgFn, **kwargs: ta.Any) -> T:
        ...

    @ta.final
    def log(self, level: LogLevel, *args, **kwargs):
        return self._log(LoggingContext(level, stack_offset=1), *args, **kwargs)

    #

    @ta.overload
    def debug(self, msg: str, *args: ta.Any, **kwargs: ta.Any) -> T:
        ...

    @ta.overload
    def debug(self, msg: ta.Tuple[ta.Any, ...], **kwargs: ta.Any) -> T:
        ...

    @ta.overload
    def debug(self, msg_fn: LoggingMsgFn, **kwargs: ta.Any) -> T:
        ...

    @ta.final
    def debug(self, *args, **kwargs):
        return self._log(LoggingContext(NamedLogLevel.DEBUG, stack_offset=1), *args, **kwargs)

    #

    @ta.overload
    def info(self, msg: str, *args: ta.Any, **kwargs: ta.Any) -> T:
        ...

    @ta.overload
    def info(self, msg: ta.Tuple[ta.Any, ...], **kwargs: ta.Any) -> T:
        ...

    @ta.overload
    def info(self, msg_fn: LoggingMsgFn, **kwargs: ta.Any) -> T:
        ...

    @ta.final
    def info(self, *args, **kwargs):
        return self._log(LoggingContext(NamedLogLevel.INFO, stack_offset=1), *args, **kwargs)

    #

    @ta.overload
    def warning(self, msg: str, *args: ta.Any, **kwargs: ta.Any) -> T:
        ...

    @ta.overload
    def warning(self, msg: ta.Tuple[ta.Any, ...], **kwargs: ta.Any) -> T:
        ...

    @ta.overload
    def warning(self, msg_fn: LoggingMsgFn, **kwargs: ta.Any) -> T:
        ...

    @ta.final
    def warning(self, *args, **kwargs):
        return self._log(LoggingContext(NamedLogLevel.WARNING, stack_offset=1), *args, **kwargs)

    #

    @ta.overload
    def error(self, msg: str, *args: ta.Any, **kwargs: ta.Any) -> T:
        ...

    @ta.overload
    def error(self, msg: ta.Tuple[ta.Any, ...], **kwargs: ta.Any) -> T:
        ...

    @ta.overload
    def error(self, msg_fn: LoggingMsgFn, **kwargs: ta.Any) -> T:
        ...

    @ta.final
    def error(self, *args, **kwargs):
        return self._log(LoggingContext(NamedLogLevel.ERROR, stack_offset=1), *args, **kwargs)

    @ta.final
    def exception(self, msg: str, *args: ta.Any, exc_info: LoggingExcInfoArg = True, **kwargs: ta.Any) -> T:
        return self._log(LoggingContext(NamedLogLevel.ERROR, exc_info=exc_info, stack_offset=1), msg, *args, **kwargs)

    #

    @ta.overload
    def critical(self, msg: str, *args: ta.Any, **kwargs: ta.Any) -> T:
        ...

    @ta.overload
    def critical(self, msg: ta.Tuple[ta.Any, ...], **kwargs: ta.Any) -> T:
        ...

    @ta.overload
    def critical(self, msg_fn: LoggingMsgFn, **kwargs: ta.Any) -> T:
        ...

    @ta.final
    def critical(self, *args, **kwargs):
        return self._log(LoggingContext(NamedLogLevel.CRITICAL, stack_offset=1), *args, **kwargs)

    ##

    @abc.abstractmethod
    def _log(self, ctx: LoggingContext, msg: ta.Union[str, LoggingMsgFn], *args: ta.Any, **kwargs: ta.Any) -> T:
        raise NotImplementedError


class Logger(AnyLogger[None], Abstract):
    @abc.abstractmethod
    def _log(self, ctx: LoggingContext, msg: ta.Union[str, LoggingMsgFn], *args: ta.Any, **kwargs: ta.Any) -> None:
        raise NotImplementedError


class AsyncLogger(AnyLogger[ta.Awaitable[None]], Abstract):
    @abc.abstractmethod
    def _log(self, ctx: LoggingContext, msg: ta.Union[str, LoggingMsgFn], *args: ta.Any, **kwargs: ta.Any) -> ta.Awaitable[None]:  # noqa
        raise NotImplementedError


##


class AnyNopLogger(AnyLogger[T], Abstract):
    @ta.final
    def get_effective_level(self) -> LogLevel:
        return 999


@ta.final
class NopLogger(AnyNopLogger[None], Logger):
    def _log(self, ctx: LoggingContext, msg: ta.Union[str, LoggingMsgFn], *args: ta.Any, **kwargs: ta.Any) -> None:
        pass


@ta.final
class AsyncNopLogger(AnyNopLogger[ta.Awaitable[None]], AsyncLogger):
    async def _log(self, ctx: LoggingContext, msg: ta.Union[str, LoggingMsgFn], *args: ta.Any, **kwargs: ta.Any) -> None:  # noqa
        pass
