#!/usr/bin/env python3
# noinspection DuplicatedCode
# @omlish-lite
# @omlish-script
# @omlish-amalg-output ../ci/cli.py
# ruff: noqa: N802 UP006 UP007 UP036
"""
Inputs:
 - requirements.txt
 - ci.Dockerfile
 - compose.yml

==

./python -m ci run --cache-dir ci/cache ci/project omlish-ci
"""
import abc
import argparse
import asyncio
import asyncio.base_subprocess
import asyncio.subprocess
import collections
import contextlib
import dataclasses as dc
import datetime
import functools
import hashlib
import inspect
import itertools
import json
import logging
import os
import os.path
import shlex
import shutil
import subprocess
import sys
import tarfile
import tempfile
import threading
import time
import types
import typing as ta
import urllib.parse


########################################


if sys.version_info < (3, 8):
    raise OSError(f'Requires python (3, 8), got {sys.version_info} from {sys.executable}')  # noqa


########################################


# shell.py
T = ta.TypeVar('T')

# ../../omlish/asyncs/asyncio/timeouts.py
AwaitableT = ta.TypeVar('AwaitableT', bound=ta.Awaitable)

# ../../omlish/lite/cached.py
CallableT = ta.TypeVar('CallableT', bound=ta.Callable)

# ../../omlish/lite/check.py
SizedT = ta.TypeVar('SizedT', bound=ta.Sized)
CheckMessage = ta.Union[str, ta.Callable[..., ta.Optional[str]], None]  # ta.TypeAlias
CheckLateConfigureFn = ta.Callable[['Checks'], None]  # ta.TypeAlias
CheckOnRaiseFn = ta.Callable[[Exception], None]  # ta.TypeAlias
CheckExceptionFactory = ta.Callable[..., Exception]  # ta.TypeAlias
CheckArgsRenderer = ta.Callable[..., ta.Optional[str]]  # ta.TypeAlias

# ../../omlish/argparse/cli.py
ArgparseCmdFn = ta.Callable[[], ta.Optional[int]]  # ta.TypeAlias

# ../../omlish/lite/contextmanagers.py
ExitStackedT = ta.TypeVar('ExitStackedT', bound='ExitStacked')
AsyncExitStackedT = ta.TypeVar('AsyncExitStackedT', bound='AsyncExitStacked')

# ../../omlish/subprocesses.py
SubprocessChannelOption = ta.Literal['pipe', 'stdout', 'devnull']  # ta.TypeAlias


########################################
# ../shell.py


##


@dc.dataclass(frozen=True)
class ShellCmd:
    s: str

    env: ta.Optional[ta.Mapping[str, str]] = None

    def build_run_kwargs(
            self,
            *,
            env: ta.Optional[ta.Mapping[str, str]] = None,
            **kwargs: ta.Any,
    ) -> ta.Dict[str, ta.Any]:
        if env is None:
            env = os.environ
        if self.env:
            if (ek := set(env) & set(self.env)):
                raise KeyError(*ek)
            env = {**env, **self.env}

        return dict(
            env=env,
            **kwargs,
        )

    def run(self, fn: ta.Callable[..., T], **kwargs) -> T:
        return fn(
            'sh', '-c', self.s,
            **self.build_run_kwargs(**kwargs),
        )


########################################
# ../../../omlish/asyncs/asyncio/timeouts.py


def asyncio_maybe_timeout(
        fut: AwaitableT,
        timeout: ta.Optional[float] = None,
) -> AwaitableT:
    if timeout is not None:
        fut = asyncio.wait_for(fut, timeout)  # type: ignore
    return fut


########################################
# ../../../omlish/lite/cached.py


##


class _AbstractCachedNullary:
    def __init__(self, fn):
        super().__init__()
        self._fn = fn
        self._value = self._missing = object()
        functools.update_wrapper(self, fn)

    def __call__(self, *args, **kwargs):  # noqa
        raise TypeError

    def __get__(self, instance, owner):  # noqa
        bound = instance.__dict__[self._fn.__name__] = self.__class__(self._fn.__get__(instance, owner))
        return bound


##


class _CachedNullary(_AbstractCachedNullary):
    def __call__(self, *args, **kwargs):  # noqa
        if self._value is self._missing:
            self._value = self._fn()
        return self._value


def cached_nullary(fn: CallableT) -> CallableT:
    return _CachedNullary(fn)  # type: ignore


def static_init(fn: CallableT) -> CallableT:
    fn = cached_nullary(fn)
    fn()
    return fn


##


class _AsyncCachedNullary(_AbstractCachedNullary):
    async def __call__(self, *args, **kwargs):
        if self._value is self._missing:
            self._value = await self._fn()
        return self._value


def async_cached_nullary(fn):  # ta.Callable[..., T]) -> ta.Callable[..., T]:
    return _AsyncCachedNullary(fn)


########################################
# ../../../omlish/lite/check.py
"""
TODO:
 - def maybe(v: lang.Maybe[T])
 - def not_ ?
 - ** class @dataclass Raise - user message should be able to be an exception type or instance or factory
"""


##


class Checks:
    def __init__(self) -> None:
        super().__init__()

        self._config_lock = threading.RLock()
        self._on_raise_fns: ta.Sequence[CheckOnRaiseFn] = []
        self._exception_factory: CheckExceptionFactory = Checks.default_exception_factory
        self._args_renderer: ta.Optional[CheckArgsRenderer] = None
        self._late_configure_fns: ta.Sequence[CheckLateConfigureFn] = []

    @staticmethod
    def default_exception_factory(exc_cls: ta.Type[Exception], *args, **kwargs) -> Exception:
        return exc_cls(*args, **kwargs)  # noqa

    #

    def register_on_raise(self, fn: CheckOnRaiseFn) -> None:
        with self._config_lock:
            self._on_raise_fns = [*self._on_raise_fns, fn]

    def unregister_on_raise(self, fn: CheckOnRaiseFn) -> None:
        with self._config_lock:
            self._on_raise_fns = [e for e in self._on_raise_fns if e != fn]

    #

    def register_on_raise_breakpoint_if_env_var_set(self, key: str) -> None:
        import os

        def on_raise(exc: Exception) -> None:  # noqa
            if key in os.environ:
                breakpoint()  # noqa

        self.register_on_raise(on_raise)

    #

    def set_exception_factory(self, factory: CheckExceptionFactory) -> None:
        self._exception_factory = factory

    def set_args_renderer(self, renderer: ta.Optional[CheckArgsRenderer]) -> None:
        self._args_renderer = renderer

    #

    def register_late_configure(self, fn: CheckLateConfigureFn) -> None:
        with self._config_lock:
            self._late_configure_fns = [*self._late_configure_fns, fn]

    def _late_configure(self) -> None:
        if not self._late_configure_fns:
            return

        with self._config_lock:
            if not (lc := self._late_configure_fns):
                return

            for fn in lc:
                fn(self)

            self._late_configure_fns = []

    #

    class _ArgsKwargs:
        def __init__(self, *args, **kwargs):
            self.args = args
            self.kwargs = kwargs

    def _raise(
            self,
            exception_type: ta.Type[Exception],
            default_message: str,
            message: CheckMessage,
            ak: _ArgsKwargs = _ArgsKwargs(),
            *,
            render_fmt: ta.Optional[str] = None,
    ) -> ta.NoReturn:
        exc_args = ()
        if callable(message):
            message = ta.cast(ta.Callable, message)(*ak.args, **ak.kwargs)
            if isinstance(message, tuple):
                message, *exc_args = message  # type: ignore

        if message is None:
            message = default_message

        self._late_configure()

        if render_fmt is not None and (af := self._args_renderer) is not None:
            rendered_args = af(render_fmt, *ak.args)
            if rendered_args is not None:
                message = f'{message} : {rendered_args}'

        exc = self._exception_factory(
            exception_type,
            message,
            *exc_args,
            *ak.args,
            **ak.kwargs,
        )

        for fn in self._on_raise_fns:
            fn(exc)

        raise exc

    #

    def _unpack_isinstance_spec(self, spec: ta.Any) -> tuple:
        if isinstance(spec, type):
            return (spec,)
        if not isinstance(spec, tuple):
            spec = (spec,)
        if None in spec:
            spec = tuple(filter(None, spec)) + (None.__class__,)  # noqa
        if ta.Any in spec:
            spec = (object,)
        return spec

    def isinstance(self, v: ta.Any, spec: ta.Union[ta.Type[T], tuple], msg: CheckMessage = None) -> T:  # noqa
        if not isinstance(v, self._unpack_isinstance_spec(spec)):
            self._raise(
                TypeError,
                'Must be instance',
                msg,
                Checks._ArgsKwargs(v, spec),
                render_fmt='not isinstance(%s, %s)',
            )

        return v

    def of_isinstance(self, spec: ta.Union[ta.Type[T], tuple], msg: CheckMessage = None) -> ta.Callable[[ta.Any], T]:
        def inner(v):
            return self.isinstance(v, self._unpack_isinstance_spec(spec), msg)

        return inner

    def cast(self, v: ta.Any, cls: ta.Type[T], msg: CheckMessage = None) -> T:  # noqa
        if not isinstance(v, cls):
            self._raise(
                TypeError,
                'Must be instance',
                msg,
                Checks._ArgsKwargs(v, cls),
            )

        return v

    def of_cast(self, cls: ta.Type[T], msg: CheckMessage = None) -> ta.Callable[[T], T]:
        def inner(v):
            return self.cast(v, cls, msg)

        return inner

    def not_isinstance(self, v: T, spec: ta.Any, msg: CheckMessage = None) -> T:  # noqa
        if isinstance(v, self._unpack_isinstance_spec(spec)):
            self._raise(
                TypeError,
                'Must not be instance',
                msg,
                Checks._ArgsKwargs(v, spec),
                render_fmt='isinstance(%s, %s)',
            )

        return v

    def of_not_isinstance(self, spec: ta.Any, msg: CheckMessage = None) -> ta.Callable[[T], T]:
        def inner(v):
            return self.not_isinstance(v, self._unpack_isinstance_spec(spec), msg)

        return inner

    ##

    def issubclass(self, v: ta.Type[T], spec: ta.Any, msg: CheckMessage = None) -> ta.Type[T]:  # noqa
        if not issubclass(v, spec):
            self._raise(
                TypeError,
                'Must be subclass',
                msg,
                Checks._ArgsKwargs(v, spec),
                render_fmt='not issubclass(%s, %s)',
            )

        return v

    def not_issubclass(self, v: ta.Type[T], spec: ta.Any, msg: CheckMessage = None) -> ta.Type[T]:  # noqa
        if issubclass(v, spec):
            self._raise(
                TypeError,
                'Must not be subclass',
                msg,
                Checks._ArgsKwargs(v, spec),
                render_fmt='issubclass(%s, %s)',
            )

        return v

    #

    def in_(self, v: T, c: ta.Container[T], msg: CheckMessage = None) -> T:
        if v not in c:
            self._raise(
                ValueError,
                'Must be in',
                msg,
                Checks._ArgsKwargs(v, c),
                render_fmt='%s not in %s',
            )

        return v

    def not_in(self, v: T, c: ta.Container[T], msg: CheckMessage = None) -> T:
        if v in c:
            self._raise(
                ValueError,
                'Must not be in',
                msg,
                Checks._ArgsKwargs(v, c),
                render_fmt='%s in %s',
            )

        return v

    def empty(self, v: SizedT, msg: CheckMessage = None) -> SizedT:
        if len(v) != 0:
            self._raise(
                ValueError,
                'Must be empty',
                msg,
                Checks._ArgsKwargs(v),
                render_fmt='%s',
            )

        return v

    def iterempty(self, v: ta.Iterable[T], msg: CheckMessage = None) -> ta.Iterable[T]:
        it = iter(v)
        try:
            next(it)
        except StopIteration:
            pass
        else:
            self._raise(
                ValueError,
                'Must be empty',
                msg,
                Checks._ArgsKwargs(v),
                render_fmt='%s',
            )

        return v

    def not_empty(self, v: SizedT, msg: CheckMessage = None) -> SizedT:
        if len(v) == 0:
            self._raise(
                ValueError,
                'Must not be empty',
                msg,
                Checks._ArgsKwargs(v),
                render_fmt='%s',
            )

        return v

    def unique(self, it: ta.Iterable[T], msg: CheckMessage = None) -> ta.Iterable[T]:
        dupes = [e for e, c in collections.Counter(it).items() if c > 1]
        if dupes:
            self._raise(
                ValueError,
                'Must be unique',
                msg,
                Checks._ArgsKwargs(it, dupes),
            )

        return it

    def single(self, obj: ta.Iterable[T], message: CheckMessage = None) -> T:
        try:
            [value] = obj
        except ValueError:
            self._raise(
                ValueError,
                'Must be single',
                message,
                Checks._ArgsKwargs(obj),
                render_fmt='%s',
            )

        return value

    def opt_single(self, obj: ta.Iterable[T], message: CheckMessage = None) -> ta.Optional[T]:
        it = iter(obj)
        try:
            value = next(it)
        except StopIteration:
            return None

        try:
            next(it)
        except StopIteration:
            return value  # noqa

        self._raise(
            ValueError,
            'Must be empty or single',
            message,
            Checks._ArgsKwargs(obj),
            render_fmt='%s',
        )

        raise RuntimeError  # noqa

    #

    def none(self, v: ta.Any, msg: CheckMessage = None) -> None:
        if v is not None:
            self._raise(
                ValueError,
                'Must be None',
                msg,
                Checks._ArgsKwargs(v),
                render_fmt='%s',
            )

    def not_none(self, v: ta.Optional[T], msg: CheckMessage = None) -> T:
        if v is None:
            self._raise(
                ValueError,
                'Must not be None',
                msg,
                Checks._ArgsKwargs(v),
                render_fmt='%s',
            )

        return v

    #

    def equal(self, v: T, o: ta.Any, msg: CheckMessage = None) -> T:
        if o != v:
            self._raise(
                ValueError,
                'Must be equal',
                msg,
                Checks._ArgsKwargs(v, o),
                render_fmt='%s != %s',
            )

        return v

    def not_equal(self, v: T, o: ta.Any, msg: CheckMessage = None) -> T:
        if o == v:
            self._raise(
                ValueError,
                'Must not be equal',
                msg,
                Checks._ArgsKwargs(v, o),
                render_fmt='%s == %s',
            )

        return v

    def is_(self, v: T, o: ta.Any, msg: CheckMessage = None) -> T:
        if o is not v:
            self._raise(
                ValueError,
                'Must be the same',
                msg,
                Checks._ArgsKwargs(v, o),
                render_fmt='%s is not %s',
            )

        return v

    def is_not(self, v: T, o: ta.Any, msg: CheckMessage = None) -> T:
        if o is v:
            self._raise(
                ValueError,
                'Must not be the same',
                msg,
                Checks._ArgsKwargs(v, o),
                render_fmt='%s is %s',
            )

        return v

    def callable(self, v: T, msg: CheckMessage = None) -> T:  # noqa
        if not callable(v):
            self._raise(
                TypeError,
                'Must be callable',
                msg,
                Checks._ArgsKwargs(v),
                render_fmt='%s',
            )

        return v  # type: ignore

    def non_empty_str(self, v: ta.Optional[str], msg: CheckMessage = None) -> str:
        if not isinstance(v, str) or not v:
            self._raise(
                ValueError,
                'Must be non-empty str',
                msg,
                Checks._ArgsKwargs(v),
                render_fmt='%s',
            )

        return v

    def replacing(self, expected: ta.Any, old: ta.Any, new: T, msg: CheckMessage = None) -> T:
        if old != expected:
            self._raise(
                ValueError,
                'Must be replacing',
                msg,
                Checks._ArgsKwargs(expected, old, new),
                render_fmt='%s -> %s -> %s',
            )

        return new

    def replacing_none(self, old: ta.Any, new: T, msg: CheckMessage = None) -> T:
        if old is not None:
            self._raise(
                ValueError,
                'Must be replacing None',
                msg,
                Checks._ArgsKwargs(old, new),
                render_fmt='%s -> %s',
            )

        return new

    #

    def arg(self, v: bool, msg: CheckMessage = None) -> None:
        if not v:
            self._raise(
                RuntimeError,
                'Argument condition not met',
                msg,
                Checks._ArgsKwargs(v),
                render_fmt='%s',
            )

    def state(self, v: bool, msg: CheckMessage = None) -> None:
        if not v:
            self._raise(
                RuntimeError,
                'State condition not met',
                msg,
                Checks._ArgsKwargs(v),
                render_fmt='%s',
            )


