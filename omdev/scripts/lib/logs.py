#!/usr/bin/env python3
# noinspection DuplicatedCode
# @omlish-lite
# @omlish-script
# @omlish-generated
# @omlish-amalg-output ../../../omlish/logs/_amalg.py
# @omlish-git-diff-omit
# ruff: noqa: N802 UP006 UP007 UP036 UP045 UP046
import abc
import collections.abc
import contextlib
import datetime
import functools
import io
import json
import logging
import os.path
import sys
import threading
import time
import traceback
import types
import typing as ta


########################################


if sys.version_info < (3, 8):
    raise OSError(f'Requires python (3, 8), got {sys.version_info} from {sys.executable}')  # noqa


########################################


# ../lite/abstract.py
T = ta.TypeVar('T')

# levels.py
LogLevel = int  # ta.TypeAlias

# infos.py
LoggingMsgFn = ta.Callable[[], ta.Union[str, tuple]]  # ta.TypeAlias
LoggingExcInfoTuple = ta.Tuple[ta.Type[BaseException], BaseException, ta.Optional[types.TracebackType]]  # ta.TypeAlias
LoggingExcInfo = ta.Union[BaseException, LoggingExcInfoTuple]  # ta.TypeAlias
LoggingExcInfoArg = ta.Union[LoggingExcInfo, bool, None]  # ta.TypeAlias
LoggingContextInfo = ta.Any  # ta.TypeAlias

# contexts.py
LoggingContextInfoT = ta.TypeVar('LoggingContextInfoT', bound=LoggingContextInfo)


########################################
# ../../lite/abstract.py


##


_ABSTRACT_METHODS_ATTR = '__abstractmethods__'
_IS_ABSTRACT_METHOD_ATTR = '__isabstractmethod__'


def is_abstract_method(obj: ta.Any) -> bool:
    return bool(getattr(obj, _IS_ABSTRACT_METHOD_ATTR, False))


def compute_abstract_methods(cls: type) -> ta.FrozenSet[str]:
    # ~> https://github.com/python/cpython/blob/f3476c6507381ca860eec0989f53647b13517423/Modules/_abc.c#L358

    # Stage 1: direct abstract methods

    abstracts = {
        a
        # Get items as a list to avoid mutation issues during iteration
        for a, v in list(cls.__dict__.items())
        if is_abstract_method(v)
    }

    # Stage 2: inherited abstract methods

    for base in cls.__bases__:
        # Get __abstractmethods__ from base if it exists
        if (base_abstracts := getattr(base, _ABSTRACT_METHODS_ATTR, None)) is None:
            continue

        # Iterate over abstract methods in base
        for key in base_abstracts:
            # Check if this class has an attribute with this name
            try:
                value = getattr(cls, key)
            except AttributeError:
                # Attribute not found in this class, skip
                continue

            # Check if it's still abstract
            if is_abstract_method(value):
                abstracts.add(key)

    return frozenset(abstracts)


def update_abstracts(cls: ta.Type[T], *, force: bool = False) -> ta.Type[T]:
    if not force and not hasattr(cls, _ABSTRACT_METHODS_ATTR):
        # Per stdlib: We check for __abstractmethods__ here because cls might by a C implementation or a python
        # implementation (especially during testing), and we want to handle both cases.
        return cls

    abstracts = compute_abstract_methods(cls)
    setattr(cls, _ABSTRACT_METHODS_ATTR, abstracts)
    return cls


#


class AbstractTypeError(TypeError):
    pass


_FORCE_ABSTRACT_ATTR = '__forceabstract__'


class Abstract:
    """
    Different from, but interoperable with, abc.ABC / abc.ABCMeta:

     - This raises AbstractTypeError during class creation, not instance instantiation - unless Abstract or abc.ABC are
       explicitly present in the class's direct bases.
     - This will forbid instantiation of classes with Abstract in their direct bases even if there are no
       abstractmethods left on the class.
     - This is a mixin, not a metaclass.
     - As it is not an ABCMeta, this does not support virtual base classes. As a result, operations like `isinstance`
       and `issubclass` are ~7x faster.
     - It additionally enforces a base class order of (Abstract, abc.ABC) to preemptively prevent common mro conflicts.

    If not mixed-in with an ABCMeta, it will update __abstractmethods__ itself.
    """

    __slots__ = ()

    __abstractmethods__: ta.ClassVar[ta.FrozenSet[str]] = frozenset()

    #

    def __forceabstract__(self):
        raise TypeError

    # This is done manually, rather than through @abc.abstractmethod, to mask it from static analysis.
    setattr(__forceabstract__, _IS_ABSTRACT_METHOD_ATTR, True)

    #

    def __init_subclass__(cls, **kwargs: ta.Any) -> None:
        setattr(
            cls,
            _FORCE_ABSTRACT_ATTR,
            getattr(Abstract, _FORCE_ABSTRACT_ATTR) if Abstract in cls.__bases__ else False,
        )

        super().__init_subclass__(**kwargs)

        if not (Abstract in cls.__bases__ or abc.ABC in cls.__bases__):
            if ams := compute_abstract_methods(cls):
                amd = {
                    a: mcls
                    for mcls in cls.__mro__[::-1]
                    for a in ams
                    if a in mcls.__dict__
                }

                raise AbstractTypeError(
                    f'Cannot subclass abstract class {cls.__name__} with abstract methods: ' +
                    ', '.join(sorted([
                        '.'.join([
                            *([
                                *([m] if (m := getattr(c, '__module__')) else []),
                                getattr(c, '__qualname__', getattr(c, '__name__')),
                            ] if c is not None else '?'),
                            a,
                        ])
                        for a in ams
                        for c in [amd.get(a)]
                    ])),
                )

        xbi = (Abstract, abc.ABC)  # , ta.Generic ?
        bis = [(cls.__bases__.index(b), b) for b in xbi if b in cls.__bases__]
        if bis != sorted(bis):
            raise TypeError(
                f'Abstract subclass {cls.__name__} must have proper base class order of '
                f'({", ".join(getattr(b, "__name__") for b in xbi)}), got: '
                f'({", ".join(getattr(b, "__name__") for _, b in sorted(bis))})',
            )

        if not isinstance(cls, abc.ABCMeta):
            update_abstracts(cls, force=True)


########################################
# ../../lite/json.py


##


JSON_PRETTY_INDENT = 2

JSON_PRETTY_KWARGS: ta.Mapping[str, ta.Any] = dict(
    indent=JSON_PRETTY_INDENT,
)

json_dump_pretty: ta.Callable[..., None] = functools.partial(json.dump, **JSON_PRETTY_KWARGS)
json_dumps_pretty: ta.Callable[..., str] = functools.partial(json.dumps, **JSON_PRETTY_KWARGS)


##


JSON_COMPACT_SEPARATORS = (',', ':')

JSON_COMPACT_KWARGS: ta.Mapping[str, ta.Any] = dict(
    indent=None,
    separators=JSON_COMPACT_SEPARATORS,
)

json_dump_compact: ta.Callable[..., None] = functools.partial(json.dump, **JSON_COMPACT_KWARGS)
json_dumps_compact: ta.Callable[..., str] = functools.partial(json.dumps, **JSON_COMPACT_KWARGS)


