# ruff: noqa: UP006 UP007 UP045 UP046
# @omlish-lite
import abc
import typing as ta

from ..lite.abstract import Abstract
from .contexts import CaptureLoggingContext
from .contexts import CaptureLoggingContextImpl
from .contexts import LoggingExcInfoArg
from .levels import LogLevel
from .levels import NamedLogLevel


T = ta.TypeVar('T')


LoggingMsgFn = ta.Callable[[], ta.Union[str, tuple]]  # ta.TypeAlias


##


class AnyLogger(Abstract, ta.Generic[T]):
    def is_enabled_for(self, level: LogLevel) -> bool:
        return level >= self.get_effective_level()

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
        return self._log(CaptureLoggingContextImpl(level, stack_offset=1), *args, **kwargs)

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
        return self._log(CaptureLoggingContextImpl(NamedLogLevel.DEBUG, stack_offset=1), *args, **kwargs)

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
        return self._log(CaptureLoggingContextImpl(NamedLogLevel.INFO, stack_offset=1), *args, **kwargs)

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
        return self._log(CaptureLoggingContextImpl(NamedLogLevel.WARNING, stack_offset=1), *args, **kwargs)

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
        return self._log(CaptureLoggingContextImpl(NamedLogLevel.ERROR, stack_offset=1), *args, **kwargs)

    #

    @ta.overload
    def exception(self, msg: str, *args: ta.Any, exc_info: LoggingExcInfoArg = True, **kwargs: ta.Any) -> T:
        ...

    @ta.overload
    def exception(self, msg: ta.Tuple[ta.Any, ...], *, exc_info: LoggingExcInfoArg = True, **kwargs: ta.Any) -> T:
        ...

    @ta.overload
    def exception(self, msg_fn: LoggingMsgFn, *, exc_info: LoggingExcInfoArg = True, **kwargs: ta.Any) -> T:
        ...

    @ta.final
    def exception(self, *args, exc_info: LoggingExcInfoArg = True, **kwargs):
        return self._log(CaptureLoggingContextImpl(NamedLogLevel.ERROR, exc_info=exc_info, stack_offset=1), *args, **kwargs)  # noqa

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
        return self._log(CaptureLoggingContextImpl(NamedLogLevel.CRITICAL, stack_offset=1), *args, **kwargs)

    ##

    @classmethod
    def _prepare_msg_args(cls, msg: ta.Union[str, tuple, LoggingMsgFn], *args: ta.Any) -> ta.Tuple[str, tuple]:
        if callable(msg):
            if args:
                raise TypeError(f'Must not provide both a message function and args: {msg=} {args=}')
            x = msg()
            if isinstance(x, str):
                return x, ()
            elif isinstance(x, tuple):
                if x:
                    return x[0], x[1:]
                else:
                    return '', ()
            else:
                raise TypeError(x)

        elif isinstance(msg, tuple):
            if args:
                raise TypeError(f'Must not provide both a tuple message and args: {msg=} {args=}')
            if msg:
                return msg[0], msg[1:]
            else:
                return '', ()

        elif isinstance(msg, str):
            return msg, args

        else:
            raise TypeError(msg)

    @abc.abstractmethod
    def _log(self, ctx: CaptureLoggingContext, msg: ta.Union[str, tuple, LoggingMsgFn], *args: ta.Any, **kwargs: ta.Any) -> T:  # noqa
        raise NotImplementedError


class Logger(AnyLogger[None], Abstract):
    @abc.abstractmethod
    def _log(self, ctx: CaptureLoggingContext, msg: ta.Union[str, tuple, LoggingMsgFn], *args: ta.Any, **kwargs: ta.Any) -> None:  # noqa
        raise NotImplementedError


class AsyncLogger(AnyLogger[ta.Awaitable[None]], Abstract):
    @abc.abstractmethod
    def _log(self, ctx: CaptureLoggingContext, msg: ta.Union[str, tuple, LoggingMsgFn], *args: ta.Any, **kwargs: ta.Any) -> ta.Awaitable[None]:  # noqa
        raise NotImplementedError


##


class AnyNopLogger(AnyLogger[T], Abstract):
    @ta.final
    def get_effective_level(self) -> LogLevel:
        return -999


@ta.final
class NopLogger(AnyNopLogger[None], Logger):
    def _log(self, ctx: CaptureLoggingContext, msg: ta.Union[str, tuple, LoggingMsgFn], *args: ta.Any, **kwargs: ta.Any) -> None:  # noqa
        pass


@ta.final
class AsyncNopLogger(AnyNopLogger[ta.Awaitable[None]], AsyncLogger):
    async def _log(self, ctx: CaptureLoggingContext, msg: ta.Union[str, tuple, LoggingMsgFn], *args: ta.Any, **kwargs: ta.Any) -> None:  # noqa
        pass