check = Checks()


########################################
# ../../../omlish/lite/json.py


##


JSON_PRETTY_INDENT = 2

JSON_PRETTY_KWARGS: ta.Mapping[str, ta.Any] = dict(
    indent=JSON_PRETTY_INDENT,
)

json_dump_pretty: ta.Callable[..., bytes] = functools.partial(json.dump, **JSON_PRETTY_KWARGS)  # type: ignore
json_dumps_pretty: ta.Callable[..., str] = functools.partial(json.dumps, **JSON_PRETTY_KWARGS)


##


JSON_COMPACT_SEPARATORS = (',', ':')

JSON_COMPACT_KWARGS: ta.Mapping[str, ta.Any] = dict(
    indent=None,
    separators=JSON_COMPACT_SEPARATORS,
)

json_dump_compact: ta.Callable[..., bytes] = functools.partial(json.dump, **JSON_COMPACT_KWARGS)  # type: ignore
json_dumps_compact: ta.Callable[..., str] = functools.partial(json.dumps, **JSON_COMPACT_KWARGS)


########################################
# ../../../omlish/lite/logs.py


log = logging.getLogger(__name__)


########################################
# ../../../omlish/lite/reflect.py


##


_GENERIC_ALIAS_TYPES = (
    ta._GenericAlias,  # type: ignore  # noqa
    *([ta._SpecialGenericAlias] if hasattr(ta, '_SpecialGenericAlias') else []),  # noqa
)


def is_generic_alias(obj, *, origin: ta.Any = None) -> bool:
    return (
        isinstance(obj, _GENERIC_ALIAS_TYPES) and
        (origin is None or ta.get_origin(obj) is origin)
    )


is_union_alias = functools.partial(is_generic_alias, origin=ta.Union)
is_callable_alias = functools.partial(is_generic_alias, origin=ta.Callable)


##


def is_optional_alias(spec: ta.Any) -> bool:
    return (
        isinstance(spec, _GENERIC_ALIAS_TYPES) and  # noqa
        ta.get_origin(spec) is ta.Union and
        len(ta.get_args(spec)) == 2 and
        any(a in (None, type(None)) for a in ta.get_args(spec))
    )


def get_optional_alias_arg(spec: ta.Any) -> ta.Any:
    [it] = [it for it in ta.get_args(spec) if it not in (None, type(None))]
    return it


##


def is_new_type(spec: ta.Any) -> bool:
    if isinstance(ta.NewType, type):
        return isinstance(spec, ta.NewType)
    else:
        # Before https://github.com/python/cpython/commit/c2f33dfc83ab270412bf243fb21f724037effa1a
        return isinstance(spec, types.FunctionType) and spec.__code__ is ta.NewType.__code__.co_consts[1]  # type: ignore  # noqa


def get_new_type_supertype(spec: ta.Any) -> ta.Any:
    return spec.__supertype__


##


def is_literal_type(spec: ta.Any) -> bool:
    if hasattr(ta, '_LiteralGenericAlias'):
        return isinstance(spec, ta._LiteralGenericAlias)  # noqa
    else:
        return (
            isinstance(spec, ta._GenericAlias) and  # type: ignore  # noqa
            spec.__origin__ is ta.Literal
        )


def get_literal_type_args(spec: ta.Any) -> ta.Iterable[ta.Any]:
    return spec.__args__


##


def deep_subclasses(cls: ta.Type[T]) -> ta.Iterator[ta.Type[T]]:
    seen = set()
    todo = list(reversed(cls.__subclasses__()))
    while todo:
        cur = todo.pop()
        if cur in seen:
            continue
        seen.add(cur)
        yield cur
        todo.extend(reversed(cur.__subclasses__()))


########################################
# ../../../omlish/lite/strings.py


##


def camel_case(name: str, *, lower: bool = False) -> str:
    if not name:
        return ''
    s = ''.join(map(str.capitalize, name.split('_')))  # noqa
    if lower:
        s = s[0].lower() + s[1:]
    return s


def snake_case(name: str) -> str:
    uppers: list[int | None] = [i for i, c in enumerate(name) if c.isupper()]
    return '_'.join([name[l:r].lower() for l, r in zip([None, *uppers], [*uppers, None])]).strip('_')


##


def is_dunder(name: str) -> bool:
    return (
        name[:2] == name[-2:] == '__' and
        name[2:3] != '_' and
        name[-3:-2] != '_' and
        len(name) > 4
    )


def is_sunder(name: str) -> bool:
    return (
        name[0] == name[-1] == '_' and
        name[1:2] != '_' and
        name[-2:-1] != '_' and
        len(name) > 2
    )


##


def strip_with_newline(s: str) -> str:
    if not s:
        return ''
    return s.strip() + '\n'


@ta.overload
def split_keep_delimiter(s: str, d: str) -> str:
    ...


@ta.overload
def split_keep_delimiter(s: bytes, d: bytes) -> bytes:
    ...


def split_keep_delimiter(s, d):
    ps = []
    i = 0
    while i < len(s):
        if (n := s.find(d, i)) < i:
            ps.append(s[i:])
            break
        ps.append(s[i:n + 1])
        i = n + 1
    return ps


##


def attr_repr(obj: ta.Any, *attrs: str) -> str:
    return f'{type(obj).__name__}({", ".join(f"{attr}={getattr(obj, attr)!r}" for attr in attrs)})'


##


FORMAT_NUM_BYTES_SUFFIXES: ta.Sequence[str] = ['B', 'kB', 'MB', 'GB', 'TB', 'PB', 'EB']


def format_num_bytes(num_bytes: int) -> str:
    for i, suffix in enumerate(FORMAT_NUM_BYTES_SUFFIXES):
        value = num_bytes / 1024 ** i
        if num_bytes < 1024 ** (i + 1):
            if value.is_integer():
                return f'{int(value)}{suffix}'
            else:
                return f'{value:.2f}{suffix}'

    return f'{num_bytes / 1024 ** (len(FORMAT_NUM_BYTES_SUFFIXES) - 1):.2f}{FORMAT_NUM_BYTES_SUFFIXES[-1]}'


########################################
# ../../../omlish/logs/filters.py


class TidLogFilter(logging.Filter):
    def filter(self, record):
        record.tid = threading.get_native_id()
        return True


########################################
# ../../../omlish/logs/proxy.py


class ProxyLogFilterer(logging.Filterer):
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


class ProxyLogHandler(ProxyLogFilterer, logging.Handler):
    def __init__(self, underlying: logging.Handler) -> None:  # noqa
        ProxyLogFilterer.__init__(self, underlying)

    _underlying: logging.Handler

    @property
    def underlying(self) -> logging.Handler:
        return self._underlying

    def get_name(self):
        return self._underlying.get_name()

    def set_name(self, name):
        self._underlying.set_name(name)

    @property
    def name(self):
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
# ../cache.py


##


@abc.abstractmethod
class FileCache(abc.ABC):
    @abc.abstractmethod
    def get_file(self, key: str) -> ta.Optional[str]:
        raise NotImplementedError

    @abc.abstractmethod
    def put_file(self, key: str, file_path: str) -> ta.Optional[str]:
        raise NotImplementedError


#