########################################
# ../levels.py


##


@ta.final
class NamedLogLevel(int):
    # logging.getLevelNamesMapping (or, as that is unavailable <3.11, logging._nameToLevel) includes the deprecated
    # aliases.
    _NAMES_BY_INT: ta.ClassVar[ta.Mapping[LogLevel, str]] = dict(sorted(logging._levelToName.items(), key=lambda t: -t[0]))  # noqa

    _INTS_BY_NAME: ta.ClassVar[ta.Mapping[str, LogLevel]] = {v: k for k, v in _NAMES_BY_INT.items()}

    _NAME_INT_PAIRS: ta.ClassVar[ta.Sequence[ta.Tuple[str, LogLevel]]] = list(_INTS_BY_NAME.items())

    #

    _CACHE: ta.ClassVar[ta.MutableMapping[int, 'NamedLogLevel']] = {}

    @ta.overload
    def __new__(cls, name: str, offset: int = 0, /) -> 'NamedLogLevel':
        ...

    @ta.overload
    def __new__(cls, i: int, /) -> 'NamedLogLevel':
        ...

    def __new__(cls, x, offset=0, /):
        if isinstance(x, str):
            return cls(cls._INTS_BY_NAME[x.upper()] + offset)
        elif not offset and (c := cls._CACHE.get(x)) is not None:
            return c
        else:
            return super().__new__(cls, x + offset)

    #

    _name_and_offset: ta.Tuple[str, int]

    @property
    def name_and_offset(self) -> ta.Tuple[str, int]:
        try:
            return self._name_and_offset
        except AttributeError:
            pass

        if (n := self._NAMES_BY_INT.get(self)) is not None:
            t = (n, 0)
        else:
            for n, i in self._NAME_INT_PAIRS:  # noqa
                if self >= i:
                    t = (n, (self - i))
                    break
            else:
                t = ('NOTSET', int(self))

        self._name_and_offset = t
        return t

    @property
    def exact_name(self) -> ta.Optional[str]:
        n, o = self.name_and_offset
        return n if not o else None

    @property
    def effective_name(self) -> str:
        n, _ = self.name_and_offset
        return n

    #

    def __str__(self) -> str:
        return self.exact_name or f'{self.effective_name}{int(self):+}'

    def __repr__(self) -> str:
        n, o = self.name_and_offset
        return f'{self.__class__.__name__}({n!r}{f", {int(o)}" if o else ""})'

    #

    CRITICAL: ta.ClassVar['NamedLogLevel']
    ERROR: ta.ClassVar['NamedLogLevel']
    WARNING: ta.ClassVar['NamedLogLevel']
    INFO: ta.ClassVar['NamedLogLevel']
    DEBUG: ta.ClassVar['NamedLogLevel']
    NOTSET: ta.ClassVar['NamedLogLevel']


NamedLogLevel.CRITICAL = NamedLogLevel(logging.CRITICAL)
NamedLogLevel.ERROR = NamedLogLevel(logging.ERROR)
NamedLogLevel.WARNING = NamedLogLevel(logging.WARNING)
NamedLogLevel.INFO = NamedLogLevel(logging.INFO)
NamedLogLevel.DEBUG = NamedLogLevel(logging.DEBUG)
NamedLogLevel.NOTSET = NamedLogLevel(logging.NOTSET)


NamedLogLevel._CACHE.update({i: NamedLogLevel(i) for i in NamedLogLevel._NAMES_BY_INT})  # noqa


########################################
# ../std/filters.py


##


class TidLoggingFilter(logging.Filter):
    def filter(self, record):
        # FIXME: handle better - missing from wasm and cosmos
        if hasattr(threading, 'get_native_id'):
            record.tid = threading.get_native_id()
        else:
            record.tid = '?'
        return True


########################################
# ../std/proxy.py


##


class ProxyLoggingFilterer(logging.Filterer):
    def __init__(self, underlying: logging.Filterer) -> None:  # noqa
        self._underlying = underlying

    @property
    def underlying(self) -> logging.Filterer:
        return self._underlying

    @property
    def filters(self):
        return self._underlying.filters

    @filters.setter
    def filters(self, filters):
        self._underlying.filters = filters

    def addFilter(self, filter):  # noqa
        self._underlying.addFilter(filter)

    def removeFilter(self, filter):  # noqa
        self._underlying.removeFilter(filter)

    def filter(self, record):
        return self._underlying.filter(record)


class ProxyLoggingHandler(ProxyLoggingFilterer, logging.Handler):
    def __init__(self, underlying: logging.Handler) -> None:  # noqa
        ProxyLoggingFilterer.__init__(self, underlying)

    _underlying: logging.Handler

    @property
    def underlying(self) -> logging.Handler:
        return self._underlying

    def get_name(self):
        return self._underlying.get_name()

    def set_name(self, name):
        self._underlying.set_name(name)

    @property
    def name(self):  # type: ignore[override]
        return self._underlying.name

    @property
    def level(self):
        return self._underlying.level

    @level.setter
    def level(self, level):
        self._underlying.level = level

    @property
    def formatter(self):
        return self._underlying.formatter

    @formatter.setter
    def formatter(self, formatter):
        self._underlying.formatter = formatter

    def createLock(self):
        self._underlying.createLock()

    def acquire(self):
        self._underlying.acquire()

    def release(self):
        self._underlying.release()

    def setLevel(self, level):
        self._underlying.setLevel(level)

    def format(self, record):
        return self._underlying.format(record)

    def emit(self, record):
        self._underlying.emit(record)

    def handle(self, record):
        return self._underlying.handle(record)

    def setFormatter(self, fmt):
        self._underlying.setFormatter(fmt)

    def flush(self):
        self._underlying.flush()

    def close(self):
        self._underlying.close()

    def handleError(self, record):
        self._underlying.handleError(record)


########################################
# ../warnings.py


##


class LoggingSetupWarning(Warning):
    pass


########################################
# ../infos.py
"""
TODO:
 - remove redundant info fields only present for std adaptation (Level.name, ...)
"""


##


def logging_context_info(cls):
    return cls


