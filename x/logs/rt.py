"""
TODO:
 - ..lol.. install resolved proxy in caller module globals..
  - ghetto invokedynamic lol
"""
import abc
import io
import logging
import sys
import traceback
import types
import typing as ta


def _find_caller(ofs: int = 0) -> types.FrameType:
    f = sys._getframe(2 + ofs)  # noqa
    while hasattr(f, 'f_code'):
        if f.f_code.co_filename != __file__:
            return f
        f = f.f_back
    raise RuntimeError


class Logger(abc.ABC):

    def __init__(self):
        super().__init__()
        self._wrapped: ta.Optional[logging.Logger] = None

    @property
    def wrapped(self) -> logging.Logger:
        if self._wrapped is None:
            self._wrapped = LoggerAdapter(self)
        return self._wrapped

    def debug(self, msg: str, *args, **kwargs) -> None:
        if self.is_enabled_for(logging.DEBUG):
            self._log(logging.DEBUG, msg, args, **kwargs)

    def info(self, msg: str, *args, **kwargs) -> None:
        if self.is_enabled_for(logging.INFO):
            self._log(logging.INFO, msg, args, **kwargs)

    def warning(self, msg: str, *args, **kwargs) -> None:
        if self.is_enabled_for(logging.WARNING):
            self._log(logging.WARNING, msg, args, **kwargs)

    def error(self, msg: str, *args, **kwargs) -> None:
        if self.is_enabled_for(logging.ERROR):
            self._log(logging.ERROR, msg, args, **kwargs)

    def exception(self, msg: str, *args, exc_info=True, **kwargs) -> None:
        self.error(msg, *args, exc_info=exc_info, **kwargs)

    def critical(self, msg: str, *args, **kwargs) -> None:
        if self.is_enabled_for(logging.CRITICAL):
            self._log(logging.CRITICAL, msg, args, **kwargs)

    def log(self, level: int, msg: str, *args, **kwargs) -> None:
        if not isinstance(level, int):
            raise TypeError('Level must be an integer.')
        if self.is_enabled_for(level):
            self._log(level, msg, args, **kwargs)

    def is_enabled_for(self, level: int) -> bool:
        return level >= self.get_effective_level()

    @abc.abstractmethod
    def get_effective_level(self) -> int:
        raise NotImplementedError

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


class StdlibLogger(Logger):
    def __init__(self, underlying: logging.Logger) -> None:
        super().__init__()
        if not isinstance(underlying, logging.Logger):
            raise TypeError(underlying)
        self._underlying = underlying

    def is_enabled_for(self, level: int) -> bool:
        return self._underlying.isEnabledFor(level)

    def get_effective_level(self) -> int:
        return self._underlying.getEffectiveLevel()

    def _find_caller(self, stack_info: bool = False) -> ta.Tuple[str, int, str, ta.Optional[str]]:
        f = _find_caller(1)
        # TODO: ('(unknown file)', 0, '(unknown function)', None) ?

        sinfo = None
        if stack_info:
            sio = io.StringIO()
            sio.write('Stack (most recent call last):\n')
            traceback.print_stack(f, file=sio)
            sinfo = sio.getvalue()
            sio.close()
            if sinfo[-1] == '\n':
                sinfo = sinfo[:-1]

        return (f.f_code.co_filename, f.f_lineno, f.f_code.co_name, sinfo)

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
        fn, lno, func, sinfo = self._find_caller(stack_info)

        if exc_info:
            if isinstance(exc_info, BaseException):
                exc_info = (type(exc_info), exc_info, exc_info.__traceback__)
            elif not isinstance(exc_info, tuple):
                exc_info = sys.exc_info()

        record = self._underlying.makeRecord(
            name=self._underlying.name,
            level=level,
            fn=fn,
            lno=lno,
            msg=msg,
            args=args,
            exc_info=exc_info,
            func=func,
            extra=extra,
            sinfo=sinfo,
        )

        self._underlying.handle(record)


def _raise_obj_type_error(obj, *args, **kwargs):
    raise TypeError(obj)


class _RaiseTypeErrorDescriptor:
    def __init__(self):
        super().__init__()
        self._name = None

    def __set_name__(self, owner, name):
        if name and self._name is None:
            self._name = name

    def __get__(self, instance, owner):
        if instance is None:
            return self
        raise TypeError(instance, *([self._name] if self._name else []))


class LoggerAdapter(logging.Logger):

    def __init__(self, underlying: Logger) -> None:  # noqa
        # Explicitly no call to super
        if not isinstance(underlying, Logger):
            raise TypeError(underlying)
        self._underlying = underlying

    name = _RaiseTypeErrorDescriptor()
    level = _RaiseTypeErrorDescriptor()
    parent = _RaiseTypeErrorDescriptor()
    propagate = _RaiseTypeErrorDescriptor()
    handlers = _RaiseTypeErrorDescriptor()
    disabled = _RaiseTypeErrorDescriptor()

    setLevel = _raise_obj_type_error

    def isEnabledFor(self, level: int) -> bool:
        return self._underlying.is_enabled_for(level)

    def getEffectiveLevel(self) -> int:
        return self._underlying.get_effective_level()

    getChild = _raise_obj_type_error

    def debug(self, msg: ta.Any, *args, **kwargs) -> None:
        self._underlying.debug(msg, *args, **kwargs)

    def info(self, msg: ta.Any, *args, **kwargs) -> None:
        self._underlying.info(msg, *args, **kwargs)

    def warning(self, msg: ta.Any, *args, **kwargs) -> None:
        self._underlying.warning(msg, *args, **kwargs)

    def warn(self, msg: ta.Any, *args, **kwargs) -> None:
        self._underlying.warning(msg, *args, **kwargs)

    def error(self, msg: ta.Any, *args, **kwargs) -> None:
        self._underlying.error(msg, *args, **kwargs)

    def exception(self, msg: ta.Any, *args, **kwargs) -> None:
        self._underlying.exception(msg, *args, **kwargs)

    def critical(self, msg: ta.Any, *args, **kwargs) -> None:
        self._underlying.critical(msg, *args, **kwargs)

    def log(self, level: int, msg: ta.Any, *args, **kwargs) -> None:
        self._underlying.log(level, msg, *args, **kwargs)

    def _log(  # noqa
            self,
            level: int,
            msg: str,
            args: ta.Any,
            exc_info: ta.Any = None,
            extra: ta.Any = None,
            stack_info: bool = False,
    ) -> None:
        self._underlying._log(  # noqa
            level,
            msg,
            args,
            exc_info=exc_info,
            extra=extra,
            stack_info=stack_info,
        )

    filter = _raise_obj_type_error
    addHandler = _raise_obj_type_error
    removeHandler = _raise_obj_type_error
    findCaller = _raise_obj_type_error
    handle = _raise_obj_type_error
    makeRecord = _raise_obj_type_error
    hasHandlers = _raise_obj_type_error