class DirectoryFileCache(FileCache):
    def __init__(self, dir: str) -> None:  # noqa
        super().__init__()

        self._dir = dir

    #

    def get_cache_file_path(
            self,
            key: str,
            *,
            make_dirs: bool = False,
    ) -> str:
        if make_dirs:
            os.makedirs(self._dir, exist_ok=True)
        return os.path.join(self._dir, key)

    def format_incomplete_file(self, f: str) -> str:
        return os.path.join(os.path.dirname(f), f'_{os.path.basename(f)}.incomplete')

    #

    def get_file(self, key: str) -> ta.Optional[str]:
        cache_file_path = self.get_cache_file_path(key)
        if not os.path.exists(cache_file_path):
            return None
        return cache_file_path

    def put_file(self, key: str, file_path: str) -> None:
        cache_file_path = self.get_cache_file_path(key, make_dirs=True)
        shutil.copyfile(file_path, cache_file_path)


##


class ShellCache(abc.ABC):
    @abc.abstractmethod
    def get_file_cmd(self, key: str) -> ta.Optional[ShellCmd]:
        raise NotImplementedError

    class PutFileCmdContext(abc.ABC):
        def __init__(self) -> None:
            super().__init__()

            self._state: ta.Literal['open', 'committed', 'aborted'] = 'open'

        @property
        def state(self) -> ta.Literal['open', 'committed', 'aborted']:
            return self._state

        #

        @property
        @abc.abstractmethod
        def cmd(self) -> ShellCmd:
            raise NotImplementedError

        #

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_val, exc_tb):
            if exc_val is None:
                self.commit()
            else:
                self.abort()

        #

        @abc.abstractmethod
        def _commit(self) -> None:
            raise NotImplementedError

        def commit(self) -> None:
            if self._state == 'committed':
                return
            elif self._state == 'open':
                self._commit()
                self._state = 'committed'
            else:
                raise RuntimeError(self._state)

        #

        @abc.abstractmethod
        def _abort(self) -> None:
            raise NotImplementedError

        def abort(self) -> None:
            if self._state == 'aborted':
                return
            elif self._state == 'open':
                self._abort()
                self._state = 'committed'
            else:
                raise RuntimeError(self._state)

    @abc.abstractmethod
    def put_file_cmd(self, key: str) -> PutFileCmdContext:
        raise NotImplementedError


#


class DirectoryShellCache(ShellCache):
    def __init__(self, dfc: DirectoryFileCache) -> None:
        super().__init__()

        self._dfc = dfc

    def get_file_cmd(self, key: str) -> ta.Optional[ShellCmd]:
        f = self._dfc.get_file(key)
        if f is None:
            return None
        return ShellCmd(f'cat {shlex.quote(f)}')

    class _PutFileCmdContext(ShellCache.PutFileCmdContext):  # noqa
        def __init__(self, tf: str, f: str) -> None:
            super().__init__()

            self._tf = tf
            self._f = f

        @property
        def cmd(self) -> ShellCmd:
            return ShellCmd(f'cat > {shlex.quote(self._tf)}')

        def _commit(self) -> None:
            os.replace(self._tf, self._f)

        def _abort(self) -> None:
            os.unlink(self._tf)

    def put_file_cmd(self, key: str) -> ShellCache.PutFileCmdContext:
        f = self._dfc.get_cache_file_path(key, make_dirs=True)
        return self._PutFileCmdContext(self._dfc.format_incomplete_file(f), f)


########################################
# ../github/cacheapi.py
"""
export FILE_SIZE=$(stat --format="%s" $FILE)

export CACHE_ID=$(curl -s \
  -X POST \
  "${ACTIONS_CACHE_URL}_apis/artifactcache/caches" \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json;api-version=6.0-preview.1' \
  -H "Authorization: Bearer $ACTIONS_RUNTIME_TOKEN" \
  -d '{"key": "'"$CACHE_KEY"'", "cacheSize": '"$FILE_SIZE"'}' \
  | jq .cacheId)

curl -s \
  -X PATCH \
  "${ACTIONS_CACHE_URL}_apis/artifactcache/caches/$CACHE_ID" \
  -H 'Content-Type: application/octet-stream' \
  -H 'Accept: application/json;api-version=6.0-preview.1' \
  -H "Authorization: Bearer $ACTIONS_RUNTIME_TOKEN" \
  -H "Content-Range: bytes 0-$((FILE_SIZE - 1))/*" \
  --data-binary @"$FILE"

curl -s \
  -X POST \
  "${ACTIONS_CACHE_URL}_apis/artifactcache/caches/$CACHE_ID" \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json;api-version=6.0-preview.1' \
  -H "Authorization: Bearer $ACTIONS_RUNTIME_TOKEN" \
  -d '{"size": '"$(stat --format="%s" $FILE)"'}'

curl -s \
  -X GET \
  "${ACTIONS_CACHE_URL}_apis/artifactcache/cache?keys=$CACHE_KEY" \
  -H 'Content-Type: application/json' \
  -H "Authorization: Bearer $ACTIONS_RUNTIME_TOKEN" \
  | jq .
"""


##


class GithubCacheServiceV1:
    API_VERSION = '6.0-preview.1'

    @classmethod
    def get_service_url(cls, base_url: str) -> str:
        return f'{base_url.rstrip("/")}/_apis/artifactcache'

    #

    @classmethod
    def dataclass_to_json(cls, obj: ta.Any) -> ta.Any:
        return {
            camel_case(k, lower=True): v
            for k, v in dc.asdict(obj).items()
            if v is not None
        }

    @classmethod
    def dataclass_from_json(cls, dcls: ta.Type[T], obj: ta.Any) -> T:
        return dcls(**{
            snake_case(k): v
            for k, v in obj.items()
        })

    #

    @dc.dataclass(frozen=True)
    class ArtifactCacheEntry:
        cache_key: ta.Optional[str]
        scope: ta.Optional[str]
        cache_version: ta.Optional[str]
        creation_time: ta.Optional[str]
        archive_location: ta.Optional[str]

    @dc.dataclass(frozen=True)
    class ArtifactCacheList:
        total_count: int
        artifact_caches: ta.Optional[ta.Sequence['GithubCacheServiceV1.ArtifactCacheEntry']]

    #

    @dc.dataclass(frozen=True)
    class ReserveCacheRequest:
        key: str
        cache_size: ta.Optional[int] = None
        version: ta.Optional[str] = None

    @dc.dataclass(frozen=True)
    class ReserveCacheResponse:
        cache_id: int

    #

    @dc.dataclass(frozen=True)
    class CommitCacheRequest:
        size: int

    #

    class CompressionMethod:
        GZIP = 'gzip'
        ZSTD_WITHOUT_LONG = 'zstd-without-long'
        ZSTD = 'zstd'

    @dc.dataclass(frozen=True)
    class InternalCacheOptions:
        compression_method: ta.Optional[str]  # CompressionMethod
        enable_cross_os_archive: ta.Optional[bool]
        cache_size: ta.Optional[int]


class GithubCacheServiceV2:
    SERVICE_NAME = 'github.actions.results.api.v1.CacheService'

    @dc.dataclass(frozen=True)
    class Method:
        name: str
        request: type
        response: type

    #

    class CacheScopePermission:
        READ = 1
        WRITE = 2
        ALL = READ | WRITE

    @dc.dataclass(frozen=True)
    class CacheScope:
        scope: str
        permission: int  # CacheScopePermission

    @dc.dataclass(frozen=True)
    class CacheMetadata:
        repository_id: int
        scope: ta.Sequence['GithubCacheServiceV2.CacheScope']

    #

    @dc.dataclass(frozen=True)
    class CreateCacheEntryRequest:
        key: str
        version: str
        metadata: ta.Optional['GithubCacheServiceV2.CacheMetadata'] = None

    @dc.dataclass(frozen=True)
    class CreateCacheEntryResponse:
        ok: bool
        signed_upload_url: str

    CREATE_CACHE_ENTRY_METHOD = Method(
        'CreateCacheEntry',
        CreateCacheEntryRequest,
        CreateCacheEntryResponse,
    )

    #

    @dc.dataclass(frozen=True)
    class FinalizeCacheEntryUploadRequest:
        key: str
        size_bytes: int
        version: str
        metadata: ta.Optional['GithubCacheServiceV2.CacheMetadata'] = None

    @dc.dataclass(frozen=True)
    class FinalizeCacheEntryUploadResponse:
        ok: bool
        entry_id: str

    FINALIZE_CACHE_ENTRY_METHOD = Method(
        'FinalizeCacheEntryUpload',
        FinalizeCacheEntryUploadRequest,
        FinalizeCacheEntryUploadResponse,
    )

    #

    @dc.dataclass(frozen=True)
    class GetCacheEntryDownloadUrlRequest:
        key: str
        restore_keys: ta.Sequence[str]
        version: str
        metadata: ta.Optional['GithubCacheServiceV2.CacheMetadata'] = None

    @dc.dataclass(frozen=True)
    class GetCacheEntryDownloadUrlResponse:
        ok: bool
        signed_download_url: str
        matched_key: str

    GET_CACHE_ENTRY_DOWNLOAD_URL_METHOD = Method(
        'GetCacheEntryDownloadURL',
        GetCacheEntryDownloadUrlRequest,
        GetCacheEntryDownloadUrlResponse,
    )


########################################
# ../utils.py


##


def make_temp_file() -> str:
    file_fd, file = tempfile.mkstemp()
    os.close(file_fd)
    return file


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

        self._log.log(self._level, f'Begin {self._description}')  # noqa

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._end_time = time.time()

        self._log.log(
            self._level,
            f'End {self._description} - {self._end_time - self._begin_time:0.2f} s elapsed',
        )


log_timing_context = LogTimingContext


########################################
# ../../../omlish/argparse/cli.py
"""
TODO:
 - default command
 - auto match all underscores to hyphens
 - pre-run, post-run hooks
 - exitstack?
"""


##


@dc.dataclass(eq=False)
class ArgparseArg:
    args: ta.Sequence[ta.Any]
    kwargs: ta.Mapping[str, ta.Any]
    dest: ta.Optional[str] = None

    def __get__(self, instance, owner=None):
        if instance is None:
            return self
        return getattr(instance.args, self.dest)  # type: ignore


def argparse_arg(*args, **kwargs) -> ArgparseArg:
    return ArgparseArg(args, kwargs)


#


@dc.dataclass(eq=False)
class ArgparseCmd:
    name: str
    fn: ArgparseCmdFn
    args: ta.Sequence[ArgparseArg] = ()  # noqa

    # _: dc.KW_ONLY

    aliases: ta.Optional[ta.Sequence[str]] = None
    parent: ta.Optional['ArgparseCmd'] = None
    accepts_unknown: bool = False

    def __post_init__(self) -> None:
        def check_name(s: str) -> None:
            check.isinstance(s, str)
            check.not_in('_', s)
            check.not_empty(s)
        check_name(self.name)
        check.not_isinstance(self.aliases, str)
        for a in self.aliases or []:
            check_name(a)

        check.arg(callable(self.fn))
        check.arg(all(isinstance(a, ArgparseArg) for a in self.args))
        check.isinstance(self.parent, (ArgparseCmd, type(None)))
        check.isinstance(self.accepts_unknown, bool)

        functools.update_wrapper(self, self.fn)

    def __get__(self, instance, owner=None):
        if instance is None:
            return self
        return dc.replace(self, fn=self.fn.__get__(instance, owner))  # noqa

    def __call__(self, *args, **kwargs) -> ta.Optional[int]:
        return self.fn(*args, **kwargs)


def argparse_cmd(
        *args: ArgparseArg,
        name: ta.Optional[str] = None,
        aliases: ta.Optional[ta.Iterable[str]] = None,
        parent: ta.Optional[ArgparseCmd] = None,
        accepts_unknown: bool = False,
) -> ta.Any:  # ta.Callable[[ArgparseCmdFn], ArgparseCmd]:  # FIXME
    for arg in args:
        check.isinstance(arg, ArgparseArg)
    check.isinstance(name, (str, type(None)))
    check.isinstance(parent, (ArgparseCmd, type(None)))
    check.not_isinstance(aliases, str)

    def inner(fn):
        return ArgparseCmd(
            (name if name is not None else fn.__name__).replace('_', '-'),
            fn,
            args,
            aliases=tuple(aliases) if aliases is not None else None,
            parent=parent,
            accepts_unknown=accepts_unknown,
        )

    return inner