@ta.final
class LoggingContextInfos:
    def __new__(cls, *args, **kwargs):  # noqa
        raise TypeError

    #

    @logging_context_info
    @ta.final
    class Name(ta.NamedTuple):
        name: str

    @logging_context_info
    @ta.final
    class Level(ta.NamedTuple):
        level: NamedLogLevel
        name: str

        @classmethod
        def build(cls, level: int) -> 'LoggingContextInfos.Level':
            nl: NamedLogLevel = level if level.__class__ is NamedLogLevel else NamedLogLevel(level)  # type: ignore[assignment]  # noqa
            return cls(
                level=nl,
                name=logging.getLevelName(nl),
            )

    @logging_context_info
    @ta.final
    class Msg(ta.NamedTuple):
        msg: str
        args: ta.Union[tuple, ta.Mapping[ta.Any, ta.Any], None]

        @classmethod
        def build(
                cls,
                msg: ta.Union[str, tuple, LoggingMsgFn],
                *args: ta.Any,
        ) -> 'LoggingContextInfos.Msg':
            s: str
            a: ta.Any

            if callable(msg):
                if args:
                    raise TypeError(f'Must not provide both a message function and args: {msg=} {args=}')
                x = msg()
                if isinstance(x, str):
                    s, a = x, ()
                elif isinstance(x, tuple):
                    if x:
                        s, a = x[0], x[1:]
                    else:
                        s, a = '', ()
                else:
                    raise TypeError(x)

            elif isinstance(msg, tuple):
                if args:
                    raise TypeError(f'Must not provide both a tuple message and args: {msg=} {args=}')
                if msg:
                    s, a = msg[0], msg[1:]
                else:
                    s, a = '', ()

            elif isinstance(msg, str):
                s, a = msg, args

            else:
                raise TypeError(msg)

            # https://github.com/python/cpython/blob/e709361fc87d0d9ab9c58033a0a7f2fef0ad43d2/Lib/logging/__init__.py#L307  # noqa
            if a and len(a) == 1 and isinstance(a[0], collections.abc.Mapping) and a[0]:
                a = a[0]

            return cls(
                msg=s,
                args=a,
            )

    @logging_context_info
    @ta.final
    class Extra(ta.NamedTuple):
        extra: ta.Mapping[ta.Any, ta.Any]

    @logging_context_info
    @ta.final
    class Time(ta.NamedTuple):
        ns: int
        secs: float
        msecs: float
        relative_secs: float

        @classmethod
        def get_std_start_ns(cls) -> int:
            x: ta.Any = logging._startTime  # type: ignore[attr-defined]  # noqa

            # Before 3.13.0b1 this will be `time.time()`, a float of seconds. After that, it will be `time.time_ns()`,
            # an int.
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
                ns: int,
                *,
                start_ns: ta.Optional[int] = None,
        ) -> 'LoggingContextInfos.Time':
            # https://github.com/python/cpython/commit/1316692e8c7c1e1f3b6639e51804f9db5ed892ea
            secs = ns / 1e9  # ns to float seconds

            # Get the number of whole milliseconds (0-999) in the fractional part of seconds.
            # Eg: 1_677_903_920_999_998_503 ns --> 999_998_503 ns--> 999 ms
            # Convert to float by adding 0.0 for historical reasons. See gh-89047
            msecs = (ns % 1_000_000_000) // 1_000_000 + 0.0

            # https://github.com/python/cpython/commit/1500a23f33f5a6d052ff1ef6383d9839928b8ff1
            if msecs == 999.0 and int(secs) != ns // 1_000_000_000:
                # ns -> sec conversion can round up, e.g:
                # 1_677_903_920_999_999_900 ns --> 1_677_903_921.0 sec
                msecs = 0.0

            if start_ns is None:
                start_ns = cls.get_std_start_ns()
            relative_secs = (ns - start_ns) / 1e6

            return cls(
                ns=ns,
                secs=secs,
                msecs=msecs,
                relative_secs=relative_secs,
            )

    @logging_context_info
    @ta.final
    class Exc(ta.NamedTuple):
        info: LoggingExcInfo
        info_tuple: LoggingExcInfoTuple

        @classmethod
        def build(
                cls,
                arg: LoggingExcInfoArg = False,
        ) -> ta.Optional['LoggingContextInfos.Exc']:
            if arg is True:
                sys_exc_info = sys.exc_info()
                if sys_exc_info[0] is not None:
                    arg = sys_exc_info
                else:
                    arg = None
            elif arg is False:
                arg = None
            if arg is None:
                return None

            info: LoggingExcInfo = arg
            if isinstance(info, BaseException):
                info_tuple: LoggingExcInfoTuple = (type(info), info, info.__traceback__)  # noqa
            else:
                info_tuple = info

            return cls(
                info=info,
                info_tuple=info_tuple,
            )

    @logging_context_info
    @ta.final
    class Caller(ta.NamedTuple):
        file_path: str
        line_no: int
        func_name: str
        stack_info: ta.Optional[str]

        @classmethod
        def is_internal_frame(cls, frame: types.FrameType) -> bool:
            file_path = os.path.normcase(frame.f_code.co_filename)

            # Yes, really.
            # https://github.com/python/cpython/blob/e709361fc87d0d9ab9c58033a0a7f2fef0ad43d2/Lib/logging/__init__.py#L204  # noqa
            # https://github.com/python/cpython/commit/5ca6d7469be53960843df39bb900e9c3359f127f
            if 'importlib' in file_path and '_bootstrap' in file_path:
                return True

            return False

        @classmethod
        def find_frame(cls, stack_offset: int = 0) -> ta.Optional[types.FrameType]:
            f: ta.Optional[types.FrameType] = sys._getframe(2 + stack_offset)  # noqa

            while f is not None:
                # NOTE: We don't check __file__ like stdlib since we may be running amalgamated - we rely on careful,
                # manual stack_offset management.
                if hasattr(f, 'f_code'):
                    return f

                f = f.f_back

            return None

        @classmethod
        def build(
                cls,
                stack_offset: int = 0,
                *,
                stack_info: bool = False,
        ) -> ta.Optional['LoggingContextInfos.Caller']:
            if (f := cls.find_frame(stack_offset + 1)) is None:
                return None

            # https://github.com/python/cpython/blob/08e9794517063c8cd92c48714071b1d3c60b71bd/Lib/logging/__init__.py#L1616-L1623  # noqa
            sinfo = None
            if stack_info:
                sio = io.StringIO()
                traceback.print_stack(f, file=sio)
                sinfo = sio.getvalue()
                sio.close()
                if sinfo[-1] == '\n':
                    sinfo = sinfo[:-1]

            return cls(
                file_path=f.f_code.co_filename,
                line_no=f.f_lineno or 0,
                func_name=f.f_code.co_name,
                stack_info=sinfo,
            )

    @logging_context_info
    @ta.final
    class SourceFile(ta.NamedTuple):
        file_name: str
        module: str

        @classmethod
        def build(cls, caller_file_path: ta.Optional[str]) -> ta.Optional['LoggingContextInfos.SourceFile']:
            if caller_file_path is None:
                return None

            # https://github.com/python/cpython/blob/e709361fc87d0d9ab9c58033a0a7f2fef0ad43d2/Lib/logging/__init__.py#L331-L336  # noqa
            try:
                file_name = os.path.basename(caller_file_path)
                module = os.path.splitext(file_name)[0]
            except (TypeError, ValueError, AttributeError):
                return None

            return cls(
                file_name=file_name,
                module=module,
            )

    @logging_context_info
    @ta.final
    class Thread(ta.NamedTuple):
        ident: int
        native_id: ta.Optional[int]
        name: str

        @classmethod
        def build(cls) -> 'LoggingContextInfos.Thread':
            return cls(
                ident=threading.get_ident(),
                native_id=threading.get_native_id() if hasattr(threading, 'get_native_id') else None,
                name=threading.current_thread().name,
            )

    @logging_context_info
    @ta.final
    class Process(ta.NamedTuple):
        pid: int

        @classmethod
        def build(cls) -> 'LoggingContextInfos.Process':
            return cls(
                pid=os.getpid(),
            )

    @logging_context_info
    @ta.final
    class Multiprocessing(ta.NamedTuple):
        process_name: str

        @classmethod
        def build(cls) -> ta.Optional['LoggingContextInfos.Multiprocessing']:
            # https://github.com/python/cpython/blob/e709361fc87d0d9ab9c58033a0a7f2fef0ad43d2/Lib/logging/__init__.py#L355-L364  # noqa
            if (mp := sys.modules.get('multiprocessing')) is None:
                return None

            return cls(
                process_name=mp.current_process().name,
            )

    @logging_context_info
    @ta.final
    class AsyncioTask(ta.NamedTuple):
        name: str

        @classmethod
        def build(cls) -> ta.Optional['LoggingContextInfos.AsyncioTask']:
            # https://github.com/python/cpython/blob/e709361fc87d0d9ab9c58033a0a7f2fef0ad43d2/Lib/logging/__init__.py#L372-L377  # noqa
            if (asyncio := sys.modules.get('asyncio')) is None:
                return None

            try:
                task = asyncio.current_task()
            except Exception:  # noqa
                return None

            if task is None:
                return None

            return cls(
                name=task.get_name(),  # Always non-None
            )