##


def _get_argparse_arg_ann_kwargs(ann: ta.Any) -> ta.Mapping[str, ta.Any]:
    if ann is str:
        return {}
    elif ann is int:
        return {'type': int}
    elif ann is bool:
        return {'action': 'store_true'}
    elif ann is list:
        return {'action': 'append'}
    elif is_optional_alias(ann):
        return _get_argparse_arg_ann_kwargs(get_optional_alias_arg(ann))
    else:
        raise TypeError(ann)


class _ArgparseCliAnnotationBox:
    def __init__(self, annotations: ta.Mapping[str, ta.Any]) -> None:
        super().__init__()
        self.__annotations__ = annotations  # type: ignore


class ArgparseCli:
    def __init__(self, argv: ta.Optional[ta.Sequence[str]] = None) -> None:
        super().__init__()

        self._argv = argv if argv is not None else sys.argv[1:]

        self._args, self._unknown_args = self.get_parser().parse_known_args(self._argv)

    #

    def __init_subclass__(cls, **kwargs: ta.Any) -> None:
        super().__init_subclass__(**kwargs)

        ns = cls.__dict__
        objs = {}
        mro = cls.__mro__[::-1]
        for bns in [bcls.__dict__ for bcls in reversed(mro)] + [ns]:
            bseen = set()  # type: ignore
            for k, v in bns.items():
                if isinstance(v, (ArgparseCmd, ArgparseArg)):
                    check.not_in(v, bseen)
                    bseen.add(v)
                    objs[k] = v
                elif k in objs:
                    del [k]

        #

        anns = ta.get_type_hints(_ArgparseCliAnnotationBox({
            **{k: v for bcls in reversed(mro) for k, v in getattr(bcls, '__annotations__', {}).items()},
            **ns.get('__annotations__', {}),
        }), globalns=ns.get('__globals__', {}))

        #

        if '_parser' in ns:
            parser = check.isinstance(ns['_parser'], argparse.ArgumentParser)
        else:
            parser = argparse.ArgumentParser()
            setattr(cls, '_parser', parser)

        #

        subparsers = parser.add_subparsers()

        for att, obj in objs.items():
            if isinstance(obj, ArgparseCmd):
                if obj.parent is not None:
                    raise NotImplementedError

                for cn in [obj.name, *(obj.aliases or [])]:
                    subparser = subparsers.add_parser(cn)

                    for arg in (obj.args or []):
                        if (
                                len(arg.args) == 1 and
                                isinstance(arg.args[0], str) and
                                not (n := check.isinstance(arg.args[0], str)).startswith('-') and
                                'metavar' not in arg.kwargs
                        ):
                            subparser.add_argument(
                                n.replace('-', '_'),
                                **arg.kwargs,
                                metavar=n,
                            )
                        else:
                            subparser.add_argument(*arg.args, **arg.kwargs)

                    subparser.set_defaults(_cmd=obj)

            elif isinstance(obj, ArgparseArg):
                if att in anns:
                    ann_kwargs = _get_argparse_arg_ann_kwargs(anns[att])
                    obj.kwargs = {**ann_kwargs, **obj.kwargs}

                if not obj.dest:
                    if 'dest' in obj.kwargs:
                        obj.dest = obj.kwargs['dest']
                    else:
                        obj.dest = obj.kwargs['dest'] = att  # type: ignore

                parser.add_argument(*obj.args, **obj.kwargs)

            else:
                raise TypeError(obj)

    #

    _parser: ta.ClassVar[argparse.ArgumentParser]

    @classmethod
    def get_parser(cls) -> argparse.ArgumentParser:
        return cls._parser

    @property
    def argv(self) -> ta.Sequence[str]:
        return self._argv

    @property
    def args(self) -> argparse.Namespace:
        return self._args

    @property
    def unknown_args(self) -> ta.Sequence[str]:
        return self._unknown_args

    #

    def _bind_cli_cmd(self, cmd: ArgparseCmd) -> ta.Callable:
        return cmd.__get__(self, type(self))

    def prepare_cli_run(self) -> ta.Optional[ta.Callable]:
        cmd = getattr(self.args, '_cmd', None)

        if self._unknown_args and not (cmd is not None and cmd.accepts_unknown):
            msg = f'unrecognized arguments: {" ".join(self._unknown_args)}'
            if (parser := self.get_parser()).exit_on_error:  # type: ignore
                parser.error(msg)
            else:
                raise argparse.ArgumentError(None, msg)

        if cmd is None:
            self.get_parser().print_help()
            return None

        return self._bind_cli_cmd(cmd)

    #

    def cli_run(self) -> ta.Optional[int]:
        if (fn := self.prepare_cli_run()) is None:
            return 0

        return fn()

    def cli_run_and_exit(self) -> ta.NoReturn:
        sys.exit(rc if isinstance(rc := self.cli_run(), int) else 0)

    def __call__(self, *, exit: bool = False) -> ta.Optional[int]:  # noqa
        if exit:
            return self.cli_run_and_exit()
        else:
            return self.cli_run()

    #

    async def async_cli_run(
            self,
            *,
            force_async: bool = False,
    ) -> ta.Optional[int]:
        if (fn := self.prepare_cli_run()) is None:
            return 0

        if force_async:
            is_async = True
        else:
            tfn = fn
            if isinstance(tfn, ArgparseCmd):
                tfn = tfn.fn
            is_async = inspect.iscoroutinefunction(tfn)

        if is_async:
            return await fn()
        else:
            return fn()


########################################
# ../../../omlish/lite/contextmanagers.py


##


class ExitStacked:
    _exit_stack: ta.Optional[contextlib.ExitStack] = None

    def __enter__(self: ExitStackedT) -> ExitStackedT:
        check.state(self._exit_stack is None)
        es = self._exit_stack = contextlib.ExitStack()
        es.__enter__()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if (es := self._exit_stack) is None:
            return None
        self._exit_contexts()
        return es.__exit__(exc_type, exc_val, exc_tb)

    def _exit_contexts(self) -> None:
        pass

    def _enter_context(self, cm: ta.ContextManager[T]) -> T:
        es = check.not_none(self._exit_stack)
        return es.enter_context(cm)


class AsyncExitStacked:
    _exit_stack: ta.Optional[contextlib.AsyncExitStack] = None

    async def __aenter__(self: AsyncExitStackedT) -> AsyncExitStackedT:
        check.state(self._exit_stack is None)
        es = self._exit_stack = contextlib.AsyncExitStack()
        await es.__aenter__()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if (es := self._exit_stack) is None:
            return None
        await self._async_exit_contexts()
        return await es.__aexit__(exc_type, exc_val, exc_tb)

    async def _async_exit_contexts(self) -> None:
        pass

    def _enter_context(self, cm: ta.ContextManager[T]) -> T:
        es = check.not_none(self._exit_stack)
        return es.enter_context(cm)

    async def _enter_async_context(self, cm: ta.AsyncContextManager[T]) -> T:
        es = check.not_none(self._exit_stack)
        return await es.enter_async_context(cm)


##


@contextlib.contextmanager
def defer(fn: ta.Callable) -> ta.Generator[ta.Callable, None, None]:
    try:
        yield fn
    finally:
        fn()


@contextlib.asynccontextmanager
async def adefer(fn: ta.Callable) -> ta.AsyncGenerator[ta.Callable, None]:
    try:
        yield fn
    finally:
        await fn()


##


@contextlib.contextmanager
def attr_setting(obj, attr, val, *, default=None):  # noqa
    not_set = object()
    orig = getattr(obj, attr, not_set)
    try:
        setattr(obj, attr, val)
        if orig is not not_set:
            yield orig
        else:
            yield default
    finally:
        if orig is not_set:
            delattr(obj, attr)
        else:
            setattr(obj, attr, orig)


##


class aclosing(contextlib.AbstractAsyncContextManager):  # noqa
    def __init__(self, thing):
        self.thing = thing

    async def __aenter__(self):
        return self.thing

    async def __aexit__(self, *exc_info):
        await self.thing.aclose()


########################################
# ../../../omlish/lite/runtime.py


@cached_nullary
def is_debugger_attached() -> bool:
    return any(frame[1].endswith('pydevd.py') for frame in inspect.stack())


LITE_REQUIRED_PYTHON_VERSION = (3, 8)


def check_lite_runtime_version() -> None:
    if sys.version_info < LITE_REQUIRED_PYTHON_VERSION:
        raise OSError(f'Requires python {LITE_REQUIRED_PYTHON_VERSION}, got {sys.version_info} from {sys.executable}')  # noqa


########################################
# ../../../omlish/logs/json.py
"""
TODO:
 - translate json keys
"""


class JsonLogFormatter(logging.Formatter):
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
# ../../../omlish/logs/standard.py
"""
TODO:
 - structured
 - prefixed
 - debug
 - optional noisy? noisy will never be lite - some kinda configure_standard callback mechanism?
"""


##


STANDARD_LOG_FORMAT_PARTS = [
    ('asctime', '%(asctime)-15s'),
    ('process', 'pid=%(process)-6s'),
    ('thread', 'tid=%(thread)x'),
    ('levelname', '%(levelname)s'),
    ('name', '%(name)s'),
    ('separator', '::'),
    ('message', '%(message)s'),
]


class StandardLogFormatter(logging.Formatter):
    @staticmethod
    def build_log_format(parts: ta.Iterable[ta.Tuple[str, str]]) -> str:
        return ' '.join(v for k, v in parts)

    converter = datetime.datetime.fromtimestamp  # type: ignore

    def formatTime(self, record, datefmt=None):
        ct = self.converter(record.created)  # type: ignore
        if datefmt:
            return ct.strftime(datefmt)  # noqa
        else:
            t = ct.strftime('%Y-%m-%d %H:%M:%S')
            return '%s.%03d' % (t, record.msecs)  # noqa


##


class StandardConfiguredLogHandler(ProxyLogHandler):
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
        json: bool = False,
        target: ta.Optional[logging.Logger] = None,
        force: bool = False,
        handler_factory: ta.Optional[ta.Callable[[], logging.Handler]] = None,
) -> ta.Optional[StandardConfiguredLogHandler]:
    with _locking_logging_module_lock():
        if target is None:
            target = logging.root

        #

        if not force:
            if any(isinstance(h, StandardConfiguredLogHandler) for h in list(target.handlers)):
                return None

        #

        if handler_factory is not None:
            handler = handler_factory()
        else:
            handler = logging.StreamHandler()

        #

        formatter: logging.Formatter
        if json:
            formatter = JsonLogFormatter()
        else:
            formatter = StandardLogFormatter(StandardLogFormatter.build_log_format(STANDARD_LOG_FORMAT_PARTS))
        handler.setFormatter(formatter)

        #

        handler.addFilter(TidLogFilter())

        #

        target.addHandler(handler)

        #

        if level is not None:
            target.setLevel(level)

        #

        return StandardConfiguredLogHandler(handler)


########################################
# ../../../omlish/subprocesses.py


##


SUBPROCESS_CHANNEL_OPTION_VALUES: ta.Mapping[SubprocessChannelOption, int] = {
    'pipe': subprocess.PIPE,
    'stdout': subprocess.STDOUT,
    'devnull': subprocess.DEVNULL,
}


##


_SUBPROCESS_SHELL_WRAP_EXECS = False


def subprocess_shell_wrap_exec(*cmd: str) -> ta.Tuple[str, ...]:
    return ('sh', '-c', ' '.join(map(shlex.quote, cmd)))


def subprocess_maybe_shell_wrap_exec(*cmd: str) -> ta.Tuple[str, ...]:
    if _SUBPROCESS_SHELL_WRAP_EXECS or is_debugger_attached():
        return subprocess_shell_wrap_exec(*cmd)
    else:
        return cmd


##


def subprocess_close(
        proc: subprocess.Popen,
        timeout: ta.Optional[float] = None,
) -> None:
    # TODO: terminate, sleep, kill
    if proc.stdout:
        proc.stdout.close()
    if proc.stderr:
        proc.stderr.close()
    if proc.stdin:
        proc.stdin.close()

    proc.wait(timeout)


##


class BaseSubprocesses(abc.ABC):  # noqa
    DEFAULT_LOGGER: ta.ClassVar[ta.Optional[logging.Logger]] = None

    def __init__(
            self,
            *,
            log: ta.Optional[logging.Logger] = None,
            try_exceptions: ta.Optional[ta.Tuple[ta.Type[Exception], ...]] = None,
    ) -> None:
        super().__init__()

        self._log = log if log is not None else self.DEFAULT_LOGGER
        self._try_exceptions = try_exceptions if try_exceptions is not None else self.DEFAULT_TRY_EXCEPTIONS

    def set_logger(self, log: ta.Optional[logging.Logger]) -> None:
        self._log = log

    #

    def prepare_args(
            self,
            *cmd: str,
            env: ta.Optional[ta.Mapping[str, ta.Any]] = None,
            extra_env: ta.Optional[ta.Mapping[str, ta.Any]] = None,
            quiet: bool = False,
            shell: bool = False,
            **kwargs: ta.Any,
    ) -> ta.Tuple[ta.Tuple[ta.Any, ...], ta.Dict[str, ta.Any]]:
        if self._log:
            self._log.debug('Subprocesses.prepare_args: cmd=%r', cmd)
            if extra_env:
                self._log.debug('Subprocesses.prepare_args: extra_env=%r', extra_env)

        if extra_env:
            env = {**(env if env is not None else os.environ), **extra_env}

        if quiet and 'stderr' not in kwargs:
            if self._log and not self._log.isEnabledFor(logging.DEBUG):
                kwargs['stderr'] = subprocess.DEVNULL

        if not shell:
            cmd = subprocess_maybe_shell_wrap_exec(*cmd)

        return cmd, dict(
            env=env,
            shell=shell,
            **kwargs,
        )

    @contextlib.contextmanager
    def wrap_call(self, *cmd: ta.Any, **kwargs: ta.Any) -> ta.Iterator[None]:
        start_time = time.time()
        try:
            if self._log:
                self._log.debug('Subprocesses.wrap_call.try: cmd=%r', cmd)
            yield

        except Exception as exc:  # noqa
            if self._log:
                self._log.debug('Subprocesses.wrap_call.except: exc=%r', exc)
            raise

        finally:
            end_time = time.time()
            elapsed_s = end_time - start_time
            if self._log:
                self._log.debug('sSubprocesses.wrap_call.finally: elapsed_s=%f cmd=%r', elapsed_s, cmd)

    @contextlib.contextmanager
    def prepare_and_wrap(
            self,
            *cmd: ta.Any,
            **kwargs: ta.Any,
    ) -> ta.Iterator[ta.Tuple[
        ta.Tuple[ta.Any, ...],
        ta.Dict[str, ta.Any],
    ]]:
        cmd, kwargs = self.prepare_args(*cmd, **kwargs)
        with self.wrap_call(*cmd, **kwargs):
            yield cmd, kwargs

    #

    DEFAULT_TRY_EXCEPTIONS: ta.Tuple[ta.Type[Exception], ...] = (
        FileNotFoundError,
        subprocess.CalledProcessError,
    )

    def try_fn(
            self,
            fn: ta.Callable[..., T],
            *cmd: str,
            try_exceptions: ta.Optional[ta.Tuple[ta.Type[Exception], ...]] = None,
            **kwargs: ta.Any,
    ) -> ta.Union[T, Exception]:
        if try_exceptions is None:
            try_exceptions = self._try_exceptions

        try:
            return fn(*cmd, **kwargs)

        except try_exceptions as e:  # noqa
            if self._log and self._log.isEnabledFor(logging.DEBUG):
                self._log.exception('command failed')
            return e

    async def async_try_fn(
            self,
            fn: ta.Callable[..., ta.Awaitable[T]],
            *cmd: ta.Any,
            try_exceptions: ta.Optional[ta.Tuple[ta.Type[Exception], ...]] = None,
            **kwargs: ta.Any,
    ) -> ta.Union[T, Exception]:
        if try_exceptions is None:
            try_exceptions = self._try_exceptions

        try:
            return await fn(*cmd, **kwargs)

        except try_exceptions as e:  # noqa
            if self._log and self._log.isEnabledFor(logging.DEBUG):
                self._log.exception('command failed')
            return e


##


class AbstractSubprocesses(BaseSubprocesses, abc.ABC):
    @abc.abstractmethod
    def check_call(
            self,
            *cmd: str,
            stdout: ta.Any = sys.stderr,
            **kwargs: ta.Any,
    ) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def check_output(
            self,
            *cmd: str,
            **kwargs: ta.Any,
    ) -> bytes:
        raise NotImplementedError

    #

    def check_output_str(
            self,
            *cmd: str,
            **kwargs: ta.Any,
    ) -> str:
        return self.check_output(*cmd, **kwargs).decode().strip()

    #

    def try_call(
            self,
            *cmd: str,
            **kwargs: ta.Any,
    ) -> bool:
        if isinstance(self.try_fn(self.check_call, *cmd, **kwargs), Exception):
            return False
        else:
            return True

    def try_output(
            self,
            *cmd: str,
            **kwargs: ta.Any,
    ) -> ta.Optional[bytes]:
        if isinstance(ret := self.try_fn(self.check_output, *cmd, **kwargs), Exception):
            return None
        else:
            return ret

    def try_output_str(
            self,
            *cmd: str,
            **kwargs: ta.Any,
    ) -> ta.Optional[str]:
        if (ret := self.try_output(*cmd, **kwargs)) is None:
            return None
        else:
            return ret.decode().strip()


##


class Subprocesses(AbstractSubprocesses):
    def check_call(
            self,
            *cmd: str,
            stdout: ta.Any = sys.stderr,
            **kwargs: ta.Any,
    ) -> None:
        with self.prepare_and_wrap(*cmd, stdout=stdout, **kwargs) as (cmd, kwargs):  # noqa
            subprocess.check_call(cmd, **kwargs)

    def check_output(
            self,
            *cmd: str,
            **kwargs: ta.Any,
    ) -> bytes:
        with self.prepare_and_wrap(*cmd, **kwargs) as (cmd, kwargs):  # noqa
            return subprocess.check_output(cmd, **kwargs)


subprocesses = Subprocesses()


##


class AbstractAsyncSubprocesses(BaseSubprocesses):
    @abc.abstractmethod
    async def check_call(
            self,
            *cmd: str,
            stdout: ta.Any = sys.stderr,
            **kwargs: ta.Any,
    ) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    async def check_output(
            self,
            *cmd: str,
            **kwargs: ta.Any,
    ) -> bytes:
        raise NotImplementedError

    #

    async def check_output_str(
            self,
            *cmd: str,
            **kwargs: ta.Any,
    ) -> str:
        return (await self.check_output(*cmd, **kwargs)).decode().strip()

    #

    async def try_call(
            self,
            *cmd: str,
            **kwargs: ta.Any,
    ) -> bool:
        if isinstance(await self.async_try_fn(self.check_call, *cmd, **kwargs), Exception):
            return False
        else:
            return True

    async def try_output(
            self,
            *cmd: str,
            **kwargs: ta.Any,
    ) -> ta.Optional[bytes]:
        if isinstance(ret := await self.async_try_fn(self.check_output, *cmd, **kwargs), Exception):
            return None
        else:
            return ret

    async def try_output_str(
            self,
            *cmd: str,
            **kwargs: ta.Any,
    ) -> ta.Optional[str]:
        if (ret := await self.try_output(*cmd, **kwargs)) is None:
            return None
        else:
            return ret.decode().strip()


########################################
# ../github/curl.py


##


class GithubServiceCurlClient:
    def __init__(
            self,
            service_url: str,
            auth_token: ta.Optional[str] = None,
            *,
            api_version: ta.Optional[str] = None,
    ) -> None:
        super().__init__()

        self._service_url = check.non_empty_str(service_url)
        self._auth_token = auth_token
        self._api_version = api_version

    #

    _MISSING = object()

    def build_headers(
            self,
            headers: ta.Optional[ta.Mapping[str, str]] = None,
            *,
            auth_token: ta.Any = _MISSING,
            content_type: ta.Optional[str] = None,
    ) -> ta.Dict[str, str]:
        dct = {
            'Accept': ';'.join([
                'application/json',
                *([f'api-version={self._api_version}'] if self._api_version else []),
            ]),
        }

        if auth_token is self._MISSING:
            auth_token = self._auth_token
        if auth_token:
            dct['Authorization'] = f'Bearer {auth_token}'

        if content_type is not None:
            dct['Content-Type'] = content_type

        if headers:
            dct.update(headers)

        return dct

    #

    HEADER_AUTH_TOKEN_ENV_KEY_PREFIX = '_GITHUB_SERVICE_AUTH_TOKEN'  # noqa

    @property
    def header_auth_token_env_key(self) -> str:
        return f'{self.HEADER_AUTH_TOKEN_ENV_KEY_PREFIX}_{id(self)}'

    def build_cmd(
            self,
            method: str,
            url: str,
            *,
            json_content: bool = False,
            content_type: ta.Optional[str] = None,
            headers: ta.Optional[ta.Dict[str, str]] = None,
    ) -> ShellCmd:
        if content_type is None and json_content:
            content_type = 'application/json'

        env = {}

        header_auth_token: ta.Optional[str]
        if self._auth_token:
            header_env_key = self.header_auth_token_env_key
            env[header_env_key] = self._auth_token
            header_auth_token = f'${header_env_key}'
        else:
            header_auth_token = None

        built_hdrs = self.build_headers(
            headers,
            auth_token=header_auth_token,
            content_type=content_type,
        )

        url = f'{self._service_url}/{url}'

        cmd = ' '.join([
            'curl',
            '-s',
            '-X', method,
            url,
            *[f'-H "{k}: {v}"' for k, v in built_hdrs.items()],
        ])

        return ShellCmd(
            cmd,
            env=env,
        )

    def build_post_json_cmd(
            self,
            url: str,
            obj: ta.Any,
            **kwargs: ta.Any,
    ) -> ShellCmd:
        curl_cmd = self.build_cmd(
            'POST',
            url,
            json_content=True,
            **kwargs,
        )

        obj_json = json_dumps_compact(obj)

        return dc.replace(curl_cmd, s=f'{curl_cmd.s} -d {shlex.quote(obj_json)}')

    #

    @dc.dataclass()
    class Error(RuntimeError):
        status_code: int
        body: ta.Optional[bytes]

        def __str__(self) -> str:
            return repr(self)

    @dc.dataclass(frozen=True)
    class Result:
        status_code: int
        body: ta.Optional[bytes]

        def as_error(self) -> 'GithubServiceCurlClient.Error':
            return GithubServiceCurlClient.Error(
                status_code=self.status_code,
                body=self.body,
            )

    def run_cmd(
            self,
            cmd: ShellCmd,
            *,
            raise_: bool = False,
            **subprocess_kwargs: ta.Any,
    ) -> Result:
        out_file = make_temp_file()
        with defer(lambda: os.unlink(out_file)):
            run_cmd = dc.replace(cmd, s=f"{cmd.s} -o {out_file} -w '%{{json}}'")

            out_json_bytes = run_cmd.run(
                subprocesses.check_output,
                **subprocess_kwargs,
            )

            out_json = json.loads(out_json_bytes.decode())
            status_code = check.isinstance(out_json['response_code'], int)

            with open(out_file, 'rb') as f:
                body = f.read()

            result = self.Result(
                status_code=status_code,
                body=body,
            )

        if raise_ and (500 <= status_code <= 600):
            raise result.as_error()

        return result

    def run_json_cmd(
            self,
            cmd: ShellCmd,
            *,
            success_status_codes: ta.Optional[ta.Container[int]] = None,
    ) -> ta.Optional[ta.Any]:
        result = self.run_cmd(cmd, raise_=True)

        if success_status_codes is not None:
            is_success = result.status_code in success_status_codes
        else:
            is_success = 200 <= result.status_code < 300

        if is_success:
            if not (body := result.body):
                return None
            return json.loads(body.decode('utf-8-sig'))

        elif result.status_code == 404:
            return None

        else:
            raise result.as_error()