##


class UnexpectedLoggingStartTimeWarning(LoggingSetupWarning):
    pass


def _check_logging_start_time() -> None:
    if (x := LoggingContextInfos.Time.get_std_start_ns()) < (t := time.time()):
        import warnings  # noqa

        warnings.warn(
            f'Unexpected logging start time detected: '
            f'get_std_start_ns={x}, '
            f'time.time()={t}',
            UnexpectedLoggingStartTimeWarning,
        )


_check_logging_start_time()


########################################
# ../std/json.py
"""
TODO:
 - translate json keys
"""


##


class JsonLoggingFormatter(logging.Formatter):
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


########################################
# ../contexts.py


##


class LoggingContext(Abstract):
    @abc.abstractmethod
    def get_info(self, ty: ta.Type[LoggingContextInfoT]) -> ta.Optional[LoggingContextInfoT]:
        raise NotImplementedError

    @ta.final
    def __getitem__(self, ty: ta.Type[LoggingContextInfoT]) -> ta.Optional[LoggingContextInfoT]:
        return self.get_info(ty)

    @ta.final
    def must_get_info(self, ty: ta.Type[LoggingContextInfoT]) -> LoggingContextInfoT:
        if (info := self.get_info(ty)) is None:
            raise TypeError(f'LoggingContextInfo absent: {ty}')
        return info


@ta.final
class SimpleLoggingContext(LoggingContext):
    def __init__(self, *infos: LoggingContextInfo) -> None:
        self._infos: ta.Dict[ta.Type[LoggingContextInfo], LoggingContextInfo] = {type(i): i for i in infos}

    def get_info(self, ty: ta.Type[LoggingContextInfoT]) -> ta.Optional[LoggingContextInfoT]:
        return self._infos.get(ty)


##


class CaptureLoggingContext(LoggingContext, Abstract):
    @abc.abstractmethod
    def set_basic(
            self,
            name: str,

            msg: ta.Union[str, tuple, LoggingMsgFn],
            args: tuple,
    ) -> 'CaptureLoggingContext':
        raise NotImplementedError

    #

    class AlreadyCapturedError(Exception):
        pass

    class NotCapturedError(Exception):
        pass

    @abc.abstractmethod
    def capture(self) -> None:
        """Must be cooperatively called only from the expected locations."""

        raise NotImplementedError


@ta.final
class CaptureLoggingContextImpl(CaptureLoggingContext):
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

            caller: ta.Union[LoggingContextInfos.Caller, ta.Type[NOT_SET], None] = NOT_SET,
            stack_offset: int = 0,
            stack_info: bool = False,
    ) -> None:
        if time_ns is None:
            time_ns = time.time_ns()

        # Done early to not trample on sys.exc_info()
        exc = LoggingContextInfos.Exc.build(exc_info)

        self._infos: ta.Dict[ta.Type[LoggingContextInfo], LoggingContextInfo] = {}
        self._set_info(
            LoggingContextInfos.Level.build(level),
            exc,
            LoggingContextInfos.Time.build(time_ns),
        )

        if caller is not CaptureLoggingContextImpl.NOT_SET:
            self._infos[LoggingContextInfos.Caller] = caller
        else:
            self._stack_offset = stack_offset
            self._stack_info = stack_info

    def _set_info(self, *infos: ta.Optional[LoggingContextInfo]) -> 'CaptureLoggingContextImpl':
        for info in infos:
            if info is not None:
                self._infos[type(info)] = info
        return self

    def get_info(self, ty: ta.Type[LoggingContextInfoT]) -> ta.Optional[LoggingContextInfoT]:
        return self._infos.get(ty)

    ##

    def set_basic(
            self,
            name: str,

            msg: ta.Union[str, tuple, LoggingMsgFn],
            args: tuple,
    ) -> 'CaptureLoggingContextImpl':
        return self._set_info(
            LoggingContextInfos.Name(name),
            LoggingContextInfos.Msg.build(msg, *args),
        )

    ##

    _stack_offset: int
    _stack_info: bool

    def inc_stack_offset(self, ofs: int = 1) -> 'CaptureLoggingContext':
        if hasattr(self, '_stack_offset'):
            self._stack_offset += ofs
        return self

    _has_captured: bool = False

    def capture(self) -> None:
        if self._has_captured:
            raise CaptureLoggingContextImpl.AlreadyCapturedError
        self._has_captured = True

        if LoggingContextInfos.Caller not in self._infos:
            self._set_info(LoggingContextInfos.Caller.build(
                self._stack_offset + 1,
                stack_info=self._stack_info,
            ))

        if (caller := self[LoggingContextInfos.Caller]) is not None:
            self._set_info(LoggingContextInfos.SourceFile.build(
                caller.file_path,
            ))

        self._set_info(
            LoggingContextInfos.Thread.build(),
            LoggingContextInfos.Process.build(),
            LoggingContextInfos.Multiprocessing.build(),
            LoggingContextInfos.AsyncioTask.build(),
        )


########################################
# ../standard.py
"""
TODO:
 - !! move to std !!
 - structured
 - prefixed
 - debug
 - optional noisy? noisy will never be lite - some kinda configure_standard callback mechanism?
"""


##


STANDARD_LOG_FORMAT_PARTS = [
    ('asctime', '%(asctime)-15s'),
    ('process', 'pid=%(process)s'),
    ('thread', 'tid=%(thread)x'),
    ('levelname', '%(levelname)s'),
    ('name', '%(name)s'),
    ('separator', '::'),
    ('message', '%(message)s'),
]


class StandardLoggingFormatter(logging.Formatter):
    @staticmethod
    def build_log_format(parts: ta.Iterable[ta.Tuple[str, str]]) -> str:
        return ' '.join(v for k, v in parts)

    converter = datetime.datetime.fromtimestamp  # type: ignore

    def formatTime(self, record, datefmt=None):
        ct = self.converter(record.created)
        if datefmt:
            return ct.strftime(datefmt)  # noqa
        else:
            t = ct.strftime('%Y-%m-%d %H:%M:%S')
            return '%s.%03d' % (t, record.msecs)  # noqa


##


class StandardConfiguredLoggingHandler(ProxyLoggingHandler):
    def __init_subclass__(cls, **kwargs):
        raise TypeError('This class serves only as a marker and should not be subclassed.')


##


@contextlib.contextmanager
def _locking_logging_module_lock() -> ta.Iterator[None]:
    if hasattr(logging, '_acquireLock'):
        logging._acquireLock()  # noqa
        try:
            yield
        finally:
            logging._releaseLock()  # type: ignore  # noqa

    elif hasattr(logging, '_lock'):
        # https://github.com/python/cpython/commit/74723e11109a320e628898817ab449b3dad9ee96
        with logging._lock:  # noqa
            yield

    else:
        raise Exception("Can't find lock in logging module")


def configure_standard_logging(
        level: ta.Union[int, str] = logging.INFO,
        *,
        target: ta.Optional[logging.Logger] = None,

        force: bool = False,

        handler_factory: ta.Optional[ta.Callable[[], logging.Handler]] = None,

        formatter: ta.Optional[logging.Formatter] = None,  # noqa
        json: bool = False,
) -> ta.Optional[StandardConfiguredLoggingHandler]:
    with _locking_logging_module_lock():
        if target is None:
            target = logging.root

        #

        if not force:
            if any(isinstance(h, StandardConfiguredLoggingHandler) for h in list(target.handlers)):
                return None

        #

        if handler_factory is not None:
            handler = handler_factory()
        else:
            handler = logging.StreamHandler()

        #

        if formatter is None:
            if json:
                formatter = JsonLoggingFormatter()
            else:
                formatter = StandardLoggingFormatter(StandardLoggingFormatter.build_log_format(STANDARD_LOG_FORMAT_PARTS))  # noqa
        handler.setFormatter(formatter)

        #

        handler.addFilter(TidLoggingFilter())

        #

        target.addHandler(handler)

        #

        if level is not None:
            target.setLevel(level)

        #

        return StandardConfiguredLoggingHandler(handler)


########################################
# ../base.py


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


########################################
# ../std/records.py
"""
TODO:
 - TypedDict?
"""


##