########################################
# ../requirements.py
"""
TODO:
 - pip compile lol
  - but still support git+ stuff
 - req.txt format aware hash
  - more than just whitespace
 - pyproject req rewriting
 - download_requirements bootstrap off prev? not worth the dl?
  - big deps (torch) change less, probably worth it
 - follow embedded -r automatically like pyp
"""


##


def build_requirements_hash(
        requirements_txts: ta.Sequence[str],
) -> str:
    txt_file_contents: dict = {}

    for txt_file in requirements_txts:
        txt_file_name = os.path.basename(txt_file)
        check.not_in(txt_file_name, txt_file_contents)
        with open(txt_file) as f:
            txt_contents = f.read()
        txt_file_contents[txt_file_name] = txt_contents

    #

    lines = []
    for txt_file, txt_contents in sorted(txt_file_contents.items()):
        txt_hash = sha256_str(txt_contents)
        lines.append(f'{txt_file}={txt_hash}')

    return sha256_str('\n'.join(lines))


##


def download_requirements(
        image: str,
        requirements_dir: str,
        requirements_txts: ta.Sequence[str],
) -> None:
    requirements_txt_dir = tempfile.mkdtemp()
    with defer(lambda: shutil.rmtree(requirements_txt_dir)):
        for rt in requirements_txts:
            shutil.copyfile(rt, os.path.join(requirements_txt_dir, os.path.basename(rt)))

        subprocesses.check_call(
            'docker',
            'run',
            '--rm',
            '-i',
            '-v', f'{os.path.abspath(requirements_dir)}:/requirements',
            '-v', f'{requirements_txt_dir}:/requirements_txt',
            image,
            'pip',
            'download',
            '-d', '/requirements',
            *itertools.chain.from_iterable(
                ['-r', f'/requirements_txt/{os.path.basename(rt)}']
                for rt in requirements_txts
            ),
        )


########################################
# ../../../omlish/asyncs/asyncio/subprocesses.py


##


class AsyncioProcessCommunicator:
    def __init__(
            self,
            proc: asyncio.subprocess.Process,
            loop: ta.Optional[ta.Any] = None,
            *,
            log: ta.Optional[logging.Logger] = None,
    ) -> None:
        super().__init__()

        if loop is None:
            loop = asyncio.get_running_loop()

        self._proc = proc
        self._loop = loop
        self._log = log

        self._transport: asyncio.base_subprocess.BaseSubprocessTransport = check.isinstance(
            proc._transport,  # type: ignore  # noqa
            asyncio.base_subprocess.BaseSubprocessTransport,
        )

    @property
    def _debug(self) -> bool:
        return self._loop.get_debug()

    async def _feed_stdin(self, input: bytes) -> None:  # noqa
        stdin = check.not_none(self._proc.stdin)
        try:
            if input is not None:
                stdin.write(input)
                if self._debug and self._log is not None:
                    self._log.debug('%r communicate: feed stdin (%s bytes)', self, len(input))

            await stdin.drain()

        except (BrokenPipeError, ConnectionResetError) as exc:
            # communicate() ignores BrokenPipeError and ConnectionResetError. write() and drain() can raise these
            # exceptions.
            if self._debug and self._log is not None:
                self._log.debug('%r communicate: stdin got %r', self, exc)

        if self._debug and self._log is not None:
            self._log.debug('%r communicate: close stdin', self)

        stdin.close()

    async def _noop(self) -> None:
        return None

    async def _read_stream(self, fd: int) -> bytes:
        transport: ta.Any = check.not_none(self._transport.get_pipe_transport(fd))

        if fd == 2:
            stream = check.not_none(self._proc.stderr)
        else:
            check.equal(fd, 1)
            stream = check.not_none(self._proc.stdout)

        if self._debug and self._log is not None:
            name = 'stdout' if fd == 1 else 'stderr'
            self._log.debug('%r communicate: read %s', self, name)

        output = await stream.read()

        if self._debug and self._log is not None:
            name = 'stdout' if fd == 1 else 'stderr'
            self._log.debug('%r communicate: close %s', self, name)

        transport.close()

        return output

    class Communication(ta.NamedTuple):
        stdout: ta.Optional[bytes]
        stderr: ta.Optional[bytes]

    async def _communicate(
            self,
            input: ta.Any = None,  # noqa
    ) -> Communication:
        stdin_fut: ta.Any
        if self._proc.stdin is not None:
            stdin_fut = self._feed_stdin(input)
        else:
            stdin_fut = self._noop()

        stdout_fut: ta.Any
        if self._proc.stdout is not None:
            stdout_fut = self._read_stream(1)
        else:
            stdout_fut = self._noop()

        stderr_fut: ta.Any
        if self._proc.stderr is not None:
            stderr_fut = self._read_stream(2)
        else:
            stderr_fut = self._noop()

        stdin_res, stdout_res, stderr_res = await asyncio.gather(stdin_fut, stdout_fut, stderr_fut)

        await self._proc.wait()

        return AsyncioProcessCommunicator.Communication(stdout_res, stderr_res)

    async def communicate(
            self,
            input: ta.Any = None,  # noqa
            timeout: ta.Optional[float] = None,
    ) -> Communication:
        return await asyncio_maybe_timeout(self._communicate(input), timeout)


##


class AsyncioSubprocesses(AbstractAsyncSubprocesses):
    async def communicate(
            self,
            proc: asyncio.subprocess.Process,
            input: ta.Any = None,  # noqa
            timeout: ta.Optional[float] = None,
    ) -> ta.Tuple[ta.Optional[bytes], ta.Optional[bytes]]:
        return await AsyncioProcessCommunicator(proc).communicate(input, timeout)  # noqa

    #

    @contextlib.asynccontextmanager
    async def popen(
            self,
            *cmd: str,
            shell: bool = False,
            timeout: ta.Optional[float] = None,
            **kwargs: ta.Any,
    ) -> ta.AsyncGenerator[asyncio.subprocess.Process, None]:
        fac: ta.Any
        if shell:
            fac = functools.partial(
                asyncio.create_subprocess_shell,
                check.single(cmd),
            )
        else:
            fac = functools.partial(
                asyncio.create_subprocess_exec,
                *cmd,
            )

        with self.prepare_and_wrap( *cmd, shell=shell, **kwargs) as (cmd, kwargs):  # noqa
            proc: asyncio.subprocess.Process = await fac(**kwargs)
            try:
                yield proc

            finally:
                await asyncio_maybe_timeout(proc.wait(), timeout)

    #

    @dc.dataclass(frozen=True)
    class RunOutput:
        proc: asyncio.subprocess.Process
        stdout: ta.Optional[bytes]
        stderr: ta.Optional[bytes]

    async def run(
            self,
            *cmd: str,
            input: ta.Any = None,  # noqa
            timeout: ta.Optional[float] = None,
            check: bool = False,  # noqa
            capture_output: ta.Optional[bool] = None,
            **kwargs: ta.Any,
    ) -> RunOutput:
        if capture_output:
            kwargs.setdefault('stdout', subprocess.PIPE)
            kwargs.setdefault('stderr', subprocess.PIPE)

        proc: asyncio.subprocess.Process
        async with self.popen(*cmd, **kwargs) as proc:
            stdout, stderr = await self.communicate(proc, input, timeout)

        if check and proc.returncode:
            raise subprocess.CalledProcessError(
                proc.returncode,
                cmd,
                output=stdout,
                stderr=stderr,
            )

        return self.RunOutput(
            proc,
            stdout,
            stderr,
        )

    #

    async def check_call(
            self,
            *cmd: str,
            stdout: ta.Any = sys.stderr,
            **kwargs: ta.Any,
    ) -> None:
        with self.prepare_and_wrap(*cmd, stdout=stdout, check=True, **kwargs) as (cmd, kwargs):  # noqa
            await self.run(*cmd, **kwargs)

    async def check_output(
            self,
            *cmd: str,
            **kwargs: ta.Any,
    ) -> bytes:
        with self.prepare_and_wrap(*cmd, stdout=subprocess.PIPE, check=True, **kwargs) as (cmd, kwargs):  # noqa
            return check.not_none((await self.run(*cmd, **kwargs)).stdout)


asyncio_subprocesses = AsyncioSubprocesses()


########################################
# ../compose.py
"""
TODO:
 - fix rmi - only when not referenced anymore
"""


##


def get_compose_service_dependencies(
        compose_file: str,
        service: str,
) -> ta.Dict[str, str]:
    compose_dct = read_yaml_file(compose_file)

    services = compose_dct['services']
    service_dct = services[service]

    out = {}
    for dep_service in service_dct.get('depends_on', []):
        dep_service_dct = services[dep_service]
        out[dep_service] = dep_service_dct['image']

    return out


##


class DockerComposeRun(AsyncExitStacked):
    @dc.dataclass(frozen=True)
    class Config:
        compose_file: str
        service: str

        image: str

        cmd: ShellCmd

        #

        run_options: ta.Optional[ta.Sequence[str]] = None

        cwd: ta.Optional[str] = None

        #

        no_dependencies: bool = False
        no_dependency_cleanup: bool = False

        #

        def __post_init__(self) -> None:
            check.not_isinstance(self.run_options, str)

    def __init__(self, cfg: Config) -> None:
        super().__init__()

        self._cfg = cfg

        self._subprocess_kwargs = {
            **(dict(cwd=self._cfg.cwd) if self._cfg.cwd is not None else {}),
        }

    #

    def _rewrite_compose_dct(self, in_dct: ta.Dict[str, ta.Any]) -> ta.Dict[str, ta.Any]:
        out = dict(in_dct)

        #

        in_services = in_dct['services']
        out['services'] = out_services = {}

        #

        in_service: dict = in_services[self._cfg.service]
        out_services[self._cfg.service] = out_service = dict(in_service)

        out_service['image'] = self._cfg.image

        for k in ['build', 'platform']:
            if k in out_service:
                del out_service[k]

        out_service['links'] = [
            f'{l}:{l}' if ':' not in l else l
            for l in out_service.get('links', [])
        ]

        #

        if not self._cfg.no_dependencies:
            depends_on = in_service.get('depends_on', [])

            for dep_service, in_dep_service_dct in list(in_services.items()):
                if dep_service not in depends_on:
                    continue

                out_dep_service: dict = dict(in_dep_service_dct)
                out_services[dep_service] = out_dep_service

                out_dep_service['ports'] = []

        else:
            out_service['depends_on'] = []
            out_service['links'] = []

        #

        return out

    @cached_nullary
    def rewrite_compose_file(self) -> str:
        in_dct = read_yaml_file(self._cfg.compose_file)

        out_dct = self._rewrite_compose_dct(in_dct)

        #

        out_compose_file = make_temp_file()
        self._enter_context(defer(lambda: os.unlink(out_compose_file)))  # noqa

        compose_json = json_dumps_pretty(out_dct)

        with open(out_compose_file, 'w') as f:
            f.write(compose_json)

        return out_compose_file

    #

    async def _cleanup_dependencies(self) -> None:
        await asyncio_subprocesses.check_call(
            'docker',
            'compose',
            '-f', self.rewrite_compose_file(),
            'down',
        )

    async def run(self) -> None:
        compose_file = self.rewrite_compose_file()

        async with contextlib.AsyncExitStack() as es:
            if not (self._cfg.no_dependencies or self._cfg.no_dependency_cleanup):
                await es.enter_async_context(adefer(self._cleanup_dependencies))  # noqa

            sh_cmd = ' '.join([
                'docker',
                'compose',
                '-f', compose_file,
                'run',
                '--rm',
                *itertools.chain.from_iterable(
                    ['-e', k]
                    for k in (self._cfg.cmd.env or [])
                ),
                *(self._cfg.run_options or []),
                self._cfg.service,
                'sh', '-c', shlex.quote(self._cfg.cmd.s),
            ])

            run_cmd = dc.replace(self._cfg.cmd, s=sh_cmd)

            await run_cmd.run(
                asyncio_subprocesses.check_call,
                **self._subprocess_kwargs,
            )