class LoggingContextInfoRecordAdapters:
    # Ref:
    #  - https://docs.python.org/3/library/logging.html#logrecord-attributes
    #
    # LogRecord:
    #  - https://github.com/python/cpython/blob/39b2f82717a69dde7212bc39b673b0f55c99e6a3/Lib/logging/__init__.py#L276 (3.8)  # noqa
    #  - https://github.com/python/cpython/blob/f070f54c5f4a42c7c61d1d5d3b8f3b7203b4a0fb/Lib/logging/__init__.py#L286 (~3.14)  # noqa
    #

    def __new__(cls, *args, **kwargs):  # noqa
        raise TypeError

    class Adapter(Abstract, ta.Generic[T]):
        @property
        @abc.abstractmethod
        def info_cls(self) -> ta.Type[LoggingContextInfo]:
            raise NotImplementedError

        #

        @ta.final
        class NOT_SET:  # noqa
            def __new__(cls, *args, **kwargs):  # noqa
                raise TypeError

        class RecordAttr(ta.NamedTuple):
            name: str
            type: ta.Any
            default: ta.Any

        # @abc.abstractmethod
        record_attrs: ta.ClassVar[ta.Mapping[str, RecordAttr]]

        @property
        @abc.abstractmethod
        def _record_attrs(self) -> ta.Union[
            ta.Mapping[str, ta.Any],
            ta.Mapping[str, ta.Tuple[ta.Any, ta.Any]],
        ]:
            raise NotImplementedError

        #

        @abc.abstractmethod
        def context_to_record(self, ctx: LoggingContext) -> ta.Mapping[str, ta.Any]:
            raise NotImplementedError

        #

        @abc.abstractmethod
        def record_to_info(self, rec: logging.LogRecord) -> ta.Optional[T]:
            raise NotImplementedError

        #

        def __init_subclass__(cls, **kwargs: ta.Any) -> None:
            super().__init_subclass__(**kwargs)

            if Abstract in cls.__bases__:
                return

            if 'record_attrs' in cls.__dict__:
                raise TypeError(cls)
            if not isinstance(ra := cls.__dict__['_record_attrs'], collections.abc.Mapping):
                raise TypeError(ra)

            rd: ta.Dict[str, LoggingContextInfoRecordAdapters.Adapter.RecordAttr] = {}
            for n, v in ra.items():
                if not n or not isinstance(n, str) or n in rd:
                    raise AttributeError(n)
                if isinstance(v, tuple):
                    t, d = v
                else:
                    t, d = v, cls.NOT_SET
                rd[n] = cls.RecordAttr(
                    name=n,
                    type=t,
                    default=d,
                )
            cls.record_attrs = rd

    class RequiredAdapter(Adapter[T], Abstract):
        @property
        @abc.abstractmethod
        def _record_attrs(self) -> ta.Mapping[str, ta.Any]:
            raise NotImplementedError

        #

        @ta.final
        def context_to_record(self, ctx: LoggingContext) -> ta.Mapping[str, ta.Any]:
            if (info := ctx.get_info(self.info_cls)) is not None:
                return self._info_to_record(info)
            else:
                raise TypeError  # FIXME: fallback?

        @abc.abstractmethod
        def _info_to_record(self, info: T) -> ta.Mapping[str, ta.Any]:
            raise NotImplementedError

        #

        @abc.abstractmethod
        def record_to_info(self, rec: logging.LogRecord) -> T:
            raise NotImplementedError

        #

        def __init_subclass__(cls, **kwargs: ta.Any) -> None:
            super().__init_subclass__(**kwargs)

            if any(a.default is not cls.NOT_SET for a in cls.record_attrs.values()):
                raise TypeError(cls.record_attrs)

    class OptionalAdapter(Adapter[T], Abstract, ta.Generic[T]):
        @property
        @abc.abstractmethod
        def _record_attrs(self) -> ta.Mapping[str, ta.Tuple[ta.Any, ta.Any]]:
            raise NotImplementedError

        record_defaults: ta.ClassVar[ta.Mapping[str, ta.Any]]

        #

        @ta.final
        def context_to_record(self, ctx: LoggingContext) -> ta.Mapping[str, ta.Any]:
            if (info := ctx.get_info(self.info_cls)) is not None:
                return self._info_to_record(info)
            else:
                return self.record_defaults

        @abc.abstractmethod
        def _info_to_record(self, info: T) -> ta.Mapping[str, ta.Any]:
            raise NotImplementedError

        #

        def __init_subclass__(cls, **kwargs: ta.Any) -> None:
            super().__init_subclass__(**kwargs)

            dd: ta.Dict[str, ta.Any] = {a.name: a.default for a in cls.record_attrs.values()}
            if any(d is cls.NOT_SET for d in dd.values()):
                raise TypeError(cls.record_attrs)
            cls.record_defaults = dd

    #

    class Name(RequiredAdapter[LoggingContextInfos.Name]):
        info_cls: ta.ClassVar[ta.Type[LoggingContextInfos.Name]] = LoggingContextInfos.Name

        _record_attrs: ta.ClassVar[ta.Mapping[str, ta.Any]] = dict(
            # Name of the logger used to log the call. Unmodified by ctor.
            name=str,
        )

        def _info_to_record(self, info: LoggingContextInfos.Name) -> ta.Mapping[str, ta.Any]:
            return dict(
                name=info.name,
            )

        def record_to_info(self, rec: logging.LogRecord) -> LoggingContextInfos.Name:
            return LoggingContextInfos.Name(
                name=rec.name,
            )

    class Level(RequiredAdapter[LoggingContextInfos.Level]):
        info_cls: ta.ClassVar[ta.Type[LoggingContextInfos.Level]] = LoggingContextInfos.Level

        _record_attrs: ta.ClassVar[ta.Mapping[str, ta.Any]] = dict(
            # Text logging level for the message ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'). Set to
            # `getLevelName(level)`.
            levelname=str,

            # Numeric logging level for the message (DEBUG, INFO, WARNING, ERROR, CRITICAL). Unmodified by ctor.
            levelno=int,
        )

        def _info_to_record(self, info: LoggingContextInfos.Level) -> ta.Mapping[str, ta.Any]:
            return dict(
                levelname=info.name,
                levelno=int(info.level),
            )

        def record_to_info(self, rec: logging.LogRecord) -> LoggingContextInfos.Level:
            return LoggingContextInfos.Level.build(rec.levelno)

    class Msg(RequiredAdapter[LoggingContextInfos.Msg]):
        info_cls: ta.ClassVar[ta.Type[LoggingContextInfos.Msg]] = LoggingContextInfos.Msg

        _record_attrs: ta.ClassVar[ta.Mapping[str, ta.Any]] = dict(
            # The format string passed in the original logging call. Merged with args to produce message, or an
            # arbitrary object (see Using arbitrary objects as messages). Unmodified by ctor.
            msg=str,

            # The tuple of arguments merged into msg to produce message, or a dict whose values are used for the merge
            # (when there is only one argument, and it is a dictionary). Ctor will transform a 1-tuple containing a
            # Mapping into just the mapping, but is otherwise unmodified.
            args=ta.Union[tuple, dict, None],
        )

        def _info_to_record(self, info: LoggingContextInfos.Msg) -> ta.Mapping[str, ta.Any]:
            return dict(
                msg=info.msg,
                args=info.args,
            )

        def record_to_info(self, rec: logging.LogRecord) -> LoggingContextInfos.Msg:
            return LoggingContextInfos.Msg(
                msg=rec.msg,
                args=rec.args,
            )

    class Time(RequiredAdapter[LoggingContextInfos.Time]):
        info_cls: ta.ClassVar[ta.Type[LoggingContextInfos.Time]] = LoggingContextInfos.Time

        _record_attrs: ta.ClassVar[ta.Mapping[str, ta.Any]] = dict(
            # Time when the LogRecord was created. Set to `time.time_ns() / 1e9` for >=3.13.0b1, otherwise simply
            # `time.time()`.
            #
            # See:
            #  - https://github.com/python/cpython/commit/1316692e8c7c1e1f3b6639e51804f9db5ed892ea
            #  - https://github.com/python/cpython/commit/1500a23f33f5a6d052ff1ef6383d9839928b8ff1
            #
            created=float,

            # Millisecond portion of the time when the LogRecord was created.
            msecs=float,

            # Time in milliseconds when the LogRecord was created, relative to the time the logging module was loaded.
            relativeCreated=float,
        )

        def _info_to_record(self, info: LoggingContextInfos.Time) -> ta.Mapping[str, ta.Any]:
            return dict(
                created=info.secs,
                msecs=info.msecs,
                relativeCreated=info.relative_secs,
            )

        def record_to_info(self, rec: logging.LogRecord) -> LoggingContextInfos.Time:
            return LoggingContextInfos.Time.build(
                int(rec.created * 1e9),
            )

    class Exc(OptionalAdapter[LoggingContextInfos.Exc]):
        info_cls: ta.ClassVar[ta.Type[LoggingContextInfos.Exc]] = LoggingContextInfos.Exc

        _record_attrs: ta.ClassVar[ta.Mapping[str, ta.Tuple[ta.Any, ta.Any]]] = dict(
            # Exception tuple (à la sys.exc_info) or, if no exception has occurred, None. Unmodified by ctor.
            exc_info=(ta.Optional[LoggingExcInfoTuple], None),

            # Used to cache the traceback text. Simply set to None by ctor, later set by Formatter.format.
            exc_text=(ta.Optional[str], None),
        )

        def _info_to_record(self, info: LoggingContextInfos.Exc) -> ta.Mapping[str, ta.Any]:
            return dict(
                exc_info=info.info_tuple,
                exc_text=None,
            )

        def record_to_info(self, rec: logging.LogRecord) -> ta.Optional[LoggingContextInfos.Exc]:
            # FIXME:
            # error: Argument 1 to "build" of "Exc" has incompatible type
            # "tuple[type[BaseException], BaseException, TracebackType | None] | tuple[None, None, None] | None"; expected  # noqa
            # "BaseException | tuple[type[BaseException], BaseException, TracebackType | None] | bool | None"  [arg-type]  # noqa
            return LoggingContextInfos.Exc.build(rec.exc_info)  # type: ignore[arg-type]

    class Caller(OptionalAdapter[LoggingContextInfos.Caller]):
        info_cls: ta.ClassVar[ta.Type[LoggingContextInfos.Caller]] = LoggingContextInfos.Caller

        _UNKNOWN_PATH_NAME: ta.ClassVar[str] = '(unknown file)'
        _UNKNOWN_FUNC_NAME: ta.ClassVar[str] = '(unknown function)'

        _STACK_INFO_PREFIX: ta.ClassVar[str] = 'Stack (most recent call last):\n'

        _record_attrs: ta.ClassVar[ta.Mapping[str, ta.Tuple[ta.Any, ta.Any]]] = dict(
            # Full pathname of the source file where the logging call was issued (if available). Unmodified by ctor. May
            # default to "(unknown file)" by Logger.findCaller / Logger._log.
            pathname=(str, _UNKNOWN_PATH_NAME),

            # Source line number where the logging call was issued (if available). Unmodified by ctor. May default to 0
            # y Logger.findCaller / Logger._log.
            lineno=(int, 0),

            # Name of function containing the logging call. Set by ctor to `func` arg, unmodified. May default to
            # "(unknown function)" by Logger.findCaller / Logger._log.
            funcName=(str, _UNKNOWN_FUNC_NAME),

            # Stack frame information (where available) from the bottom of the stack in the current thread, up to and
            # including the stack frame of the logging call which resulted in the creation of this record. Set by ctor
            # to `sinfo` arg, unmodified. Mostly set, if requested, by `Logger.findCaller`, to
            # `traceback.print_stack(f)`, but prepended with the literal "Stack (most recent call last):\n", and
            # stripped of exactly one trailing `\n` if present.
            stack_info=(ta.Optional[str], None),
        )

        def _info_to_record(self, caller: LoggingContextInfos.Caller) -> ta.Mapping[str, ta.Any]:
            if (sinfo := caller.stack_info) is not None:
                stack_info: ta.Optional[str] = '\n'.join([
                    self._STACK_INFO_PREFIX,
                    sinfo[1:] if sinfo.endswith('\n') else sinfo,
                ])
            else:
                stack_info = None

            return dict(
                pathname=caller.file_path,

                lineno=caller.line_no,
                funcName=caller.func_name,

                stack_info=stack_info,
            )

        def record_to_info(self, rec: logging.LogRecord) -> ta.Optional[LoggingContextInfos.Caller]:
            # FIXME: piecemeal?
            if (
                    rec.pathname != self._UNKNOWN_PATH_NAME and
                    rec.lineno != 0 and
                    rec.funcName != self._UNKNOWN_FUNC_NAME
            ):
                if (sinfo := rec.stack_info) is not None and sinfo.startswith(self._STACK_INFO_PREFIX):
                    sinfo = sinfo[len(self._STACK_INFO_PREFIX):]
                return LoggingContextInfos.Caller(
                    file_path=rec.pathname,

                    line_no=rec.lineno,
                    func_name=rec.funcName,

                    stack_info=sinfo,
                )

            return None

    class SourceFile(Adapter[LoggingContextInfos.SourceFile]):
        info_cls: ta.ClassVar[ta.Type[LoggingContextInfos.SourceFile]] = LoggingContextInfos.SourceFile

        _record_attrs: ta.ClassVar[ta.Mapping[str, ta.Any]] = dict(
            # Filename portion of pathname. Set to `os.path.basename(pathname)` if successful, otherwise defaults to
            # pathname.
            filename=str,

            # Module (name portion of filename). Set to `os.path.splitext(filename)[0]`, otherwise defaults to
            # "Unknown module".
            module=str,
        )

        _UNKNOWN_MODULE: ta.ClassVar[str] = 'Unknown module'

        def context_to_record(self, ctx: LoggingContext) -> ta.Mapping[str, ta.Any]:
            if (info := ctx.get_info(LoggingContextInfos.SourceFile)) is not None:
                return dict(
                    filename=info.file_name,
                    module=info.module,
                )

            if (caller := ctx.get_info(LoggingContextInfos.Caller)) is not None:
                return dict(
                    filename=caller.file_path,
                    module=self._UNKNOWN_MODULE,
                )

            return dict(
                filename=LoggingContextInfoRecordAdapters.Caller._UNKNOWN_PATH_NAME,  # noqa
                module=self._UNKNOWN_MODULE,
            )

        def record_to_info(self, rec: logging.LogRecord) -> ta.Optional[LoggingContextInfos.SourceFile]:
            if (
                    rec.module is not None and
                    rec.module != self._UNKNOWN_MODULE
            ):
                return LoggingContextInfos.SourceFile(
                    file_name=rec.filename,
                    module=rec.module,  # FIXME: piecemeal?
                )

            return None

    class Thread(OptionalAdapter[LoggingContextInfos.Thread]):
        info_cls: ta.ClassVar[ta.Type[LoggingContextInfos.Thread]] = LoggingContextInfos.Thread

        _record_attrs: ta.ClassVar[ta.Mapping[str, ta.Tuple[ta.Any, ta.Any]]] = dict(
            # Thread ID if available, and `logging.logThreads` is truthy.
            thread=(ta.Optional[int], None),

            # Thread name if available, and `logging.logThreads` is truthy.
            threadName=(ta.Optional[str], None),
        )

        def _info_to_record(self, info: LoggingContextInfos.Thread) -> ta.Mapping[str, ta.Any]:
            if logging.logThreads:
                return dict(
                    thread=info.ident,
                    threadName=info.name,
                )

            return self.record_defaults

        def record_to_info(self, rec: logging.LogRecord) -> ta.Optional[LoggingContextInfos.Thread]:
            if (
                    (ident := rec.thread) is not None and
                    (name := rec.threadName) is not None
            ):
                return LoggingContextInfos.Thread(
                    ident=ident,
                    native_id=None,
                    name=name,
                )

            return None

    class Process(OptionalAdapter[LoggingContextInfos.Process]):
        info_cls: ta.ClassVar[ta.Type[LoggingContextInfos.Process]] = LoggingContextInfos.Process

        _record_attrs: ta.ClassVar[ta.Mapping[str, ta.Tuple[ta.Any, ta.Any]]] = dict(
            # Process ID if available - that is, if `hasattr(os, 'getpid')` - and `logging.logProcesses` is truthy,
            # otherwise None.
            process=(ta.Optional[int], None),
        )

        def _info_to_record(self, info: LoggingContextInfos.Process) -> ta.Mapping[str, ta.Any]:
            if logging.logProcesses:
                return dict(
                    process=info.pid,
                )

            return self.record_defaults

        def record_to_info(self, rec: logging.LogRecord) -> ta.Optional[LoggingContextInfos.Process]:
            if (
                    (pid := rec.process) is not None
            ):
                return LoggingContextInfos.Process(
                    pid=pid,
                )

            return None

    class Multiprocessing(OptionalAdapter[LoggingContextInfos.Multiprocessing]):
        info_cls: ta.ClassVar[ta.Type[LoggingContextInfos.Multiprocessing]] = LoggingContextInfos.Multiprocessing

        _record_attrs: ta.ClassVar[ta.Mapping[str, ta.Tuple[ta.Any, ta.Any]]] = dict(
            # Process name if available. Set to None if `logging.logMultiprocessing` is not truthy. Otherwise, set to
            # 'MainProcess', then `sys.modules.get('multiprocessing').current_process().name` if that works, otherwise
            # remains as 'MainProcess'.
            #
            # As noted by stdlib:
            #
            #   Errors may occur if multiprocessing has not finished loading yet - e.g. if a custom import hook causes
            #   third-party code to run when multiprocessing calls import. See issue 8200 for an example
            #
            processName=(ta.Optional[str], None),
        )

        def _info_to_record(self, info: LoggingContextInfos.Multiprocessing) -> ta.Mapping[str, ta.Any]:
            if logging.logMultiprocessing:
                return dict(
                    processName=info.process_name,
                )

            return self.record_defaults

        def record_to_info(self, rec: logging.LogRecord) -> ta.Optional[LoggingContextInfos.Multiprocessing]:
            if (
                    (process_name := rec.processName) is not None
            ):
                return LoggingContextInfos.Multiprocessing(
                    process_name=process_name,
                )

            return None

    class AsyncioTask(OptionalAdapter[LoggingContextInfos.AsyncioTask]):
        info_cls: ta.ClassVar[ta.Type[LoggingContextInfos.AsyncioTask]] = LoggingContextInfos.AsyncioTask

        _record_attrs: ta.ClassVar[ta.Mapping[str, ta.Union[ta.Any, ta.Tuple[ta.Any, ta.Any]]]] = dict(
            # Absent <3.12, otherwise asyncio.Task name if available, and `logging.logAsyncioTasks` is truthy. Set to
            # `sys.modules.get('asyncio').current_task().get_name()`, otherwise None.
            taskName=(ta.Optional[str], None),
        )

        def _info_to_record(self, info: LoggingContextInfos.AsyncioTask) -> ta.Mapping[str, ta.Any]:
            if getattr(logging, 'logAsyncioTasks', None):  # Absent <3.12
                return dict(
                    taskName=info.name,
                )

            return self.record_defaults

        def record_to_info(self, rec: logging.LogRecord) -> ta.Optional[LoggingContextInfos.AsyncioTask]:
            if (
                    (name := getattr(rec, 'taskName', None)) is not None
            ):
                return LoggingContextInfos.AsyncioTask(
                    name=name,
                )

            return None