########################################
# ../docker.py
"""
TODO:
 - some less stupid Dockerfile hash
  - doesn't change too much though
"""


##


def build_docker_file_hash(docker_file: str) -> str:
    with open(docker_file) as f:
        contents = f.read()

    return sha256_str(contents)


##


def read_docker_tar_image_tag(tar_file: str) -> str:
    with tarfile.open(tar_file) as tf:
        with contextlib.closing(check.not_none(tf.extractfile('manifest.json'))) as mf:
            m = mf.read()

    manifests = json.loads(m.decode('utf-8'))
    manifest = check.single(manifests)
    tag = check.non_empty_str(check.single(manifest['RepoTags']))
    return tag


def read_docker_tar_image_id(tar_file: str) -> str:
    with tarfile.open(tar_file) as tf:
        with contextlib.closing(check.not_none(tf.extractfile('index.json'))) as mf:
            i = mf.read()

    index = json.loads(i.decode('utf-8'))
    manifest = check.single(index['manifests'])
    image_id = check.non_empty_str(manifest['digest'])
    return image_id


##


async def is_docker_image_present(image: str) -> bool:
    out = await asyncio_subprocesses.check_output(
        'docker',
        'images',
        '--format', 'json',
        image,
    )

    out_s = out.decode('utf-8').strip()
    if not out_s:
        return False

    json.loads(out_s)  # noqa
    return True


async def pull_docker_image(
        image: str,
) -> None:
    await asyncio_subprocesses.check_call(
        'docker',
        'pull',
        image,
    )


async def build_docker_image(
        docker_file: str,
        *,
        tag: ta.Optional[str] = None,
        cwd: ta.Optional[str] = None,
) -> str:
    id_file = make_temp_file()
    with defer(lambda: os.unlink(id_file)):
        await asyncio_subprocesses.check_call(
            'docker',
            'build',
            '-f', os.path.abspath(docker_file),
            '--iidfile', id_file,
            '--squash',
            *(['--tag', tag] if tag is not None else []),
            '.',
            **(dict(cwd=cwd) if cwd is not None else {}),
        )

        with open(id_file) as f:  # noqa
            image_id = check.single(f.read().strip().splitlines()).strip()

    return image_id


async def tag_docker_image(image: str, tag: str) -> None:
    await asyncio_subprocesses.check_call(
        'docker',
        'tag',
        image,
        tag,
    )


async def delete_docker_tag(tag: str) -> None:
    await asyncio_subprocesses.check_call(
        'docker',
        'rmi',
        tag,
    )


##


async def save_docker_tar_cmd(
        image: str,
        output_cmd: ShellCmd,
) -> None:
    cmd = dc.replace(output_cmd, s=f'docker save {image} | {output_cmd.s}')
    await cmd.run(asyncio_subprocesses.check_call)


async def save_docker_tar(
        image: str,
        tar_file: str,
) -> None:
    return await save_docker_tar_cmd(
        image,
        ShellCmd(f'cat > {shlex.quote(tar_file)}'),
    )


#


async def load_docker_tar_cmd(
        input_cmd: ShellCmd,
) -> str:
    cmd = dc.replace(input_cmd, s=f'{input_cmd.s} | docker load')

    out = (await cmd.run(asyncio_subprocesses.check_output)).decode()

    line = check.single(out.strip().splitlines())
    loaded = line.partition(':')[2].strip()
    return loaded


async def load_docker_tar(
        tar_file: str,
) -> str:
    return await load_docker_tar_cmd(ShellCmd(f'cat {shlex.quote(tar_file)}'))


########################################
# ../github/cache.py


##


class GithubCacheShellClient(abc.ABC):
    class Entry(abc.ABC):  # noqa
        pass

    @abc.abstractmethod
    def run_get_entry(self, key: str) -> ta.Optional[Entry]:
        raise NotImplementedError

    @abc.abstractmethod
    def download_get_entry(self, entry: Entry, out_file: str) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def upload_cache_entry(self, key: str, in_file: str) -> None:
        raise NotImplementedError


#