_LOGGING_CONTEXT_INFO_RECORD_ADAPTERS_: ta.Sequence[LoggingContextInfoRecordAdapters.Adapter] = [  # noqa
    LoggingContextInfoRecordAdapters.Name(),
    LoggingContextInfoRecordAdapters.Level(),
    LoggingContextInfoRecordAdapters.Msg(),
    LoggingContextInfoRecordAdapters.Time(),
    LoggingContextInfoRecordAdapters.Exc(),
    LoggingContextInfoRecordAdapters.Caller(),
    LoggingContextInfoRecordAdapters.SourceFile(),
    LoggingContextInfoRecordAdapters.Thread(),
    LoggingContextInfoRecordAdapters.Process(),
    LoggingContextInfoRecordAdapters.Multiprocessing(),
    LoggingContextInfoRecordAdapters.AsyncioTask(),
]

_LOGGING_CONTEXT_INFO_RECORD_ADAPTERS: ta.Mapping[ta.Type[LoggingContextInfo], LoggingContextInfoRecordAdapters.Adapter] = {  # noqa
    ad.info_cls: ad for ad in _LOGGING_CONTEXT_INFO_RECORD_ADAPTERS_
}


##


# Formatter:
#  - https://github.com/python/cpython/blob/39b2f82717a69dde7212bc39b673b0f55c99e6a3/Lib/logging/__init__.py#L514 (3.8)
#  - https://github.com/python/cpython/blob/f070f54c5f4a42c7c61d1d5d3b8f3b7203b4a0fb/Lib/logging/__init__.py#L554 (~3.14)  # noqa
#
_KNOWN_STD_LOGGING_FORMATTER_RECORD_ATTRS: ta.Dict[str, ta.Any] = dict(
    # The logged message, computed as msg % args. Set to `record.getMessage()`.
    message=str,

    # Human-readable time when the LogRecord was created. By default this is of the form '2003-07-08 16:49:45,896' (the
    # numbers after the comma are millisecond portion of the time). Set to `self.formatTime(record, self.datefmt)` if
    # `self.usesTime()`, otherwise unset.
    asctime=str,

    # Used to cache the traceback text. If unset (falsey) on the record and `exc_info` is truthy, set to
    # `self.formatException(record.exc_info)` - otherwise unmodified.
    exc_text=ta.Optional[str],
)