class GithubCacheServiceV1ShellClient(GithubCacheShellClient):
    BASE_URL_ENV_KEY = 'ACTIONS_CACHE_URL'
    AUTH_TOKEN_ENV_KEY = 'ACTIONS_RUNTIME_TOKEN'  # noqa

    KEY_SUFFIX_ENV_KEY = 'GITHUB_RUN_ID'

    CACHE_VERSION: ta.ClassVar[int] = 1

    #

    def __init__(
            self,
            *,
            base_url: ta.Optional[str] = None,
            auth_token: ta.Optional[str] = None,

            key_prefix: ta.Optional[str] = None,
            key_suffix: ta.Optional[str] = None,
    ) -> None:
        super().__init__()

        #

        if base_url is None:
            base_url = os.environ[self.BASE_URL_ENV_KEY]
        service_url = GithubCacheServiceV1.get_service_url(base_url)

        if auth_token is None:
            auth_token = os.environ.get(self.AUTH_TOKEN_ENV_KEY)

        self._curl = GithubServiceCurlClient(
            service_url,
            auth_token,
            api_version=GithubCacheServiceV1.API_VERSION,
        )

        #

        self._key_prefix = key_prefix

        if key_suffix is None:
            key_suffix = os.environ[self.KEY_SUFFIX_ENV_KEY]
        self._key_suffix = check.non_empty_str(key_suffix)

    #

    KEY_PART_SEPARATOR = '--'

    def fix_key(self, s: str) -> str:
        return self.KEY_PART_SEPARATOR.join([
            *([self._key_prefix] if self._key_prefix else []),
            s,
            self._key_suffix,
        ])

    #

    @dc.dataclass(frozen=True)
    class Entry(GithubCacheShellClient.Entry):
        artifact: GithubCacheServiceV1.ArtifactCacheEntry

    #

    def build_get_entry_curl_cmd(self, key: str) -> ShellCmd:
        fixed_key = self.fix_key(key)

        qp = dict(
            keys=fixed_key,
            version=str(self.CACHE_VERSION),
        )

        return self._curl.build_cmd(
            'GET',
            shlex.quote('?'.join([
                'cache',
                '&'.join([
                    f'{k}={urllib.parse.quote_plus(v)}'
                    for k, v in qp.items()
                ]),
            ])),
        )

    def run_get_entry(self, key: str) -> ta.Optional[Entry]:
        fixed_key = self.fix_key(key)
        curl_cmd = self.build_get_entry_curl_cmd(fixed_key)

        obj = self._curl.run_json_cmd(
            curl_cmd,
            success_status_codes=[200, 204],
        )
        if obj is None:
            return None

        return self.Entry(GithubCacheServiceV1.dataclass_from_json(
            GithubCacheServiceV1.ArtifactCacheEntry,
            obj,
        ))

    #

    def build_download_get_entry_cmd(self, entry: Entry, out_file: str) -> ShellCmd:
        return ShellCmd(' '.join([
            'aria2c',
            '-x', '4',
            '-o', out_file,
            check.non_empty_str(entry.artifact.archive_location),
        ]))

    def download_get_entry(self, entry: GithubCacheShellClient.Entry, out_file: str) -> None:
        dl_cmd = self.build_download_get_entry_cmd(
            check.isinstance(entry, GithubCacheServiceV1ShellClient.Entry),
            out_file,
        )
        dl_cmd.run(subprocesses.check_call)

    #

    def upload_cache_entry(self, key: str, in_file: str) -> None:
        fixed_key = self.fix_key(key)

        check.state(os.path.isfile(in_file))

        file_size = os.stat(in_file).st_size

        #

        reserve_req = GithubCacheServiceV1.ReserveCacheRequest(
            key=fixed_key,
            cache_size=file_size,
            version=str(self.CACHE_VERSION),
        )
        reserve_cmd = self._curl.build_post_json_cmd(
            'caches',
            GithubCacheServiceV1.dataclass_to_json(reserve_req),
        )
        reserve_resp_obj: ta.Any = check.not_none(self._curl.run_json_cmd(
            reserve_cmd,
            success_status_codes=[201],
        ))
        reserve_resp = GithubCacheServiceV1.dataclass_from_json(  # noqa
            GithubCacheServiceV1.ReserveCacheResponse,
            reserve_resp_obj,
        )
        cache_id = check.isinstance(reserve_resp.cache_id, int)

        #

        tmp_file = make_temp_file()

        print(f'{file_size=}')
        num_written = 0
        chunk_size = 32 * 1024 * 1024
        for i in range((file_size // chunk_size) + (1 if file_size % chunk_size else 0)):
            ofs = i * chunk_size
            sz = min(chunk_size, file_size - ofs)

            patch_cmd = self._curl.build_cmd(
                'PATCH',
                f'caches/{cache_id}',
                content_type='application/octet-stream',
                headers={
                    'Content-Range': f'bytes {ofs}-{ofs + sz - 1}/*',
                },
            )

            #

            # patch_data_cmd = dc.replace(patch_cmd, s=' | '.join([
            #     f'dd if={in_file} bs={chunk_size} skip={i} count=1 status=none',
            #     f'{patch_cmd.s} --data-binary -',
            # ]))
            # print(f'{patch_data_cmd.s=}')
            # patch_result = self._curl.run_cmd(patch_data_cmd, raise_=True)

            #

            with open(in_file, 'rb') as f:
                f.seek(ofs)
                buf = f.read(sz)
            with open(tmp_file, 'wb') as f:
                f.write(buf)
            num_written += len(buf)
            print(f'{num_written=}')
            patch_data_cmd = dc.replace(patch_cmd, s=f'{patch_cmd.s} --data-binary @{tmp_file}')
            print(f'{patch_data_cmd.s=}')
            patch_result = self._curl.run_cmd(patch_data_cmd, raise_=True)

            #

            check.equal(patch_result.status_code, 204)
            ofs += sz

        #

        commit_req = GithubCacheServiceV1.CommitCacheRequest(
            size=file_size,
        )
        commit_cmd = self._curl.build_post_json_cmd(
            f'caches/{cache_id}',
            GithubCacheServiceV1.dataclass_to_json(commit_req),
        )
        commit_result = self._curl.run_cmd(commit_cmd, raise_=True)
        check.equal(commit_result.status_code, 204)


##


class GithubShellCache(ShellCache):
    def __init__(
            self,
            dir: str,  # noqa
            *,
            client: ta.Optional[GithubCacheShellClient] = None,
    ) -> None:
        super().__init__()

        self._dir = check.not_none(dir)

        if client is None:
            client = GithubCacheServiceV1ShellClient()
        self._client: GithubCacheShellClient = client

        self._local = DirectoryFileCache(self._dir)

    def get_file_cmd(self, key: str) -> ta.Optional[ShellCmd]:
        local_file = self._local.get_cache_file_path(key)
        if os.path.exists(local_file):
            return ShellCmd(f'cat {shlex.quote(local_file)}')

        if (entry := self._client.run_get_entry(key)) is None:
            return None

        tmp_file = self._local.format_incomplete_file(local_file)
        try:
            self._client.download_get_entry(entry, tmp_file)

            os.replace(tmp_file, local_file)

        except BaseException:  # noqa
            os.unlink(tmp_file)

            raise

        return ShellCmd(f'cat {shlex.quote(local_file)}')

    class _PutFileCmdContext(ShellCache.PutFileCmdContext):  # noqa
        def __init__(
                self,
                owner: 'GithubShellCache',
                key: str,
                tmp_file: str,
                local_file: str,
        ) -> None:
            super().__init__()

            self._owner = owner
            self._key = key
            self._tmp_file = tmp_file
            self._local_file = local_file

        @property
        def cmd(self) -> ShellCmd:
            return ShellCmd(f'cat > {shlex.quote(self._tmp_file)}')

        def _commit(self) -> None:
            os.replace(self._tmp_file, self._local_file)

            self._owner._client.upload_cache_entry(self._key, self._local_file)  # noqa

        def _abort(self) -> None:
            os.unlink(self._tmp_file)

    def put_file_cmd(self, key: str) -> ShellCache.PutFileCmdContext:
        local_file = self._local.get_cache_file_path(key, make_dirs=True)
        return self._PutFileCmdContext(
            self,
            key,
            self._local.format_incomplete_file(local_file),
            local_file,
        )


########################################
# ../ci.py


class Ci(AsyncExitStacked):
    FILE_NAME_HASH_LEN = 16

    @dc.dataclass(frozen=True)
    class Config:
        project_dir: str

        docker_file: str

        compose_file: str
        service: str

        cmd: ShellCmd

        requirements_txts: ta.Optional[ta.Sequence[str]] = None

        always_pull: bool = False
        always_build: bool = False

        no_dependencies: bool = False

        def __post_init__(self) -> None:
            check.not_isinstance(self.requirements_txts, str)

    def __init__(
            self,
            cfg: Config,
            *,
            shell_cache: ta.Optional[ShellCache] = None,
            file_cache: ta.Optional[FileCache] = None,
    ) -> None:
        super().__init__()

        self._cfg = cfg
        self._shell_cache = shell_cache
        self._file_cache = file_cache

    #

    async def _load_cache_docker_image(self, key: str) -> ta.Optional[str]:
        if self._shell_cache is None:
            return None

        get_cache_cmd = self._shell_cache.get_file_cmd(key)
        if get_cache_cmd is None:
            return None

        get_cache_cmd = dc.replace(get_cache_cmd, s=f'{get_cache_cmd.s} | zstd -cd --long')  # noqa

        return await load_docker_tar_cmd(get_cache_cmd)

    async def _save_cache_docker_image(self, key: str, image: str) -> None:
        if self._shell_cache is None:
            return

        with self._shell_cache.put_file_cmd(key) as put_cache:
            put_cache_cmd = put_cache.cmd

            put_cache_cmd = dc.replace(put_cache_cmd, s=f'zstd | {put_cache_cmd.s}')

            await save_docker_tar_cmd(image, put_cache_cmd)

    #

    async def _load_docker_image(self, image: str) -> None:
        if not self._cfg.always_pull and (await is_docker_image_present(image)):
            return

        dep_suffix = image
        for c in '/:.-_':
            dep_suffix = dep_suffix.replace(c, '-')

        cache_key = f'docker-{dep_suffix}'
        if (await self._load_cache_docker_image(cache_key)) is not None:
            return

        await pull_docker_image(image)

        await self._save_cache_docker_image(cache_key, image)

    async def load_docker_image(self, image: str) -> None:
        with log_timing_context(f'Load docker image: {image}'):
            await self._load_docker_image(image)

    @async_cached_nullary
    async def load_compose_service_dependencies(self) -> None:
        deps = get_compose_service_dependencies(
            self._cfg.compose_file,
            self._cfg.service,
        )

        for dep_image in deps.values():
            await self.load_docker_image(dep_image)

    #

    @cached_nullary
    def docker_file_hash(self) -> str:
        return build_docker_file_hash(self._cfg.docker_file)[:self.FILE_NAME_HASH_LEN]

    async def _resolve_ci_image(self) -> str:
        cache_key = f'ci-{self.docker_file_hash()}'
        image_tag = f'{self._cfg.service}:{cache_key}'

        if not self._cfg.always_build and (await is_docker_image_present(image_tag)):
            return image_tag

        if (cache_image_id := await self._load_cache_docker_image(cache_key)) is not None:
            await tag_docker_image(
                cache_image_id,
                image_tag,
            )
            return image_tag

        image_id = await build_docker_image(
            self._cfg.docker_file,
            tag=image_tag,
            cwd=self._cfg.project_dir,
        )

        await self._save_cache_docker_image(cache_key, image_id)

        return image_tag

    @async_cached_nullary
    async def resolve_ci_image(self) -> str:
        with log_timing_context('Resolve ci image') as ltc:
            image_id = await self._resolve_ci_image()
            ltc.set_description(f'Resolve ci image: {image_id}')
            return image_id

    #

    @cached_nullary
    def requirements_txts(self) -> ta.Sequence[str]:
        return [
            os.path.join(self._cfg.project_dir, rf)
            for rf in check.not_none(self._cfg.requirements_txts)
        ]

    @cached_nullary
    def requirements_hash(self) -> str:
        return build_requirements_hash(self.requirements_txts())[:self.FILE_NAME_HASH_LEN]

    async def _resolve_requirements_dir(self) -> str:
        tar_file_key = f'requirements-{self.docker_file_hash()}-{self.requirements_hash()}'
        tar_file_name = f'{tar_file_key}.tar'

        temp_dir = tempfile.mkdtemp()
        self._enter_context(defer(lambda: shutil.rmtree(temp_dir)))  # noqa

        if self._file_cache is not None and (cache_tar_file := self._file_cache.get_file(tar_file_key)):
            with tarfile.open(cache_tar_file) as tar:
                tar.extractall(path=temp_dir)  # noqa

            return temp_dir

        temp_requirements_dir = os.path.join(temp_dir, 'requirements')
        os.makedirs(temp_requirements_dir)

        download_requirements(
            await self.resolve_ci_image(),
            temp_requirements_dir,
            self.requirements_txts(),
        )

        if self._file_cache is not None:
            temp_tar_file = os.path.join(temp_dir, tar_file_name)

            with tarfile.open(temp_tar_file, 'w') as tar:
                for requirement_file in os.listdir(temp_requirements_dir):
                    tar.add(
                        os.path.join(temp_requirements_dir, requirement_file),
                        arcname=requirement_file,
                    )

            self._file_cache.put_file(os.path.basename(tar_file_key), temp_tar_file)

        return temp_requirements_dir

    @async_cached_nullary
    async def resolve_requirements_dir(self) -> str:
        with log_timing_context('Resolve requirements dir') as ltc:
            requirements_dir = await self._resolve_requirements_dir()
            ltc.set_description(f'Resolve requirements dir: {requirements_dir}')
            return requirements_dir

    #

    async def _run_compose_(self) -> None:
        setup_cmds = [
            'pip install --root-user-action ignore --find-links /requirements --no-index uv',
            (
                'uv pip install --system --find-links /requirements ' +
                ' '.join(f'-r /project/{rf}' for rf in self._cfg.requirements_txts or [])
            ),
        ]

        #

        ci_cmd = dc.replace(self._cfg.cmd, s=' && '.join([
            *setup_cmds,
            f'({self._cfg.cmd.s})',
        ]))

        #

        async with DockerComposeRun(DockerComposeRun.Config(
            compose_file=self._cfg.compose_file,
            service=self._cfg.service,

            image=await self.resolve_ci_image(),

            cmd=ci_cmd,

            run_options=[
                '-v', f'{os.path.abspath(self._cfg.project_dir)}:/project',
                '-v', f'{os.path.abspath(await self.resolve_requirements_dir())}:/requirements',
            ],

            cwd=self._cfg.project_dir,

            no_dependencies=self._cfg.no_dependencies,
        )) as ci_compose_run:
            await ci_compose_run.run()

    async def _run_compose(self) -> None:
        with log_timing_context('Run compose'):
            await self._run_compose_()

    #

    async def run(self) -> None:
        await self.load_compose_service_dependencies()

        await self.resolve_ci_image()

        await self.resolve_requirements_dir()

        await self._run_compose()


########################################
# ../github/cli.py
"""
See:
 - https://docs.github.com/en/rest/actions/cache?apiVersion=2022-11-28
"""


class GithubCli(ArgparseCli):
    @argparse_cmd(
        argparse_arg('key'),
    )
    def get_cache_entry(self) -> None:
        shell_client = GithubCacheServiceV1ShellClient()
        entry = shell_client.run_get_entry(self.args.key)
        if entry is None:
            return
        print(json_dumps_pretty(dc.asdict(entry)))  # noqa

    @argparse_cmd(
        argparse_arg('repository-id'),
    )
    def list_cache_entries(self) -> None:
        raise NotImplementedError


########################################
# cli.py


class CiCli(ArgparseCli):
    #

    @argparse_cmd(
        argparse_arg('requirements-txt', nargs='+'),
    )
    def print_requirements_hash(self) -> None:
        requirements_txts = self.args.requirements_txt

        print(build_requirements_hash(requirements_txts))

    #

    @argparse_cmd(
        argparse_arg('compose-file'),
        argparse_arg('service'),
    )
    def dump_compose_deps(self) -> None:
        compose_file = self.args.compose_file
        service = self.args.service

        print(get_compose_service_dependencies(
            compose_file,
            service,
        ))

    #

    @argparse_cmd(
        accepts_unknown=True,
    )
    def github(self) -> ta.Optional[int]:
        return GithubCli(self.unknown_args).cli_run()

    #

    @argparse_cmd(
        argparse_arg('project-dir'),
        argparse_arg('service'),
        argparse_arg('--docker-file'),
        argparse_arg('--compose-file'),
        argparse_arg('-r', '--requirements-txt', action='append'),

        argparse_arg('--github-cache', action='store_true'),
        argparse_arg('--cache-dir'),

        argparse_arg('--always-pull', action='store_true'),
        argparse_arg('--always-build', action='store_true'),

        argparse_arg('--no-dependencies', action='store_true'),
    )
    async def run(self) -> None:
        project_dir = self.args.project_dir
        docker_file = self.args.docker_file
        compose_file = self.args.compose_file
        requirements_txts = self.args.requirements_txt
        cache_dir = self.args.cache_dir

        #

        check.state(os.path.isdir(project_dir))

        #

        def find_alt_file(*alts: str) -> ta.Optional[str]:
            for alt in alts:
                alt_file = os.path.abspath(os.path.join(project_dir, alt))
                if os.path.isfile(alt_file):
                    return alt_file
            return None

        if docker_file is None:
            docker_file = find_alt_file(
                'docker/ci/Dockerfile',
                'docker/ci.Dockerfile',
                'ci.Dockerfile',
                'Dockerfile',
            )
        check.state(os.path.isfile(docker_file))

        if compose_file is None:
            compose_file = find_alt_file(*[
                f'{f}.{x}'
                for f in [
                    'docker/docker-compose',
                    'docker/compose',
                    'docker-compose',
                    'compose',
                ]
                for x in ['yaml', 'yml']
            ])
        check.state(os.path.isfile(compose_file))

        if not requirements_txts:
            requirements_txts = []
            for rf in [
                'requirements.txt',
                'requirements-dev.txt',
                'requirements-ci.txt',
            ]:
                if os.path.exists(os.path.join(project_dir, rf)):
                    requirements_txts.append(rf)
        else:
            for rf in requirements_txts:
                check.state(os.path.isfile(rf))

        #

        shell_cache: ta.Optional[ShellCache] = None
        file_cache: ta.Optional[FileCache] = None
        if cache_dir is not None:
            if not os.path.exists(cache_dir):
                os.makedirs(cache_dir)
            check.state(os.path.isdir(cache_dir))

            directory_file_cache = DirectoryFileCache(cache_dir)

            file_cache = directory_file_cache

            if self.args.github_cache:
                shell_cache = GithubShellCache(cache_dir)
            else:
                shell_cache = DirectoryShellCache(directory_file_cache)

        #

        async with Ci(
                Ci.Config(
                    project_dir=project_dir,

                    docker_file=docker_file,

                    compose_file=compose_file,
                    service=self.args.service,

                    requirements_txts=requirements_txts,

                    cmd=ShellCmd(' && '.join([
                        'cd /project',
                        'python3 -m pytest -svv test.py',
                    ])),

                    always_pull=self.args.always_pull,
                    always_build=self.args.always_build,

                    no_dependencies=self.args.no_dependencies,
                ),
                file_cache=file_cache,
                shell_cache=shell_cache,
        ) as ci:
            await ci.run()


async def _async_main() -> ta.Optional[int]:
    return await CiCli().async_cli_run()


def _main() -> None:
    configure_standard_logging('DEBUG')

    sys.exit(rc if isinstance(rc := asyncio.run(_async_main()), int) else 0)


if __name__ == '__main__':
    _main()