##


_KNOWN_STD_LOGGING_RECORD_ATTR_SET: ta.FrozenSet[str] = frozenset(
    a for ad in _LOGGING_CONTEXT_INFO_RECORD_ADAPTERS.values() for a in ad.record_attrs
)

_KNOWN_STD_LOGGING_FORMATTER_RECORD_ATTR_SET: ta.FrozenSet[str] = frozenset(_KNOWN_STD_LOGGING_FORMATTER_RECORD_ATTRS)


class UnknownStdLoggingRecordAttrsWarning(LoggingSetupWarning):
    pass


def _check_std_logging_record_attrs() -> None:
    if (
            len([a for ad in _LOGGING_CONTEXT_INFO_RECORD_ADAPTERS.values() for a in ad.record_attrs]) !=
            len(_KNOWN_STD_LOGGING_RECORD_ATTR_SET)
    ):
        raise RuntimeError('Duplicate LoggingContextInfoRecordAdapter record attrs')

    rec_dct = dict(logging.makeLogRecord({}).__dict__)

    if (unk_rec_fields := frozenset(rec_dct) - _KNOWN_STD_LOGGING_RECORD_ATTR_SET):
        import warnings  # noqa

        warnings.warn(
            f'Unknown log record attrs detected: {sorted(unk_rec_fields)!r}',
            UnknownStdLoggingRecordAttrsWarning,
        )


_check_std_logging_record_attrs()


##


class LoggingContextLogRecord(logging.LogRecord):
    # LogRecord.__init__ args:
    #  - name: str
    #  - level: int
    #  - pathname: str - Confusingly referred to as `fn` before the LogRecord ctor. May be empty or "(unknown file)".
    #  - lineno: int - May be 0.
    #  - msg: str
    #  - args: tuple | dict | 1-tuple[dict]
    #  - exc_info: LoggingExcInfoTuple | None
    #  - func: str | None = None -> funcName
    #  - sinfo: str | None = None -> stack_info
    #

    def __init__(self, *, _logging_context: LoggingContext) -> None:  # noqa
        self.__dict__.update(_logging_context=_logging_context)

        for ad in _LOGGING_CONTEXT_INFO_RECORD_ADAPTERS_:
            self.__dict__.update(ad.context_to_record(_logging_context))

    _logging_context: LoggingContext

    # FIXME: track extra
    # def __setattr__(self, key, value):
    #     super().__setattr__(key, value)


##


@ta.final
class LogRecordLoggingContext(LoggingContext):
    def __init__(self, rec: logging.LogRecord) -> None:
        if isinstance(rec, LoggingContextLogRecord):
            raise TypeError(rec)

        self._rec = rec

        infos: ta.List[LoggingContextInfo] = [
            info
            for ad in _LOGGING_CONTEXT_INFO_RECORD_ADAPTERS_
            if (info := ad.record_to_info(rec)) is not None
        ]

        # FIXME:
        # if extra is not None:
        #     for key in extra:
        #         if (key in ["message", "asctime"]) or (key in rv.__dict__):
        #             raise KeyError("Attempt to overwrite %r in LogRecord" % key)
        #         rv.__dict__[key] = extra[key]

        if (extra := {
            a: v
            for a, v in rec.__dict__.items()
            if a not in _KNOWN_STD_LOGGING_RECORD_ATTR_SET
        }):
            infos.append(LoggingContextInfos.Extra(extra))

        self._infos: ta.Dict[ta.Type[LoggingContextInfo], LoggingContextInfo] = {
            type(info): info
            for info in infos
        }

    def get_info(self, ty: ta.Type[LoggingContextInfoT]) -> ta.Optional[LoggingContextInfoT]:
        return self._infos.get(ty)


########################################
# ../std/loggers.py


##


class StdLogger(Logger):
    def __init__(self, std: logging.Logger) -> None:
        super().__init__()

        self._std = std

    @property
    def std(self) -> logging.Logger:
        return self._std

    def is_enabled_for(self, level: LogLevel) -> bool:
        return self._std.isEnabledFor(level)

    def get_effective_level(self) -> LogLevel:
        return self._std.getEffectiveLevel()

    def _log(self, ctx: CaptureLoggingContext, msg: ta.Union[str, tuple, LoggingMsgFn], *args: ta.Any) -> None:
        if not self.is_enabled_for(ctx.must_get_info(LoggingContextInfos.Level).level):
            return

        ctx.set_basic(
            name=self._std.name,

            msg=msg,
            args=args,
        )

        ctx.capture()

        rec = LoggingContextLogRecord(_logging_context=ctx)

        self._std.handle(rec)


########################################
# _amalg.py


##
