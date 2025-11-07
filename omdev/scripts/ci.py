#!/usr/bin/env python3
# noinspection DuplicatedCode
# @omlish-lite
# @omlish-script
# @omlish-generated
# @omlish-amalg-output ../ci/cli.py
# @omlish-git-diff-omit
# ruff: noqa: N802 TC003 UP006 UP007 UP036 UP043 UP045 UP046
"""
Inputs:
 - requirements.txt
 - ci.Dockerfile
 - compose.yml

==

./python -m omdev.ci run --cache-dir omdev/ci/tests/cache omdev/ci/tests/project omlish-ci
"""
import abc
import argparse
import asyncio
import asyncio.base_subprocess
import asyncio.subprocess
import base64
import collections
import collections.abc
import concurrent.futures as cf
import contextlib
import contextvars
import copy
import dataclasses as dc
import datetime
import decimal
import email.utils
import enum
import errno
import fcntl
import fractions
import functools
import gzip
import hashlib
import heapq
import html
import http
import http.client
import http.server
import inspect
import io
import itertools
import json
import logging
import operator
import os
import os.path
import re
import selectors
import shlex
import shutil
import socket
import socket as socket_
import ssl
import stat
import subprocess
import sys
import tarfile
import tempfile
import textwrap
import threading
import time
import traceback
import types
import typing as ta
import urllib.parse
import urllib.request
import uuid
import weakref
import xml.etree.ElementTree as ET


########################################


if sys.version_info < (3, 8):
    raise OSError(f'Requires python (3, 8), got {sys.version_info} from {sys.executable}')  # noqa


########################################


# shell.py
T = ta.TypeVar('T')

# ../../omlish/asyncs/asyncio/utils.py
CallableT = ta.TypeVar('CallableT', bound=ta.Callable)

# ../../omlish/lite/check.py
SizedT = ta.TypeVar('SizedT', bound=ta.Sized)
CheckMessage = ta.Union[str, ta.Callable[..., ta.Optional[str]], None]  # ta.TypeAlias
CheckLateConfigureFn = ta.Callable[['Checks'], None]  # ta.TypeAlias
CheckOnRaiseFn = ta.Callable[[Exception], None]  # ta.TypeAlias
CheckExceptionFactory = ta.Callable[..., Exception]  # ta.TypeAlias
CheckArgsRenderer = ta.Callable[..., ta.Optional[str]]  # ta.TypeAlias

# ../../omlish/lite/contextmanagers.py
ExitStackedT = ta.TypeVar('ExitStackedT', bound='ExitStacked')
AsyncExitStackedT = ta.TypeVar('AsyncExitStackedT', bound='AsyncExitStacked')

# ../../omlish/logs/levels.py
LogLevel = int  # ta.TypeAlias

# ../../omlish/sockets/addresses.py
SocketAddress = ta.Any  # ta.TypeAlias

# github/api/v2/api.py
GithubCacheServiceV2RequestT = ta.TypeVar('GithubCacheServiceV2RequestT')
GithubCacheServiceV2ResponseT = ta.TypeVar('GithubCacheServiceV2ResponseT')

# ../../omlish/argparse/cli.py
ArgparseCmdFn = ta.Callable[[], ta.Optional[int]]  # ta.TypeAlias

# ../../omlish/http/parsing.py
HttpHeaders = http.client.HTTPMessage  # ta.TypeAlias

# ../../omlish/lite/maybes.py
U = ta.TypeVar('U')

# ../../omlish/lite/timeouts.py
TimeoutLike = ta.Union['Timeout', ta.Type['Timeout.DEFAULT'], ta.Iterable['TimeoutLike'], float, None]  # ta.TypeAlias

# ../../omlish/logs/infos.py
LoggingMsgFn = ta.Callable[[], ta.Union[str, tuple]]  # ta.TypeAlias
LoggingExcInfoTuple = ta.Tuple[ta.Type[BaseException], BaseException, ta.Optional[types.TracebackType]]  # ta.TypeAlias
LoggingExcInfo = ta.Union[BaseException, LoggingExcInfoTuple]  # ta.TypeAlias
LoggingExcInfoArg = ta.Union[LoggingExcInfo, bool, None]  # ta.TypeAlias
LoggingContextInfo = ta.Any  # ta.TypeAlias

# ../../omlish/sockets/bind.py
SocketBinderT = ta.TypeVar('SocketBinderT', bound='SocketBinder')
SocketBinderConfigT = ta.TypeVar('SocketBinderConfigT', bound='SocketBinder.Config')
CanSocketBinderConfig = ta.Union['SocketBinder.Config', int, ta.Tuple[str, int], str]  # ta.TypeAlias
CanSocketBinder = ta.Union['SocketBinder', CanSocketBinderConfig]  # ta.TypeAlias

# ../../omlish/sockets/handlers.py
SocketHandler = ta.Callable[[SocketAddress, 'SocketIoPair'], None]  # ta.TypeAlias

# ../../omlish/asyncs/asyncio/timeouts.py
AwaitableT = ta.TypeVar('AwaitableT', bound=ta.Awaitable)

# ../../omlish/http/handlers.py
HttpHandler = ta.Callable[['HttpHandlerRequest'], 'HttpHandlerResponse']  # ta.TypeAlias
HttpHandlerResponseData = ta.Union[bytes, 'HttpHandlerResponseStreamedData']  # ta.TypeAlias  # noqa

# ../../omlish/lite/inject.py
InjectorKeyCls = ta.Union[type, ta.NewType]  # ta.TypeAlias
InjectorProviderFn = ta.Callable[['Injector'], ta.Any]  # ta.TypeAlias
InjectorProviderFnMap = ta.Mapping['InjectorKey', 'InjectorProviderFn']  # ta.TypeAlias
InjectorBindingOrBindings = ta.Union['InjectorBinding', 'InjectorBindings']  # ta.TypeAlias

# ../../omlish/logs/contexts.py
LoggingContextInfoT = ta.TypeVar('LoggingContextInfoT', bound=LoggingContextInfo)

# ../../omlish/sockets/server/handlers.py
SocketServerHandler = ta.Callable[['SocketAndAddress'], None]  # ta.TypeAlias

# ../dataserver/handlers.py
DataServerTargetT = ta.TypeVar('DataServerTargetT', bound='DataServerTarget')

# ../../omlish/http/coro/server/server.py
CoroHttpServerFactory = ta.Callable[[SocketAddress], 'CoroHttpServer']  # ta.TypeAlias

# ../../omlish/subprocesses/base.py
SubprocessChannelOption = ta.Literal['pipe', 'stdout', 'devnull']  # ta.TypeAlias

# ../oci/building.py
OciMediaDataclassT = ta.TypeVar('OciMediaDataclassT', bound='OciMediaDataclass')


########################################
# ../consts.py


CI_CACHE_VERSION = 2


########################################
# ../github/env.py


##


@dc.dataclass(frozen=True)
class GithubEnvVar:
    k: str

    def __call__(self) -> ta.Optional[str]:
        return os.environ.get(self.k)


GITHUB_ENV_VARS: ta.Set[GithubEnvVar] = set()


def register_github_env_var(k: str) -> GithubEnvVar:
    ev = GithubEnvVar(k)
    GITHUB_ENV_VARS.add(ev)
    return ev


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
# ../utils.py


##


def read_yaml_file(yaml_file: str) -> ta.Any:
    import yaml  # noqa

    with open(yaml_file) as f:
        return yaml.safe_load(f)


##


def sha256_str(s: str) -> str:
    return hashlib.sha256(s.encode('utf-8')).hexdigest()


########################################
# ../../oci/compression.py


##


class OciCompression(enum.Enum):
    GZIP = enum.auto()
    ZSTD = enum.auto()


########################################
# ../../../omlish/asyncs/asyncio/utils.py
"""
TODO:
 - split module
"""


##


def asyncio_ensure_task(obj: ta.Awaitable) -> asyncio.Task:
    if isinstance(obj, asyncio.Task):
        return obj
    elif isinstance(obj, ta.Coroutine):
        return asyncio.create_task(obj)
    else:
        raise TypeError(obj)


##


def asyncio_once(fn: CallableT) -> CallableT:
    task = None

    @functools.wraps(fn)
    async def inner(*args, **kwargs):
        nonlocal task
        if not task:
            task = asyncio.create_task(fn(*args, **kwargs))
        return await task

    return ta.cast(CallableT, inner)


##


def drain_asyncio_tasks(loop=None):
    if loop is None:
        loop = asyncio.get_running_loop()

    while loop._ready or loop._scheduled:  # noqa
        loop._run_once()  # noqa


@contextlib.contextmanager
def draining_asyncio_tasks() -> ta.Iterator[None]:
    loop = asyncio.get_running_loop()
    try:
        yield
    finally:
        if loop is not None:
            drain_asyncio_tasks(loop)  # noqa


##


async def asyncio_wait_concurrent(
        awaitables: ta.Iterable[ta.Awaitable[T]],
        concurrency: ta.Union[int, asyncio.Semaphore],
        *,
        return_when: ta.Any = asyncio.FIRST_EXCEPTION,
) -> ta.List[T]:
    if isinstance(concurrency, asyncio.Semaphore):
        semaphore = concurrency
    elif isinstance(concurrency, int):
        semaphore = asyncio.Semaphore(concurrency)
    else:
        raise TypeError(concurrency)

    async def limited_task(a):
        async with semaphore:
            return await a

    futs = [asyncio.create_task(limited_task(a)) for a in awaitables]
    done, pending = await asyncio.wait(futs, return_when=return_when)

    for fut in pending:
        fut.cancel()

    for fut in done:
        if fut.exception():
            raise fut.exception()  # type: ignore

    return [fut.result() for fut in done]


async def asyncio_wait_maybe_concurrent(
        awaitables: ta.Iterable[ta.Awaitable[T]],
        concurrency: ta.Union[int, asyncio.Semaphore, None],
) -> ta.List[T]:
    # Note: Only supports return_when=asyncio.FIRST_EXCEPTION
    if concurrency is None:
        return [await a for a in awaitables]

    else:
        return await asyncio_wait_concurrent(awaitables, concurrency)


########################################
# ../../../omlish/docker/ports.py
"""
TODO:
 - docstring
 - timebomb
 - auto-discover available ports
"""


##


@dc.dataclass(frozen=True)
class DockerPortRelay:
    """
    Uses roughly the following command to forward connections from inside docker-for-mac's vm to the mac host:

      docker run --rm -i -p 5001:5000 alpine/socat -d -d TCP-LISTEN:5000,fork,reuseaddr TCP:host.docker.internal:5021

    This allows requests made by the docker daemon running inside the vm to `host.docker.internal:5001` to be forwarded
    to the mac host on port 5021. The reason for this is to be able to use a docker registry running locally directly on
    the host mac - specifically to be able to do so with ssl certificate checking disabled (which docker will only do on
    localhost, which on a mac in the vm isn't actually the mac host - hence the necessity of the relay).
    """

    docker_port: int  # port
    host_port: int

    name: ta.Optional[str] = None

    DEFAULT_HOST_NAME: ta.ClassVar[str] = 'host.docker.internal'
    host_name: str = DEFAULT_HOST_NAME

    DEFAULT_INTERMEDIATE_PORT: ta.ClassVar[int] = 5000
    intermediate_port: int = DEFAULT_INTERMEDIATE_PORT

    DEFAULT_IMAGE: ta.ClassVar[str] = 'alpine/socat'
    image: str = DEFAULT_IMAGE

    def socat_args(self) -> ta.List[str]:
        return [
            '-d',
            f'TCP-LISTEN:{self.intermediate_port},fork,reuseaddr',
            f'TCP:{self.host_name}:{self.host_port}',
        ]

    def run_args(self) -> ta.List[str]:
        if (name := self.name) is None:
            name = f'docker_port_relay-{os.getpid()}-{self.docker_port}-{self.intermediate_port}-{self.host_port}'

        return [
            '--name', name,
            '--rm',
            '-p', f'{self.docker_port}:{self.intermediate_port}',
            self.image,
            *self.socat_args(),
        ]

    def run_cmd(self) -> ta.List[str]:
        return [
            'docker',
            'run',
            '-i',
            *self.run_args(),
        ]


########################################
# ../../../omlish/http/urllib.py


##


class NonRaisingUrllibErrorProcessor(urllib.request.HTTPErrorProcessor):
    """
    https://stackoverflow.com/a/74844056

    Usage:

        opener = urllib.request.build_opener(NonRaisingUrllibErrorProcessor)
        with opener.open(req) as resp:
            ...
    """

    def http_response(self, request, response):
        return response

    def https_response(self, request, response):
        return response


########################################
# ../../../omlish/http/versions.py


##


class HttpProtocolVersion(ta.NamedTuple):
    major: int
    minor: int

    def __str__(self) -> str:
        return f'HTTP/{self.major}.{self.minor}'


class HttpProtocolVersions:
    HTTP_0_9 = HttpProtocolVersion(0, 9)
    HTTP_1_0 = HttpProtocolVersion(1, 0)
    HTTP_1_1 = HttpProtocolVersion(1, 1)
    HTTP_2_0 = HttpProtocolVersion(2, 0)


########################################
# ../../../omlish/lite/abstract.py


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

    def __get__(self, instance, owner=None):  # noqa
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


##


cached_property = functools.cached_property


class _cached_property:  # noqa
    """Backported to pick up https://github.com/python/cpython/commit/056dfc71dce15f81887f0bd6da09d6099d71f979 ."""

    def __init__(self, func):
        self.func = func
        self.attrname = None  # noqa
        self.__doc__ = func.__doc__
        self.__module__ = func.__module__

    _NOT_FOUND = object()

    def __set_name__(self, owner, name):
        if self.attrname is None:
            self.attrname = name  # noqa
        elif name != self.attrname:
            raise TypeError(
                f'Cannot assign the same cached_property to two different names ({self.attrname!r} and {name!r}).',
            )

    def __get__(self, instance, owner=None):
        if instance is None:
            return self
        if self.attrname is None:
            raise TypeError('Cannot use cached_property instance without calling __set_name__ on it.')

        try:
            cache = instance.__dict__
        except AttributeError:  # not all objects have __dict__ (e.g. class defines slots)
            raise TypeError(
                f"No '__dict__' attribute on {type(instance).__name__!r} instance to cache {self.attrname!r} property.",
            ) from None

        val = cache.get(self.attrname, self._NOT_FOUND)

        if val is self._NOT_FOUND:
            val = self.func(instance)
            try:
                cache[self.attrname] = val
            except TypeError:
                raise TypeError(
                    f"The '__dict__' attribute on {type(instance).__name__!r} instance does not support item "
                    f"assignment for caching {self.attrname!r} property.",
                ) from None

        return val


globals()['cached_property'] = _cached_property


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

    @ta.overload
    def isinstance(self, v: ta.Any, spec: ta.Type[T], msg: CheckMessage = None) -> T:
        ...

    @ta.overload
    def isinstance(self, v: ta.Any, spec: ta.Any, msg: CheckMessage = None) -> ta.Any:
        ...

    def isinstance(self, v, spec, msg=None):
        if not isinstance(v, self._unpack_isinstance_spec(spec)):
            self._raise(
                TypeError,
                'Must be instance',
                msg,
                Checks._ArgsKwargs(v, spec),
                render_fmt='not isinstance(%s, %s)',
            )

        return v

    @ta.overload
    def of_isinstance(self, spec: ta.Type[T], msg: CheckMessage = None) -> ta.Callable[[ta.Any], T]:
        ...

    @ta.overload
    def of_isinstance(self, spec: ta.Any, msg: CheckMessage = None) -> ta.Callable[[ta.Any], ta.Any]:
        ...

    def of_isinstance(self, spec, msg=None):
        def inner(v):
            return self.isinstance(v, self._unpack_isinstance_spec(spec), msg)

        return inner

    def cast(self, v: ta.Any, cls: ta.Type[T], msg: CheckMessage = None) -> T:
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

    def not_issubclass(self, v: ta.Type[T], spec: ta.Any, msg: CheckMessage = None) -> ta.Type[T]:
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

    def single(self, obj: ta.Iterable[T], msg: CheckMessage = None) -> T:
        try:
            [value] = obj
        except ValueError:
            self._raise(
                ValueError,
                'Must be single',
                msg,
                Checks._ArgsKwargs(obj),
                render_fmt='%s',
            )

        return value

    def opt_single(self, obj: ta.Iterable[T], msg: CheckMessage = None) -> ta.Optional[T]:
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
            msg,
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

        return v

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
# ../../../omlish/lite/contextmanagers.py


##


class ExitStacked:
    def __init_subclass__(cls, **kwargs: ta.Any) -> None:
        super().__init_subclass__(**kwargs)

        for a in ('__enter__', '__exit__'):
            for b in cls.__bases__:
                if b is ExitStacked:
                    continue
                try:
                    fn = getattr(b, a)
                except AttributeError:
                    pass
                else:
                    if fn is not getattr(ExitStacked, a):
                        raise TypeError(f'ExitStacked subclass {cls} must not not override {a} via {b}')

    _exit_stack: ta.Optional[contextlib.ExitStack] = None

    @contextlib.contextmanager
    def _exit_stacked_init_wrapper(self) -> ta.Iterator[None]:
        """
        Overridable wrapper around __enter__ which deliberately does not have access to an _exit_stack yet. Intended for
        things like wrapping __enter__ in a lock.
        """

        yield

    @ta.final
    def __enter__(self: ExitStackedT) -> ExitStackedT:
        """
        Final because any contexts entered during this init must be exited if any exception is thrown, and user
        overriding would likely interfere with that. Override `_enter_contexts` for such init.
        """

        with self._exit_stacked_init_wrapper():
            if self._exit_stack is not None:
                raise RuntimeError
            es = self._exit_stack = contextlib.ExitStack()
            es.__enter__()
            try:
                self._enter_contexts()
            except BaseException:  # noqa
                es.__exit__(*sys.exc_info())
                raise
            return self

    @ta.final
    def __exit__(self, exc_type, exc_val, exc_tb):
        if (es := self._exit_stack) is None:
            return None
        try:
            self._exit_contexts()
        except BaseException:  # noqa
            es.__exit__(*sys.exc_info())
            raise
        return es.__exit__(exc_type, exc_val, exc_tb)

    def _enter_contexts(self) -> None:
        pass

    def _exit_contexts(self) -> None:
        pass

    def _enter_context(self, cm: ta.ContextManager[T]) -> T:
        if (es := self._exit_stack) is None:
            raise RuntimeError
        return es.enter_context(cm)


class AsyncExitStacked:
    def __init_subclass__(cls, **kwargs: ta.Any) -> None:
        super().__init_subclass__(**kwargs)

        for a in ('__aenter__', '__aexit__'):
            for b in cls.__bases__:
                if b is AsyncExitStacked:
                    continue
                try:
                    fn = getattr(b, a)
                except AttributeError:
                    pass
                else:
                    if fn is not getattr(AsyncExitStacked, a):
                        raise TypeError(f'AsyncExitStacked subclass {cls} must not not override {a} via {b}')

    _exit_stack: ta.Optional[contextlib.AsyncExitStack] = None

    @contextlib.asynccontextmanager
    async def _async_exit_stacked_init_wrapper(self) -> ta.AsyncGenerator[None, None]:
        yield

    @ta.final
    async def __aenter__(self: AsyncExitStackedT) -> AsyncExitStackedT:
        async with self._async_exit_stacked_init_wrapper():
            if self._exit_stack is not None:
                raise RuntimeError
            es = self._exit_stack = contextlib.AsyncExitStack()
            await es.__aenter__()
            try:
                await self._async_enter_contexts()
            except BaseException:  # noqa
                await es.__aexit__(*sys.exc_info())
                raise
            return self

    @ta.final
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if (es := self._exit_stack) is None:
            return None
        try:
            await self._async_exit_contexts()
        except BaseException:  # noqa
            await es.__aexit__(*sys.exc_info())
            raise
        return await es.__aexit__(exc_type, exc_val, exc_tb)

    async def _async_enter_contexts(self) -> None:
        pass

    async def _async_exit_contexts(self) -> None:
        pass

    def _enter_context(self, cm: ta.ContextManager[T]) -> T:
        if (es := self._exit_stack) is None:
            raise RuntimeError
        return es.enter_context(cm)

    async def _enter_async_context(self, cm: ta.AsyncContextManager[T]) -> T:
        if (es := self._exit_stack) is None:
            raise RuntimeError
        return await es.enter_async_context(cm)


##


@contextlib.contextmanager
def defer(fn: ta.Callable, *args: ta.Any, **kwargs: ta.Any) -> ta.Generator[ta.Callable, None, None]:
    if args or kwargs:
        fn = functools.partial(fn, *args, **kwargs)
    try:
        yield fn
    finally:
        fn()


@contextlib.asynccontextmanager
async def adefer(fn: ta.Awaitable) -> ta.AsyncGenerator[ta.Awaitable, None]:
    try:
        yield fn
    finally:
        await fn


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


class AsyncClosingManager(contextlib.AbstractAsyncContextManager):
    def __init__(self, thing):
        self.thing = thing

    async def __aenter__(self):
        return self.thing

    async def __aexit__(self, *exc_info):
        await self.thing.aclose()


aclosing = AsyncClosingManager


########################################
# ../../../omlish/lite/dataclasses.py


##


def dataclass_shallow_astuple(o: ta.Any) -> ta.Tuple[ta.Any, ...]:
    return tuple(getattr(o, f.name) for f in dc.fields(o))


def dataclass_shallow_asdict(o: ta.Any) -> ta.Dict[str, ta.Any]:
    return {f.name: getattr(o, f.name) for f in dc.fields(o)}


##


def is_immediate_dataclass(cls: type) -> bool:
    if not isinstance(cls, type):
        raise TypeError(cls)
    return dc._FIELDS in cls.__dict__  # type: ignore[attr-defined]  # noqa


##


def dataclass_cache_hash(
        *,
        cached_hash_attr: str = '__dataclass_hash__',
):
    def inner(cls):
        if not isinstance(cls, type) and dc.is_dataclass(cls):
            raise TypeError(cls)

        if (
                cls.__hash__ is object.__hash__ or
                '__hash__' not in cls.__dict__
        ):
            raise TypeError(cls)

        real_hash = cls.__hash__

        def cached_hash(self) -> int:
            try:
                return object.__getattribute__(self, cached_hash_attr)
            except AttributeError:
                object.__setattr__(self, cached_hash_attr, h := real_hash(self))  # type: ignore[call-arg]
            return h

        cls.__hash__ = cached_hash  # type: ignore[method-assign]

        return cls

    return inner


##


def dataclass_maybe_post_init(sup: ta.Any) -> bool:
    if not isinstance(sup, super):
        raise TypeError(sup)
    try:
        fn = sup.__post_init__  # type: ignore
    except AttributeError:
        return False
    fn()
    return True


##


def dataclass_repr_filtered(
        obj: ta.Any,
        fn: ta.Callable[[ta.Any, dc.Field, ta.Any], bool],
) -> str:
    return (
        f'{obj.__class__.__qualname__}(' +
        ', '.join([
            f'{f.name}={v!r}'
            for f in dc.fields(obj)
            if fn(obj, f, v := getattr(obj, f.name))
        ]) +
        ')'
    )


def dataclass_repr_omit_none(obj: ta.Any) -> str:
    return dataclass_repr_filtered(obj, lambda o, f, v: v is not None)


def dataclass_repr_omit_falsey(obj: ta.Any) -> str:
    return dataclass_repr_filtered(obj, lambda o, f, v: bool(v))


##


def dataclass_descriptor_method(*bind_attrs: str, bind_owner: bool = False) -> ta.Callable:
    if not bind_attrs:
        def __get__(self, instance, owner=None):  # noqa
            return self

    elif bind_owner:
        def __get__(self, instance, owner=None):  # noqa
            # Guaranteed to return a new instance even with no attrs
            return dc.replace(self, **{
                a: v.__get__(instance, owner) if (v := getattr(self, a)) is not None else None
                for a in bind_attrs
            })

    else:
        def __get__(self, instance, owner=None):  # noqa
            if instance is None:
                return self

            # Guaranteed to return a new instance even with no attrs
            return dc.replace(self, **{
                a: v.__get__(instance, owner) if (v := getattr(self, a)) is not None else None
                for a in bind_attrs
            })

    return __get__


##


def dataclass_kw_only_init():
    def inner(cls):
        if not isinstance(cls, type) and dc.is_dataclass(cls):
            raise TypeError(cls)

        real_init = cls.__init__  # type: ignore[misc]

        flds = dc.fields(cls)  # noqa

        if any(f.name == 'self' for f in flds):
            self_name = '__dataclass_self__'
        else:
            self_name = 'self'

        src = '\n'.join([
            'def __init__(',
            f'    {self_name},',
            '    *,',
            *[
                ''.join([
                    f'    {f.name}: __dataclass_type_{f.name}__',
                    f' = __dataclass_default_{f.name}__' if f.default is not dc.MISSING else '',
                    ',',
                ])
                for f in flds
            ],
            ') -> __dataclass_None__:',
            '    __dataclass_real_init__(',
            f'        {self_name},',
            *[
                f'        {f.name}={f.name},'
                for f in flds
            ],
            '    )',
        ])

        ns: dict = {
            '__dataclass_None__': None,
            '__dataclass_real_init__': real_init,
            **{
                f'__dataclass_type_{f.name}__': f.type
                for f in flds
            },
            **{
                f'__dataclass_default_{f.name}__': f.default
                for f in flds
                if f.default is not dc.MISSING
            },
        }

        exec(src, ns)

        kw_only_init = ns['__init__']

        functools.update_wrapper(kw_only_init, real_init)

        cls.__init__ = kw_only_init  # type: ignore[misc]

        return cls

    return inner


##


@dc.dataclass()
class DataclassFieldRequiredError(Exception):
    name: str


def dataclass_field_required(name: str) -> ta.Callable[[], ta.Any]:
    def inner() -> ta.NoReturn:
        raise DataclassFieldRequiredError(name)
    return inner


########################################
# ../../../omlish/lite/json.py


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
# ../../../omlish/lite/objects.py


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


##


def mro_owner_dict(
        instance_cls: type,
        owner_cls: ta.Optional[type] = None,
        *,
        bottom_up_key_order: bool = False,
        sort_keys: bool = False,
) -> ta.Mapping[str, ta.Tuple[type, ta.Any]]:
    if owner_cls is None:
        owner_cls = instance_cls

    mro = instance_cls.__mro__[-2::-1]
    try:
        pos = mro.index(owner_cls)
    except ValueError:
        raise TypeError(f'Owner class {owner_cls} not in mro of instance class {instance_cls}') from None

    dct: ta.Dict[str, ta.Tuple[type, ta.Any]] = {}
    if not bottom_up_key_order:
        for cur_cls in mro[:pos + 1][::-1]:
            for k, v in cur_cls.__dict__.items():
                if k not in dct:
                    dct[k] = (cur_cls, v)

    else:
        for cur_cls in mro[:pos + 1]:
            dct.update({k: (cur_cls, v) for k, v in cur_cls.__dict__.items()})

    if sort_keys:
        dct = dict(sorted(dct.items(), key=lambda t: t[0]))

    return dct


def mro_dict(
        instance_cls: type,
        owner_cls: ta.Optional[type] = None,
        *,
        bottom_up_key_order: bool = False,
        sort_keys: bool = False,
) -> ta.Mapping[str, ta.Any]:
    return {
        k: v
        for k, (o, v) in mro_owner_dict(
            instance_cls,
            owner_cls,
            bottom_up_key_order=bottom_up_key_order,
            sort_keys=sort_keys,
        ).items()
    }


def dir_dict(o: ta.Any) -> ta.Dict[str, ta.Any]:
    return {
        a: getattr(o, a)
        for a in dir(o)
    }


########################################
# ../../../omlish/lite/reflect.py


##


_GENERIC_ALIAS_TYPES = (
    ta._GenericAlias,  # type: ignore  # noqa
    *([ta._SpecialGenericAlias] if hasattr(ta, '_SpecialGenericAlias') else []),  # noqa
)


def is_generic_alias(obj: ta.Any, *, origin: ta.Any = None) -> bool:
    return (
        isinstance(obj, _GENERIC_ALIAS_TYPES) and
        (origin is None or ta.get_origin(obj) is origin)
    )


is_callable_alias = functools.partial(is_generic_alias, origin=ta.Callable)


##


_UNION_ALIAS_ORIGINS = frozenset([
    ta.get_origin(ta.Optional[int]),
    *(
        [
            ta.get_origin(int | None),
            ta.get_origin(getattr(ta, 'TypeVar')('_T') | None),
        ] if sys.version_info >= (3, 10) else ()
    ),
])


def is_union_alias(obj: ta.Any) -> bool:
    return ta.get_origin(obj) in _UNION_ALIAS_ORIGINS


#


def is_optional_alias(spec: ta.Any) -> bool:
    return (
        is_union_alias(spec) and
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
# ../../../omlish/logs/levels.py


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
# ../../../omlish/logs/std/filters.py


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
# ../../../omlish/logs/std/proxy.py


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
# ../../../omlish/logs/warnings.py


##


class LoggingSetupWarning(Warning):
    pass


########################################
# ../../../omlish/os/files.py


##


def is_fd_open(fd: int) -> bool:
    try:
        fcntl.fcntl(fd, fcntl.F_GETFD)
    except OSError as e:
        if e.errno == errno.EBADF:
            return False
        raise
    else:
        return True


def touch(path: str, mode: int = 0o666, exist_ok: bool = True) -> None:
    if exist_ok:
        # First try to bump modification time
        # Implementation note: GNU touch uses the UTIME_NOW option of the utimensat() / futimens() functions.
        try:
            os.utime(path, None)
        except OSError:
            pass
        else:
            return

    flags = os.O_CREAT | os.O_WRONLY
    if not exist_ok:
        flags |= os.O_EXCL

    fd = os.open(path, flags, mode)
    os.close(fd)


def unlink_if_exists(path: str) -> None:
    try:
        os.unlink(path)
    except FileNotFoundError:
        pass


@contextlib.contextmanager
def unlinking_if_exists(path: str) -> ta.Iterator[None]:
    try:
        yield
    finally:
        unlink_if_exists(path)


########################################
# ../../../omlish/os/paths.py


##


@ta.overload
def path_dirname(p: str, n: int = 1) -> str:
    ...


@ta.overload
def path_dirname(p: bytes, n: int = 1) -> bytes:
    ...


def path_dirname(p, n=1):
    if isinstance(p, bytes):
        sep: ta.Any = b'/'
    else:
        sep = '/'
    p = os.fspath(p)
    i = -1
    for _ in range(n):
        i = p.rindex(sep, 0, i)
    head = p[:i + 1]
    if head and head != sep * len(head):
        head = head.rstrip(sep)
    return head


def abs_real_path(p: str) -> str:
    return os.path.abspath(os.path.realpath(p))


def is_path_in_dir(base_dir: str, target_path: str) -> bool:
    base_dir = abs_real_path(base_dir)
    target_path = abs_real_path(target_path)

    return target_path.startswith(base_dir + os.path.sep)


def relative_symlink(
        src: str,
        dst: str,
        *,
        target_is_directory: bool = False,
        dir_fd: ta.Optional[int] = None,
        make_dirs: bool = False,
        **kwargs: ta.Any,
) -> None:
    if make_dirs:
        os.makedirs(os.path.dirname(dst), exist_ok=True)

    os.symlink(
        os.path.relpath(src, os.path.dirname(dst)),
        dst,
        target_is_directory=target_is_directory,
        dir_fd=dir_fd,
        **kwargs,
    )


########################################
# ../../../omlish/secrets/ssl.py


##


@dc.dataclass(frozen=True)
class SslCert:
    key_file: str
    cert_file: str


########################################
# ../../../omlish/sockets/addresses.py
"""
TODO:
 - codification of https://docs.python.org/3/library/socket.html#socket-families
"""


##


@dc.dataclass(frozen=True)
class SocketAddressInfoArgs:
    host: ta.Optional[str]
    port: ta.Union[str, int, None]
    family: socket_.AddressFamily = socket_.AddressFamily.AF_UNSPEC
    type: int = 0
    proto: int = 0
    flags: socket_.AddressInfo = socket_.AddressInfo(0)


@dc.dataclass(frozen=True)
class SocketAddressInfo:
    family: socket_.AddressFamily
    type: int
    proto: int
    canonname: ta.Optional[str]
    sockaddr: SocketAddress


class SocketFamilyAndAddress(ta.NamedTuple):
    family: socket_.AddressFamily
    address: SocketAddress


def get_best_socket_family(
        host: ta.Optional[str],
        port: ta.Union[str, int, None],
        family: ta.Union[int, socket_.AddressFamily] = socket_.AddressFamily.AF_UNSPEC,
) -> SocketFamilyAndAddress:
    """https://github.com/python/cpython/commit/f289084c83190cc72db4a70c58f007ec62e75247"""

    infos = socket_.getaddrinfo(
        host,
        port,
        family,
        type=socket_.SOCK_STREAM,
        flags=socket_.AI_PASSIVE,
    )
    ai = SocketAddressInfo(*next(iter(infos)))
    return SocketFamilyAndAddress(ai.family, ai.sockaddr)


class SocketAndAddress(ta.NamedTuple):
    socket: socket_.socket
    address: SocketAddress

    def wrap_socket(self, fn: ta.Callable[[socket_.socket], socket_.socket]):
        return self._replace(socket=fn(self.socket))

    @classmethod
    def socket_wrapper(
            cls,
            fn: ta.Callable[[socket_.socket], socket_.socket],
    ) -> ta.Callable[['SocketAndAddress'], 'SocketAndAddress']:
        def inner(conn):
            return conn.wrap_socket(fn)
        return inner


########################################
# ../../../omlish/sockets/io.py


##


class SocketWriter(io.BufferedIOBase):
    """
    Simple writable BufferedIOBase implementation for a socket

    Does not hold data in a buffer, avoiding any need to call flush().
    """

    def __init__(self, sock):
        super().__init__()

        self._sock = sock

    def writable(self):
        return True

    def write(self, b):
        self._sock.sendall(b)
        with memoryview(b) as view:
            return view.nbytes

    def fileno(self):
        return self._sock.fileno()


class SocketIoPair(ta.NamedTuple):
    r: ta.BinaryIO
    w: ta.BinaryIO

    @classmethod
    def from_socket(
            cls,
            sock: socket.socket,
            *,
            r_buf_size: int = -1,
            w_buf_size: int = 0,
    ) -> 'SocketIoPair':
        rf: ta.Any = sock.makefile('rb', r_buf_size)

        if w_buf_size:
            wf: ta.Any = SocketWriter(sock)
        else:
            wf = sock.makefile('wb', w_buf_size)

        return cls(rf, wf)


##


def close_socket_immediately(sock: socket.socket) -> None:
    try:
        # Explicitly shutdown. socket.close() merely releases the socket and waits for GC to perform the actual close.
        sock.shutdown(socket.SHUT_WR)

    except OSError:
        # Some platforms may raise ENOTCONN here
        pass

    sock.close()


########################################
# ../docker/utils.py
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


########################################
# ../github/api/v1/api.py
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
    def __new__(cls, *args, **kwargs):  # noqa
        raise TypeError

    #

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


########################################
# ../github/api/v2/api.py
"""
https://github.com/tonistiigi/go-actions-cache/blob/3e9a6642607fd6e4d5d4fdab7c91fe8bf4c36a25/cache_v2.go

==

curl -s \
  -X POST \
  "${ACTIONS_RESULTS_URL}twirp/github.actions.results.api.v1.CacheService/CreateCacheEntry" \
  -H 'Content-Type: application/json' \
  -H "Authorization: Bearer $ACTIONS_RUNTIME_TOKEN" \
  -d '{"key": "foo", "version": "0000000000000000000000000000000000000000000000000000000000000001" }' \
  | jq .

curl -s \
  -X POST \
  "${ACTIONS_RESULTS_URL}twirp/github.actions.results.api.v1.CacheService/GetCacheEntryDownloadURL" \
  -H 'Content-Type: application/json' \
  -H "Authorization: Bearer $ACTIONS_RUNTIME_TOKEN" \
  -d '{"key": "foo", "restoreKeys": [], "version": "0000000000000000000000000000000000000000000000000000000000000001" }' \
  | jq .

"""  # noqa


##


class GithubCacheServiceV2:
    def __new__(cls, *args, **kwargs):  # noqa
        raise TypeError

    #

    SERVICE_NAME = 'github.actions.results.api.v1.CacheService'

    @classmethod
    def get_service_url(cls, base_url: str) -> str:
        return f'{base_url.rstrip("/")}/twirp/{cls.SERVICE_NAME}'

    #

    @dc.dataclass(frozen=True)
    class Method(ta.Generic[GithubCacheServiceV2RequestT, GithubCacheServiceV2ResponseT]):
        name: str
        request: ta.Type[GithubCacheServiceV2RequestT]
        response: ta.Type[GithubCacheServiceV2ResponseT]

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

    VERSION_LENGTH: int = 64

    #

    @dc.dataclass(frozen=True)
    class CreateCacheEntryRequest:
        key: str
        version: str
        metadata: ta.Optional['GithubCacheServiceV2.CacheMetadata'] = None

        def __post_init__(self) -> None:
            check.equal(len(self.version), GithubCacheServiceV2.VERSION_LENGTH)

    @dc.dataclass(frozen=True)
    class CreateCacheEntryResponse:
        ok: bool
        signed_upload_url: str
        message: ta.Optional[str] = None

    CREATE_CACHE_ENTRY_METHOD: Method[
        CreateCacheEntryRequest,
        CreateCacheEntryResponse,
    ] = Method(
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
        message: ta.Optional[str] = None

    FINALIZE_CACHE_ENTRY_METHOD: Method[
        FinalizeCacheEntryUploadRequest,
        FinalizeCacheEntryUploadResponse,
    ] = Method(
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

    GET_CACHE_ENTRY_DOWNLOAD_URL_METHOD: Method[
        GetCacheEntryDownloadUrlRequest,
        GetCacheEntryDownloadUrlResponse,
    ] = Method(
        'GetCacheEntryDownloadURL',
        GetCacheEntryDownloadUrlRequest,
        GetCacheEntryDownloadUrlResponse,
    )


########################################
# ../github/bootstrap.py
"""
sudo rm -rf \
    /usr/local/.ghcup \
    /opt/hostedtoolcache \

/usr/local/.ghcup       6.4G, 3391250 files
/opt/hostedtoolcache    8.0G, 14843980 files
/usr/local/lib/android  6.4G, 17251667 files
"""


##


GITHUB_ACTIONS_ENV_VAR = register_github_env_var('GITHUB_ACTIONS')


def is_in_github_actions() -> bool:
    return GITHUB_ACTIONS_ENV_VAR() is not None


########################################
# ../../oci/datarefs.py


##


@dc.dataclass(frozen=True)
class OciDataRef(Abstract):
    pass


@dc.dataclass(frozen=True)
class BytesOciDataRef(OciDataRef):
    data: bytes


@dc.dataclass(frozen=True)
class FileOciDataRef(OciDataRef):
    path: str


@dc.dataclass(frozen=True)
class TarFileOciDataRef(OciDataRef):
    tar_file: tarfile.TarFile
    tar_info: tarfile.TarInfo


##


@functools.singledispatch
def write_oci_data_ref_to_file(
        src_data: OciDataRef,
        dst_file: str,
        *,
        symlink: bool = False,  # noqa
        chunk_size: int = 1024 * 1024,
) -> None:
    with open_oci_data_ref(src_data) as f_src:
        with open(dst_file, 'wb') as f_dst:
            shutil.copyfileobj(f_src, f_dst, length=chunk_size)  # noqa


@write_oci_data_ref_to_file.register
def _(
        src_data: FileOciDataRef,
        dst_file: str,
        *,
        symlink: bool = False,
        **kwargs: ta.Any,
) -> None:
    if symlink:
        os.symlink(
            os.path.relpath(src_data.path, os.path.dirname(dst_file)),
            dst_file,
        )
    else:
        shutil.copyfile(src_data.path, dst_file)


#


@functools.singledispatch
def open_oci_data_ref(data: OciDataRef) -> ta.BinaryIO:
    raise TypeError(data)


@open_oci_data_ref.register
def _(data: FileOciDataRef) -> ta.BinaryIO:
    return open(data.path, 'rb')


@open_oci_data_ref.register
def _(data: BytesOciDataRef) -> ta.BinaryIO:
    return io.BytesIO(data.data)


@open_oci_data_ref.register
def _(data: TarFileOciDataRef) -> ta.BinaryIO:
    return check.not_none(data.tar_file.extractfile(data.tar_info))  # type: ignore[return-value]


#


@functools.singledispatch
def get_oci_data_ref_size(data: OciDataRef) -> int:
    raise TypeError(data)


@get_oci_data_ref_size.register
def _(data: FileOciDataRef) -> int:
    return os.path.getsize(data.path)


@get_oci_data_ref_size.register
def _(data: BytesOciDataRef) -> int:
    return len(data.data)


@get_oci_data_ref_size.register
def _(data: TarFileOciDataRef) -> int:
    return data.tar_info.size


##


@dc.dataclass(frozen=True)
class OciDataRefInfo:
    data: OciDataRef

    @cached_nullary
    def sha256(self) -> str:
        with open_oci_data_ref(self.data) as f:
            return hashlib.file_digest(f, 'sha256').hexdigest()  # type: ignore[arg-type]

    @cached_nullary
    def digest(self) -> str:
        return f'sha256:{self.sha256()}'

    @cached_nullary
    def size(self) -> int:
        return get_oci_data_ref_size(self.data)


########################################
# ../../oci/pack/unpacking.py


##


class OciLayerUnpacker(ExitStacked):
    def __init__(
            self,
            input_files: ta.Sequence[ta.Union[str, tarfile.TarFile]],
            output_file_path: str,
    ) -> None:
        super().__init__()

        self._input_files = list(input_files)
        self._output_file_path = output_file_path

    #

    @contextlib.contextmanager
    def _open_input_file(self, input_file: ta.Union[str, tarfile.TarFile]) -> ta.Iterator[tarfile.TarFile]:
        if isinstance(input_file, tarfile.TarFile):
            yield input_file

        elif isinstance(input_file, str):
            with tarfile.open(input_file) as tar_file:
                yield tar_file

        else:
            raise TypeError(input_file)

    #

    class _Entry(ta.NamedTuple):
        file: ta.Union[str, tarfile.TarFile]
        info: tarfile.TarInfo

    def _build_input_file_sorted_entries(self, input_file: ta.Union[str, tarfile.TarFile]) -> ta.Sequence[_Entry]:
        dct: ta.Dict[str, OciLayerUnpacker._Entry] = {}

        with self._open_input_file(input_file) as input_tar_file:
            for info in input_tar_file.getmembers():
                check.not_in(info.name, dct)
                dct[info.name] = self._Entry(
                    file=input_file,
                    info=info,
                )

        return sorted(dct.values(), key=lambda entry: entry.info.name)

    @cached_nullary
    def _entries_by_name(self) -> ta.Mapping[str, _Entry]:
        root: dict = {}

        def find_dir(dir_name: str) -> dict:  # noqa
            if dir_name:
                dir_parts = dir_name.split('/')
            else:
                dir_parts = []

            cur = root  # noqa
            for dir_part in dir_parts:
                cur = cur[dir_part]  # noqa

            return check.isinstance(cur, dict)

        #

        for input_file in self._input_files:
            sorted_entries = self._build_input_file_sorted_entries(input_file)

            wh_names = set()
            wh_opaques = set()

            #

            for entry in sorted_entries:
                info = entry.info
                name = check.non_empty_str(info.name)
                base_name = os.path.basename(name)
                dir_name = os.path.dirname(name)

                if base_name == '.wh..wh..opq':
                    wh_opaques.add(dir_name)
                    continue

                if base_name.startswith('.wh.'):
                    wh_base_name = os.path.basename(base_name[4:])
                    wh_name = os.path.join(dir_name, wh_base_name)
                    wh_names.add(wh_name)
                    continue

                cur = find_dir(dir_name)

                if info.type == tarfile.DIRTYPE:
                    try:
                        ex = cur[base_name]
                    except KeyError:
                        cur[base_name] = {'': entry}
                    else:
                        ex[''] = entry

                else:
                    cur[base_name] = entry

            #

            for wh_name in reversed(sorted(wh_names)):  # noqa
                wh_dir_name = os.path.dirname(wh_name)
                wh_base_name = os.path.basename(wh_name)

                cur = find_dir(wh_dir_name)
                rm = cur[wh_base_name]

                if isinstance(rm, dict):
                    # Whiteouts wipe out whole directory:
                    # https://github.com/containerd/containerd/blob/59c8cf6ea5f4175ad512914dd5ce554942bf144f/pkg/archive/tar_test.go#L648
                    # check.equal(set(rm), '')
                    del cur[wh_base_name]

                elif isinstance(rm, self._Entry):
                    del cur[wh_base_name]

                else:
                    raise TypeError(rm)

            if wh_opaques:
                raise NotImplementedError

        #

        out: ta.Dict[str, OciLayerUnpacker._Entry] = {}

        def rec(cur):  # noqa
            for _, child in sorted(cur.items(), key=lambda t: t[0]):
                if isinstance(child, dict):
                    rec(child)

                elif isinstance(child, self._Entry):
                    check.not_in(child.info.name, out)
                    out[child.info.name] = child

                else:
                    raise TypeError(child)

        rec(root)

        return out

    #

    @cached_nullary
    def _output_tar_file(self) -> tarfile.TarFile:
        return self._enter_context(tarfile.open(self._output_file_path, 'w'))

    #

    def _add_unpacked_entry(
            self,
            input_tar_file: tarfile.TarFile,
            info: tarfile.TarInfo,
    ) -> None:
        base_name = os.path.basename(info.name)
        check.state(not base_name.startswith('.wh.'))

        if info.type in tarfile.REGULAR_TYPES:
            with check.not_none(input_tar_file.extractfile(info)) as f:
                self._output_tar_file().addfile(info, f)

        else:
            self._output_tar_file().addfile(info)

    def _unpack_file(
            self,
            input_file: ta.Union[str, tarfile.TarFile],
    ) -> None:
        entries_by_name = self._entries_by_name()

        with self._open_input_file(input_file) as input_tar_file:
            info: tarfile.TarInfo
            for info in input_tar_file.getmembers():
                try:
                    entry = entries_by_name[info.name]
                except KeyError:
                    continue

                if entry.file != input_file:
                    continue

                self._add_unpacked_entry(input_tar_file, info)

    @cached_nullary
    def write(self) -> None:
        for input_file in self._input_files:
            self._unpack_file(input_file)


########################################
# ../../../omlish/argparse/cli.py
"""
FIXME:
 - exit_on_error lol

TODO:
 - default command
 - auto match all underscores to hyphens
 - pre-run, post-run hooks
 - exitstack?
 - suggestion - difflib.get_close_matches
 - add_argument_group - group kw on ArgparseKwarg?
"""


##


@dc.dataclass(eq=False)
class ArgparseArg:
    args: ta.Sequence[ta.Any]
    kwargs: ta.Mapping[str, ta.Any]
    group: ta.Optional[str] = None
    dest: ta.Optional[str] = None

    def __get__(self, instance, owner=None):
        if instance is None:
            return self
        return getattr(instance.args, self.dest)  # type: ignore


def argparse_arg(*args, **kwargs) -> ArgparseArg:
    return ArgparseArg(
        args=args,
        group=kwargs.pop('group', None),
        kwargs=kwargs,
    )


def argparse_arg_(*args, **kwargs) -> ta.Any:
    return argparse_arg(*args, **kwargs)


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
                if obj.group is not None:
                    # FIXME: add_argument_group
                    raise NotImplementedError

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
            if (parser := self.get_parser()).exit_on_error:  # noqa
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
        rc = self.cli_run()
        if not isinstance(rc, int):
            rc = 0
        raise SystemExit(rc)

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
# ../../../omlish/http/coro/io.py


##


class CoroHttpIo:
    def __new__(cls, *args, **kwargs):  # noqa
        raise TypeError

    def __init_subclass__(cls, **kwargs):  # noqa
        raise TypeError

    #

    MAX_LINE: ta.ClassVar[int] = 65536

    #

    class Io(Abstract):
        pass

    #

    class AnyLogIo(Io, Abstract):
        pass

    #

    @dc.dataclass(frozen=True)
    class ConnectIo(Io):
        args: ta.Tuple[ta.Any, ...]
        kwargs: ta.Optional[ta.Dict[str, ta.Any]] = None

        server_hostname: ta.Optional[str] = None

    #

    class CloseIo(Io):
        pass

    #

    class AnyReadIo(Io):  # noqa
        pass

    @dc.dataclass(frozen=True)
    class ReadIo(AnyReadIo):
        sz: ta.Optional[int]

    @dc.dataclass(frozen=True)
    class ReadLineIo(AnyReadIo):
        sz: int

    @dc.dataclass(frozen=True)
    class PeekIo(AnyReadIo):
        sz: int

    #

    @dc.dataclass(frozen=True)
    class WriteIo(Io):
        data: bytes


########################################
# ../../../omlish/http/parsing.py
# PYTHON SOFTWARE FOUNDATION LICENSE VERSION 2
# --------------------------------------------
#
# 1. This LICENSE AGREEMENT is between the Python Software Foundation ("PSF"), and the Individual or Organization
# ("Licensee") accessing and otherwise using this software ("Python") in source or binary form and its associated
# documentation.
#
# 2. Subject to the terms and conditions of this License Agreement, PSF hereby grants Licensee a nonexclusive,
# royalty-free, world-wide license to reproduce, analyze, test, perform and/or display publicly, prepare derivative
# works, distribute, and otherwise use Python alone or in any derivative version, provided, however, that PSF's License
# Agreement and PSF's notice of copyright, i.e., "Copyright (c) 2001, 2002, 2003, 2004, 2005, 2006, 2007, 2008, 2009,
# 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017 Python Software Foundation; All Rights Reserved" are retained in Python
# alone or in any derivative version prepared by Licensee.
#
# 3. In the event Licensee prepares a derivative work that is based on or incorporates Python or any part thereof, and
# wants to make the derivative work available to others as provided herein, then Licensee hereby agrees to include in
# any such work a brief summary of the changes made to Python.
#
# 4. PSF is making Python available to Licensee on an "AS IS" basis.  PSF MAKES NO REPRESENTATIONS OR WARRANTIES,
# EXPRESS OR IMPLIED.  BY WAY OF EXAMPLE, BUT NOT LIMITATION, PSF MAKES NO AND DISCLAIMS ANY REPRESENTATION OR WARRANTY
# OF MERCHANTABILITY OR FITNESS FOR ANY PARTICULAR PURPOSE OR THAT THE USE OF PYTHON WILL NOT INFRINGE ANY THIRD PARTY
# RIGHTS.
#
# 5. PSF SHALL NOT BE LIABLE TO LICENSEE OR ANY OTHER USERS OF PYTHON FOR ANY INCIDENTAL, SPECIAL, OR CONSEQUENTIAL
# DAMAGES OR LOSS AS A RESULT OF MODIFYING, DISTRIBUTING, OR OTHERWISE USING PYTHON, OR ANY DERIVATIVE THEREOF, EVEN IF
# ADVISED OF THE POSSIBILITY THEREOF.
#
# 6. This License Agreement will automatically terminate upon a material breach of its terms and conditions.
#
# 7. Nothing in this License Agreement shall be deemed to create any relationship of agency, partnership, or joint
# venture between PSF and Licensee.  This License Agreement does not grant permission to use PSF trademarks or trade
# name in a trademark sense to endorse or promote products or services of Licensee, or any third party.
#
# 8. By copying, installing or otherwise using Python, Licensee agrees to be bound by the terms and conditions of this
# License Agreement.


##


class ParseHttpRequestResult(Abstract):
    __slots__ = (
        'server_version',
        'request_line',
        'request_version',
        'version',
        'headers',
        'close_connection',
    )

    def __init__(
            self,
            *,
            server_version: HttpProtocolVersion,
            request_line: str,
            request_version: HttpProtocolVersion,
            version: HttpProtocolVersion,
            headers: ta.Optional[HttpHeaders],
            close_connection: bool,
    ) -> None:
        super().__init__()

        self.server_version = server_version
        self.request_line = request_line
        self.request_version = request_version
        self.version = version
        self.headers = headers
        self.close_connection = close_connection

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({", ".join(f"{a}={getattr(self, a)!r}" for a in self.__slots__)})'


class EmptyParsedHttpResult(ParseHttpRequestResult):
    pass


class ParseHttpRequestError(ParseHttpRequestResult):
    __slots__ = (
        'code',
        'message',
        *ParseHttpRequestResult.__slots__,
    )

    def __init__(
            self,
            *,
            code: http.HTTPStatus,
            message: ta.Union[str, ta.Tuple[str, str]],

            **kwargs: ta.Any,
    ) -> None:
        super().__init__(**kwargs)

        self.code = code
        self.message = message


class ParsedHttpRequest(ParseHttpRequestResult):
    __slots__ = (
        'method',
        'path',
        'headers',
        'expects_continue',
        *[a for a in ParseHttpRequestResult.__slots__ if a != 'headers'],
    )

    def __init__(
            self,
            *,
            method: str,
            path: str,
            headers: HttpHeaders,
            expects_continue: bool,

            **kwargs: ta.Any,
    ) -> None:
        super().__init__(
            headers=headers,
            **kwargs,
        )

        self.method = method
        self.path = path
        self.expects_continue = expects_continue

    headers: HttpHeaders


#


class HttpRequestParser:
    DEFAULT_SERVER_VERSION = HttpProtocolVersions.HTTP_1_0

    # The default request version. This only affects responses up until the point where the request line is parsed, so
    # it mainly decides what the client gets back when sending a malformed request line.
    # Most web servers default to HTTP 0.9, i.e. don't send a status line.
    DEFAULT_REQUEST_VERSION = HttpProtocolVersions.HTTP_0_9

    #

    DEFAULT_MAX_LINE: int = 0x10000
    DEFAULT_MAX_HEADERS: int = 100

    #

    def __init__(
            self,
            *,
            server_version: HttpProtocolVersion = DEFAULT_SERVER_VERSION,

            max_line: int = DEFAULT_MAX_LINE,
            max_headers: int = DEFAULT_MAX_HEADERS,
    ) -> None:
        super().__init__()

        if server_version >= HttpProtocolVersions.HTTP_2_0:
            raise ValueError(f'Unsupported protocol version: {server_version}')
        self._server_version = server_version

        self._max_line = max_line
        self._max_headers = max_headers

    #

    @property
    def server_version(self) -> HttpProtocolVersion:
        return self._server_version

    #

    def _run_read_line_coro(
            self,
            gen: ta.Generator[int, bytes, T],
            read_line: ta.Callable[[int], bytes],
    ) -> T:
        sz = next(gen)
        while True:
            try:
                sz = gen.send(read_line(sz))
            except StopIteration as e:
                return e.value

    #

    def parse_request_version(self, version_str: str) -> HttpProtocolVersion:
        if not version_str.startswith('HTTP/'):
            raise ValueError(version_str)  # noqa

        base_version_number = version_str.split('/', 1)[1]
        version_number_parts = base_version_number.split('.')

        # RFC 2145 section 3.1 says there can be only one "." and
        #   - major and minor numbers MUST be treated as separate integers;
        #   - HTTP/2.4 is a lower version than HTTP/2.13, which in turn is lower than HTTP/12.3;
        #   - Leading zeros MUST be ignored by recipients.
        if len(version_number_parts) != 2:
            raise ValueError(version_number_parts)  # noqa
        if any(not component.isdigit() for component in version_number_parts):
            raise ValueError('non digit in http version')  # noqa
        if any(len(component) > 10 for component in version_number_parts):
            raise ValueError('unreasonable length http version')  # noqa

        return HttpProtocolVersion(
            int(version_number_parts[0]),
            int(version_number_parts[1]),
        )

    #

    def coro_read_raw_headers(self) -> ta.Generator[int, bytes, ta.List[bytes]]:
        raw_headers: ta.List[bytes] = []
        while True:
            line = yield self._max_line + 1
            if len(line) > self._max_line:
                raise http.client.LineTooLong('header line')
            raw_headers.append(line)
            if len(raw_headers) > self._max_headers:
                raise http.client.HTTPException(f'got more than {self._max_headers} headers')
            if line in (b'\r\n', b'\n', b''):
                break
        return raw_headers

    def read_raw_headers(self, read_line: ta.Callable[[int], bytes]) -> ta.List[bytes]:
        return self._run_read_line_coro(self.coro_read_raw_headers(), read_line)

    def parse_raw_headers(self, raw_headers: ta.Sequence[bytes]) -> HttpHeaders:
        return http.client.parse_headers(io.BytesIO(b''.join(raw_headers)))

    #

    _TLS_HANDSHAKE_PREFIX = b'\x16'

    def coro_parse(self) -> ta.Generator[int, bytes, ParseHttpRequestResult]:
        raw_request_line = yield self._max_line + 1

        # Common result kwargs

        request_line = '-'
        request_version = self.DEFAULT_REQUEST_VERSION

        # Set to min(server, request) when it gets that far, but if it fails before that the server authoritatively
        # responds with its own version.
        version = self._server_version

        headers: HttpHeaders | None = None

        close_connection = True

        def result_kwargs():
            return dict(
                server_version=self._server_version,
                request_line=request_line,
                request_version=request_version,
                version=version,
                headers=headers,
                close_connection=close_connection,
            )

        # Decode line

        if len(raw_request_line) > self._max_line:
            return ParseHttpRequestError(
                code=http.HTTPStatus.REQUEST_URI_TOO_LONG,
                message='Request line too long',
                **result_kwargs(),
            )

        if not raw_request_line:
            return EmptyParsedHttpResult(**result_kwargs())

        # Detect TLS

        if raw_request_line.startswith(self._TLS_HANDSHAKE_PREFIX):
            return ParseHttpRequestError(
                code=http.HTTPStatus.BAD_REQUEST,
                message='Bad request version (probable TLS handshake)',
                **result_kwargs(),
            )

        # Decode line

        request_line = raw_request_line.decode('iso-8859-1').rstrip('\r\n')

        # Split words

        words = request_line.split()
        if len(words) == 0:
            return EmptyParsedHttpResult(**result_kwargs())

        # Parse and set version

        if len(words) >= 3:  # Enough to determine protocol version
            version_str = words[-1]
            try:
                request_version = self.parse_request_version(version_str)

            except (ValueError, IndexError):
                return ParseHttpRequestError(
                    code=http.HTTPStatus.BAD_REQUEST,
                    message=f'Bad request version ({version_str!r})',
                    **result_kwargs(),
                )

            if (
                    request_version < HttpProtocolVersions.HTTP_0_9 or
                    request_version >= HttpProtocolVersions.HTTP_2_0
            ):
                return ParseHttpRequestError(
                    code=http.HTTPStatus.HTTP_VERSION_NOT_SUPPORTED,
                    message=f'Invalid HTTP version ({version_str})',
                    **result_kwargs(),
                )

            version = min([self._server_version, request_version])

            if version >= HttpProtocolVersions.HTTP_1_1:
                close_connection = False

        # Verify word count

        if not 2 <= len(words) <= 3:
            return ParseHttpRequestError(
                code=http.HTTPStatus.BAD_REQUEST,
                message=f'Bad request syntax ({request_line!r})',
                **result_kwargs(),
            )

        # Parse method and path

        method, path = words[:2]
        if len(words) == 2:
            close_connection = True
            if method != 'GET':
                return ParseHttpRequestError(
                    code=http.HTTPStatus.BAD_REQUEST,
                    message=f'Bad HTTP/0.9 request type ({method!r})',
                    **result_kwargs(),
                )

        # gh-87389: The purpose of replacing '//' with '/' is to protect against open redirect attacks possibly
        # triggered if the path starts with '//' because http clients treat //path as an absolute URI without scheme
        # (similar to http://path) rather than a path.
        if path.startswith('//'):
            path = '/' + path.lstrip('/')  # Reduce to a single /

        # Parse headers

        try:
            raw_gen = self.coro_read_raw_headers()
            raw_sz = next(raw_gen)
            while True:
                buf = yield raw_sz
                try:
                    raw_sz = raw_gen.send(buf)
                except StopIteration as e:
                    raw_headers = e.value
                    break

            headers = self.parse_raw_headers(raw_headers)

        except http.client.LineTooLong as err:
            return ParseHttpRequestError(
                code=http.HTTPStatus.REQUEST_HEADER_FIELDS_TOO_LARGE,
                message=('Line too long', str(err)),
                **result_kwargs(),
            )

        except http.client.HTTPException as err:
            return ParseHttpRequestError(
                code=http.HTTPStatus.REQUEST_HEADER_FIELDS_TOO_LARGE,
                message=('Too many headers', str(err)),
                **result_kwargs(),
            )

        # Check for connection directive

        conn_type = headers.get('Connection', '')
        if conn_type.lower() == 'close':
            close_connection = True
        elif (
                conn_type.lower() == 'keep-alive' and
                version >= HttpProtocolVersions.HTTP_1_1
        ):
            close_connection = False

        # Check for expect directive

        expect = headers.get('Expect', '')
        if (
                expect.lower() == '100-continue' and
                version >= HttpProtocolVersions.HTTP_1_1
        ):
            expects_continue = True
        else:
            expects_continue = False

        # Return

        return ParsedHttpRequest(
            method=method,
            path=path,
            expects_continue=expects_continue,
            **result_kwargs(),
        )

    def parse(self, read_line: ta.Callable[[int], bytes]) -> ParseHttpRequestResult:
        return self._run_read_line_coro(self.coro_parse(), read_line)


########################################
# ../../../omlish/lite/marshal.py
"""
TODO:
 - pickle stdlib objs? have to pin to 3.8 pickle protocol, will be cross-version
 - Options.sequence_cls = list, mapping_cls = dict, ... - def with_mutable_containers() -> Options
"""


##


@dc.dataclass(frozen=True)
class ObjMarshalOptions:
    raw_bytes: bool = False
    non_strict_fields: bool = False


class ObjMarshaler(Abstract):
    @abc.abstractmethod
    def marshal(self, o: ta.Any, ctx: 'ObjMarshalContext') -> ta.Any:
        raise NotImplementedError

    @abc.abstractmethod
    def unmarshal(self, o: ta.Any, ctx: 'ObjMarshalContext') -> ta.Any:
        raise NotImplementedError


class NopObjMarshaler(ObjMarshaler):
    def marshal(self, o: ta.Any, ctx: 'ObjMarshalContext') -> ta.Any:
        return o

    def unmarshal(self, o: ta.Any, ctx: 'ObjMarshalContext') -> ta.Any:
        return o


class ProxyObjMarshaler(ObjMarshaler):
    def __init__(self, m: ta.Optional[ObjMarshaler] = None) -> None:
        super().__init__()

        self._m = m

    def marshal(self, o: ta.Any, ctx: 'ObjMarshalContext') -> ta.Any:
        return check.not_none(self._m).marshal(o, ctx)

    def unmarshal(self, o: ta.Any, ctx: 'ObjMarshalContext') -> ta.Any:
        return check.not_none(self._m).unmarshal(o, ctx)


class CastObjMarshaler(ObjMarshaler):
    def __init__(self, ty: type) -> None:
        super().__init__()

        self._ty = ty

    def marshal(self, o: ta.Any, ctx: 'ObjMarshalContext') -> ta.Any:
        return o

    def unmarshal(self, o: ta.Any, ctx: 'ObjMarshalContext') -> ta.Any:
        return self._ty(o)


class DynamicObjMarshaler(ObjMarshaler):
    def marshal(self, o: ta.Any, ctx: 'ObjMarshalContext') -> ta.Any:
        return ctx.manager.marshal_obj(o, opts=ctx.options)

    def unmarshal(self, o: ta.Any, ctx: 'ObjMarshalContext') -> ta.Any:
        return o


class Base64ObjMarshaler(ObjMarshaler):
    def __init__(self, ty: type) -> None:
        super().__init__()

        self._ty = ty

    def marshal(self, o: ta.Any, ctx: 'ObjMarshalContext') -> ta.Any:
        return base64.b64encode(o).decode('ascii')

    def unmarshal(self, o: ta.Any, ctx: 'ObjMarshalContext') -> ta.Any:
        return self._ty(base64.b64decode(o))


class BytesSwitchedObjMarshaler(ObjMarshaler):
    def __init__(self, m: ObjMarshaler) -> None:
        super().__init__()

        self._m = m

    def marshal(self, o: ta.Any, ctx: 'ObjMarshalContext') -> ta.Any:
        if ctx.options.raw_bytes:
            return o
        return self._m.marshal(o, ctx)

    def unmarshal(self, o: ta.Any, ctx: 'ObjMarshalContext') -> ta.Any:
        if ctx.options.raw_bytes:
            return o
        return self._m.unmarshal(o, ctx)


class EnumObjMarshaler(ObjMarshaler):
    def __init__(self, ty: type) -> None:
        super().__init__()

        self._ty = ty

    def marshal(self, o: ta.Any, ctx: 'ObjMarshalContext') -> ta.Any:
        return o.name

    def unmarshal(self, o: ta.Any, ctx: 'ObjMarshalContext') -> ta.Any:
        return self._ty.__members__[o]  # type: ignore


class OptionalObjMarshaler(ObjMarshaler):
    def __init__(self, item: ObjMarshaler) -> None:
        super().__init__()

        self._item = item

    def marshal(self, o: ta.Any, ctx: 'ObjMarshalContext') -> ta.Any:
        if o is None:
            return None
        return self._item.marshal(o, ctx)

    def unmarshal(self, o: ta.Any, ctx: 'ObjMarshalContext') -> ta.Any:
        if o is None:
            return None
        return self._item.unmarshal(o, ctx)


class PrimitiveUnionObjMarshaler(ObjMarshaler):
    def __init__(
            self,
            pt: ta.Tuple[type, ...],
            x: ta.Optional[ObjMarshaler] = None,
    ) -> None:
        super().__init__()

        self._pt = pt
        self._x = x

    def marshal(self, o: ta.Any, ctx: 'ObjMarshalContext') -> ta.Any:
        if isinstance(o, self._pt):
            return o
        elif self._x is not None:
            return self._x.marshal(o, ctx)
        else:
            raise TypeError(o)

    def unmarshal(self, o: ta.Any, ctx: 'ObjMarshalContext') -> ta.Any:
        if isinstance(o, self._pt):
            return o
        elif self._x is not None:
            return self._x.unmarshal(o, ctx)
        else:
            raise TypeError(o)


class LiteralObjMarshaler(ObjMarshaler):
    def __init__(
            self,
            item: ObjMarshaler,
            vs: frozenset,
    ) -> None:
        super().__init__()

        self._item = item
        self._vs = vs

    def marshal(self, o: ta.Any, ctx: 'ObjMarshalContext') -> ta.Any:
        return self._item.marshal(check.in_(o, self._vs), ctx)

    def unmarshal(self, o: ta.Any, ctx: 'ObjMarshalContext') -> ta.Any:
        return check.in_(self._item.unmarshal(o, ctx), self._vs)


class MappingObjMarshaler(ObjMarshaler):
    def __init__(
            self,
            ty: type,
            km: ObjMarshaler,
            vm: ObjMarshaler,
    ) -> None:
        super().__init__()

        self._ty = ty
        self._km = km
        self._vm = vm

    def marshal(self, o: ta.Any, ctx: 'ObjMarshalContext') -> ta.Any:
        return {self._km.marshal(k, ctx): self._vm.marshal(v, ctx) for k, v in o.items()}

    def unmarshal(self, o: ta.Any, ctx: 'ObjMarshalContext') -> ta.Any:
        return self._ty((self._km.unmarshal(k, ctx), self._vm.unmarshal(v, ctx)) for k, v in o.items())


class IterableObjMarshaler(ObjMarshaler):
    def __init__(
            self,
            ty: type,
            item: ObjMarshaler,
    ) -> None:
        super().__init__()

        self._ty = ty
        self._item = item

    def marshal(self, o: ta.Any, ctx: 'ObjMarshalContext') -> ta.Any:
        return [self._item.marshal(e, ctx) for e in o]

    def unmarshal(self, o: ta.Any, ctx: 'ObjMarshalContext') -> ta.Any:
        return self._ty(self._item.unmarshal(e, ctx) for e in o)


class FieldsObjMarshaler(ObjMarshaler):
    @dc.dataclass(frozen=True)
    class Field:
        att: str
        key: str
        m: ObjMarshaler

        omit_if_none: bool = False

    def __init__(
            self,
            ty: type,
            fs: ta.Sequence[Field],
            *,
            non_strict: bool = False,
    ) -> None:
        super().__init__()

        self._ty = ty
        self._fs = fs
        self._non_strict = non_strict

        fs_by_att: dict = {}
        fs_by_key: dict = {}
        for f in self._fs:
            check.not_in(check.non_empty_str(f.att), fs_by_att)
            check.not_in(check.non_empty_str(f.key), fs_by_key)
            fs_by_att[f.att] = f
            fs_by_key[f.key] = f

        self._fs_by_att: ta.Mapping[str, FieldsObjMarshaler.Field] = fs_by_att
        self._fs_by_key: ta.Mapping[str, FieldsObjMarshaler.Field] = fs_by_key

    @property
    def ty(self) -> type:
        return self._ty

    @property
    def fs(self) -> ta.Sequence[Field]:
        return self._fs

    #

    def marshal(self, o: ta.Any, ctx: 'ObjMarshalContext') -> ta.Any:
        d = {}
        for f in self._fs:
            mv = f.m.marshal(getattr(o, f.att), ctx)
            if mv is None and f.omit_if_none:
                continue
            d[f.key] = mv
        return d

    def unmarshal(self, o: ta.Any, ctx: 'ObjMarshalContext') -> ta.Any:
        kw = {}
        for k, v in o.items():
            if (f := self._fs_by_key.get(k)) is None:
                if not (self._non_strict or ctx.options.non_strict_fields):
                    raise KeyError(k)
                continue
            kw[f.att] = f.m.unmarshal(v, ctx)
        return self._ty(**kw)


class SingleFieldObjMarshaler(ObjMarshaler):
    def __init__(
            self,
            ty: type,
            fld: str,
    ) -> None:
        super().__init__()

        self._ty = ty
        self._fld = fld

    def marshal(self, o: ta.Any, ctx: 'ObjMarshalContext') -> ta.Any:
        return getattr(o, self._fld)

    def unmarshal(self, o: ta.Any, ctx: 'ObjMarshalContext') -> ta.Any:
        return self._ty(**{self._fld: o})


class PolymorphicObjMarshaler(ObjMarshaler):
    class Impl(ta.NamedTuple):
        ty: type
        tag: str
        m: ObjMarshaler

    def __init__(
            self,
            impls_by_ty: ta.Mapping[type, Impl],
            impls_by_tag: ta.Mapping[str, Impl],
    ) -> None:
        super().__init__()

        self._impls_by_ty = impls_by_ty
        self._impls_by_tag = impls_by_tag

    @classmethod
    def of(cls, impls: ta.Iterable[Impl]) -> 'PolymorphicObjMarshaler':
        return cls(
            {i.ty: i for i in impls},
            {i.tag: i for i in impls},
        )

    def marshal(self, o: ta.Any, ctx: 'ObjMarshalContext') -> ta.Any:
        impl = self._impls_by_ty[type(o)]
        return {impl.tag: impl.m.marshal(o, ctx)}

    def unmarshal(self, o: ta.Any, ctx: 'ObjMarshalContext') -> ta.Any:
        [(t, v)] = o.items()
        impl = self._impls_by_tag[t]
        return impl.m.unmarshal(v, ctx)


class DatetimeObjMarshaler(ObjMarshaler):
    def __init__(
            self,
            ty: type,
    ) -> None:
        super().__init__()

        self._ty = ty

    def marshal(self, o: ta.Any, ctx: 'ObjMarshalContext') -> ta.Any:
        return o.isoformat()

    def unmarshal(self, o: ta.Any, ctx: 'ObjMarshalContext') -> ta.Any:
        return self._ty.fromisoformat(o)  # type: ignore


class DecimalObjMarshaler(ObjMarshaler):
    def marshal(self, o: ta.Any, ctx: 'ObjMarshalContext') -> ta.Any:
        return str(check.isinstance(o, decimal.Decimal))

    def unmarshal(self, v: ta.Any, ctx: 'ObjMarshalContext') -> ta.Any:
        return decimal.Decimal(check.isinstance(v, str))


class FractionObjMarshaler(ObjMarshaler):
    def marshal(self, o: ta.Any, ctx: 'ObjMarshalContext') -> ta.Any:
        fr = check.isinstance(o, fractions.Fraction)
        return [fr.numerator, fr.denominator]

    def unmarshal(self, v: ta.Any, ctx: 'ObjMarshalContext') -> ta.Any:
        num, denom = check.isinstance(v, list)
        return fractions.Fraction(num, denom)


class UuidObjMarshaler(ObjMarshaler):
    def marshal(self, o: ta.Any, ctx: 'ObjMarshalContext') -> ta.Any:
        return str(o)

    def unmarshal(self, o: ta.Any, ctx: 'ObjMarshalContext') -> ta.Any:
        return uuid.UUID(o)


##


_DEFAULT_OBJ_MARSHALERS: ta.Dict[ta.Any, ObjMarshaler] = {
    **{t: NopObjMarshaler() for t in (type(None),)},
    **{t: CastObjMarshaler(t) for t in (int, float, str, bool)},
    **{t: BytesSwitchedObjMarshaler(Base64ObjMarshaler(t)) for t in (bytes, bytearray)},
    **{t: IterableObjMarshaler(t, DynamicObjMarshaler()) for t in (list, tuple, set, frozenset)},
    **{t: MappingObjMarshaler(t, DynamicObjMarshaler(), DynamicObjMarshaler()) for t in (dict,)},

    **{t: DynamicObjMarshaler() for t in (ta.Any, object)},

    **{t: DatetimeObjMarshaler(t) for t in (datetime.date, datetime.time, datetime.datetime)},
    decimal.Decimal: DecimalObjMarshaler(),
    fractions.Fraction: FractionObjMarshaler(),
    uuid.UUID: UuidObjMarshaler(),
}

_OBJ_MARSHALER_GENERIC_MAPPING_TYPES: ta.Dict[ta.Any, type] = {
    **{t: t for t in (dict,)},
    **{t: dict for t in (collections.abc.Mapping, collections.abc.MutableMapping)},  # noqa
}

_OBJ_MARSHALER_GENERIC_ITERABLE_TYPES: ta.Dict[ta.Any, type] = {
    **{t: t for t in (list, tuple, set, frozenset)},
    collections.abc.Set: frozenset,
    collections.abc.MutableSet: set,
    collections.abc.Sequence: tuple,
    collections.abc.MutableSequence: list,
}

_OBJ_MARSHALER_PRIMITIVE_TYPES: ta.Set[type] = {
    int,
    float,
    bool,
    str,
}


##


_REGISTERED_OBJ_MARSHALERS_BY_TYPE: ta.MutableMapping[type, ObjMarshaler] = weakref.WeakKeyDictionary()


def register_type_obj_marshaler(ty: type, om: ObjMarshaler) -> None:
    _REGISTERED_OBJ_MARSHALERS_BY_TYPE[ty] = om


def register_single_field_type_obj_marshaler(fld, ty=None):
    def inner(ty):  # noqa
        register_type_obj_marshaler(ty, SingleFieldObjMarshaler(ty, fld))
        return ty

    if ty is not None:
        return inner(ty)
    else:
        return inner


##


class ObjMarshalerFieldMetadata:
    def __new__(cls, *args, **kwargs):  # noqa
        raise TypeError


class OBJ_MARSHALER_FIELD_KEY(ObjMarshalerFieldMetadata):  # noqa
    pass


class OBJ_MARSHALER_OMIT_IF_NONE(ObjMarshalerFieldMetadata):  # noqa
    pass


##


class ObjMarshalerManager(Abstract):
    @abc.abstractmethod
    def make_obj_marshaler(
            self,
            ty: ta.Any,
            rec: ta.Callable[[ta.Any], ObjMarshaler],
            *,
            non_strict_fields: bool = False,
    ) -> ObjMarshaler:
        raise NotImplementedError

    @abc.abstractmethod
    def set_obj_marshaler(
            self,
            ty: ta.Any,
            m: ObjMarshaler,
            *,
            override: bool = False,
    ) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def get_obj_marshaler(
            self,
            ty: ta.Any,
            *,
            no_cache: bool = False,
            **kwargs: ta.Any,
    ) -> ObjMarshaler:
        raise NotImplementedError

    @abc.abstractmethod
    def make_context(self, opts: ta.Optional[ObjMarshalOptions]) -> 'ObjMarshalContext':
        raise NotImplementedError

    #

    def marshal_obj(
            self,
            o: ta.Any,
            ty: ta.Any = None,
            opts: ta.Optional[ObjMarshalOptions] = None,
    ) -> ta.Any:
        m = self.get_obj_marshaler(ty if ty is not None else type(o))
        return m.marshal(o, self.make_context(opts))

    def unmarshal_obj(
            self,
            o: ta.Any,
            ty: ta.Union[ta.Type[T], ta.Any],
            opts: ta.Optional[ObjMarshalOptions] = None,
    ) -> T:
        m = self.get_obj_marshaler(ty)
        return m.unmarshal(o, self.make_context(opts))

    def roundtrip_obj(
            self,
            o: ta.Any,
            ty: ta.Any = None,
            opts: ta.Optional[ObjMarshalOptions] = None,
    ) -> ta.Any:
        if ty is None:
            ty = type(o)
        m: ta.Any = self.marshal_obj(o, ty, opts)
        u: ta.Any = self.unmarshal_obj(m, ty, opts)
        return u


#


class ObjMarshalerManagerImpl(ObjMarshalerManager):
    def __init__(
            self,
            *,
            default_options: ObjMarshalOptions = ObjMarshalOptions(),

            default_obj_marshalers: ta.Dict[ta.Any, ObjMarshaler] = _DEFAULT_OBJ_MARSHALERS,  # noqa
            generic_mapping_types: ta.Dict[ta.Any, type] = _OBJ_MARSHALER_GENERIC_MAPPING_TYPES,  # noqa
            generic_iterable_types: ta.Dict[ta.Any, type] = _OBJ_MARSHALER_GENERIC_ITERABLE_TYPES,  # noqa

            registered_obj_marshalers: ta.Mapping[type, ObjMarshaler] = _REGISTERED_OBJ_MARSHALERS_BY_TYPE,
    ) -> None:
        super().__init__()

        self._default_options = default_options

        self._obj_marshalers = dict(default_obj_marshalers)
        self._generic_mapping_types = generic_mapping_types
        self._generic_iterable_types = generic_iterable_types
        self._registered_obj_marshalers = registered_obj_marshalers

        self._lock = threading.RLock()
        self._marshalers: ta.Dict[ta.Any, ObjMarshaler] = dict(_DEFAULT_OBJ_MARSHALERS)
        self._proxies: ta.Dict[ta.Any, ProxyObjMarshaler] = {}

    #

    @classmethod
    def _is_abstract(cls, ty: type) -> bool:
        return abc.ABC in ty.__bases__ or Abstract in ty.__bases__

    #

    def make_obj_marshaler(
            self,
            ty: ta.Any,
            rec: ta.Callable[[ta.Any], ObjMarshaler],
            *,
            non_strict_fields: bool = False,
    ) -> ObjMarshaler:
        if isinstance(ty, type):
            if (reg := self._registered_obj_marshalers.get(ty)) is not None:
                return reg

            if self._is_abstract(ty):
                tn = ty.__name__
                impls: ta.List[ta.Tuple[type, str]] = [  # type: ignore[var-annotated]
                    (ity, ity.__name__)
                    for ity in deep_subclasses(ty)
                    if not self._is_abstract(ity)
                ]

                if all(itn.endswith(tn) for _, itn in impls):
                    impls = [
                        (ity, snake_case(itn[:-len(tn)]))
                        for ity, itn in impls
                    ]

                dupe_tns = sorted(
                    dn
                    for dn, dc in collections.Counter(itn for _, itn in impls).items()
                    if dc > 1
                )
                if dupe_tns:
                    raise KeyError(f'Duplicate impl names for {ty}: {dupe_tns}')

                return PolymorphicObjMarshaler.of([
                    PolymorphicObjMarshaler.Impl(
                        ity,
                        itn,
                        rec(ity),
                    )
                    for ity, itn in impls
                ])

            if issubclass(ty, enum.Enum):
                return EnumObjMarshaler(ty)

            if dc.is_dataclass(ty):
                return FieldsObjMarshaler(
                    ty,
                    [
                        FieldsObjMarshaler.Field(
                            att=f.name,
                            key=check.non_empty_str(fk),
                            m=rec(f.type),
                            omit_if_none=check.isinstance(f.metadata.get(OBJ_MARSHALER_OMIT_IF_NONE, False), bool),
                        )
                        for f in dc.fields(ty)
                        if (fk := f.metadata.get(OBJ_MARSHALER_FIELD_KEY, f.name)) is not None
                    ],
                    non_strict=non_strict_fields,
                )

            if issubclass(ty, tuple) and hasattr(ty, '_fields'):
                return FieldsObjMarshaler(
                    ty,
                    [
                        FieldsObjMarshaler.Field(
                            att=p.name,
                            key=p.name,
                            m=rec(p.annotation),
                        )
                        for p in inspect.signature(ty).parameters.values()
                    ],
                    non_strict=non_strict_fields,
                )

        if is_new_type(ty):
            return rec(get_new_type_supertype(ty))

        if is_literal_type(ty):
            lvs = frozenset(get_literal_type_args(ty))
            if None in lvs:
                is_opt = True
                lvs -= frozenset([None])
            else:
                is_opt = False
            lty = check.single(set(map(type, lvs)))
            lm: ObjMarshaler = LiteralObjMarshaler(rec(lty), lvs)
            if is_opt:
                lm = OptionalObjMarshaler(lm)
            return lm

        if is_generic_alias(ty):
            try:
                mt = self._generic_mapping_types[ta.get_origin(ty)]
            except KeyError:
                pass
            else:
                k, v = ta.get_args(ty)
                return MappingObjMarshaler(mt, rec(k), rec(v))

            try:
                st = self._generic_iterable_types[ta.get_origin(ty)]
            except KeyError:
                pass
            else:
                [e] = ta.get_args(ty)
                return IterableObjMarshaler(st, rec(e))

        if is_union_alias(ty):
            uts = frozenset(ta.get_args(ty))
            if None in uts or type(None) in uts:
                is_opt = True
                uts = frozenset(ut for ut in uts if ut not in (None, type(None)))
            else:
                is_opt = False

            um: ObjMarshaler
            if not uts:
                raise TypeError(ty)
            elif len(uts) == 1:
                um = rec(check.single(uts))
            else:
                pt = tuple({ut for ut in uts if ut in _OBJ_MARSHALER_PRIMITIVE_TYPES})
                np_uts = {ut for ut in uts if ut not in _OBJ_MARSHALER_PRIMITIVE_TYPES}
                if not np_uts:
                    um = PrimitiveUnionObjMarshaler(pt)
                elif len(np_uts) == 1:
                    um = PrimitiveUnionObjMarshaler(pt, x=rec(check.single(np_uts)))
                else:
                    raise TypeError(ty)

            if is_opt:
                um = OptionalObjMarshaler(um)
            return um

        raise TypeError(ty)

    #

    def set_obj_marshaler(
            self,
            ty: ta.Any,
            m: ObjMarshaler,
            *,
            override: bool = False,
    ) -> None:
        with self._lock:
            if not override and ty in self._obj_marshalers:
                raise KeyError(ty)
            self._obj_marshalers[ty] = m

    def get_obj_marshaler(
            self,
            ty: ta.Any,
            *,
            no_cache: bool = False,
            **kwargs: ta.Any,
    ) -> ObjMarshaler:
        with self._lock:
            if not no_cache:
                try:
                    return self._obj_marshalers[ty]
                except KeyError:
                    pass

            try:
                return self._proxies[ty]
            except KeyError:
                pass

            rec = functools.partial(
                self.get_obj_marshaler,
                no_cache=no_cache,
                **kwargs,
            )

            p = ProxyObjMarshaler()
            self._proxies[ty] = p
            try:
                m = self.make_obj_marshaler(ty, rec, **kwargs)
            finally:
                del self._proxies[ty]
            p._m = m  # noqa

            if not no_cache:
                self._obj_marshalers[ty] = m
            return m

    def make_context(self, opts: ta.Optional[ObjMarshalOptions]) -> 'ObjMarshalContext':
        return ObjMarshalContext(
            options=opts or self._default_options,
            manager=self,
        )


def new_obj_marshaler_manager(**kwargs: ta.Any) -> ObjMarshalerManager:
    return ObjMarshalerManagerImpl(**kwargs)


##


@dc.dataclass(frozen=True)
class ObjMarshalContext:
    options: ObjMarshalOptions
    manager: ObjMarshalerManager


##


OBJ_MARSHALER_MANAGER = new_obj_marshaler_manager()

set_obj_marshaler = OBJ_MARSHALER_MANAGER.set_obj_marshaler
get_obj_marshaler = OBJ_MARSHALER_MANAGER.get_obj_marshaler

marshal_obj = OBJ_MARSHALER_MANAGER.marshal_obj
unmarshal_obj = OBJ_MARSHALER_MANAGER.unmarshal_obj


########################################
# ../../../omlish/lite/maybes.py


##


@functools.total_ordering
class Maybe(ta.Generic[T]):
    class ValueNotPresentError(BaseException):
        pass

    #

    @property
    @abc.abstractmethod
    def present(self) -> bool:
        raise NotImplementedError

    @abc.abstractmethod
    def must(self) -> T:
        raise NotImplementedError

    #

    @abc.abstractmethod
    def __repr__(self) -> str:
        raise NotImplementedError

    @abc.abstractmethod
    def __hash__(self) -> int:
        raise NotImplementedError

    @abc.abstractmethod
    def __eq__(self, other) -> bool:
        raise NotImplementedError

    @abc.abstractmethod
    def __lt__(self, other) -> bool:
        raise NotImplementedError

    #

    @ta.final
    def __ne__(self, other):
        return not (self == other)

    @ta.final
    def __iter__(self) -> ta.Iterator[T]:
        if self.present:
            yield self.must()

    @ta.final
    def __bool__(self) -> ta.NoReturn:
        raise TypeError

    #

    @ta.final
    def if_present(self, consumer: ta.Callable[[T], None]) -> None:
        if self.present:
            consumer(self.must())

    @ta.final
    def filter(self, predicate: ta.Callable[[T], bool]) -> 'Maybe[T]':
        if self.present and predicate(self.must()):
            return self
        else:
            return Maybe.empty()

    @ta.final
    def map(self, mapper: ta.Callable[[T], U]) -> 'Maybe[U]':
        if self.present:
            return Maybe.just(mapper(self.must()))
        else:
            return Maybe.empty()

    @ta.final
    def flat_map(self, mapper: ta.Callable[[T], 'Maybe[U]']) -> 'Maybe[U]':
        if self.present:
            if not isinstance(v := mapper(self.must()), Maybe):
                raise TypeError(v)
            return v
        else:
            return Maybe.empty()

    @ta.final
    def or_else(self, other: ta.Union[T, U]) -> ta.Union[T, U]:
        if self.present:
            return self.must()
        else:
            return other

    @ta.final
    def or_else_get(self, supplier: ta.Callable[[], ta.Union[T, U]]) -> ta.Union[T, U]:
        if self.present:
            return self.must()
        else:
            return supplier()

    @ta.final
    def or_else_raise(self, exception_supplier: ta.Callable[[], Exception]) -> T:
        if self.present:
            return self.must()
        else:
            raise exception_supplier()

    #

    @classmethod
    def of_optional(cls, v: ta.Optional[T]) -> 'Maybe[T]':
        if v is not None:
            return cls.just(v)
        else:
            return cls.empty()

    @classmethod
    def just(cls, v: T) -> 'Maybe[T]':
        return _JustMaybe(v)

    _empty: ta.ClassVar['Maybe']

    @classmethod
    def empty(cls) -> 'Maybe[T]':
        return Maybe._empty


##


class _Maybe(Maybe[T], Abstract):
    def __lt__(self, other):
        if not isinstance(other, _Maybe):
            return NotImplemented
        sp = self.present
        op = other.present
        if self.present and other.present:
            return self.must() < other.must()
        else:
            return op and not sp


@ta.final
class _JustMaybe(_Maybe[T]):
    __slots__ = ('_v', '_hash')

    def __init__(self, v: T) -> None:
        self._v = v

    @property
    def present(self) -> bool:
        return True

    def must(self) -> T:
        return self._v

    #

    def __repr__(self) -> str:
        return f'just({self._v!r})'

    _hash: int

    def __hash__(self) -> int:
        try:
            return self._hash
        except AttributeError:
            pass
        h = self._hash = hash((_JustMaybe, self._v))
        return h

    def __eq__(self, other):
        return (
            self.__class__ is other.__class__ and
            self._v == other._v  # noqa
        )


@ta.final
class _EmptyMaybe(_Maybe[T]):
    __slots__ = ()

    @property
    def present(self) -> bool:
        return False

    def must(self) -> T:
        raise Maybe.ValueNotPresentError

    #

    def __repr__(self) -> str:
        return 'empty()'

    def __hash__(self) -> int:
        return hash(_EmptyMaybe)

    def __eq__(self, other):
        return self.__class__ is other.__class__


Maybe._empty = _EmptyMaybe()  # noqa


##


setattr(Maybe, 'just', _JustMaybe)  # noqa
setattr(Maybe, 'empty', functools.partial(operator.attrgetter('_empty'), Maybe))


########################################
# ../../../omlish/lite/runtime.py


##


@cached_nullary
def is_debugger_attached() -> bool:
    return any(frame[1].endswith('pydevd.py') for frame in inspect.stack())


LITE_REQUIRED_PYTHON_VERSION = (3, 8)


def check_lite_runtime_version() -> None:
    if sys.version_info < LITE_REQUIRED_PYTHON_VERSION:
        raise OSError(f'Requires python {LITE_REQUIRED_PYTHON_VERSION}, got {sys.version_info} from {sys.executable}')  # noqa


########################################
# ../../../omlish/lite/timeouts.py
"""
TODO:
 - Event (/ Predicate)
"""


##


class Timeout(Abstract):
    @property
    @abc.abstractmethod
    def can_expire(self) -> bool:
        """Indicates whether or not this timeout will ever expire."""

        raise NotImplementedError

    @abc.abstractmethod
    def expired(self) -> bool:
        """Return whether or not this timeout has expired."""

        raise NotImplementedError

    @abc.abstractmethod
    def remaining(self) -> float:
        """Returns the time (in seconds) remaining until the timeout expires. May be negative and/or infinite."""

        raise NotImplementedError

    @abc.abstractmethod
    def __call__(self) -> float:
        """Returns the time (in seconds) remaining until the timeout expires, or raises if the timeout has expired."""

        raise NotImplementedError

    @abc.abstractmethod
    def or_(self, o: ta.Any) -> ta.Any:
        """Evaluates time remaining via remaining() if this timeout can expire, otherwise returns `o`."""

        raise NotImplementedError

    #

    @classmethod
    def _now(cls) -> float:
        return time.monotonic()

    #

    class DEFAULT:  # Noqa
        def __new__(cls, *args, **kwargs):  # noqa
            raise TypeError

    class _NOT_SPECIFIED:  # noqa
        def __new__(cls, *args, **kwargs):  # noqa
            raise TypeError

    @classmethod
    def of(
            cls,
            obj: TimeoutLike,
            default: ta.Union[TimeoutLike, ta.Type[_NOT_SPECIFIED]] = _NOT_SPECIFIED,
    ) -> 'Timeout':
        if obj is None:
            return InfiniteTimeout()

        elif isinstance(obj, Timeout):
            return obj

        elif isinstance(obj, (float, int)):
            return DeadlineTimeout(cls._now() + obj)

        elif isinstance(obj, ta.Iterable):
            return CompositeTimeout(*[Timeout.of(c) for c in obj])

        elif obj is Timeout.DEFAULT:
            if default is Timeout._NOT_SPECIFIED or default is Timeout.DEFAULT:
                raise RuntimeError('Must specify a default timeout')

            else:
                return Timeout.of(default)  # type: ignore[arg-type]

        else:
            raise TypeError(obj)

    @classmethod
    def of_deadline(cls, deadline: float) -> 'DeadlineTimeout':
        return DeadlineTimeout(deadline)

    @classmethod
    def of_predicate(cls, expired_fn: ta.Callable[[], bool]) -> 'PredicateTimeout':
        return PredicateTimeout(expired_fn)


class DeadlineTimeout(Timeout):
    def __init__(
            self,
            deadline: float,
            exc: ta.Union[ta.Type[BaseException], BaseException] = TimeoutError,
    ) -> None:
        super().__init__()

        self.deadline = deadline
        self.exc = exc

    @property
    def can_expire(self) -> bool:
        return True

    def expired(self) -> bool:
        return not (self.remaining() > 0)

    def remaining(self) -> float:
        return self.deadline - self._now()

    def __call__(self) -> float:
        if (rem := self.remaining()) > 0:
            return rem
        raise self.exc

    def or_(self, o: ta.Any) -> ta.Any:
        return self()


class InfiniteTimeout(Timeout):
    @property
    def can_expire(self) -> bool:
        return False

    def expired(self) -> bool:
        return False

    def remaining(self) -> float:
        return float('inf')

    def __call__(self) -> float:
        return float('inf')

    def or_(self, o: ta.Any) -> ta.Any:
        return o


class CompositeTimeout(Timeout):
    def __init__(self, *children: Timeout) -> None:
        super().__init__()

        self.children = children

    @property
    def can_expire(self) -> bool:
        return any(c.can_expire for c in self.children)

    def expired(self) -> bool:
        return any(c.expired() for c in self.children)

    def remaining(self) -> float:
        return min(c.remaining() for c in self.children)

    def __call__(self) -> float:
        return min(c() for c in self.children)

    def or_(self, o: ta.Any) -> ta.Any:
        if self.can_expire:
            return self()
        return o


class PredicateTimeout(Timeout):
    def __init__(
            self,
            expired_fn: ta.Callable[[], bool],
            exc: ta.Union[ta.Type[BaseException], BaseException] = TimeoutError,
    ) -> None:
        super().__init__()

        self.expired_fn = expired_fn
        self.exc = exc

    @property
    def can_expire(self) -> bool:
        return True

    def expired(self) -> bool:
        return self.expired_fn()

    def remaining(self) -> float:
        return float('inf')

    def __call__(self) -> float:
        if not self.expired_fn():
            return float('inf')
        raise self.exc

    def or_(self, o: ta.Any) -> ta.Any:
        return self()


########################################
# ../../../omlish/logs/infos.py
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
# ../../../omlish/logs/protocols.py


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


########################################
# ../../../omlish/logs/std/json.py
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
# ../../../omlish/os/temp.py


##


def make_temp_file(**kwargs: ta.Any) -> str:
    file_fd, file = tempfile.mkstemp(**kwargs)
    os.close(file_fd)
    return file


@contextlib.contextmanager
def temp_file_context(**kwargs: ta.Any) -> ta.Iterator[str]:
    path = make_temp_file(**kwargs)
    try:
        yield path
    finally:
        unlink_if_exists(path)


@contextlib.contextmanager
def temp_dir_context(
        root_dir: ta.Optional[str] = None,
        **kwargs: ta.Any,
) -> ta.Iterator[str]:
    path = tempfile.mkdtemp(dir=root_dir, **kwargs)
    try:
        yield path
    finally:
        shutil.rmtree(path, ignore_errors=True)


@contextlib.contextmanager
def temp_named_file_context(
        root_dir: ta.Optional[str] = None,
        cleanup: bool = True,
        **kwargs: ta.Any,
) -> ta.Iterator[tempfile._TemporaryFileWrapper]:  # noqa
    with tempfile.NamedTemporaryFile(dir=root_dir, delete=False, **kwargs) as f:
        try:
            yield f
        finally:
            if cleanup:
                shutil.rmtree(f.name, ignore_errors=True)


########################################
# ../../../omlish/sockets/bind.py
"""
TODO:
 - def parse: (<bind>)?:<port>, unix://, fd://
 - unix chown/chgrp
 - DupSocketBinder
 - udp
"""


##


class SocketBinder(Abstract, ta.Generic[SocketBinderConfigT]):
    @dc.dataclass(frozen=True)
    class Config:
        listen_backlog: int = 5

        allow_reuse_address: bool = True
        allow_reuse_port: bool = True

        set_inheritable: bool = False

        #

        @classmethod
        def of(cls, obj: CanSocketBinderConfig) -> 'SocketBinder.Config':
            if isinstance(obj, SocketBinder.Config):
                return obj

            elif isinstance(obj, int):
                return TcpSocketBinder.Config(
                    port=obj,
                )

            elif isinstance(obj, tuple):
                host, port = obj
                return TcpSocketBinder.Config(
                    host=host,
                    port=port,
                )

            elif isinstance(obj, str):
                return UnixSocketBinder.Config(
                    file=obj,
                )

            else:
                raise TypeError(obj)

    #

    def __init__(self, config: SocketBinderConfigT) -> None:
        super().__init__()

        self._config = config

    #

    @classmethod
    def of(cls, obj: CanSocketBinder) -> 'SocketBinder':
        if isinstance(obj, SocketBinder):
            return obj

        config: SocketBinder.Config
        if isinstance(obj, SocketBinder.Config):
            config = obj

        else:
            config = SocketBinder.Config.of(obj)

        if isinstance(config, TcpSocketBinder.Config):
            return TcpSocketBinder(config)

        elif isinstance(config, UnixSocketBinder.Config):
            return UnixSocketBinder(config)

        else:
            raise TypeError(config)

    #

    class Error(RuntimeError):
        pass

    class NotBoundError(Error):
        pass

    class AlreadyBoundError(Error):
        pass

    #

    @property
    @abc.abstractmethod
    def address_family(self) -> int:
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def address(self) -> SocketAddress:
        raise NotImplementedError

    #

    _socket: socket_.socket

    @property
    def is_bound(self) -> bool:
        return hasattr(self, '_socket')

    @property
    def socket(self) -> socket_.socket:
        try:
            return self._socket
        except AttributeError:
            raise self.NotBoundError from None

    _name: str

    @property
    def name(self) -> str:
        try:
            return self._name
        except AttributeError:
            raise self.NotBoundError from None

    _port: ta.Optional[int]

    @property
    def port(self) -> ta.Optional[int]:
        try:
            return self._port
        except AttributeError:
            raise self.NotBoundError from None

    #

    def fileno(self) -> int:
        return self.socket.fileno()

    #

    def __enter__(self: SocketBinderT) -> SocketBinderT:
        self.bind()

        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.close()

    #

    def _init_socket(self) -> None:
        if hasattr(self, '_socket'):
            raise self.AlreadyBoundError

        sock = socket_.socket(self.address_family, socket_.SOCK_STREAM)
        self._socket = sock

        if self._config.allow_reuse_address and hasattr(socket_, 'SO_REUSEADDR'):
            sock.setsockopt(socket_.SOL_SOCKET, socket_.SO_REUSEADDR, 1)

        # Since Linux 6.12.9, SO_REUSEPORT is not allowed on other address families than AF_INET/AF_INET6.
        if (
                self._config.allow_reuse_port and hasattr(socket_, 'SO_REUSEPORT') and
                self.address_family in (socket_.AF_INET, socket_.AF_INET6)
        ):
            try:
                sock.setsockopt(socket_.SOL_SOCKET, socket_.SO_REUSEPORT, 1)
            except OSError as err:
                if err.errno not in (errno.ENOPROTOOPT, errno.EINVAL):
                    raise

        if self._config.set_inheritable and hasattr(sock, 'set_inheritable'):
            sock.set_inheritable(True)

    def _pre_bind(self) -> None:
        pass

    def _post_bind(self) -> None:
        pass

    def bind(self) -> None:
        self._init_socket()

        self._pre_bind()

        self.socket.bind(self.address)

        self._post_bind()

        check.state(all(hasattr(self, a) for a in ('_socket', '_name', '_port')))

    #

    def close(self) -> None:
        if hasattr(self, '_socket'):
            self._socket.close()

    #

    def listen(self) -> None:
        self.socket.listen(self._config.listen_backlog)

    @abc.abstractmethod
    def accept(self, sock: ta.Optional[socket_.socket] = None) -> SocketAndAddress:
        raise NotImplementedError


##


class TcpSocketBinder(SocketBinder):
    @dc.dataclass(frozen=True)
    class Config(SocketBinder.Config):
        DEFAULT_HOST: ta.ClassVar[str] = 'localhost'
        host: str = DEFAULT_HOST

        port: int = 0

        def __post_init__(self) -> None:
            dataclass_maybe_post_init(super())
            check.non_empty_str(self.host)
            check.isinstance(self.port, int)
            check.arg(self.port > 0)

    def __init__(self, config: Config) -> None:
        super().__init__(check.isinstance(config, self.Config))

        self._address = (config.host, config.port)

    #

    address_family = socket_.AF_INET

    @property
    def address(self) -> SocketAddress:
        return self._address

    #

    def _post_bind(self) -> None:
        super()._post_bind()

        host, port, *_ = self.socket.getsockname()

        self._name = socket_.getfqdn(host)
        self._port = port

    #

    def accept(self, sock: ta.Optional[socket_.socket] = None) -> SocketAndAddress:
        if sock is None:
            sock = self.socket

        conn, client_address = sock.accept()
        return SocketAndAddress(conn, client_address)


##


class UnixSocketBinder(SocketBinder):
    @dc.dataclass(frozen=True)
    class Config(SocketBinder.Config):
        file: str = ''

        unlink: bool = False

        def __post_init__(self) -> None:
            dataclass_maybe_post_init(super())
            check.non_empty_str(self.file)

    def __init__(self, config: Config) -> None:
        super().__init__(check.isinstance(config, self.Config))

        self._address = config.file

    #

    address_family = socket_.AF_UNIX

    @property
    def address(self) -> SocketAddress:
        return self._address

    #

    def _pre_bind(self) -> None:
        super()._pre_bind()

        if self._config.unlink:
            try:
                if stat.S_ISSOCK(os.stat(self._config.file).st_mode):
                    os.unlink(self._config.file)
            except FileNotFoundError:
                pass

    def _post_bind(self) -> None:
        super()._post_bind()

        name = self.socket.getsockname()

        os.chmod(name, stat.S_IRWXU | stat.S_IRWXG)  # noqa

        self._name = name
        self._port = None

    #

    def accept(self, sock: ta.Optional[socket_.socket] = None) -> SocketAndAddress:
        if sock is None:
            sock = self.socket

        conn, _ = sock.accept()
        client_address = ('', 0)
        return SocketAndAddress(conn, client_address)


########################################
# ../../../omlish/sockets/handlers.py


##


class SocketHandler_(Abstract):  # noqa
    @abc.abstractmethod
    def __call__(self, addr: SocketAddress, f: SocketIoPair) -> None:
        raise NotImplementedError


class SocketHandlerClose(Exception):  # noqa
    pass


########################################
# ../../../omlish/text/mangle.py


##


@dc.dataclass(frozen=True)
class StringMangler:
    escape: str
    escaped: ta.Sequence[str]

    @classmethod
    def of(cls, escape: str, escaped: ta.Iterable[str]) -> 'StringMangler':
        check.arg(len(escape) == 1)
        return StringMangler(escape, sorted(set(escaped) - {escape}))

    def __post_init__(self) -> None:
        check.non_empty_str(self.escape)
        check.arg(len(self.escape) == 1)
        check.not_in(self.escape, self.escaped)
        check.arg(len(set(self.escaped)) == len(self.escaped))

    #

    @cached_nullary
    def replaced(self) -> ta.Tuple[str, ...]:
        return (self.escape, *self.escaped)

    @cached_nullary
    def replaced_set(self) -> ta.FrozenSet[str]:
        return frozenset(self.replaced())

    @cached_nullary
    def replaced_indexes(self) -> ta.Mapping[str, int]:
        return {s: i for i, s in enumerate(self.replaced())}

    @cached_nullary
    def replaced_pat(self) -> re.Pattern:
        return re.compile('|'.join(re.escape(k) for k in self.replaced()))

    #

    @cached_nullary
    def replacement_pad(self) -> int:
        return len('%x' % (len(self.replaced()),))  # noqa

    @cached_nullary
    def replacements(self) -> ta.Sequence[ta.Tuple[str, str]]:
        fmt = f'%0{self.replacement_pad()}x'
        return [
            (l, self.escape + fmt % (i,))
            for i, l in enumerate(self.replaced())
        ]

    @cached_nullary
    def replacements_dict(self) -> ta.Mapping[str, str]:
        return dict(self.replacements())

    @cached_nullary
    def inverse_replacements_dict(self) -> ta.Mapping[str, str]:
        return {v: k for k, v in self.replacements()}

    @cached_nullary
    def replacements_pat(self) -> re.Pattern:
        return re.compile(''.join([re.escape(self.escape), '.' * self.replacement_pad()]))

    #

    # def mangle(self, s: str) -> str:
    #     ecs = sorted(
    #         frozenset(s) & self.replaced_set(),
    #         key=self.replaced_indexes().__getitem__,
    #         )
    #     rd = self.replacements_dict()
    #     for l in ecs:
    #         r = rd[l]
    #         s = s.replace(l, r)
    #     return s

    def mangle(self, s: str) -> str:
        rd = self.replacements_dict()
        return self.replaced_pat().sub(lambda m: rd[m.group(0)], s)

    #

    # def unmangle(self, s: str) -> str:
    #     for l, r in reversed(self.replacements()):
    #         s = s.replace(r, l)
    #     return s

    def unmangle(self, s: str) -> str:
        ird = self.inverse_replacements_dict()
        return self.replacements_pat().sub(lambda m: ird[m.group(0)], s)


########################################
# ../../dataserver/targets.py


##


@dc.dataclass(frozen=True)
class DataServerTarget(Abstract):
    content_type: ta.Optional[str] = dc.field(default=None, metadata={OBJ_MARSHALER_OMIT_IF_NONE: True})
    content_length: ta.Optional[int] = dc.field(default=None, metadata={OBJ_MARSHALER_OMIT_IF_NONE: True})

    #

    @classmethod
    def of(
            cls,
            obj: ta.Union[
                'DataServerTarget',
                bytes,
                None,
            ] = None,
            *,

            file_path: ta.Optional[str] = None,
            url: ta.Optional[str] = None,

            **kwargs: ta.Any,
    ) -> 'DataServerTarget':
        if isinstance(obj, DataServerTarget):
            check.none(file_path)
            check.none(url)
            check.empty(kwargs)
            return obj

        elif isinstance(obj, bytes):
            return BytesDataServerTarget(
                data=obj,
                **kwargs,
            )

        elif file_path is not None:
            check.none(obj)
            check.none(url)
            return FileDataServerTarget(
                file_path=file_path,
                **kwargs,
            )

        elif url is not None:
            check.none(obj)
            check.none(file_path)
            return UrlDataServerTarget(
                url=url,
                **kwargs,
            )

        else:
            raise TypeError('No target type provided')

    #

    @classmethod
    def of_bytes(cls, data: bytes) -> 'BytesDataServerTarget':
        return BytesDataServerTarget(
            data=data,
            content_type='application/octet-stream',
        )

    @classmethod
    def of_text(cls, data: str) -> 'BytesDataServerTarget':
        return BytesDataServerTarget(
            data=data.encode('utf-8'),
            content_type='text/plain; charset=utf-8',
        )

    @classmethod
    def of_json(cls, data: str) -> 'BytesDataServerTarget':
        return BytesDataServerTarget(
            data=data.encode('utf-8'),
            content_type='application/json; charset=utf-8',
        )

    @classmethod
    def of_html(cls, data: str) -> 'BytesDataServerTarget':
        return BytesDataServerTarget(
            data=data.encode('utf-8'),
            content_type='text/html; charset=utf-8',
        )


@dc.dataclass(frozen=True)
class BytesDataServerTarget(DataServerTarget):
    data: ta.Optional[bytes] = None  # required


@dc.dataclass(frozen=True)
class FileDataServerTarget(DataServerTarget):
    file_path: ta.Optional[str] = None  # required

    def __post_init__(self) -> None:
        dataclass_maybe_post_init(super())
        check.non_empty_str(self.file_path)


@dc.dataclass(frozen=True)
class UrlDataServerTarget(DataServerTarget):
    url: ta.Optional[str] = None  # required
    methods: ta.Optional[ta.Sequence[str]] = None  # required

    def __post_init__(self) -> None:
        dataclass_maybe_post_init(super())
        check.non_empty_str(self.url)
        check.not_none(self.methods)
        check.not_isinstance(self.methods, str)


########################################
# ../../oci/data.py


##


@dc.dataclass()
class OciDataclass(Abstract):
    pass


##


@dc.dataclass()
class OciImageIndex(OciDataclass):
    manifests: ta.List[ta.Union['OciImageIndex', 'OciImageManifest']]

    annotations: ta.Optional[ta.Dict[str, str]] = None


#


@dc.dataclass()
class OciImageManifest(OciDataclass):
    config: 'OciImageConfig'

    layers: ta.List['OciImageLayer']

    annotations: ta.Optional[ta.Dict[str, str]] = None


#


@dc.dataclass()
class OciImageLayer(OciDataclass):
    class Kind(enum.Enum):
        TAR = enum.auto()
        TAR_GZIP = enum.auto()
        TAR_ZSTD = enum.auto()

        @property
        def compression(self) -> ta.Optional[OciCompression]:
            if self is self.TAR:
                return None
            elif self is self.TAR_GZIP:
                return OciCompression.GZIP
            elif self is self.TAR_ZSTD:
                return OciCompression.ZSTD
            else:
                raise ValueError(self)

        @classmethod
        def from_compression(cls, compression: ta.Optional[OciCompression]) -> 'OciImageLayer.Kind':
            if compression is None:
                return cls.TAR
            elif compression == OciCompression.GZIP:
                return cls.TAR_GZIP
            elif compression == OciCompression.ZSTD:
                return cls.TAR_ZSTD
            else:
                raise ValueError(compression)

    kind: Kind

    data: OciDataRef


#


@dc.dataclass()
class OciImageConfig(OciDataclass):
    """https://github.com/opencontainers/image-spec/blob/92353b0bee778725c617e7d57317b568a7796bd0/config.md"""

    architecture: str
    os: str

    @dc.dataclass()
    class RootFs:
        type: str
        diff_ids: ta.List[str]

    rootfs: RootFs

    #

    created: ta.Optional[str] = dc.field(default=None, metadata={OBJ_MARSHALER_OMIT_IF_NONE: True})
    author: ta.Optional[str] = dc.field(default=None, metadata={OBJ_MARSHALER_OMIT_IF_NONE: True})
    os_version: ta.Optional[str] = dc.field(default=None, metadata={OBJ_MARSHALER_FIELD_KEY: 'os.version', OBJ_MARSHALER_OMIT_IF_NONE: True})  # noqa
    os_features: ta.Optional[ta.List[str]] = dc.field(default=None, metadata={OBJ_MARSHALER_FIELD_KEY: 'os.features', OBJ_MARSHALER_OMIT_IF_NONE: True})  # noqa
    variant: ta.Optional[str] = dc.field(default=None, metadata={OBJ_MARSHALER_OMIT_IF_NONE: True})

    """
    config object, OPTIONAL
        User string, OPTIONAL
        ExposedPorts object, OPTIONAL
        Env array of strings, OPTIONAL
        Entrypoint array of strings, OPTIONAL
        Cmd array of strings, OPTIONAL
        Volumes object, OPTIONAL
        WorkingDir string, OPTIONAL
        Labels object, OPTIONAL
        StopSignal string, OPTIONAL
        ArgsEscaped boolean, OPTIONAL
        Memory integer, OPTIONAL
        MemorySwap integer, OPTIONAL
        CpuShares integer, OPTIONAL
        Healthcheck object, OPTIONAL
    """
    config: ta.Optional[ta.Dict[str, ta.Any]] = dc.field(default=None, metadata={OBJ_MARSHALER_OMIT_IF_NONE: True})

    @dc.dataclass()
    class History:
        created: ta.Optional[str] = dc.field(default=None, metadata={OBJ_MARSHALER_OMIT_IF_NONE: True})
        author: ta.Optional[str] = dc.field(default=None, metadata={OBJ_MARSHALER_OMIT_IF_NONE: True})
        created_by: ta.Optional[str] = dc.field(default=None, metadata={OBJ_MARSHALER_OMIT_IF_NONE: True})
        comment: ta.Optional[str] = dc.field(default=None, metadata={OBJ_MARSHALER_OMIT_IF_NONE: True})
        empty_layer: ta.Optional[bool] = dc.field(default=None, metadata={OBJ_MARSHALER_OMIT_IF_NONE: True})

    history: ta.Optional[ta.List[History]] = dc.field(default=None, metadata={OBJ_MARSHALER_OMIT_IF_NONE: True})


##


def is_empty_oci_dataclass(obj: OciDataclass) -> bool:
    if not isinstance(obj, OciDataclass):
        raise TypeError(obj)

    elif isinstance(obj, OciImageIndex):
        return not obj.manifests

    elif isinstance(obj, OciImageManifest):
        return not obj.layers

    else:
        return False


##


def get_single_leaf_oci_image_index(image_index: OciImageIndex) -> OciImageIndex:
    while True:
        child_manifest = check.single(image_index.manifests)
        if isinstance(child_manifest, OciImageManifest):
            break
        image_index = check.isinstance(child_manifest, OciImageIndex)

    return image_index


def get_single_oci_image_manifest(image_index: OciImageIndex) -> OciImageManifest:
    child_index = check.single(image_index.manifests)
    return check.isinstance(child_index, OciImageManifest)


########################################
# ../../oci/repositories.py


##


class OciRepository(Abstract):
    @abc.abstractmethod
    def contains_blob(self, digest: str) -> bool:
        raise NotImplementedError

    @abc.abstractmethod
    def read_blob(self, digest: str) -> bytes:
        raise NotImplementedError

    @abc.abstractmethod
    def ref_blob(self, digest: str) -> OciDataRef:
        raise NotImplementedError

    @classmethod
    def of(
            cls,
            obj: ta.Union[
                'OciRepository',
                str,
                tarfile.TarFile,
                ta.Mapping[str, bytes],
            ],
    ) -> 'OciRepository':
        if isinstance(obj, OciRepository):
            return obj

        elif isinstance(obj, str):
            check.arg(os.path.isdir(obj))
            return DirectoryOciRepository(obj)

        elif isinstance(obj, tarfile.TarFile):
            return TarFileOciRepository(obj)

        elif isinstance(obj, ta.Mapping):
            return DictOciRepository(obj)

        else:
            raise TypeError(obj)


class FileOciRepository(OciRepository, Abstract):
    @abc.abstractmethod
    def read_file(self, path: str) -> bytes:
        raise NotImplementedError


#


class DirectoryOciRepository(FileOciRepository):
    def __init__(self, data_dir: str) -> None:
        super().__init__()

        self._data_dir = check.non_empty_str(data_dir)

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({self._data_dir!r})'

    def read_file(self, path: str) -> bytes:
        full_path = os.path.join(self._data_dir, path)
        check.arg(is_path_in_dir(self._data_dir, full_path))
        with open(full_path, 'rb') as f:
            return f.read()

    def blob_path(self, digest: str) -> str:
        scheme, value = digest.split(':')
        return os.path.join('blobs', scheme, value)

    def blob_full_path(self, digest: str) -> str:
        path = self.blob_path(digest)
        full_path = os.path.join(self._data_dir, path)
        check.arg(is_path_in_dir(self._data_dir, full_path))
        return full_path

    def contains_blob(self, digest: str) -> bool:
        return os.path.isfile(self.blob_full_path(digest))

    def read_blob(self, digest: str) -> bytes:
        return self.read_file(self.blob_path(digest))

    def ref_blob(self, digest: str) -> OciDataRef:
        return FileOciDataRef(self.blob_full_path(digest))


#


class TarFileOciRepository(FileOciRepository):
    def __init__(self, tar_file: tarfile.TarFile) -> None:
        super().__init__()

        check.arg('r' in tar_file.mode)

        self._tar_file = tar_file

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({self._tar_file!r})'

    def read_file(self, path: str) -> bytes:
        if (ti := self._tar_file.getmember(path)) is None:
            raise FileNotFoundError(path)
        with check.not_none(self._tar_file.extractfile(ti)) as f:
            return f.read()

    def blob_name(self, digest: str) -> str:
        scheme, value = digest.split(':')
        return os.path.join('blobs', scheme, value)

    def contains_blob(self, digest: str) -> bool:
        try:
            self._tar_file.getmember(self.blob_name(digest))
        except KeyError:
            return False
        else:
            return True

    def read_blob(self, digest: str) -> bytes:
        if (ti := self._tar_file.getmember(self.blob_name(digest))) is None:
            raise KeyError(digest)
        with check.not_none(self._tar_file.extractfile(ti)) as f:
            return f.read()

    def ref_blob(self, digest: str) -> OciDataRef:
        return TarFileOciDataRef(
            tar_file=self._tar_file,
            tar_info=self._tar_file.getmember(self.blob_name(digest)),
        )


#


class DictOciRepository(OciRepository):
    def __init__(self, blobs: ta.Mapping[str, bytes]) -> None:
        super().__init__()

        self._blobs = blobs

    def contains_blob(self, digest: str) -> bool:
        return digest in self._blobs

    def read_blob(self, digest: str) -> bytes:
        return self._blobs[digest]

    def ref_blob(self, digest: str) -> OciDataRef:
        return BytesOciDataRef(self._blobs[digest])


########################################
# ../../oci/tars.py


##


class WrittenOciDataTarFileInfo(ta.NamedTuple):
    compressed_sz: int
    compressed_sha256: str

    tar_sz: int
    tar_sha256: str


class OciDataTarWriter(ExitStacked):
    def __init__(
            self,
            f: ta.BinaryIO,
            compression: ta.Optional[OciCompression] = None,
            *,
            gzip_level: int = 1,
            zstd_level: int = 10,
    ) -> None:
        super().__init__()

        self._f = f
        self._compression = compression

        self._gzip_level = gzip_level
        self._zstd_level = zstd_level

    class _FileWrapper:
        def __init__(self, f):
            super().__init__()

            self._f = f
            self._c = 0
            self._h = hashlib.sha256()

        @property
        def size(self) -> int:
            return self._c

        def sha256(self) -> str:
            return self._h.hexdigest()

        def write(self, d):
            self._c += len(d)
            self._h.update(d)
            self._f.write(d)

        def tell(self) -> int:
            return self._f.tell()

    _cw: _FileWrapper
    _cf: ta.BinaryIO

    _tw: _FileWrapper
    _tf: tarfile.TarFile

    def info(self) -> WrittenOciDataTarFileInfo:
        return WrittenOciDataTarFileInfo(
            compressed_sz=self._cw.size,
            compressed_sha256=self._cw.sha256(),

            tar_sz=self._tw.size,
            tar_sha256=self._tw.sha256(),
        )

    def _enter_contexts(self) -> None:
        self._cw = self._FileWrapper(self._f)

        if self._compression is OciCompression.GZIP:
            self._cf = self._enter_context(
                gzip.GzipFile(  # type: ignore
                    fileobj=self._cw,
                    mode='wb',
                    compresslevel=self._gzip_level,
                ),
            )

        elif self._compression is OciCompression.ZSTD:
            import zstandard  # noqa

            zc = zstandard.ZstdCompressor(
                level=self._zstd_level,
            )
            self._cf = self._enter_context(zc.stream_writer(self._cw))  # type: ignore

        elif self._compression is None:
            self._cf = self._cw  # type: ignore

        else:
            raise ValueError(self._compression)

        #

        self._tw = self._FileWrapper(self._cf)

        self._tf = self._enter_context(
            tarfile.open(  # type: ignore  # noqa
                fileobj=self._tw,
                mode='w',
            ),
        )

    def tar_file(self) -> tarfile.TarFile:
        return self._tf

    def add_file(self, ti: tarfile.TarInfo, f: ta.Optional[ta.BinaryIO] = None) -> None:
        self._tf.addfile(ti, f)


def write_oci_data_tar_file(
        f: ta.BinaryIO,
        data: ta.Mapping[str, OciDataRef],
) -> WrittenOciDataTarFileInfo:
    with OciDataTarWriter(f) as tgw:
        for n, dr in data.items():
            ti = tarfile.TarInfo(name=n)
            ri = OciDataRefInfo(dr)
            ti.size = ri.size()
            with open_oci_data_ref(dr) as df:
                tgw.add_file(ti, df)

    return tgw.info()


########################################
# ../../../omlish/asyncs/asyncio/sockets.py


##


async def asyncio_wait_until_can_connect(
        host: ta.Any = None,
        port: ta.Any = None,
        *,
        timeout: TimeoutLike = None,
        on_fail: ta.Optional[ta.Callable[[BaseException], None]] = None,
        sleep_s: float = .1,
        exception: ta.Union[ta.Type[BaseException], ta.Tuple[ta.Type[BaseException], ...]] = (Exception,),
) -> None:
    timeout = Timeout.of(timeout)

    async def inner():
        while True:
            timeout()

            try:
                reader, writer = await asyncio.open_connection(host, port)

            except asyncio.CancelledError:
                raise

            except exception as e:  # noqa
                if on_fail is not None:
                    on_fail(e)

            else:
                writer.close()
                await asyncio.wait_for(writer.wait_closed(), timeout=timeout.or_(None))
                break

            await asyncio.sleep(min(sleep_s, timeout.remaining()))

    if timeout() != float('inf'):
        await asyncio.wait_for(inner(), timeout=timeout())
    else:
        await inner()


########################################
# ../../../omlish/asyncs/asyncio/timeouts.py


##


def asyncio_maybe_timeout(
        fut: AwaitableT,
        timeout: TimeoutLike = None,
) -> AwaitableT:
    if timeout is not None:
        fut = asyncio.wait_for(fut, Timeout.of(timeout)())  # type: ignore
    return fut


########################################
# ../../../omlish/http/handlers.py


##


@dc.dataclass(frozen=True)
class HttpHandlerRequest:
    client_address: SocketAddress
    method: str
    path: str
    headers: HttpHeaders
    data: ta.Optional[bytes]


@dc.dataclass(frozen=True)
class HttpHandlerResponse:
    status: ta.Union[http.HTTPStatus, int]

    headers: ta.Optional[ta.Mapping[str, str]] = None
    data: ta.Optional[HttpHandlerResponseData] = None
    close_connection: ta.Optional[bool] = None

    def close(self) -> None:
        if isinstance(d := self.data, HttpHandlerResponseStreamedData):
            d.close()


@dc.dataclass(frozen=True)
class HttpHandlerResponseStreamedData:
    iter: ta.Iterable[bytes]
    length: ta.Optional[int] = None

    def close(self) -> None:
        if hasattr(d := self.iter, 'close'):
            d.close()  # noqa


class HttpHandlerError(Exception):
    pass


class UnsupportedMethodHttpHandlerError(Exception):
    pass


class HttpHandler_(Abstract):  # noqa
    @abc.abstractmethod
    def __call__(self, req: HttpHandlerRequest) -> HttpHandlerResponse:
        raise NotImplementedError


##


@dc.dataclass(frozen=True)
class LoggingHttpHandler(HttpHandler_):
    handler: HttpHandler
    log: LoggerLike
    level: int = logging.DEBUG

    def __call__(self, req: HttpHandlerRequest) -> HttpHandlerResponse:
        self.log.log(self.level, '%r', req)
        resp = self.handler(req)
        self.log.log(self.level, '%r', resp)
        return resp


@dc.dataclass(frozen=True)
class ExceptionLoggingHttpHandler(HttpHandler_):
    handler: HttpHandler
    log: LoggerLike
    message: ta.Union[str, ta.Callable[[HttpHandlerRequest, BaseException], str]] = 'Error in http handler'

    def __call__(self, req: HttpHandlerRequest) -> HttpHandlerResponse:
        try:
            return self.handler(req)
        except Exception as e:  # noqa
            if callable(msg := self.message):
                msg = msg(req, e)
            self.log.exception(msg)
            raise


##


@dc.dataclass(frozen=True)
class BytesResponseHttpHandler(HttpHandler_):
    data: bytes

    status: ta.Union[http.HTTPStatus, int] = 200
    content_type: ta.Optional[str] = 'application/octet-stream'
    headers: ta.Optional[ta.Mapping[str, str]] = None
    close_connection: bool = True

    def __call__(self, req: HttpHandlerRequest) -> HttpHandlerResponse:
        return HttpHandlerResponse(
            status=self.status,
            headers={
                **({'Content-Type': self.content_type} if self.content_type else {}),
                'Content-Length': str(len(self.data)),
                **(self.headers or {}),
            },
            data=self.data,
            close_connection=self.close_connection,
        )


@dc.dataclass(frozen=True)
class StringResponseHttpHandler(HttpHandler_):
    data: str

    status: ta.Union[http.HTTPStatus, int] = 200
    content_type: ta.Optional[str] = 'text/plain; charset=utf-8'
    headers: ta.Optional[ta.Mapping[str, str]] = None
    close_connection: bool = True

    def __call__(self, req: HttpHandlerRequest) -> HttpHandlerResponse:
        data = self.data.encode('utf-8')
        return HttpHandlerResponse(
            status=self.status,
            headers={
                **({'Content-Type': self.content_type} if self.content_type else {}),
                'Content-Length': str(len(data)),
                **(self.headers or {}),
            },
            data=data,
            close_connection=self.close_connection,
        )


########################################
# ../../../omlish/lite/inject.py


###
# types


@dc.dataclass(frozen=True)
class InjectorKey(ta.Generic[T]):
    # Before PEP-560 typing.Generic was a metaclass with a __new__ that takes a 'cls' arg, so instantiating a dataclass
    # with kwargs (such as through dc.replace) causes `TypeError: __new__() got multiple values for argument 'cls'`.
    # See:
    #  - https://github.com/python/cpython/commit/d911e40e788fb679723d78b6ea11cabf46caed5a
    #  - https://gist.github.com/wrmsr/4468b86efe9f373b6b114bfe85b98fd3
    cls_: InjectorKeyCls

    tag: ta.Any = None
    array: bool = False


def is_valid_injector_key_cls(cls: ta.Any) -> bool:
    return isinstance(cls, type) or is_new_type(cls)


def check_valid_injector_key_cls(cls: T) -> T:
    if not is_valid_injector_key_cls(cls):
        raise TypeError(cls)
    return cls


##


class InjectorProvider(Abstract):
    @abc.abstractmethod
    def provider_fn(self) -> InjectorProviderFn:
        raise NotImplementedError


##


@dc.dataclass(frozen=True)
class InjectorBinding:
    key: InjectorKey
    provider: InjectorProvider

    def __post_init__(self) -> None:
        check.isinstance(self.key, InjectorKey)
        check.isinstance(self.provider, InjectorProvider)


class InjectorBindings(Abstract):
    @abc.abstractmethod
    def bindings(self) -> ta.Iterator[InjectorBinding]:
        raise NotImplementedError

##


class Injector(Abstract):
    @abc.abstractmethod
    def try_provide(self, key: ta.Any) -> Maybe[ta.Any]:
        raise NotImplementedError

    @abc.abstractmethod
    def provide(self, key: ta.Any) -> ta.Any:
        raise NotImplementedError

    @abc.abstractmethod
    def provide_kwargs(
            self,
            obj: ta.Any,
            *,
            skip_args: int = 0,
            skip_kwargs: ta.Optional[ta.Iterable[ta.Any]] = None,
    ) -> ta.Mapping[str, ta.Any]:
        raise NotImplementedError

    @abc.abstractmethod
    def inject(
            self,
            obj: ta.Any,
            *,
            args: ta.Optional[ta.Sequence[ta.Any]] = None,
            kwargs: ta.Optional[ta.Mapping[str, ta.Any]] = None,
    ) -> ta.Any:
        raise NotImplementedError

    def __getitem__(
            self,
            target: ta.Union[InjectorKey[T], ta.Type[T]],
    ) -> T:
        return self.provide(target)


###
# exceptions


class InjectorError(Exception):
    pass


@dc.dataclass()
class InjectorKeyError(InjectorError):
    key: InjectorKey

    source: ta.Any = None
    name: ta.Optional[str] = None


class UnboundInjectorKeyError(InjectorKeyError):
    pass


class DuplicateInjectorKeyError(InjectorKeyError):
    pass


class CyclicDependencyInjectorKeyError(InjectorKeyError):
    pass


###
# keys


def as_injector_key(o: ta.Any) -> InjectorKey:
    if o is inspect.Parameter.empty:
        raise TypeError(o)
    if isinstance(o, InjectorKey):
        return o
    if is_valid_injector_key_cls(o):
        return InjectorKey(o)
    raise TypeError(o)


###
# providers


@dc.dataclass(frozen=True)
class FnInjectorProvider(InjectorProvider):
    fn: ta.Any

    def __post_init__(self) -> None:
        check.not_isinstance(self.fn, type)

    def provider_fn(self) -> InjectorProviderFn:
        def pfn(i: Injector) -> ta.Any:
            return i.inject(self.fn)

        return pfn


@dc.dataclass(frozen=True)
class CtorInjectorProvider(InjectorProvider):
    cls_: type

    def __post_init__(self) -> None:
        check.isinstance(self.cls_, type)

    def provider_fn(self) -> InjectorProviderFn:
        def pfn(i: Injector) -> ta.Any:
            return i.inject(self.cls_)

        return pfn


@dc.dataclass(frozen=True)
class ConstInjectorProvider(InjectorProvider):
    v: ta.Any

    def provider_fn(self) -> InjectorProviderFn:
        return lambda _: self.v


@dc.dataclass(frozen=True)
class SingletonInjectorProvider(InjectorProvider):
    p: InjectorProvider

    def __post_init__(self) -> None:
        check.isinstance(self.p, InjectorProvider)

    def provider_fn(self) -> InjectorProviderFn:
        v = not_set = object()

        def pfn(i: Injector) -> ta.Any:
            nonlocal v
            if v is not_set:
                v = ufn(i)
            return v

        ufn = self.p.provider_fn()
        return pfn


@dc.dataclass(frozen=True)
class LinkInjectorProvider(InjectorProvider):
    k: InjectorKey

    def __post_init__(self) -> None:
        check.isinstance(self.k, InjectorKey)

    def provider_fn(self) -> InjectorProviderFn:
        def pfn(i: Injector) -> ta.Any:
            return i.provide(self.k)

        return pfn


@dc.dataclass(frozen=True)
class ArrayInjectorProvider(InjectorProvider):
    ps: ta.Sequence[InjectorProvider]

    def provider_fn(self) -> InjectorProviderFn:
        ps = [p.provider_fn() for p in self.ps]

        def pfn(i: Injector) -> ta.Any:
            rv = []
            for ep in ps:
                o = ep(i)
                rv.append(o)
            return rv

        return pfn


###
# bindings


@dc.dataclass(frozen=True)
class _InjectorBindings(InjectorBindings):
    bs: ta.Optional[ta.Sequence[InjectorBinding]] = None
    ps: ta.Optional[ta.Sequence[InjectorBindings]] = None

    def bindings(self) -> ta.Iterator[InjectorBinding]:
        if self.bs is not None:
            yield from self.bs
        if self.ps is not None:
            for p in self.ps:
                yield from p.bindings()


def as_injector_bindings(*args: InjectorBindingOrBindings) -> InjectorBindings:
    bs: ta.List[InjectorBinding] = []
    ps: ta.List[InjectorBindings] = []

    for a in args:
        if isinstance(a, InjectorBindings):
            ps.append(a)
        elif isinstance(a, InjectorBinding):
            bs.append(a)
        else:
            raise TypeError(a)

    return _InjectorBindings(
        bs or None,
        ps or None,
    )


##


def build_injector_provider_map(bs: InjectorBindings) -> ta.Mapping[InjectorKey, InjectorProvider]:
    pm: ta.Dict[InjectorKey, InjectorProvider] = {}
    am: ta.Dict[InjectorKey, ta.List[InjectorProvider]] = {}

    for b in bs.bindings():
        if b.key.array:
            al = am.setdefault(b.key, [])
            if isinstance(b.provider, ArrayInjectorProvider):
                al.extend(b.provider.ps)
            else:
                al.append(b.provider)
        else:
            if b.key in pm:
                raise KeyError(b.key)
            pm[b.key] = b.provider

    if am:
        for k, aps in am.items():
            pm[k] = ArrayInjectorProvider(aps)

    return pm


###
# overrides


@dc.dataclass(frozen=True)
class OverridesInjectorBindings(InjectorBindings):
    p: InjectorBindings
    m: ta.Mapping[InjectorKey, InjectorBinding]

    def bindings(self) -> ta.Iterator[InjectorBinding]:
        for b in self.p.bindings():
            yield self.m.get(b.key, b)


def injector_override(p: InjectorBindings, *args: InjectorBindingOrBindings) -> InjectorBindings:
    m: ta.Dict[InjectorKey, InjectorBinding] = {}

    for b in as_injector_bindings(*args).bindings():
        if b.key in m:
            raise DuplicateInjectorKeyError(b.key)
        m[b.key] = b

    return OverridesInjectorBindings(p, m)


###
# scopes


class InjectorScope(Abstract):
    def __init__(
            self,
            *,
            _i: Injector,
    ) -> None:
        super().__init__()

        self._i = _i

        all_seeds: ta.Iterable[_InjectorScopeSeed] = self._i.provide(InjectorKey(_InjectorScopeSeed, array=True))
        self._sks = {s.k for s in all_seeds if s.sc is type(self)}

    #

    @dc.dataclass(frozen=True)
    class State:
        seeds: ta.Dict[InjectorKey, ta.Any]
        provisions: ta.Dict[InjectorKey, ta.Any] = dc.field(default_factory=dict)

    def new_state(self, vs: ta.Mapping[InjectorKey, ta.Any]) -> State:
        vs = dict(vs)
        check.equal(set(vs.keys()), self._sks)
        return InjectorScope.State(vs)

    #

    @abc.abstractmethod
    def state(self) -> State:
        raise NotImplementedError

    @abc.abstractmethod
    def enter(self, vs: ta.Mapping[InjectorKey, ta.Any]) -> ta.ContextManager[None]:
        raise NotImplementedError


class ExclusiveInjectorScope(InjectorScope, Abstract):
    _st: ta.Optional[InjectorScope.State] = None

    def state(self) -> InjectorScope.State:
        return check.not_none(self._st)

    @contextlib.contextmanager
    def enter(self, vs: ta.Mapping[InjectorKey, ta.Any]) -> ta.Iterator[None]:
        check.none(self._st)
        self._st = self.new_state(vs)
        try:
            yield
        finally:
            self._st = None


class ContextvarInjectorScope(InjectorScope, Abstract):
    _cv: contextvars.ContextVar

    def __init_subclass__(cls, **kwargs: ta.Any) -> None:
        super().__init_subclass__(**kwargs)

        check.not_in(Abstract, cls.__bases__)
        check.not_in(abc.ABC, cls.__bases__)
        check.state(not hasattr(cls, '_cv'))
        cls._cv = contextvars.ContextVar(f'{cls.__name__}_cv')

    def state(self) -> InjectorScope.State:
        return self._cv.get()

    @contextlib.contextmanager
    def enter(self, vs: ta.Mapping[InjectorKey, ta.Any]) -> ta.Iterator[None]:
        try:
            self._cv.get()
        except LookupError:
            pass
        else:
            raise RuntimeError(f'Scope already entered: {self}')
        st = self.new_state(vs)
        tok = self._cv.set(st)
        try:
            yield
        finally:
            self._cv.reset(tok)


#


@dc.dataclass(frozen=True)
class ScopedInjectorProvider(InjectorProvider):
    p: InjectorProvider
    k: InjectorKey
    sc: ta.Type[InjectorScope]

    def __post_init__(self) -> None:
        check.isinstance(self.p, InjectorProvider)
        check.isinstance(self.k, InjectorKey)
        check.issubclass(self.sc, InjectorScope)

    def provider_fn(self) -> InjectorProviderFn:
        def pfn(i: Injector) -> ta.Any:
            st = i[self.sc].state()
            try:
                return st.provisions[self.k]
            except KeyError:
                pass
            v = ufn(i)
            st.provisions[self.k] = v
            return v

        ufn = self.p.provider_fn()
        return pfn


@dc.dataclass(frozen=True)
class _ScopeSeedInjectorProvider(InjectorProvider):
    k: InjectorKey
    sc: ta.Type[InjectorScope]

    def __post_init__(self) -> None:
        check.isinstance(self.k, InjectorKey)
        check.issubclass(self.sc, InjectorScope)

    def provider_fn(self) -> InjectorProviderFn:
        def pfn(i: Injector) -> ta.Any:
            st = i[self.sc].state()
            return st.seeds[self.k]
        return pfn


def bind_injector_scope(sc: ta.Type[InjectorScope]) -> InjectorBindingOrBindings:
    return InjectorBinder.bind(sc, singleton=True)


#


@dc.dataclass(frozen=True)
class _InjectorScopeSeed:
    sc: ta.Type['InjectorScope']
    k: InjectorKey

    def __post_init__(self) -> None:
        check.issubclass(self.sc, InjectorScope)
        check.isinstance(self.k, InjectorKey)


def bind_injector_scope_seed(k: ta.Any, sc: ta.Type[InjectorScope]) -> InjectorBindingOrBindings:
    kk = as_injector_key(k)
    return as_injector_bindings(
        InjectorBinding(kk, _ScopeSeedInjectorProvider(kk, sc)),
        InjectorBinder.bind(_InjectorScopeSeed(sc, kk), array=True),
    )


###
# inspection


class _InjectionInspection(ta.NamedTuple):
    signature: inspect.Signature
    type_hints: ta.Mapping[str, ta.Any]
    args_offset: int


_INJECTION_INSPECTION_CACHE: ta.MutableMapping[ta.Any, _InjectionInspection] = weakref.WeakKeyDictionary()


def _do_injection_inspect(obj: ta.Any) -> _InjectionInspection:
    tgt = obj

    # inspect.signature(eval_str=True) was added in 3.10 and we have to support 3.8, so we have to get_type_hints to
    # eval str annotations *in addition to* getting the signature for parameter information.
    uw = tgt
    has_partial = False
    while True:
        if isinstance(uw, functools.partial):
            uw = uw.func
            has_partial = True
        else:
            if (uw2 := inspect.unwrap(uw)) is uw:
                break
            uw = uw2

    has_args_offset = False

    if isinstance(tgt, type) and tgt.__new__ is not object.__new__:
        # Python 3.8's inspect.signature can't handle subclasses overriding __new__, always generating *args/**kwargs.
        #  - https://bugs.python.org/issue40897
        #  - https://github.com/python/cpython/commit/df7c62980d15acd3125dfbd81546dad359f7add7
        tgt = tgt.__init__  # type: ignore[misc]
        has_args_offset = True

    if tgt in (object.__init__, object.__new__):
        # inspect strips self for types but not the underlying methods.
        def dummy(self):
            pass
        tgt = dummy
        has_args_offset = True

    if has_partial and has_args_offset:
        # TODO: unwrap partials masking parameters like modern python
        raise InjectorError(
            'Injector inspection does not currently support both an args offset and a functools.partial: '
            f'{obj}',
        )

    return _InjectionInspection(
        inspect.signature(tgt),
        ta.get_type_hints(uw),
        1 if has_args_offset else 0,
    )


def _injection_inspect(obj: ta.Any) -> _InjectionInspection:
    try:
        return _INJECTION_INSPECTION_CACHE[obj]
    except TypeError:
        return _do_injection_inspect(obj)
    except KeyError:
        pass
    insp = _do_injection_inspect(obj)
    _INJECTION_INSPECTION_CACHE[obj] = insp
    return insp


class InjectionKwarg(ta.NamedTuple):
    name: str
    key: InjectorKey
    has_default: bool


class InjectionKwargsTarget(ta.NamedTuple):
    obj: ta.Any
    kwargs: ta.Sequence[InjectionKwarg]


def build_injection_kwargs_target(
        obj: ta.Any,
        *,
        skip_args: int = 0,
        skip_kwargs: ta.Optional[ta.Iterable[str]] = None,
        raw_optional: bool = False,
) -> InjectionKwargsTarget:
    insp = _injection_inspect(obj)

    params = list(insp.signature.parameters.values())

    skip_names: ta.Set[str] = set()
    if skip_kwargs is not None:
        skip_names.update(check.not_isinstance(skip_kwargs, str))

    seen: ta.Set[InjectorKey] = set()
    kws: ta.List[InjectionKwarg] = []
    for p in params[insp.args_offset + skip_args:]:
        if p.name in skip_names:
            continue

        if p.annotation is inspect.Signature.empty:
            if p.default is not inspect.Parameter.empty:
                raise KeyError(f'{obj}, {p.name}')
            continue

        if p.kind not in (inspect.Parameter.POSITIONAL_OR_KEYWORD, inspect.Parameter.KEYWORD_ONLY):
            raise TypeError(insp)

        # 3.8 inspect.signature doesn't eval_str but typing.get_type_hints does, so prefer that.
        ann = insp.type_hints.get(p.name, p.annotation)
        if (
                not raw_optional and
                is_optional_alias(ann)
        ):
            ann = get_optional_alias_arg(ann)

        k = as_injector_key(ann)

        if k in seen:
            raise DuplicateInjectorKeyError(k)
        seen.add(k)

        kws.append(InjectionKwarg(
            p.name,
            k,
            p.default is not inspect.Parameter.empty,
        ))

    return InjectionKwargsTarget(
        obj,
        kws,
    )


###
# injector


_INJECTOR_INJECTOR_KEY: InjectorKey[Injector] = InjectorKey(Injector)


@dc.dataclass(frozen=True)
class _InjectorEager:
    key: InjectorKey


_INJECTOR_EAGER_ARRAY_KEY: InjectorKey[_InjectorEager] = InjectorKey(_InjectorEager, array=True)


class _Injector(Injector):
    _DEFAULT_BINDINGS: ta.ClassVar[ta.List[InjectorBinding]] = []

    def __init__(self, bs: InjectorBindings, p: ta.Optional[Injector] = None) -> None:
        super().__init__()

        self._bs = check.isinstance(bs, InjectorBindings)
        self._p: ta.Optional[Injector] = check.isinstance(p, (Injector, type(None)))

        self._pfm = {
            k: v.provider_fn()
            for k, v in build_injector_provider_map(as_injector_bindings(
                *self._DEFAULT_BINDINGS,
                bs,
            )).items()
        }

        if _INJECTOR_INJECTOR_KEY in self._pfm:
            raise DuplicateInjectorKeyError(_INJECTOR_INJECTOR_KEY)

        self.__cur_req: ta.Optional[_Injector._Request] = None

        if _INJECTOR_EAGER_ARRAY_KEY in self._pfm:
            for e in self.provide(_INJECTOR_EAGER_ARRAY_KEY):
                self.provide(e.key)

    class _Request:
        def __init__(self, injector: '_Injector') -> None:
            super().__init__()

            self._injector = injector
            self._provisions: ta.Dict[InjectorKey, Maybe] = {}
            self._seen_keys: ta.Set[InjectorKey] = set()

        def handle_key(self, key: InjectorKey) -> Maybe[Maybe]:
            try:
                return Maybe.just(self._provisions[key])
            except KeyError:
                pass
            if key in self._seen_keys:
                raise CyclicDependencyInjectorKeyError(key)
            self._seen_keys.add(key)
            return Maybe.empty()

        def handle_provision(self, key: InjectorKey, mv: Maybe) -> Maybe:
            check.in_(key, self._seen_keys)
            check.not_in(key, self._provisions)
            self._provisions[key] = mv
            return mv

    @contextlib.contextmanager
    def _current_request(self) -> ta.Generator[_Request, None, None]:
        if (cr := self.__cur_req) is not None:
            yield cr
            return

        cr = self._Request(self)
        try:
            self.__cur_req = cr
            yield cr
        finally:
            self.__cur_req = None

    def try_provide(self, key: ta.Any) -> Maybe[ta.Any]:
        key = as_injector_key(key)

        cr: _Injector._Request
        with self._current_request() as cr:
            if (rv := cr.handle_key(key)).present:
                return rv.must()

            if key == _INJECTOR_INJECTOR_KEY:
                return cr.handle_provision(key, Maybe.just(self))

            fn = self._pfm.get(key)
            if fn is not None:
                return cr.handle_provision(key, Maybe.just(fn(self)))

            if self._p is not None:
                pv = self._p.try_provide(key)
                if pv is not None:
                    return cr.handle_provision(key, Maybe.empty())

            return cr.handle_provision(key, Maybe.empty())

    def provide(self, key: ta.Any) -> ta.Any:
        v = self.try_provide(key)
        if v.present:
            return v.must()
        raise UnboundInjectorKeyError(key)

    def provide_kwargs(
            self,
            obj: ta.Any,
            *,
            skip_args: int = 0,
            skip_kwargs: ta.Optional[ta.Iterable[ta.Any]] = None,
    ) -> ta.Mapping[str, ta.Any]:
        kt = build_injection_kwargs_target(
            obj,
            skip_args=skip_args,
            skip_kwargs=skip_kwargs,
        )

        ret: ta.Dict[str, ta.Any] = {}
        for kw in kt.kwargs:
            if kw.has_default:
                if not (mv := self.try_provide(kw.key)).present:
                    continue
                v = mv.must()
            else:
                v = self.provide(kw.key)
            ret[kw.name] = v
        return ret

    def inject(
            self,
            obj: ta.Any,
            *,
            args: ta.Optional[ta.Sequence[ta.Any]] = None,
            kwargs: ta.Optional[ta.Mapping[str, ta.Any]] = None,
    ) -> ta.Any:
        provided = self.provide_kwargs(
            obj,
            skip_args=len(args) if args is not None else 0,
            skip_kwargs=kwargs if kwargs is not None else None,
        )

        return obj(
            *(args if args is not None else ()),
            **(kwargs if kwargs is not None else {}),
            **provided,
        )


###
# binder


class InjectorBinder:
    def __new__(cls, *args, **kwargs):  # noqa
        raise TypeError

    _FN_TYPES: ta.ClassVar[ta.Tuple[type, ...]] = (
        types.FunctionType,
        types.MethodType,

        classmethod,
        staticmethod,

        functools.partial,
        functools.partialmethod,
    )

    @classmethod
    def _is_fn(cls, obj: ta.Any) -> bool:
        return isinstance(obj, cls._FN_TYPES)

    @classmethod
    def bind_as_fn(cls, icls: ta.Type[T]) -> ta.Type[T]:
        check.isinstance(icls, type)
        if icls not in cls._FN_TYPES:
            cls._FN_TYPES = (*cls._FN_TYPES, icls)
        return icls

    _BANNED_BIND_TYPES: ta.ClassVar[ta.Tuple[type, ...]] = (
        InjectorProvider,
    )

    @classmethod
    def bind(
            cls,
            obj: ta.Any,
            *,
            key: ta.Any = None,
            tag: ta.Any = None,
            array: ta.Optional[bool] = None,  # noqa

            to_fn: ta.Any = None,
            to_ctor: ta.Any = None,
            to_const: ta.Any = None,
            to_key: ta.Any = None,

            in_: ta.Optional[ta.Type[InjectorScope]] = None,
            singleton: bool = False,

            eager: bool = False,
    ) -> InjectorBindingOrBindings:
        if obj is None or obj is inspect.Parameter.empty:
            raise TypeError(obj)
        if isinstance(obj, cls._BANNED_BIND_TYPES):
            raise TypeError(obj)

        #

        if key is not None:
            key = as_injector_key(key)

        #

        has_to = (
            to_fn is not None or
            to_ctor is not None or
            to_const is not None or
            to_key is not None
        )
        if isinstance(obj, InjectorKey):
            if key is None:
                key = obj
        elif isinstance(obj, type):
            if not has_to:
                to_ctor = obj
            if key is None:
                key = InjectorKey(obj)
        elif cls._is_fn(obj) and not has_to:
            to_fn = obj
            if key is None:
                insp = _injection_inspect(obj)
                key_cls: ta.Any = check_valid_injector_key_cls(check.not_none(insp.type_hints.get('return')))
                key = InjectorKey(key_cls)
        else:
            if to_const is not None:
                raise TypeError('Cannot bind instance with to_const')
            to_const = obj
            if key is None:
                key = InjectorKey(type(obj))
        del has_to

        #

        if tag is not None:
            if key.tag is not None:
                raise TypeError('Tag already set')
            key = dc.replace(key, tag=tag)

        if array is not None:
            key = dc.replace(key, array=array)

        #

        providers: ta.List[InjectorProvider] = []
        if to_fn is not None:
            providers.append(FnInjectorProvider(to_fn))
        if to_ctor is not None:
            providers.append(CtorInjectorProvider(to_ctor))
        if to_const is not None:
            providers.append(ConstInjectorProvider(to_const))
        if to_key is not None:
            providers.append(LinkInjectorProvider(as_injector_key(to_key)))
        if not providers:
            raise TypeError('Must specify provider')
        if len(providers) > 1:
            raise TypeError('May not specify multiple providers')
        provider = check.single(providers)

        #

        pws: ta.List[ta.Any] = []
        if in_ is not None:
            check.issubclass(in_, InjectorScope)
            check.not_in(Abstract, in_.__bases__)
            pws.append(functools.partial(ScopedInjectorProvider, k=key, sc=in_))
        if singleton:
            pws.append(SingletonInjectorProvider)
        if len(pws) > 1:
            raise TypeError('May not specify multiple provider wrappers')
        elif pws:
            provider = check.single(pws)(provider)

        #

        binding = InjectorBinding(key, provider)

        #

        extras: ta.List[InjectorBinding] = []

        if eager:
            extras.append(bind_injector_eager_key(key))

        #

        if extras:
            return as_injector_bindings(binding, *extras)
        else:
            return binding


###
# injection helpers


def make_injector_factory(
        fn: ta.Callable[..., T],
        cls: U,
        ann: ta.Any = None,
) -> ta.Callable[..., U]:
    if ann is None:
        ann = cls

    def outer(injector: Injector) -> ann:
        def inner(*args, **kwargs):
            return injector.inject(fn, args=args, kwargs=kwargs)
        return cls(inner)  # type: ignore

    return outer


def bind_injector_array(
        obj: ta.Any = None,
        *,
        tag: ta.Any = None,
) -> InjectorBindingOrBindings:
    key = as_injector_key(obj)
    if tag is not None:
        if key.tag is not None:
            raise ValueError('Must not specify multiple tags')
        key = dc.replace(key, tag=tag)

    if key.array:
        raise ValueError('Key must not be array')

    return InjectorBinding(
        dc.replace(key, array=True),
        ArrayInjectorProvider([]),
    )


def make_injector_array_type(
        ele: ta.Union[InjectorKey, InjectorKeyCls],
        cls: U,
        ann: ta.Any = None,
) -> ta.Callable[..., U]:
    if isinstance(ele, InjectorKey):
        if not ele.array:
            raise InjectorError('Provided key must be array', ele)
        key = ele
    else:
        key = dc.replace(as_injector_key(ele), array=True)

    if ann is None:
        ann = cls

    def inner(injector: Injector) -> ann:
        return cls(injector.provide(key))  # type: ignore[operator]

    return inner


def bind_injector_eager_key(key: ta.Any) -> InjectorBinding:
    return InjectorBinding(_INJECTOR_EAGER_ARRAY_KEY, ConstInjectorProvider(_InjectorEager(as_injector_key(key))))


###
# api


class InjectionApi:
    # keys

    def as_key(self, o: ta.Any) -> InjectorKey:
        return as_injector_key(o)

    def array(self, o: ta.Any) -> InjectorKey:
        return dc.replace(as_injector_key(o), array=True)

    def tag(self, o: ta.Any, t: ta.Any) -> InjectorKey:
        return dc.replace(as_injector_key(o), tag=t)

    # bindings

    def as_bindings(self, *args: InjectorBindingOrBindings) -> InjectorBindings:
        return as_injector_bindings(*args)

    # overrides

    def override(self, p: InjectorBindings, *args: InjectorBindingOrBindings) -> InjectorBindings:
        return injector_override(p, *args)

    # scopes

    def bind_scope(self, sc: ta.Type[InjectorScope]) -> InjectorBindingOrBindings:
        return bind_injector_scope(sc)

    def bind_scope_seed(self, k: ta.Any, sc: ta.Type[InjectorScope]) -> InjectorBindingOrBindings:
        return bind_injector_scope_seed(k, sc)

    # injector

    def create_injector(self, *args: InjectorBindingOrBindings, parent: ta.Optional[Injector] = None) -> Injector:
        return _Injector(as_injector_bindings(*args), parent)

    # binder

    def bind(
            self,
            obj: ta.Any,
            *,
            key: ta.Any = None,
            tag: ta.Any = None,
            array: ta.Optional[bool] = None,  # noqa

            to_fn: ta.Any = None,
            to_ctor: ta.Any = None,
            to_const: ta.Any = None,
            to_key: ta.Any = None,

            in_: ta.Optional[ta.Type[InjectorScope]] = None,
            singleton: bool = False,

            eager: bool = False,
    ) -> InjectorBindingOrBindings:
        return InjectorBinder.bind(
            obj,

            key=key,
            tag=tag,
            array=array,

            to_fn=to_fn,
            to_ctor=to_ctor,
            to_const=to_const,
            to_key=to_key,

            in_=in_,
            singleton=singleton,

            eager=eager,
        )

    # helpers

    def bind_factory(
            self,
            fn: ta.Callable[..., T],
            cls_: U,
            ann: ta.Any = None,
    ) -> InjectorBindingOrBindings:
        return self.bind(make_injector_factory(fn, cls_, ann))

    def bind_array(
            self,
            obj: ta.Any = None,
            *,
            tag: ta.Any = None,
    ) -> InjectorBindingOrBindings:
        return bind_injector_array(obj, tag=tag)

    def bind_array_type(
            self,
            ele: ta.Union[InjectorKey, InjectorKeyCls],
            cls_: U,
            ann: ta.Any = None,
    ) -> InjectorBindingOrBindings:
        return self.bind(make_injector_array_type(ele, cls_, ann))


inj = InjectionApi()


########################################
# ../../../omlish/logs/contexts.py


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
# ../../../omlish/logs/standard.py
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
# ../../../omlish/logs/utils.py


##


def exception_logging(log):  # noqa
    def outer(fn):
        @functools.wraps(fn)
        def inner(*args, **kwargs):
            try:
                return fn(*args, **kwargs)
            except Exception:
                log.exception('Error in %r', fn)
                raise

        return inner

    return outer


##


class LogTimingContext:
    DEFAULT_LOG: ta.ClassVar[ta.Optional[LoggerLike]] = None

    class _NOT_SPECIFIED:  # noqa
        def __new__(cls, *args, **kwargs):  # noqa
            raise TypeError

    def __init__(
            self,
            description: str,
            *,
            log: ta.Union[LoggerLike, ta.Type[_NOT_SPECIFIED], None] = _NOT_SPECIFIED,  # noqa
            level: int = logging.DEBUG,
    ) -> None:
        super().__init__()

        self._description = description
        if log is self._NOT_SPECIFIED:
            log = self.DEFAULT_LOG  # noqa
        self._log: ta.Optional[LoggerLike] = log  # type: ignore
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


########################################
# ../../../omlish/sockets/server/handlers.py


##


class SocketServerHandler_(Abstract):  # noqa
    @abc.abstractmethod
    def __call__(self, conn: SocketAndAddress) -> None:
        raise NotImplementedError


##


@dc.dataclass(frozen=True)
class StandardSocketServerHandler(SocketServerHandler_):
    handler: SocketServerHandler

    timeout: ta.Optional[float] = None

    # http://bugs.python.org/issue6192
    # TODO: https://eklitzke.org/the-caveats-of-tcp-nodelay
    disable_nagle_algorithm: bool = False

    no_close: bool = False

    def __call__(self, conn: SocketAndAddress) -> None:
        try:
            if self.timeout is not None:
                conn.socket.settimeout(self.timeout)

            if self.disable_nagle_algorithm:
                conn.socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, True)

            self.handler(conn)

        finally:
            close_socket_immediately(conn.socket)


#


@dc.dataclass(frozen=True)
class CallbackWrappedSocketServerHandler(SocketServerHandler_):
    handler: SocketServerHandler

    before_handle: ta.Optional[SocketServerHandler] = None
    after_handle: ta.Optional[SocketServerHandler] = None

    # Return True if suppress like __exit__
    on_error: ta.Optional[ta.Callable[[SocketAndAddress, Exception], bool]] = None

    finally_: ta.Optional[SocketServerHandler] = None

    def __call__(self, conn: SocketAndAddress) -> None:
        try:
            if (before_handle := self.before_handle) is not None:
                before_handle(conn)

            self.handler(conn)

        except Exception as e:
            if (on_error := self.on_error) is not None and on_error(conn, e):
                pass
            else:
                raise

        else:
            if (after_handle := self.after_handle) is not None:
                after_handle(conn)

        finally:
            if (finally_ := self.finally_) is not None:
                finally_(conn)


#


@dc.dataclass(frozen=True)
class SocketHandlerSocketServerHandler(SocketServerHandler_):
    handler: SocketHandler

    r_buf_size: int = -1
    w_buf_size: int = 0

    def __call__(self, conn: SocketAndAddress) -> None:
        fp = SocketIoPair.from_socket(
            conn.socket,
            r_buf_size=self.r_buf_size,
            w_buf_size=self.w_buf_size,
        )

        self.handler(conn.address, fp)


#


@dc.dataclass(frozen=True)
class SocketWrappingSocketServerHandler(SocketServerHandler_):
    handler: SocketServerHandler
    wrapper: ta.Callable[[SocketAndAddress], SocketAndAddress]

    def __call__(self, conn: SocketAndAddress) -> None:
        wrapped_conn = self.wrapper(conn)
        self.handler(wrapped_conn)


#

@dc.dataclass(frozen=True)
class ExecutorSocketServerHandler(SocketServerHandler_):
    handler: SocketServerHandler
    executor: cf.Executor

    def __call__(self, conn: SocketAndAddress) -> None:
        self.executor.submit(self.handler, conn)


#


@dc.dataclass(frozen=True)
class ExceptionLoggingSocketServerHandler(SocketServerHandler_):
    handler: SocketServerHandler
    log: LoggerLike

    ignored: ta.Optional[ta.Container[ta.Type[Exception]]] = None

    def __call__(self, conn: SocketAndAddress) -> None:
        try:
            return self.handler(conn)

        except Exception as e:  # noqa
            if (ignored := self.ignored) is None or type(e) not in ignored:
                self.log.exception('Error in handler %r for conn %r', self.handler, conn)

            raise


########################################
# ../../../omlish/subprocesses/run.py


##


@dc.dataclass(frozen=True)
class SubprocessRunOutput(ta.Generic[T]):
    proc: T

    returncode: int  # noqa

    stdout: ta.Optional[bytes] = None
    stderr: ta.Optional[bytes] = None


##


@dc.dataclass(frozen=True)
class SubprocessRun:
    cmd: ta.Sequence[str]
    input: ta.Any = None
    timeout: TimeoutLike = None
    check: bool = False
    capture_output: ta.Optional[bool] = None
    kwargs: ta.Optional[ta.Mapping[str, ta.Any]] = None

    #

    _FIELD_NAMES: ta.ClassVar[ta.FrozenSet[str]]

    def replace(self, **kwargs: ta.Any) -> 'SubprocessRun':
        if not kwargs:
            return self

        field_kws = {}
        extra_kws = {}
        for k, v in kwargs.items():
            if k in self._FIELD_NAMES:
                field_kws[k] = v
            else:
                extra_kws[k] = v

        return dc.replace(self, **{
            **dict(kwargs={
                **(self.kwargs or {}),
                **extra_kws,
            }),
            **field_kws,  # passing a kwarg named 'kwargs' intentionally clobbers
        })

    #

    @classmethod
    def of(
            cls,
            *cmd: str,
            input: ta.Any = None,  # noqa
            timeout: TimeoutLike = None,
            check: bool = False,  # noqa
            capture_output: ta.Optional[bool] = None,
            **kwargs: ta.Any,
    ) -> 'SubprocessRun':
        return cls(
            cmd=cmd,
            input=input,
            timeout=timeout,
            check=check,
            capture_output=capture_output,
            kwargs=kwargs,
        )

    #

    _DEFAULT_SUBPROCESSES: ta.ClassVar[ta.Optional[ta.Any]] = None  # AbstractSubprocesses

    def run(
            self,
            subprocesses: ta.Optional[ta.Any] = None,  # AbstractSubprocesses
            **kwargs: ta.Any,
    ) -> SubprocessRunOutput:
        if subprocesses is None:
            subprocesses = self._DEFAULT_SUBPROCESSES
        return check.not_none(subprocesses).run_(self.replace(**kwargs))

    _DEFAULT_ASYNC_SUBPROCESSES: ta.ClassVar[ta.Optional[ta.Any]] = None  # AbstractAsyncSubprocesses

    async def async_run(
            self,
            async_subprocesses: ta.Optional[ta.Any] = None,  # AbstractAsyncSubprocesses
            **kwargs: ta.Any,
    ) -> SubprocessRunOutput:
        if async_subprocesses is None:
            async_subprocesses = self._DEFAULT_ASYNC_SUBPROCESSES
        return await check.not_none(async_subprocesses).run_(self.replace(**kwargs))

    _DEFAULT_MAYSYNC_SUBPROCESSES: ta.ClassVar[ta.Optional[ta.Any]] = None  # AbstractMaysyncSubprocesses

    async def maysync_run(
            self,
            maysync_subprocesses: ta.Optional[ta.Any] = None,  # AbstractMaysyncSubprocesses
            **kwargs: ta.Any,
    ) -> SubprocessRunOutput:
        if maysync_subprocesses is None:
            maysync_subprocesses = self._DEFAULT_MAYSYNC_SUBPROCESSES
        return await check.not_none(maysync_subprocesses).run_(self.replace(**kwargs))


SubprocessRun._FIELD_NAMES = frozenset(fld.name for fld in dc.fields(SubprocessRun))  # noqa


##


class SubprocessRunnable(Abstract, ta.Generic[T]):
    @abc.abstractmethod
    def make_run(self) -> SubprocessRun:
        raise NotImplementedError

    @abc.abstractmethod
    def handle_run_output(self, output: SubprocessRunOutput) -> T:
        raise NotImplementedError

    #

    def run(
            self,
            subprocesses: ta.Optional[ta.Any] = None,  # AbstractSubprocesses
            **kwargs: ta.Any,
    ) -> T:
        return self.handle_run_output(self.make_run().run(subprocesses, **kwargs))

    async def async_run(
            self,
            async_subprocesses: ta.Optional[ta.Any] = None,  # AbstractAsyncSubprocesses
            **kwargs: ta.Any,
    ) -> T:
        return self.handle_run_output(await self.make_run().async_run(async_subprocesses, **kwargs))

    async def maysync_run(
            self,
            maysync_subprocesses: ta.Optional[ta.Any] = None,  # AbstractMaysyncSubprocesses
            **kwargs: ta.Any,
    ) -> T:
        return self.handle_run_output(await self.make_run().maysync_run(maysync_subprocesses, **kwargs))


########################################
# ../../../omlish/subprocesses/wrap.py
"""
This bypasses debuggers attaching to spawned subprocess children that look like python processes. See:

  https://github.com/JetBrains/intellij-community/blob/e9d8f126c286acf9df3ff272f440b305bf2ff585/python/helpers/pydev/_pydev_bundle/pydev_monkey.py
"""


##


_SUBPROCESS_SHELL_WRAP_EXECS = False


def subprocess_shell_wrap_exec(*cmd: str) -> ta.Tuple[str, ...]:
    return ('sh', '-c', ' '.join(map(shlex.quote, cmd)))


def subprocess_maybe_shell_wrap_exec(*cmd: str) -> ta.Tuple[str, ...]:
    if _SUBPROCESS_SHELL_WRAP_EXECS or is_debugger_attached():
        return subprocess_shell_wrap_exec(*cmd)
    else:
        return cmd


########################################
# ../../dataserver/handlers.py


##


@dc.dataclass(frozen=True)
class DataServerRequest:
    method: str
    path: str


@dc.dataclass(frozen=True)
class DataServerResponse:
    status: int
    headers: ta.Optional[ta.Mapping[str, str]] = None
    body: ta.Optional[io.IOBase] = None

    #

    def close(self) -> None:
        if (body := self.body) is not None:
            body.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


class DataServerError(Exception):
    pass


class DataServerHandler(Abstract):
    @abc.abstractmethod
    def handle(self, req: DataServerRequest) -> DataServerResponse:
        raise NotImplementedError


##


class DataServerTargetHandler(DataServerHandler, Abstract, ta.Generic[DataServerTargetT]):
    def __init__(self, target: DataServerTargetT) -> None:
        super().__init__()

        self._target = target

    #

    @classmethod
    def for_target(cls, tgt: DataServerTarget, **kwargs: ta.Any) -> 'DataServerTargetHandler':
        try:
            hc = _DATA_SERVER_TARGET_HANDLERS[type(tgt)]
        except KeyError:
            raise TypeError(tgt)  # noqa
        else:
            return hc(tgt, **kwargs)

    #

    def _make_headers(self) -> ta.Dict[str, str]:
        dct = {}
        if (ct := self._target.content_type) is not None:
            dct['Content-Type'] = ct
        if (cl := self._target.content_length) is not None:
            dct['Content-Length'] = str(cl)
        return dct


#


_DATA_SERVER_TARGET_HANDLERS: ta.Dict[ta.Type[DataServerTarget], ta.Type[DataServerTargetHandler]] = {}


def _register_data_server_target_handler(*tcs):
    def inner(hc):
        check.issubclass(hc, DataServerTargetHandler)
        for tc in tcs:
            check.issubclass(tc, DataServerTarget)
            check.not_in(tc, _DATA_SERVER_TARGET_HANDLERS)
            _DATA_SERVER_TARGET_HANDLERS[tc] = hc
        return hc
    return inner


#


@_register_data_server_target_handler(BytesDataServerTarget)
class BytesDataServerTargetHandler(DataServerTargetHandler[BytesDataServerTarget]):
    def _make_headers(self) -> ta.Dict[str, str]:
        dct = super()._make_headers()
        if 'Content-Length' not in dct and self._target.data is not None:
            dct['Content-Length'] = str(len(self._target.data))
        return dct

    def handle(self, req: DataServerRequest) -> DataServerResponse:
        if req.method not in ('GET', 'HEAD'):
            return DataServerResponse(http.HTTPStatus.METHOD_NOT_ALLOWED)

        return DataServerResponse(
            http.HTTPStatus.OK,
            headers=self._make_headers(),
            body=io.BytesIO(self._target.data) if self._target.data is not None and req.method == 'GET' else None,
        )


#


@_register_data_server_target_handler(FileDataServerTarget)
class FileDataServerTargetHandler(DataServerTargetHandler[FileDataServerTarget]):
    def handle(self, req: DataServerRequest) -> DataServerResponse:
        if req.method == 'HEAD':
            try:
                st = os.stat(check.not_none(self._target.file_path))
            except FileNotFoundError:
                return DataServerResponse(http.HTTPStatus.NOT_FOUND)

            return DataServerResponse(
                http.HTTPStatus.OK,
                headers={
                    'Content-Length': str(st.st_size),
                    **self._make_headers(),
                },
            )

        elif req.method == 'GET':
            try:
                f = open(check.not_none(self._target.file_path), 'rb')  # noqa
            except FileNotFoundError:
                return DataServerResponse(http.HTTPStatus.NOT_FOUND)

            try:
                sz = os.fstat(f.fileno())

                return DataServerResponse(
                    http.HTTPStatus.OK,
                    headers={
                        'Content-Length': str(sz.st_size),
                        **self._make_headers(),
                    },
                    body=f,  # noqa
                )

            except Exception:  # noqa
                f.close()
                raise

        else:
            return DataServerResponse(http.HTTPStatus.METHOD_NOT_ALLOWED)


#


@_register_data_server_target_handler(UrlDataServerTarget)
class UrlDataServerTargetHandler(DataServerTargetHandler[UrlDataServerTarget]):
    def handle(self, req: DataServerRequest) -> DataServerResponse:
        if req.method not in check.not_none(self._target.methods):
            return DataServerResponse(http.HTTPStatus.METHOD_NOT_ALLOWED)

        resp: http.client.HTTPResponse = urllib.request.urlopen(urllib.request.Request(  # noqa
            method=req.method,
            url=check.not_none(self._target.url),
        ))

        try:
            return DataServerResponse(
                resp.status,
                headers=dict(resp.headers.items()),
                body=resp,
            )

        except Exception:  # noqa
            resp.close()
            raise


########################################
# ../../dataserver/routes.py
"""
TODO:
 - generate to nginx config
"""


##


@dc.dataclass(frozen=True)
class DataServerRoute:
    paths: ta.Sequence[str]
    target: DataServerTarget

    @classmethod
    def of(cls, obj: ta.Union[
        'DataServerRoute',
        ta.Tuple[
            ta.Union[str, ta.Iterable[str]],
            DataServerTarget,
        ],
    ]) -> 'DataServerRoute':
        if isinstance(obj, cls):
            return obj

        elif isinstance(obj, tuple):
            p, t = obj

            if isinstance(p, str):
                p = [p]

            return cls(
                paths=tuple(p),
                target=check.isinstance(t, DataServerTarget),
            )

        else:
            raise TypeError(obj)

    @classmethod
    def of_(cls, *objs: ta.Any) -> ta.List['DataServerRoute']:
        return [cls.of(obj) for obj in objs]


########################################
# ../../oci/media.py


##


OCI_MEDIA_FIELDS: ta.Collection[str] = frozenset([
    'schema_version',
    'media_type',
])


@dc.dataclass()
class OciMediaDataclass(Abstract):
    SCHEMA_VERSION: ta.ClassVar[int]

    @property
    def schema_version(self) -> int:
        raise TypeError

    MEDIA_TYPE: ta.ClassVar[str]

    @property
    def media_type(self) -> str:
        raise TypeError

    #

    def __init_subclass__(cls, **kwargs: ta.Any) -> None:
        super().__init_subclass__(**kwargs)

        for a in OCI_MEDIA_FIELDS:
            check.in_(a, cls.__dict__)


_REGISTERED_OCI_MEDIA_DATACLASSES: ta.Dict[str, ta.Type[OciMediaDataclass]] = {}


def _register_oci_media_dataclass(cls):
    check.issubclass(cls, OciMediaDataclass)
    check.arg(dc.is_dataclass(cls))
    mt = check.non_empty_str(cls.__dict__['MEDIA_TYPE'])
    check.not_in(mt, _REGISTERED_OCI_MEDIA_DATACLASSES)
    _REGISTERED_OCI_MEDIA_DATACLASSES[mt] = cls
    return cls


def get_registered_oci_media_dataclass(media_type: str) -> ta.Optional[ta.Type[OciMediaDataclass]]:
    return _REGISTERED_OCI_MEDIA_DATACLASSES.get(media_type)


def unmarshal_oci_media_dataclass(
        dct: ta.Mapping[str, ta.Any],
        *,
        media_type: ta.Optional[str] = None,
) -> ta.Any:
    if media_type is None:
        media_type = check.non_empty_str(dct['mediaType'])
    cls = _REGISTERED_OCI_MEDIA_DATACLASSES[media_type]
    return unmarshal_obj(dct, cls)


##


@dc.dataclass()
class OciMediaDescriptor:
    """https://github.com/opencontainers/image-spec/blob/92353b0bee778725c617e7d57317b568a7796bd0/descriptor.md#properties"""  # noqa

    media_type: str = dc.field(metadata={OBJ_MARSHALER_FIELD_KEY: 'mediaType'})
    digest: str
    size: int

    #

    urls: ta.Optional[ta.Sequence[str]] = dc.field(default=None, metadata={OBJ_MARSHALER_OMIT_IF_NONE: True})
    annotations: ta.Optional[ta.Mapping[str, str]] = dc.field(default=None, metadata={OBJ_MARSHALER_OMIT_IF_NONE: True})  # noqa
    data: ta.Optional[str] = dc.field(default=None, metadata={OBJ_MARSHALER_OMIT_IF_NONE: True})
    artifact_type: ta.Optional[str] = dc.field(default=None, metadata={OBJ_MARSHALER_FIELD_KEY: 'artifactType', OBJ_MARSHALER_OMIT_IF_NONE: True})  # noqa

    #

    platform: ta.Optional[ta.Mapping[str, ta.Any]] = dc.field(default=None, metadata={OBJ_MARSHALER_OMIT_IF_NONE: True})  # noqa


##


@_register_oci_media_dataclass
@dc.dataclass()
class OciMediaImageIndex(OciMediaDataclass):
    """https://github.com/opencontainers/image-spec/blob/92353b0bee778725c617e7d57317b568a7796bd0/image-index.md"""

    manifests: ta.Sequence[OciMediaDescriptor]  # -> OciMediaImageIndex | OciMediaImageManifest

    #

    annotations: ta.Optional[ta.Mapping[str, str]] = dc.field(default=None, metadata={OBJ_MARSHALER_OMIT_IF_NONE: True})  # noqa

    #

    SCHEMA_VERSION: ta.ClassVar[int] = 2
    schema_version: int = dc.field(default=SCHEMA_VERSION, metadata={OBJ_MARSHALER_FIELD_KEY: 'schemaVersion'})

    MEDIA_TYPE: ta.ClassVar[str] = 'application/vnd.oci.image.index.v1+json'
    media_type: str = dc.field(default=MEDIA_TYPE, metadata={OBJ_MARSHALER_FIELD_KEY: 'mediaType'})


#


@_register_oci_media_dataclass
@dc.dataclass()
class OciMediaImageManifest(OciMediaDataclass):
    """https://github.com/opencontainers/image-spec/blob/92353b0bee778725c617e7d57317b568a7796bd0/manifest.md"""

    config: OciMediaDescriptor  # -> OciMediaImageConfig

    layers: ta.Sequence[OciMediaDescriptor]

    #

    annotations: ta.Optional[ta.Mapping[str, str]] = dc.field(default=None, metadata={OBJ_MARSHALER_OMIT_IF_NONE: True})  # noqa

    #

    SCHEMA_VERSION: ta.ClassVar[int] = 2
    schema_version: int = dc.field(default=SCHEMA_VERSION, metadata={OBJ_MARSHALER_FIELD_KEY: 'schemaVersion'})

    MEDIA_TYPE: ta.ClassVar[str] = 'application/vnd.oci.image.manifest.v1+json'
    media_type: str = dc.field(default=MEDIA_TYPE, metadata={OBJ_MARSHALER_FIELD_KEY: 'mediaType'})


#


OCI_IMAGE_LAYER_KIND_MEDIA_TYPES: ta.Mapping[OciImageLayer.Kind, str] = {
    OciImageLayer.Kind.TAR: 'application/vnd.oci.image.layer.v1.tar',
    OciImageLayer.Kind.TAR_GZIP: 'application/vnd.oci.image.layer.v1.tar+gzip',
    OciImageLayer.Kind.TAR_ZSTD: 'application/vnd.oci.image.layer.v1.tar+zstd',
}

OCI_IMAGE_LAYER_KIND_MEDIA_TYPES_: ta.Mapping[str, OciImageLayer.Kind] = {
    v: k
    for k, v in OCI_IMAGE_LAYER_KIND_MEDIA_TYPES.items()
}


#


@_register_oci_media_dataclass
@dc.dataclass()
class OciMediaImageConfig(OciImageConfig, OciMediaDataclass):
    SCHEMA_VERSION: ta.ClassVar[int] = 2
    schema_version: int = dc.field(default=SCHEMA_VERSION, metadata={OBJ_MARSHALER_FIELD_KEY: 'schemaVersion'})

    MEDIA_TYPE: ta.ClassVar[str] = 'application/vnd.oci.image.config.v1+json'
    media_type: str = dc.field(default=MEDIA_TYPE, metadata={OBJ_MARSHALER_FIELD_KEY: 'mediaType'})


##


OCI_MANIFEST_MEDIA_TYPES: ta.AbstractSet[str] = frozenset([
    OciMediaImageIndex.MEDIA_TYPE,
    OciMediaImageManifest.MEDIA_TYPE,
])


########################################
# ../../oci/pack/packing.py


##


class OciLayerPacker(ExitStacked):
    def __init__(
            self,
            input_file_path: str,
            output_file_paths: ta.Sequence[str],
            *,
            compression: ta.Optional[OciCompression] = None,
    ) -> None:
        super().__init__()

        self._input_file_path = input_file_path
        self._output_file_paths = list(output_file_paths)
        self._compression = compression

        self._output_file_indexes_by_name: ta.Dict[str, int] = {}

    #

    @cached_nullary
    def _input_tar_file(self) -> tarfile.TarFile:
        # FIXME: check uncompressed
        return self._enter_context(tarfile.open(self._input_file_path))

    #

    @cached_nullary
    def _entries_by_name(self) -> ta.Mapping[str, tarfile.TarInfo]:
        return {
            info.name: info
            for info in self._input_tar_file().getmembers()
        }

    #

    class _CategorizedEntries(ta.NamedTuple):
        files_by_name: ta.Mapping[str, tarfile.TarInfo]
        non_files_by_name: ta.Mapping[str, tarfile.TarInfo]
        links_by_name: ta.Mapping[str, tarfile.TarInfo]

    @cached_nullary
    def _categorized_entries(self) -> _CategorizedEntries:
        files_by_name: ta.Dict[str, tarfile.TarInfo] = {}
        non_files_by_name: ta.Dict[str, tarfile.TarInfo] = {}
        links_by_name: ta.Dict[str, tarfile.TarInfo] = {}

        for name, info in self._entries_by_name().items():
            if info.type in tarfile.REGULAR_TYPES:
                files_by_name[name] = info
            elif info.type in (tarfile.LNKTYPE, tarfile.GNUTYPE_LONGLINK):
                links_by_name[name] = info
            else:
                non_files_by_name[name] = info

        return self._CategorizedEntries(
            files_by_name=files_by_name,
            non_files_by_name=non_files_by_name,
            links_by_name=links_by_name,
        )

    #

    @cached_nullary
    def _non_files_sorted_by_name(self) -> ta.Sequence[tarfile.TarInfo]:
        return sorted(
            self._categorized_entries().non_files_by_name.values(),
            key=lambda info: info.name,
        )

    @cached_nullary
    def _files_descending_by_size(self) -> ta.Sequence[tarfile.TarInfo]:
        return sorted(
            self._categorized_entries().files_by_name.values(),
            key=lambda info: -check.isinstance(info.size, int),
        )

    #

    @cached_nullary
    def _output_files(self) -> ta.Sequence[ta.BinaryIO]:
        return [
            self._enter_context(open(output_file_path, 'wb'))
            for output_file_path in self._output_file_paths
        ]

    @cached_nullary
    def _output_tar_writers(self) -> ta.Sequence[OciDataTarWriter]:
        return [
            self._enter_context(
                OciDataTarWriter(
                    output_file,
                    compression=self._compression,
                ),
            )
            for output_file in self._output_files()
        ]

    #

    def _write_entry(
            self,
            info: tarfile.TarInfo,
            output_file_idx: int,
    ) -> None:
        check.not_in(info.name, self._output_file_indexes_by_name)

        writer = self._output_tar_writers()[output_file_idx]

        if info.type in tarfile.REGULAR_TYPES:
            with check.not_none(self._input_tar_file().extractfile(info)) as f:
                writer.add_file(info, f)  # type: ignore

        else:
            writer.add_file(info)

        self._output_file_indexes_by_name[info.name] = output_file_idx

    @cached_nullary
    def _write_non_files(self) -> None:
        for non_file in self._non_files_sorted_by_name():
            self._write_entry(non_file, 0)

    @cached_nullary
    def _write_files(self) -> None:
        writers = self._output_tar_writers()

        bins = [
            (writer.info().compressed_sz, i)
            for i, writer in enumerate(writers)
        ]

        heapq.heapify(bins)

        for file in self._files_descending_by_size():
            _, bin_index = heapq.heappop(bins)

            writer = writers[bin_index]

            self._write_entry(file, bin_index)

            bin_size = writer.info().compressed_sz

            heapq.heappush(bins, (bin_size, bin_index))

    @cached_nullary
    def _write_links(self) -> None:
        for link in self._categorized_entries().links_by_name.values():
            link_name = check.non_empty_str(link.linkname)

            output_file_idx = self._output_file_indexes_by_name[link_name]

            self._write_entry(link, output_file_idx)

    @cached_nullary
    def write(self) -> ta.Mapping[str, WrittenOciDataTarFileInfo]:
        writers = self._output_tar_writers()

        self._write_non_files()
        self._write_files()
        self._write_links()

        for output_tar_writer in writers:
            output_tar_writer.tar_file().close()

        return {
            output_file_path: output_tar_writer.info()
            for output_file_path, output_tar_writer in zip(self._output_file_paths, writers)
        }


########################################
# ../../../omlish/http/coro/server/server.py
# PYTHON SOFTWARE FOUNDATION LICENSE VERSION 2
# --------------------------------------------
#
# 1. This LICENSE AGREEMENT is between the Python Software Foundation ("PSF"), and the Individual or Organization
# ("Licensee") accessing and otherwise using this software ("Python") in source or binary form and its associated
# documentation.
#
# 2. Subject to the terms and conditions of this License Agreement, PSF hereby grants Licensee a nonexclusive,
# royalty-free, world-wide license to reproduce, analyze, test, perform and/or display publicly, prepare derivative
# works, distribute, and otherwise use Python alone or in any derivative version, provided, however, that PSF's License
# Agreement and PSF's notice of copyright, i.e., "Copyright (c) 2001, 2002, 2003, 2004, 2005, 2006, 2007, 2008, 2009,
# 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017 Python Software Foundation; All Rights Reserved" are retained in Python
# alone or in any derivative version prepared by Licensee.
#
# 3. In the event Licensee prepares a derivative work that is based on or incorporates Python or any part thereof, and
# wants to make the derivative work available to others as provided herein, then Licensee hereby agrees to include in
# any such work a brief summary of the changes made to Python.
#
# 4. PSF is making Python available to Licensee on an "AS IS" basis.  PSF MAKES NO REPRESENTATIONS OR WARRANTIES,
# EXPRESS OR IMPLIED.  BY WAY OF EXAMPLE, BUT NOT LIMITATION, PSF MAKES NO AND DISCLAIMS ANY REPRESENTATION OR WARRANTY
# OF MERCHANTABILITY OR FITNESS FOR ANY PARTICULAR PURPOSE OR THAT THE USE OF PYTHON WILL NOT INFRINGE ANY THIRD PARTY
# RIGHTS.
#
# 5. PSF SHALL NOT BE LIABLE TO LICENSEE OR ANY OTHER USERS OF PYTHON FOR ANY INCIDENTAL, SPECIAL, OR CONSEQUENTIAL
# DAMAGES OR LOSS AS A RESULT OF MODIFYING, DISTRIBUTING, OR OTHERWISE USING PYTHON, OR ANY DERIVATIVE THEREOF, EVEN IF
# ADVISED OF THE POSSIBILITY THEREOF.
#
# 6. This License Agreement will automatically terminate upon a material breach of its terms and conditions.
#
# 7. Nothing in this License Agreement shall be deemed to create any relationship of agency, partnership, or joint
# venture between PSF and Licensee.  This License Agreement does not grant permission to use PSF trademarks or trade
# name in a trademark sense to endorse or promote products or services of Licensee, or any third party.
#
# 8. By copying, installing or otherwise using Python, Licensee agrees to be bound by the terms and conditions of this
# License Agreement.
"""
"Test suite" lol:

curl -v localhost:8000
curl -v localhost:8000 -d 'foo'
curl -v -XFOO localhost:8000 -d 'foo'
curl -v -XPOST -H 'Expect: 100-Continue' localhost:8000 -d 'foo'

curl -v -0 localhost:8000
curl -v -0 localhost:8000 -d 'foo'
curl -v -0 -XFOO localhost:8000 -d 'foo'

curl -v -XPOST localhost:8000 -d 'foo' --next -XPOST localhost:8000 -d 'bar'
curl -v -XPOST localhost:8000 -d 'foo' --next -XFOO localhost:8000 -d 'bar'
curl -v -XFOO localhost:8000 -d 'foo' --next -XPOST localhost:8000 -d 'bar'
curl -v -XFOO localhost:8000 -d 'foo' --next -XFOO localhost:8000 -d 'bar'
"""


##


class CoroHttpServer:
    """
    Adapted from stdlib:
     - https://github.com/python/cpython/blob/4b4e0dbdf49adc91c35a357ad332ab3abd4c31b1/Lib/http/server.py#L146
    """

    #

    def __init__(
            self,
            client_address: SocketAddress,
            *,
            handler: HttpHandler,
            parser: HttpRequestParser = HttpRequestParser(),

            default_content_type: ta.Optional[str] = None,

            error_message_format: ta.Optional[str] = None,
            error_content_type: ta.Optional[str] = None,
    ) -> None:
        super().__init__()

        self._client_address = client_address

        self._handler = handler
        self._parser = parser

        self._default_content_type = default_content_type or self.DEFAULT_CONTENT_TYPE

        self._error_message_format = error_message_format or self.DEFAULT_ERROR_MESSAGE
        self._error_content_type = error_content_type or self.DEFAULT_ERROR_CONTENT_TYPE

    #

    @property
    def client_address(self) -> SocketAddress:
        return self._client_address

    @property
    def handler(self) -> HttpHandler:
        return self._handler

    @property
    def parser(self) -> HttpRequestParser:
        return self._parser

    #

    def _format_timestamp(self, timestamp: ta.Optional[float] = None) -> str:
        if timestamp is None:
            timestamp = time.time()
        return email.utils.formatdate(timestamp, usegmt=True)

    #

    def _header_encode(self, s: str) -> bytes:
        return s.encode('latin-1', 'strict')

    class _Header(ta.NamedTuple):
        key: str
        value: str

    def _format_header_line(self, h: _Header) -> str:
        return f'{h.key}: {h.value}\r\n'

    def _get_header_close_connection_action(self, h: _Header) -> ta.Optional[bool]:
        if h.key.lower() != 'connection':
            return None
        elif h.value.lower() == 'close':
            return True
        elif h.value.lower() == 'keep-alive':
            return False
        else:
            return None

    def _make_default_headers(self) -> ta.List[_Header]:
        return [
            self._Header('Date', self._format_timestamp()),
        ]

    #

    _STATUS_RESPONSES: ta.Mapping[int, ta.Tuple[str, str]] = {
        v: (v.phrase, v.description)
        for v in http.HTTPStatus.__members__.values()
    }

    def _format_status_line(
            self,
            version: HttpProtocolVersion,
            code: ta.Union[http.HTTPStatus, int],
            message: ta.Optional[str] = None,
    ) -> str:
        if message is None:
            if code in self._STATUS_RESPONSES:
                message = self._STATUS_RESPONSES[code][0]
            else:
                message = ''

        return f'{version} {int(code)} {message}\r\n'

    #

    @dc.dataclass(frozen=True)
    class _Response:
        version: HttpProtocolVersion
        code: http.HTTPStatus

        message: ta.Optional[str] = None
        headers: ta.Optional[ta.Sequence['CoroHttpServer._Header']] = None
        data: ta.Optional[HttpHandlerResponseData] = None
        close_connection: ta.Optional[bool] = False

        def get_header(self, key: str) -> ta.Optional['CoroHttpServer._Header']:
            for h in self.headers or []:
                if h.key.lower() == key.lower():
                    return h
            return None

        def close(self) -> None:
            if isinstance(d := self.data, HttpHandlerResponseStreamedData):
                d.close()

    #

    def _build_response_head_bytes(self, a: _Response) -> bytes:
        out = io.BytesIO()

        if a.version >= HttpProtocolVersions.HTTP_1_0:
            out.write(self._header_encode(self._format_status_line(
                a.version,
                a.code,
                a.message,
            )))

            for h in a.headers or []:
                out.write(self._header_encode(self._format_header_line(h)))

            out.write(b'\r\n')

        return out.getvalue()

    def _yield_response_data(self, a: _Response) -> ta.Iterator[bytes]:
        if a.data is None:
            return

        elif isinstance(a.data, bytes):
            yield a.data
            return

        elif isinstance(a.data, HttpHandlerResponseStreamedData):
            yield from a.data.iter

        else:
            raise TypeError(a.data)

    #

    DEFAULT_CONTENT_TYPE = 'text/plain'

    def _preprocess_response(self, resp: _Response) -> _Response:
        nh: ta.List[CoroHttpServer._Header] = []
        kw: ta.Dict[str, ta.Any] = {}

        if resp.get_header('Content-Type') is None:
            nh.append(self._Header('Content-Type', self._default_content_type))

        if resp.data is not None and resp.get_header('Content-Length') is None:
            cl: ta.Optional[int]
            if isinstance(resp.data, bytes):
                cl = len(resp.data)
            elif isinstance(resp.data, HttpHandlerResponseStreamedData):
                cl = resp.data.length
            else:
                raise TypeError(resp.data)
            if cl is not None:
                nh.append(self._Header('Content-Length', str(cl)))

        if nh:
            kw.update(headers=[*(resp.headers or []), *nh])

        if (clh := resp.get_header('Connection')) is not None:
            if self._get_header_close_connection_action(clh):
                kw.update(close_connection=True)

        if not kw:
            return resp
        return dc.replace(resp, **kw)

    #

    @dc.dataclass(frozen=True)
    class Error:
        version: HttpProtocolVersion
        code: http.HTTPStatus
        message: str
        explain: str

        method: ta.Optional[str] = None

    def _build_error(
            self,
            code: ta.Union[http.HTTPStatus, int],
            message: ta.Optional[str] = None,
            explain: ta.Optional[str] = None,
            *,
            version: ta.Optional[HttpProtocolVersion] = None,
            method: ta.Optional[str] = None,
    ) -> Error:
        code = http.HTTPStatus(code)

        try:
            short_msg, long_msg = self._STATUS_RESPONSES[code]
        except KeyError:
            short_msg, long_msg = '???', '???'
        if message is None:
            message = short_msg
        if explain is None:
            explain = long_msg

        if version is None:
            version = self._parser.server_version

        return self.Error(
            version=version,
            code=code,
            message=message,
            explain=explain,

            method=method,
        )

    #

    DEFAULT_ERROR_MESSAGE = textwrap.dedent("""\
        <!DOCTYPE HTML>
        <html lang="en">
            <head>
                <meta charset="utf-8">
                <title>Error response</title>
            </head>
            <body>
                <h1>Error response</h1>
                <p>Error code: %(code)d</p>
                <p>Message: %(message)s.</p>
                <p>Error code explanation: %(code)s - %(explain)s.</p>
            </body>
        </html>
    """)

    DEFAULT_ERROR_CONTENT_TYPE = 'text/html;charset=utf-8'

    def _build_error_response(self, err: Error) -> _Response:
        headers: ta.List[CoroHttpServer._Header] = [
            *self._make_default_headers(),
            self._Header('Connection', 'close'),
        ]

        # Message body is omitted for cases described in:
        #  - RFC7230: 3.3. 1xx, 204(No Content), 304(Not Modified)
        #  - RFC7231: 6.3.6. 205(Reset Content)
        data: ta.Optional[bytes] = None
        if (
                err.code >= http.HTTPStatus.OK and
                err.code not in (
                    http.HTTPStatus.NO_CONTENT,
                    http.HTTPStatus.RESET_CONTENT,
                    http.HTTPStatus.NOT_MODIFIED,
                )
        ):
            # HTML encode to prevent Cross Site Scripting attacks (see bug #1100201)
            content = self._error_message_format.format(
                code=err.code,
                message=html.escape(err.message, quote=False),
                explain=html.escape(err.explain, quote=False),
            )
            body = content.encode('UTF-8', 'replace')

            headers.extend([
                self._Header('Content-Type', self._error_content_type),
                self._Header('Content-Length', str(len(body))),
            ])

            if err.method != 'HEAD' and body:
                data = body

        return self._Response(
            version=err.version,
            code=err.code,
            message=err.message,
            headers=headers,
            data=data,
            close_connection=True,
        )

    #

    @dc.dataclass(frozen=True)
    class ParsedRequestLogIo(CoroHttpIo.AnyLogIo):
        request: ParsedHttpRequest

    @dc.dataclass(frozen=True)
    class ErrorLogIo(CoroHttpIo.AnyLogIo):
        error: 'CoroHttpServer.Error'

    #

    @dc.dataclass(frozen=True)
    class CoroHandleResult:
        close_reason: ta.Literal['response', 'internal', None] = None

    def coro_handle(self) -> ta.Generator[CoroHttpIo.Io, ta.Optional[bytes], CoroHandleResult]:
        return self._coro_run_handler(self._coro_handle_one())

    class Close(Exception):  # noqa
        pass

    def _coro_run_handler(
            self,
            gen: ta.Generator[
                ta.Union[CoroHttpIo.AnyLogIo, CoroHttpIo.AnyReadIo, _Response],
                ta.Optional[bytes],
                None,
            ],
    ) -> ta.Generator[CoroHttpIo.Io, ta.Optional[bytes], CoroHandleResult]:
        i: ta.Optional[bytes]
        o: ta.Any = next(gen)
        while True:
            try:
                if isinstance(o, CoroHttpIo.AnyLogIo):
                    i = None
                    yield o

                elif isinstance(o, CoroHttpIo.AnyReadIo):
                    i = check.isinstance((yield o), bytes)

                elif isinstance(o, self._Response):
                    i = None

                    r = self._preprocess_response(o)
                    hb = self._build_response_head_bytes(r)
                    check.none((yield CoroHttpIo.WriteIo(hb)))

                    for b in self._yield_response_data(r):
                        yield CoroHttpIo.WriteIo(b)

                    o.close()
                    if o.close_connection:
                        return self.CoroHandleResult(
                            close_reason='response',
                        )
                    o = None

                else:
                    raise TypeError(o)  # noqa

                try:
                    o = gen.send(i)
                except self.Close:
                    return self.CoroHandleResult(
                        close_reason='internal',
                    )
                except StopIteration:
                    return self.CoroHandleResult()

            except Exception:  # noqa
                if hasattr(o, 'close'):
                    o.close()

                raise

    def _coro_handle_one(self) -> ta.Generator[
        ta.Union[CoroHttpIo.AnyLogIo, CoroHttpIo.AnyReadIo, _Response],
        ta.Optional[bytes],
        None,
    ]:
        # Parse request

        gen = self._parser.coro_parse()
        sz = next(gen)
        while True:
            try:
                line = check.isinstance((yield CoroHttpIo.ReadLineIo(sz)), bytes)
                sz = gen.send(line)
            except StopIteration as e:
                parsed = e.value
                break

        if isinstance(parsed, EmptyParsedHttpResult):
            raise self.Close

        if isinstance(parsed, ParseHttpRequestError):
            err = self._build_error(
                parsed.code,
                *([parsed.message] if isinstance(parsed.message, str) else parsed.message),
                version=parsed.version,
            )
            yield self.ErrorLogIo(err)
            yield self._build_error_response(err)
            return

        parsed = check.isinstance(parsed, ParsedHttpRequest)

        # Log

        check.none((yield self.ParsedRequestLogIo(parsed)))

        # Handle CONTINUE

        if parsed.expects_continue:
            # https://bugs.python.org/issue1491
            # https://github.com/python/cpython/commit/0f476d49f8d4aa84210392bf13b59afc67b32b31
            yield self._Response(
                version=parsed.version,
                code=http.HTTPStatus.CONTINUE,
            )

        # Read data

        request_data: ta.Optional[bytes]
        if (cl := parsed.headers.get('Content-Length')) is not None:
            request_data = check.isinstance((yield CoroHttpIo.ReadIo(int(cl))), bytes)
        else:
            request_data = None

        # Build request

        handler_request = HttpHandlerRequest(
            client_address=self._client_address,
            method=check.not_none(parsed.method),
            path=parsed.path,
            headers=parsed.headers,
            data=request_data,
        )

        # Build handler response

        try:
            handler_response = self._handler(handler_request)

        except UnsupportedMethodHttpHandlerError:
            err = self._build_error(
                http.HTTPStatus.NOT_IMPLEMENTED,
                f'Unsupported method ({parsed.method!r})',
                version=parsed.version,
                method=parsed.method,
            )
            yield self.ErrorLogIo(err)
            yield self._build_error_response(err)
            return

        try:
            # Build internal response

            response_headers = handler_response.headers or {}
            response_data = handler_response.data

            headers: ta.List[CoroHttpServer._Header] = [
                *self._make_default_headers(),
            ]

            for k, v in response_headers.items():
                headers.append(self._Header(k, v))

            if handler_response.close_connection and 'Connection' not in headers:
                headers.append(self._Header('Connection', 'close'))

            yield self._Response(
                version=parsed.version,
                code=http.HTTPStatus(handler_response.status),
                headers=headers,
                data=response_data,
                close_connection=handler_response.close_connection,
            )

        except Exception:  # noqa
            handler_response.close()

            raise


########################################
# ../../../omlish/logs/base.py


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
# ../../../omlish/logs/std/records.py
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
# ../../../omlish/secrets/tempssl.py


##


class TempSslCert(ta.NamedTuple):
    cert: SslCert
    temp_dir: str


@dc.dataclass(frozen=True)
class TempSslCertGenerator(SubprocessRunnable[TempSslCert]):
    @cached_nullary
    def temp_dir(self) -> str:
        return tempfile.mkdtemp()

    @cached_nullary
    def make_run(self) -> SubprocessRun:
        return SubprocessRun.of(
            'openssl',
            'req',
            '-x509',
            '-newkey', 'rsa:2048',

            '-keyout', 'key.pem',
            '-out', 'cert.pem',

            '-days', '365',

            '-nodes',

            '-subj', '/CN=localhost',
            '-addext', 'subjectAltName = DNS:localhost,IP:127.0.0.1',

            cwd=self.temp_dir(),
            capture_output=True,
            check=False,
        )

    def handle_run_output(self, proc: SubprocessRunOutput) -> TempSslCert:
        if proc.returncode:
            raise RuntimeError(f'Failed to generate temp ssl cert: {proc.stderr=}')

        key_file = os.path.join(self.temp_dir(), 'key.pem')
        cert_file = os.path.join(self.temp_dir(), 'cert.pem')
        for file in [key_file, cert_file]:
            if not os.path.isfile(file):
                raise RuntimeError(f'Failed to generate temp ssl cert (file not found): {file}')

        return TempSslCert(
            SslCert(
                key_file=key_file,
                cert_file=cert_file,
            ),
            temp_dir=self.temp_dir(),
        )


def generate_temp_localhost_ssl_cert() -> TempSslCert:
    return TempSslCertGenerator().run()


########################################
# ../../../omlish/sockets/server/server.py


##


class SocketServer:
    _DEFAULT_LOGGER: LoggerLike = logging.getLogger('.'.join([__name__, 'SocketServer']))  # FIXME

    def __init__(
            self,
            binder: SocketBinder,
            handler: SocketServerHandler,
            *,
            on_error: ta.Optional[ta.Callable[[BaseException, ta.Optional[SocketAndAddress]], None]] = None,
            error_logger: ta.Optional[LoggerLike] = _DEFAULT_LOGGER,
            poll_interval: float = .5,
            shutdown_timeout: ta.Optional[float] = None,
    ) -> None:
        super().__init__()

        self._binder = binder
        self._handler = handler
        self._on_error = on_error
        self._error_logger = error_logger
        self._poll_interval = poll_interval
        self._shutdown_timeout = shutdown_timeout

        self._lock = threading.RLock()
        self._is_shutdown = threading.Event()
        self._should_shutdown = False

    @property
    def binder(self) -> SocketBinder:
        return self._binder

    @property
    def handler(self) -> SocketServerHandler:
        return self._handler

    #

    def _handle_error(self, exc: BaseException, conn: ta.Optional[SocketAndAddress] = None) -> None:
        if (error_logger := self._error_logger) is not None:
            error_logger.exception('Error in socket server: %r', conn)

        if (on_error := self._on_error) is not None:
            on_error(exc, conn)

    #

    class SelectorProtocol(ta.Protocol):
        def register(self, *args, **kwargs) -> None:
            raise NotImplementedError

        def select(self, *args, **kwargs) -> bool:
            raise NotImplementedError

    Selector: ta.ClassVar[ta.Any]
    if hasattr(selectors, 'PollSelector'):
        Selector = selectors.PollSelector
    else:
        Selector = selectors.SelectSelector

    #

    class PollResult(enum.Enum):
        TIMEOUT = enum.auto()
        CONNECTION = enum.auto()
        ERROR = enum.auto()
        SHUTDOWN = enum.auto()

    class PollContext(ExitStacked, Abstract):
        @abc.abstractmethod
        def poll(self, timeout: ta.Optional[float] = None) -> 'SocketServer.PollResult':
            raise NotImplementedError

    class _PollContext(PollContext):
        def __init__(self, server: 'SocketServer') -> None:
            super().__init__()

            self._server = server

        _selector: ta.Any = None

        def _enter_contexts(self) -> None:
            self._enter_context(self._server._lock)  # noqa: SLF001
            self._enter_context(self._server._binder)  # noqa: SLF001

            self._server._binder.listen()  # noqa: SLF001

            self._server._is_shutdown.clear()  # noqa: SLF001
            self._enter_context(defer(self._server._is_shutdown.set))  # noqa

            # XXX: Consider using another file descriptor or connecting to the socket to wake this up instead of
            # polling. Polling reduces our responsiveness to a shutdown request and wastes cpu at all other times.
            self._selector = self._enter_context(self._server.Selector())
            self._selector.register(self._server._binder.fileno(), selectors.EVENT_READ)  # noqa: SLF001

        def poll(self, timeout: ta.Optional[float] = None) -> 'SocketServer.PollResult':
            if self._server._should_shutdown:  # noqa: SLF001
                return SocketServer.PollResult.SHUTDOWN

            ready = self._selector.select(timeout)

            # bpo-35017: shutdown() called during select(), exit immediately.
            if self._server._should_shutdown:  # noqa: SLF001
                return SocketServer.PollResult.SHUTDOWN  # type: ignore[unreachable]

            if not ready:
                return SocketServer.PollResult.TIMEOUT

            try:
                conn = self._server._binder.accept()  # noqa: SLF001

            except OSError as exc:
                self._server._handle_error(exc)  # noqa: SLF001

                return SocketServer.PollResult.ERROR

            try:
                self._server._handler(conn)  # noqa: SLF001

            except Exception as exc:  # noqa
                self._server._handle_error(exc, conn)  # noqa: SLF001

                close_socket_immediately(conn.socket)

            return SocketServer.PollResult.CONNECTION

    def poll_context(self) -> PollContext:
        return self._PollContext(self)

    #

    @contextlib.contextmanager
    def loop_context(self, poll_interval: ta.Optional[float] = None) -> ta.Iterator[ta.Iterator[bool]]:
        if poll_interval is None:
            poll_interval = self._poll_interval

        with self.poll_context() as pc:
            def loop():
                while True:
                    res = pc.poll(poll_interval)
                    if res in (SocketServer.PollResult.ERROR, SocketServer.PollResult.SHUTDOWN):
                        return
                    else:
                        yield res == SocketServer.PollResult.CONNECTION

            yield loop()

    def run(self, poll_interval: ta.Optional[float] = None) -> None:
        with self.loop_context(poll_interval=poll_interval) as loop:
            for _ in loop:
                pass

    #

    class _NOT_SET:  # noqa
        def __new__(cls, *args, **kwargs):  # noqa
            raise TypeError

    def shutdown(
            self,
            block: bool = False,
            timeout: ta.Union[float, None, ta.Type[_NOT_SET]] = _NOT_SET,
    ) -> None:
        self._should_shutdown = True

        if block:
            if timeout is self._NOT_SET:
                timeout = self._shutdown_timeout

            if not self._is_shutdown.wait(timeout=timeout):  # type: ignore
                raise TimeoutError

    #

    def __enter__(self) -> 'SocketServer':
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.shutdown()


########################################
# ../../../omlish/sockets/server/ssl.py


##


@dc.dataclass(frozen=True)
class SslErrorHandlingSocketServerHandler(SocketServerHandler_):
    handler: SocketServerHandler

    log: ta.Optional[LoggerLike] = None

    #

    _error_cls: ta.ClassVar[ta.Optional[ta.Type[BaseException]]] = None

    @classmethod
    def _get_error_cls(cls) -> ta.Type[BaseException]:
        if (error_cls := cls._error_cls) is None:
            import ssl
            error_cls = cls._error_cls = ssl.SSLError
        return error_cls

    def __call__(self, conn: SocketAndAddress) -> None:
        try:
            self.handler(conn)
        except self._get_error_cls():  # noqa
            if (log := self.log) is not None:
                log.exception('SSL Error in connection %r', conn)
            close_socket_immediately(conn.socket)


########################################
# ../../../omlish/sockets/server/threading.py


##


class ThreadingSocketServerHandler:
    def __init__(
            self,
            handler: SocketServerHandler,
            *,
            shutdown_timeout: ta.Optional[float] = None,
    ) -> None:
        super().__init__()

        self._handler = handler
        self._shutdown_timeout = shutdown_timeout

        self._lock = threading.RLock()
        self._threads: ta.List[threading.Thread] = []
        self._is_shutdown = False

    @property
    def handler(self) -> SocketServerHandler:
        return self._handler

    #

    def __call__(self, conn: SocketAndAddress) -> None:
        self.handle(conn)

    def handle(self, conn: SocketAndAddress) -> None:
        with self._lock:
            check.state(not self._is_shutdown)

            self._reap()

            t = threading.Thread(
                target=self._handler,
                args=(conn,),
            )

            self._threads.append(t)

            t.start()

    #

    def _reap(self) -> None:
        with self._lock:
            self._threads[:] = (thread for thread in self._threads if thread.is_alive())

    def is_alive(self) -> bool:
        with self._lock:
            self._reap()

            return bool(self._threads)

    def join(self, timeout: ta.Optional[float] = None) -> None:
        if timeout is not None:
            deadline: ta.Optional[float] = time.time() + timeout
        else:
            deadline = None

        def calc_timeout() -> ta.Optional[float]:
            if deadline is None:
                return None

            tt = deadline - time.time()
            if tt <= 0:
                raise TimeoutError

            return tt

        if not (self._lock.acquire(timeout=calc_timeout() or -1)):
            raise TimeoutError

        try:
            self._reap()

            for t in self._threads:
                t.join(timeout=calc_timeout())

                if t.is_alive():
                    raise TimeoutError

        finally:
            self._lock.release()

    #

    class _NOT_SET:  # noqa
        def __new__(cls, *args, **kwargs):  # noqa
            raise TypeError

    def shutdown(
            self,
            block: bool = False,
            timeout: ta.Union[float, None, ta.Type[_NOT_SET]] = _NOT_SET,
    ) -> None:
        self._is_shutdown = True

        if block:
            if timeout is self._NOT_SET:
                timeout = self._shutdown_timeout

            self.join(timeout=timeout)  # type: ignore

    #

    def __enter__(self) -> 'ThreadingSocketServerHandler':
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.shutdown()


########################################
# ../../../omlish/subprocesses/base.py


##


# Valid channel type kwarg values:
#  - A special flag negative int
#  - A positive fd int
#  - A file-like object
#  - None

SUBPROCESS_CHANNEL_OPTION_VALUES: ta.Mapping[SubprocessChannelOption, int] = {
    'pipe': subprocess.PIPE,
    'stdout': subprocess.STDOUT,
    'devnull': subprocess.DEVNULL,
}


##


class VerboseCalledProcessError(subprocess.CalledProcessError):
    @classmethod
    def from_std(cls, e: subprocess.CalledProcessError) -> 'VerboseCalledProcessError':
        return cls(
            e.returncode,
            e.cmd,
            output=e.output,
            stderr=e.stderr,
        )

    def __str__(self) -> str:
        msg = super().__str__()
        if self.output is not None:
            msg += f' Output: {self.output!r}'
        if self.stderr is not None:
            msg += f' Stderr: {self.stderr!r}'
        return msg


class BaseSubprocesses(Abstract):
    DEFAULT_LOGGER: ta.ClassVar[ta.Optional[LoggerLike]] = None

    def __init__(
            self,
            *,
            log: ta.Optional[LoggerLike] = None,
            try_exceptions: ta.Optional[ta.Tuple[ta.Type[Exception], ...]] = None,
    ) -> None:
        super().__init__()

        self._log = log if log is not None else self.DEFAULT_LOGGER
        self._try_exceptions = try_exceptions if try_exceptions is not None else self.DEFAULT_TRY_EXCEPTIONS

    def set_logger(self, log: ta.Optional[LoggerLike]) -> None:
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

        #

        if extra_env:
            env = {**(env if env is not None else os.environ), **extra_env}

        #

        if quiet and 'stderr' not in kwargs:
            if self._log and not self._log.isEnabledFor(logging.DEBUG):
                kwargs['stderr'] = subprocess.DEVNULL

        for chk in ('stdout', 'stderr'):
            try:
                chv = kwargs[chk]
            except KeyError:
                continue
            kwargs[chk] = SUBPROCESS_CHANNEL_OPTION_VALUES.get(chv, chv)

        #

        if not shell:
            cmd = subprocess_maybe_shell_wrap_exec(*cmd)

        #

        if 'timeout' in kwargs:
            kwargs['timeout'] = Timeout.of(kwargs['timeout']).or_(None)

        #

        return cmd, dict(
            env=env,
            shell=shell,
            **kwargs,
        )

    @contextlib.contextmanager
    def wrap_call(
            self,
            *cmd: ta.Any,
            raise_verbose: bool = False,
            **kwargs: ta.Any,
    ) -> ta.Iterator[None]:
        start_time = time.time()
        try:
            if self._log:
                self._log.debug('Subprocesses.wrap_call.try: cmd=%r', cmd)

            yield

        except Exception as exc:  # noqa
            if self._log:
                self._log.debug('Subprocesses.wrap_call.except: exc=%r', exc)

            if (
                    raise_verbose and
                    isinstance(exc, subprocess.CalledProcessError) and
                    not isinstance(exc, VerboseCalledProcessError) and
                    (exc.output is not None or exc.stderr is not None)
            ):
                raise VerboseCalledProcessError.from_std(exc) from exc

            raise

        finally:
            end_time = time.time()
            elapsed_s = end_time - start_time

            if self._log:
                self._log.debug('Subprocesses.wrap_call.finally: elapsed_s=%f cmd=%r', elapsed_s, cmd)

    @contextlib.contextmanager
    def prepare_and_wrap(
            self,
            *cmd: ta.Any,
            raise_verbose: bool = False,
            **kwargs: ta.Any,
    ) -> ta.Iterator[ta.Tuple[
        ta.Tuple[ta.Any, ...],
        ta.Dict[str, ta.Any],
    ]]:
        cmd, kwargs = self.prepare_args(*cmd, **kwargs)

        with self.wrap_call(
                *cmd,
                raise_verbose=raise_verbose,
                **kwargs,
        ):
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


########################################
# ../docker/cacheserved/manifests.py


##


@dc.dataclass(frozen=True)
class CacheServedDockerImageManifest:
    @dc.dataclass(frozen=True)
    class Route:
        paths: ta.Sequence[str]

        content_type: str
        content_length: int

        @dc.dataclass(frozen=True)
        class Target(Abstract):
            pass

        @dc.dataclass(frozen=True)
        class BytesTarget(Target):
            data: bytes

        @dc.dataclass(frozen=True)
        class CacheKeyTarget(Target):
            key: str

        target: Target

        def __post_init__(self) -> None:
            check.not_isinstance(self.paths, str)

    routes: ta.Sequence[Route]


#


async def build_cache_served_docker_image_manifest(
        data_server_routes: ta.Iterable[DataServerRoute],
        make_file_cache_key: ta.Callable[[str], ta.Awaitable[str]],
) -> CacheServedDockerImageManifest:
    routes: ta.List[CacheServedDockerImageManifest.Route] = []

    for data_server_route in data_server_routes:
        content_length: int

        data_server_target = data_server_route.target
        target: CacheServedDockerImageManifest.Route.Target
        if isinstance(data_server_target, BytesDataServerTarget):
            bytes_data = check.isinstance(data_server_target.data, bytes)
            content_length = len(bytes_data)
            target = CacheServedDockerImageManifest.Route.BytesTarget(bytes_data)

        elif isinstance(data_server_target, FileDataServerTarget):
            file_path = check.non_empty_str(data_server_target.file_path)
            content_length = os.path.getsize(file_path)
            cache_key = await make_file_cache_key(file_path)
            target = CacheServedDockerImageManifest.Route.CacheKeyTarget(cache_key)

        else:
            raise TypeError(data_server_target)

        routes.append(CacheServedDockerImageManifest.Route(
            paths=data_server_route.paths,

            content_type=check.non_empty_str(data_server_target.content_type),
            content_length=content_length,

            target=target,
        ))

    return CacheServedDockerImageManifest(
        routes=routes,
    )


#


async def build_cache_served_docker_image_data_server_routes(
        manifest: CacheServedDockerImageManifest,
        make_cache_key_target: ta.Callable[..., ta.Awaitable[DataServerTarget]],
) -> ta.List[DataServerRoute]:
    routes: ta.List[DataServerRoute] = []

    for manifest_route in manifest.routes:
        manifest_target = manifest_route.target

        target_kwargs: dict = dict(
            content_type=manifest_route.content_type,
            content_length=manifest_route.content_length,
        )

        target: DataServerTarget

        if isinstance(manifest_target, CacheServedDockerImageManifest.Route.BytesTarget):
            target = DataServerTarget.of(manifest_target.data, **target_kwargs)

        elif isinstance(manifest_target, CacheServedDockerImageManifest.Route.CacheKeyTarget):
            target = await make_cache_key_target(manifest_target.key, **target_kwargs)

        else:
            raise TypeError(manifest_target)

        routes.append(DataServerRoute(
            paths=manifest_route.paths,
            target=target,
        ))

    return routes


########################################
# ../../dataserver/server.py


##


class DataServer:
    @dc.dataclass(frozen=True)
    class HandlerRoute:
        paths: ta.Sequence[str]
        handler: DataServerHandler

        def __post_init__(self) -> None:
            check.not_isinstance(self.paths, str)
            for p in self.paths:
                check.non_empty_str(p)
            check.isinstance(self.handler, DataServerHandler)

        @classmethod
        def of(cls, obj: ta.Union[
            'DataServer.HandlerRoute',
            DataServerRoute,
        ]) -> 'DataServer.HandlerRoute':
            if isinstance(obj, cls):
                return obj

            elif isinstance(obj, DataServerRoute):
                return cls(
                    paths=obj.paths,
                    handler=DataServerTargetHandler.for_target(obj.target),
                )

            else:
                raise TypeError(obj)

        @classmethod
        def of_(cls, *objs: ta.Any) -> ta.List['DataServer.HandlerRoute']:
            return [cls.of(obj) for obj in objs]

    #

    @dc.dataclass(frozen=True)
    class Config:
        pass

    def __init__(
            self,
            routes: ta.Optional[ta.Iterable[HandlerRoute]] = None,
            config: Config = Config(),
    ) -> None:
        super().__init__()

        self._config = config

        self.set_routes(routes)

    #

    _routes_by_path: ta.Dict[str, HandlerRoute]

    def set_routes(self, routes: ta.Optional[ta.Iterable[HandlerRoute]]) -> None:
        routes_by_path: ta.Dict[str, DataServer.HandlerRoute] = {}

        for r in routes or []:
            for p in r.paths:
                check.not_in(p, routes_by_path)
                routes_by_path[p] = r

        self._routes_by_path = routes_by_path

    #

    def handle(self, req: DataServerRequest) -> DataServerResponse:
        try:
            rt = self._routes_by_path[req.path]
        except KeyError:
            return DataServerResponse(http.HTTPStatus.NOT_FOUND)

        return rt.handler.handle(req)


########################################
# ../../oci/building.py


##


class OciRepositoryBuilder:
    @dc.dataclass(frozen=True)
    class Blob:
        digest: str

        data: OciDataRef
        info: OciDataRefInfo

        media_type: ta.Optional[str] = None

        #

        def read(self) -> bytes:
            with open_oci_data_ref(self.data) as f:
                return f.read()

        def read_json(self) -> ta.Any:
            return json.loads(self.read().decode('utf-8'))

        def read_media(
                self,
                cls: ta.Type[OciMediaDataclassT] = OciMediaDataclass,  # type: ignore[assignment]
        ) -> OciMediaDataclassT:
            mt = check.non_empty_str(self.media_type)
            dct = self.read_json()
            obj = unmarshal_oci_media_dataclass(
                dct,
                media_type=mt,
            )
            return check.isinstance(obj, cls)

    def __init__(self) -> None:
        super().__init__()

        self._blobs: ta.Dict[str, OciRepositoryBuilder.Blob] = {}

    #

    def get_blobs(self) -> ta.Dict[str, Blob]:
        return dict(self._blobs)

    def add_blob(
            self,
            r: OciDataRef,
            ri: ta.Optional[OciDataRefInfo] = None,
            *,
            media_type: ta.Optional[str] = None,
    ) -> Blob:
        if ri is None:
            ri = OciDataRefInfo(r)

        if (dg := ri.digest()) in self._blobs:
            raise KeyError(ri.digest())

        blob = self.Blob(
            digest=dg,

            data=r,
            info=ri,

            media_type=media_type,
        )

        self._blobs[dg] = blob

        return blob

    #

    def marshal_media(self, obj: OciMediaDataclass) -> bytes:
        check.isinstance(obj, OciMediaDataclass)
        m = marshal_obj(obj)
        j = json_dumps_compact(m)
        b = j.encode('utf-8')
        return b

    def add_media(self, obj: OciMediaDataclass) -> OciMediaDescriptor:
        b = self.marshal_media(obj)

        r = BytesOciDataRef(b)
        ri = OciDataRefInfo(r)
        self.add_blob(
            r,
            ri,
            media_type=obj.media_type,
        )

        return OciMediaDescriptor(
            media_type=obj.media_type,
            digest=ri.digest(),
            size=ri.size(),
        )

    #

    def to_media(self, obj: OciDataclass) -> ta.Union[OciMediaDataclass, OciMediaDescriptor]:
        def make_kw(*exclude):
            return {
                a: v
                for f in dc.fields(obj)
                if (a := f.name) not in exclude
                for v in [getattr(obj, a)]
                if v is not None
            }

        if isinstance(obj, OciImageIndex):
            return OciMediaImageIndex(
                **make_kw('manifests'),
                manifests=[
                    self.add_data(m)
                    for m in obj.manifests
                ],
            )

        elif isinstance(obj, OciImageManifest):
            return OciMediaImageManifest(
                **make_kw('config', 'layers'),
                config=self.add_data(obj.config),
                layers=[
                    self.add_data(l)
                    for l in obj.layers
                ],
            )

        elif isinstance(obj, OciImageLayer):
            ri = OciDataRefInfo(obj.data)
            mt = OCI_IMAGE_LAYER_KIND_MEDIA_TYPES[obj.kind]
            self.add_blob(
                obj.data,
                ri,
                media_type=mt,
            )
            return OciMediaDescriptor(
                media_type=mt,
                digest=ri.digest(),
                size=ri.size(),
            )

        elif isinstance(obj, OciImageConfig):
            return OciMediaImageConfig(**make_kw())

        else:
            raise TypeError(obj)

    def add_data(self, obj: OciDataclass) -> OciMediaDescriptor:
        ret = self.to_media(obj)

        if isinstance(ret, OciMediaDataclass):
            return self.add_media(ret)

        elif isinstance(ret, OciMediaDescriptor):
            return ret

        else:
            raise TypeError(ret)


##


@dc.dataclass(frozen=True)
class BuiltOciImageIndexRepository:
    index: OciImageIndex

    media_index_descriptor: OciMediaDescriptor
    media_index: OciMediaImageIndex

    blobs: ta.Mapping[str, OciRepositoryBuilder.Blob]


def build_oci_index_repository(index: OciImageIndex) -> BuiltOciImageIndexRepository:
    builder = OciRepositoryBuilder()

    media_index_descriptor = builder.add_data(index)

    blobs = builder.get_blobs()

    media_index = blobs[media_index_descriptor.digest].read_media(OciMediaImageIndex)

    return BuiltOciImageIndexRepository(
        index=index,

        media_index_descriptor=media_index_descriptor,
        media_index=media_index,

        blobs=blobs,
    )


########################################
# ../../oci/loading.py


##


class OciRepositoryLoader:
    def __init__(
            self,
            repo: OciRepository,
    ) -> None:
        super().__init__()

        self._repo = repo

    #

    def load_object(
            self,
            data: bytes,
            cls: ta.Type[T] = object,  # type: ignore[assignment]
            *,
            media_type: ta.Optional[str] = None,
    ) -> T:
        text = data.decode('utf-8')
        dct = json.loads(text)
        obj = unmarshal_oci_media_dataclass(
            dct,
            media_type=media_type,
        )
        return check.isinstance(obj, cls)

    def read_object(
            self,
            digest: str,
            cls: ta.Type[T] = object,  # type: ignore[assignment]
            *,
            media_type: ta.Optional[str] = None,
    ) -> T:
        data = self._repo.read_blob(digest)
        return self.load_object(
            data,
            cls,
            media_type=media_type,
        )

    def read_descriptor(
            self,
            desc: OciMediaDescriptor,
            cls: ta.Type[T] = object,  # type: ignore[assignment]
    ) -> ta.Any:
        return self.read_object(
            desc.digest,
            cls,
            media_type=desc.media_type,
        )

    #

    def from_media(self, obj: ta.Any) -> ta.Any:
        def make_kw(*exclude):
            return {
                a: getattr(obj, a)
                for f in dc.fields(obj)
                if (a := f.name) not in OCI_MEDIA_FIELDS
                and a not in exclude
            }

        if isinstance(obj, OciMediaImageConfig):
            return OciImageConfig(**make_kw())

        elif isinstance(obj, OciMediaImageManifest):
            return OciImageManifest(
                **make_kw('config', 'layers'),
                config=self.from_media(self.read_descriptor(obj.config)),
                layers=[
                    OciImageLayer(
                        kind=lk,
                        data=self._repo.ref_blob(l.digest),
                    )
                    for l in obj.layers
                    if (lk := OCI_IMAGE_LAYER_KIND_MEDIA_TYPES_.get(l.media_type)) is not None
                ],
            )

        elif isinstance(obj, OciMediaImageIndex):
            return OciImageIndex(
                **make_kw('manifests'),
                manifests=[
                    fm
                    for m in obj.manifests
                    if self._repo.contains_blob(m.digest)
                    for fm in [self.from_media(self.read_descriptor(m))]
                    if not is_empty_oci_dataclass(fm)
                ],
            )

        else:
            raise TypeError(obj)


##


def read_oci_repository_root_index(
        obj: ta.Any,
        *,
        file_name: str = 'index.json',
) -> OciImageIndex:
    file_repo = check.isinstance(OciRepository.of(obj), FileOciRepository)

    repo_ldr = OciRepositoryLoader(file_repo)

    media_image_idx = repo_ldr.load_object(file_repo.read_file(file_name), OciMediaImageIndex)

    image_idx = repo_ldr.from_media(media_image_idx)

    return check.isinstance(image_idx, OciImageIndex)


########################################
# ../../../omlish/http/coro/server/sockets.py


##


class CoroHttpServerSocketHandler(SocketHandler_):
    def __init__(
            self,
            server_factory: CoroHttpServerFactory,
            *,
            keep_alive: bool = False,
            log_handler: ta.Optional[ta.Callable[[CoroHttpServer, CoroHttpIo.AnyLogIo], None]] = None,
    ) -> None:
        super().__init__()

        self._server_factory = server_factory
        self._keep_alive = keep_alive
        self._log_handler = log_handler

    def __call__(self, client_address: SocketAddress, fp: SocketIoPair) -> None:
        server = self._server_factory(client_address)

        if self._keep_alive:
            for i in itertools.count():  # noqa
                res = self._handle_one(server, fp)
                if res.close_reason is not None:
                    break

        else:
            self._handle_one(server, fp)

    def _handle_one(
            self,
            server: CoroHttpServer,
            fp: SocketIoPair,
    ) -> CoroHttpServer.CoroHandleResult:
        gen = server.coro_handle()

        o = next(gen)
        while True:
            if isinstance(o, CoroHttpIo.AnyLogIo):
                i = None
                if self._log_handler is not None:
                    self._log_handler(server, o)

            elif isinstance(o, CoroHttpIo.ReadIo):
                i = fp.r.read(check.not_none(o.sz))

            elif isinstance(o, CoroHttpIo.ReadLineIo):
                i = fp.r.readline(o.sz)

            elif isinstance(o, CoroHttpIo.WriteIo):
                i = None
                fp.w.write(o.data)
                fp.w.flush()

            else:
                raise TypeError(o)

            try:
                if i is not None:
                    o = gen.send(i)
                else:
                    o = next(gen)
            except StopIteration as e:
                return check.isinstance(e.value, CoroHttpServer.CoroHandleResult)


########################################
# ../../../omlish/logs/std/loggers.py


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
# ../../../omlish/subprocesses/asyncs.py


##


class AbstractAsyncSubprocesses(BaseSubprocesses, Abstract):
    @abc.abstractmethod
    def run_(self, run: SubprocessRun) -> ta.Awaitable[SubprocessRunOutput]:
        raise NotImplementedError

    def run(
            self,
            *cmd: str,
            input: ta.Any = None,  # noqa
            timeout: TimeoutLike = None,
            check: bool = False,
            capture_output: ta.Optional[bool] = None,
            **kwargs: ta.Any,
    ) -> ta.Awaitable[SubprocessRunOutput]:
        return self.run_(SubprocessRun(
            cmd=cmd,
            input=input,
            timeout=timeout,
            check=check,
            capture_output=capture_output,
            kwargs=kwargs,
        ))

    #

    async def check_call(
            self,
            *cmd: str,
            stdout: ta.Any = sys.stderr,
            **kwargs: ta.Any,
    ) -> None:
        await self.run(
            *cmd,
            stdout=stdout,
            check=True,
            **kwargs,
        )

    async def check_output(
            self,
            *cmd: str,
            stdout: ta.Any = subprocess.PIPE,
            **kwargs: ta.Any,
    ) -> bytes:
        return check.not_none((await self.run(
            *cmd,
            stdout=stdout,
            check=True,
            **kwargs,
        )).stdout)

    async def check_output_str(
            self,
            *cmd: str,
            **kwargs: ta.Any,
    ) -> str:
        return (await self.check_output(
            *cmd,
            **kwargs,
        )).decode().strip()

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
# ../../../omlish/subprocesses/sync.py
"""
TODO:
 - popen
 - route check_calls through run_?
"""


##


class AbstractSubprocesses(BaseSubprocesses, Abstract):
    @abc.abstractmethod
    def run_(self, run: SubprocessRun) -> SubprocessRunOutput:
        raise NotImplementedError

    def run(
            self,
            *cmd: str,
            input: ta.Any = None,  # noqa
            timeout: TimeoutLike = None,
            check: bool = False,
            capture_output: ta.Optional[bool] = None,
            **kwargs: ta.Any,
    ) -> SubprocessRunOutput:
        return self.run_(SubprocessRun(
            cmd=cmd,
            input=input,
            timeout=timeout,
            check=check,
            capture_output=capture_output,
            kwargs=kwargs,
        ))

    #

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
    def run_(self, run: SubprocessRun) -> SubprocessRunOutput[subprocess.CompletedProcess]:
        with self.prepare_and_wrap(
                *run.cmd,
                input=run.input,
                timeout=run.timeout,
                check=run.check,
                capture_output=run.capture_output or False,
                **(run.kwargs or {}),
        ) as (cmd, kwargs):
            proc = subprocess.run(cmd, **kwargs)  # noqa

        return SubprocessRunOutput(
            proc=proc,

            returncode=proc.returncode,

            stdout=proc.stdout,  # noqa
            stderr=proc.stderr,  # noqa
        )

    #

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


##


subprocesses = Subprocesses()

SubprocessRun._DEFAULT_SUBPROCESSES = subprocesses  # noqa


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
# ../../dataserver/http.py
"""
TODO:
 - asyncio
 - chunked transfer - both output and urllib input
 - range headers
"""


##


class DataServerHttpHandler(HttpHandler_):
    DEFAULT_READ_CHUNK_SIZE = 0x10000

    def __init__(
            self,
            ps: DataServer,
            *,
            read_chunk_size: int = DEFAULT_READ_CHUNK_SIZE,
    ) -> None:
        super().__init__()

        self._ps = ps
        self._read_chunk_size = read_chunk_size

    def __call__(self, req: HttpHandlerRequest) -> HttpHandlerResponse:
        p_req = DataServerRequest(
            req.method,
            req.path,
        )

        p_resp = self._ps.handle(p_req)
        try:
            data: ta.Any
            if (p_body := p_resp.body) is not None:
                def stream_data():
                    try:
                        while (b := p_body.read(self._read_chunk_size)):
                            yield b
                    finally:
                        p_body.close()

                data = HttpHandlerResponseStreamedData(stream_data())

            else:
                data = None

            resp = HttpHandlerResponse(
                status=p_resp.status,
                headers=p_resp.headers,
                data=data,
                close_connection=True,
            )

            return resp

        except Exception:  # noqa
            p_resp.close()

            raise


########################################
# ../../oci/dataserver.py


##


def build_oci_repository_data_server_routes(
        repo_name: str,
        built_repo: BuiltOciImageIndexRepository,
) -> ta.List[DataServerRoute]:
    base_url_path = f'/v2/{repo_name}'

    repo_contents: ta.Dict[str, OciRepositoryBuilder.Blob] = {}

    repo_contents[f'{base_url_path}/manifests/latest'] = built_repo.blobs[built_repo.media_index_descriptor.digest]

    for blob in built_repo.blobs.values():
        repo_contents['/'.join([
            base_url_path,
            'manifests' if blob.media_type in OCI_MANIFEST_MEDIA_TYPES else 'blobs',
            blob.digest,
        ])] = blob

    #

    def build_blob_target(blob: OciRepositoryBuilder.Blob) -> ta.Optional[DataServerTarget]:  # noqa
        kw: dict = dict(
            content_type=check.non_empty_str(blob.media_type),
        )

        if isinstance(blob.data, BytesOciDataRef):
            return DataServerTarget.of(blob.data.data, **kw)

        elif isinstance(blob.data, FileOciDataRef):
            return DataServerTarget.of(file_path=blob.data.path, **kw)

        else:
            with open_oci_data_ref(blob.data) as f:
                data = f.read()

            return DataServerTarget.of(data, **kw)

    #

    return [
        DataServerRoute(
            paths=[path],
            target=target,
        )
        for path, blob in repo_contents.items()
        if (target := build_blob_target(blob)) is not None
    ]


########################################
# ../../../omlish/asyncs/asyncio/subprocesses.py


##


class AsyncioProcessCommunicator:
    def __init__(
            self,
            proc: asyncio.subprocess.Process,
            loop: ta.Optional[ta.Any] = None,
            *,
            log: ta.Optional[LoggerLike] = None,
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
            timeout: TimeoutLike = None,
    ) -> Communication:
        return await asyncio_maybe_timeout(self._communicate(input), timeout)


##


class AsyncioSubprocesses(AbstractAsyncSubprocesses):
    async def communicate(
            self,
            proc: asyncio.subprocess.Process,
            input: ta.Any = None,  # noqa
            timeout: TimeoutLike = None,
    ) -> ta.Tuple[ta.Optional[bytes], ta.Optional[bytes]]:
        return await AsyncioProcessCommunicator(proc).communicate(input, timeout)  # noqa

    #

    @contextlib.asynccontextmanager
    async def popen(
            self,
            *cmd: str,
            shell: bool = False,
            timeout: TimeoutLike = None,
            **kwargs: ta.Any,
    ) -> ta.AsyncGenerator[asyncio.subprocess.Process, None]:
        with self.prepare_and_wrap( *cmd, shell=shell, **kwargs) as (cmd, kwargs):  # noqa
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

            proc: asyncio.subprocess.Process = await fac(**kwargs)
            try:
                yield proc

            finally:
                await asyncio_maybe_timeout(proc.wait(), timeout)

    #

    async def run_(self, run: SubprocessRun) -> SubprocessRunOutput[asyncio.subprocess.Process]:
        kwargs = dict(run.kwargs or {})

        if run.capture_output:
            kwargs.setdefault('stdout', subprocess.PIPE)
            kwargs.setdefault('stderr', subprocess.PIPE)

        proc: asyncio.subprocess.Process
        async with self.popen(*run.cmd, **kwargs) as proc:
            stdout, stderr = await self.communicate(proc, run.input, run.timeout)

        if run.check and proc.returncode:
            raise subprocess.CalledProcessError(
                proc.returncode,
                run.cmd,
                output=stdout,
                stderr=stderr,
            )

        return SubprocessRunOutput(
            proc=proc,

            returncode=check.isinstance(proc.returncode, int),

            stdout=stdout,
            stderr=stderr,
        )


asyncio_subprocesses = AsyncioSubprocesses()


########################################
# ../../../omlish/http/coro/server/simple.py
"""
TODO:
 - logging
"""


@contextlib.contextmanager
def make_simple_http_server(
        bind: CanSocketBinder,
        handler: HttpHandler,
        *,
        server_version: HttpProtocolVersion = HttpProtocolVersions.HTTP_1_1,
        keep_alive: bool = False,
        ssl_context: ta.Optional['ssl.SSLContext'] = None,
        ignore_ssl_errors: bool = False,
        executor: ta.Optional[cf.Executor] = None,
        use_threads: bool = False,
        **kwargs: ta.Any,
) -> ta.Iterator[SocketServer]:
    check.arg(not (executor is not None and use_threads))

    #

    with contextlib.ExitStack() as es:
        server_factory = functools.partial(
            CoroHttpServer,
            handler=handler,
            parser=HttpRequestParser(
                server_version=server_version,
            ),
        )

        socket_handler = CoroHttpServerSocketHandler(
            server_factory,
            keep_alive=keep_alive,
        )

        #

        server_handler: SocketServerHandler = SocketHandlerSocketServerHandler(
            socket_handler,
        )

        #

        if ssl_context is not None:
            server_handler = SocketWrappingSocketServerHandler(
                server_handler,
                SocketAndAddress.socket_wrapper(functools.partial(
                    ssl_context.wrap_socket,
                    server_side=True,
                )),
            )

        if ignore_ssl_errors:
            server_handler = SslErrorHandlingSocketServerHandler(
                server_handler,
            )

        #

        server_handler = StandardSocketServerHandler(
            server_handler,
        )

        #

        if executor is not None:
            server_handler = ExecutorSocketServerHandler(
                server_handler,
                executor,
            )

        elif use_threads:
            server_handler = es.enter_context(ThreadingSocketServerHandler(
                server_handler,
            ))

        #

        server = es.enter_context(SocketServer(
            SocketBinder.of(bind),
            server_handler,
            **kwargs,
        ))

        yield server


########################################
# ../../../omlish/logs/modules.py


##


def get_module_logger(mod_globals: ta.Mapping[str, ta.Any]) -> Logger:
    return StdLogger(logging.getLogger(mod_globals.get('__name__')))  # noqa


########################################
# ../cache.py
"""
TODO:
 - os.mtime, Config.purge_after_days
  - nice to have: get a total set of might-need keys ahead of time and keep those
  - okay: just purge after running
"""


CacheVersion = ta.NewType('CacheVersion', int)


log = get_module_logger(globals())  # noqa


##


class FileCache(Abstract):
    DEFAULT_CACHE_VERSION: ta.ClassVar[CacheVersion] = CacheVersion(CI_CACHE_VERSION)

    def __init__(
            self,
            *,
            version: ta.Optional[CacheVersion] = None,
    ) -> None:
        super().__init__()

        if version is None:
            version = self.DEFAULT_CACHE_VERSION
        check.isinstance(version, int)
        check.arg(version >= 0)
        self._version: CacheVersion = version

    @property
    def version(self) -> CacheVersion:
        return self._version

    #

    @abc.abstractmethod
    def get_file(self, key: str) -> ta.Awaitable[ta.Optional[str]]:
        raise NotImplementedError

    @abc.abstractmethod
    def put_file(
            self,
            key: str,
            file_path: str,
            *,
            steal: bool = False,
    ) -> ta.Awaitable[str]:
        raise NotImplementedError


#


class DirectoryFileCache(FileCache):
    @dc.dataclass(frozen=True)
    class Config:
        dir: str

        no_create: bool = False
        no_purge: bool = False

        no_update_mtime: bool = False

        purge_max_age_s: ta.Optional[float] = None
        purge_max_size_b: ta.Optional[int] = None

    def __init__(
            self,
            config: Config,
            *,
            version: ta.Optional[CacheVersion] = None,
    ) -> None:  # noqa
        super().__init__(
            version=version,
        )

        self._config = config

    @property
    def dir(self) -> str:
        return self._config.dir

    #

    VERSION_FILE_NAME = '.ci-cache-version'

    def _iter_dir_contents(self) -> ta.Iterator[str]:
        for n in sorted(os.listdir(self.dir)):
            if n.startswith('.'):
                continue
            yield os.path.join(self.dir, n)

    @cached_nullary
    def setup_dir(self) -> None:
        version_file = os.path.join(self.dir, self.VERSION_FILE_NAME)

        if self._config.no_create:
            check.state(os.path.isdir(self.dir))

        elif not os.path.isdir(self.dir):
            os.makedirs(self.dir)
            with open(version_file, 'w') as f:
                f.write(f'{self._version}\n')
            return

        # NOTE: intentionally raises FileNotFoundError to refuse to use an existing non-cache dir as a cache dir.
        with open(version_file) as f:
            dir_version = int(f.read().strip())

        if dir_version == self._version:
            return

        if self._config.no_purge:
            raise RuntimeError(f'{dir_version=} != {self._version=}')

        dirs = [n for n in sorted(os.listdir(self.dir)) if os.path.isdir(os.path.join(self.dir, n))]
        if dirs:
            raise RuntimeError(
                f'Refusing to remove stale cache dir {self.dir!r} '
                f'due to present directories: {", ".join(dirs)}',
            )

        for fp in self._iter_dir_contents():
            check.state(os.path.isfile(fp))
            log.debug('Purging stale cache file: %s', fp)
            os.unlink(fp)

        os.unlink(version_file)

        with open(version_file, 'w') as f:
            f.write(str(self._version))

    #

    def purge(self, *, dry_run: bool = False) -> None:
        purge_max_age_s = self._config.purge_max_age_s
        purge_max_size_b = self._config.purge_max_size_b
        if self._config.no_purge or (purge_max_age_s is None and purge_max_size_b is None):
            return

        self.setup_dir()

        purge_min_mtime: ta.Optional[float] = None
        if purge_max_age_s is not None:
            purge_min_mtime = time.time() - purge_max_age_s

        dct: ta.Dict[str, os.stat_result] = {}
        for fp in self._iter_dir_contents():
            check.state(os.path.isfile(fp))
            dct[fp] = os.stat(fp)

        total_size_b = 0
        for fp, st in sorted(dct.items(), key=lambda t: -t[1].st_mtime):
            total_size_b += st.st_size

            purge = False
            if purge_min_mtime is not None and st.st_mtime < purge_min_mtime:
                purge = True
            if purge_max_size_b is not None and total_size_b >= purge_max_size_b:
                purge = True

            if not purge:
                continue

            log.debug('Purging cache file: %s', fp)
            if not dry_run:
                os.unlink(fp)

    #

    def get_cache_file_path(
            self,
            key: str,
    ) -> str:
        self.setup_dir()
        return os.path.join(self.dir, key)

    def format_incomplete_file(self, f: str) -> str:
        return os.path.join(os.path.dirname(f), f'_{os.path.basename(f)}.incomplete')

    #

    async def get_file(self, key: str) -> ta.Optional[str]:
        cache_file_path = self.get_cache_file_path(key)
        if not os.path.exists(cache_file_path):
            return None

        if not self._config.no_update_mtime:
            stat_info = os.stat(cache_file_path)
            os.utime(cache_file_path, (stat_info.st_atime, time.time()))

        return cache_file_path

    async def put_file(
            self,
            key: str,
            file_path: str,
            *,
            steal: bool = False,
    ) -> str:
        cache_file_path = self.get_cache_file_path(key)
        if steal:
            shutil.move(file_path, cache_file_path)
        else:
            shutil.copyfile(file_path, cache_file_path)
        return cache_file_path


##


class DataCache:
    @dc.dataclass(frozen=True)
    class Data(Abstract):
        pass

    @dc.dataclass(frozen=True)
    class BytesData(Data):
        data: bytes

    @dc.dataclass(frozen=True)
    class FileData(Data):
        file_path: str

    @dc.dataclass(frozen=True)
    class UrlData(Data):
        url: str

    #

    @abc.abstractmethod
    def get_data(self, key: str) -> ta.Awaitable[ta.Optional[Data]]:
        raise NotImplementedError

    @abc.abstractmethod
    def put_data(self, key: str, data: Data) -> ta.Awaitable[None]:
        raise NotImplementedError


#


@functools.singledispatch
async def read_data_cache_data(data: DataCache.Data) -> bytes:
    raise TypeError(data)


@read_data_cache_data.register
async def _(data: DataCache.BytesData) -> bytes:
    return data.data


@read_data_cache_data.register
async def _(data: DataCache.FileData) -> bytes:
    with open(data.file_path, 'rb') as f:  # noqa
        return f.read()


@read_data_cache_data.register
async def _(data: DataCache.UrlData) -> bytes:
    def inner() -> bytes:
        with urllib.request.urlopen(urllib.request.Request(  # noqa
            data.url,
        )) as resp:
            return resp.read()

    return await asyncio.get_running_loop().run_in_executor(None, inner)


#


class FileCacheDataCache(DataCache):
    def __init__(
            self,
            file_cache: FileCache,
    ) -> None:
        super().__init__()

        self._file_cache = file_cache

    async def get_data(self, key: str) -> ta.Optional[DataCache.Data]:
        if (file_path := await self._file_cache.get_file(key)) is None:
            return None

        return DataCache.FileData(file_path)

    async def put_data(self, key: str, data: DataCache.Data) -> None:
        steal = False

        if isinstance(data, DataCache.BytesData):
            file_path = make_temp_file()
            with open(file_path, 'wb') as f:  # noqa
                f.write(data.data)
            steal = True

        elif isinstance(data, DataCache.FileData):
            file_path = data.file_path

        elif isinstance(data, DataCache.UrlData):
            raise NotImplementedError

        else:
            raise TypeError(data)

        await self._file_cache.put_file(
            key,
            file_path,
            steal=steal,
        )


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
            out_service.pop(k, None)

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
                await es.enter_async_context(adefer(self._cleanup_dependencies()))  # noqa

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
# ../docker/cmds.py


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
        run_options: ta.Optional[ta.Sequence[str]] = None,
) -> str:
    with temp_file_context() as id_file:
        await asyncio_subprocesses.check_call(
            'docker',
            'build',
            '-f', os.path.abspath(docker_file),
            '--iidfile', id_file,
            *(['--tag', tag] if tag is not None else []),
            *(run_options or []),
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


##


async def ensure_docker_image_setup(
        image: str,
        *,
        cwd: ta.Optional[str] = None,
) -> None:
    await asyncio_subprocesses.check_call(
        'docker',
        'run',
        '--rm',
        '--entrypoint', '/bin/true',  # FIXME: lol
        image,
        **(dict(cwd=cwd) if cwd is not None else {}),
    )


########################################
# ../docker/dataserver.py


##


@contextlib.asynccontextmanager
async def start_docker_port_relay(
        docker_port: int,
        host_port: int,
        **kwargs: ta.Any,
) -> ta.AsyncGenerator[None, None]:
    proc = await asyncio.create_subprocess_exec(*DockerPortRelay(
        docker_port,
        host_port,
        **kwargs,
    ).run_cmd())

    try:
        yield

    finally:
        try:
            proc.kill()
        except ProcessLookupError:
            pass
        await proc.wait()


##


class AsyncioManagedSimpleHttpServer(AsyncExitStacked):
    def __init__(
            self,
            port: int,
            handler: HttpHandler,
            *,
            temp_ssl: bool = False,
    ) -> None:
        super().__init__()

        self._port = port
        self._handler = handler

        self._temp_ssl = temp_ssl

        self._lock = threading.RLock()

        self._loop: ta.Optional[asyncio.AbstractEventLoop] = None
        self._thread: ta.Optional[threading.Thread] = None
        self._thread_exit_event = asyncio.Event()
        self._server: ta.Optional[SocketServer] = None

    @cached_nullary
    def _ssl_context(self) -> ta.Optional['ssl.SSLContext']:
        if not self._temp_ssl:
            return None

        ssl_cert = generate_temp_localhost_ssl_cert().cert  # FIXME: async blocking

        ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        ssl_context.load_cert_chain(
            keyfile=ssl_cert.key_file,
            certfile=ssl_cert.cert_file,
        )

        return ssl_context

    @contextlib.contextmanager
    def _make_server(self) -> ta.Iterator[SocketServer]:
        with make_simple_http_server(
                self._port,
                self._handler,
                ssl_context=self._ssl_context(),
                ignore_ssl_errors=True,
                use_threads=True,
        ) as server:
            yield server

    def _thread_main(self) -> None:
        try:
            check.none(self._server)
            with self._make_server() as server:
                self._server = server

                server.run()

        finally:
            check.not_none(self._loop).call_soon_threadsafe(self._thread_exit_event.set)

    def is_running(self) -> bool:
        return self._server is not None

    def shutdown(self) -> None:
        if (server := self._server) is not None:
            server.shutdown(block=False)

    async def run(self) -> None:
        with self._lock:
            check.none(self._loop)
            check.none(self._thread)
            check.state(not self._thread_exit_event.is_set())

            if self._temp_ssl:
                # Hit the ExitStack from this thread
                self._ssl_context()

            self._loop = check.not_none(asyncio.get_running_loop())
            self._thread = threading.Thread(
                target=self._thread_main,
                daemon=True,
            )
            self._thread.start()

        await self._thread_exit_event.wait()


##


class DockerDataServer(AsyncExitStacked):
    def __init__(
            self,
            port: int,
            data_server: DataServer,
            *,
            handler_log: ta.Optional[LoggerLike] = None,
            stop_event: ta.Optional[asyncio.Event] = None,
    ) -> None:
        super().__init__()

        self._port = port
        self._data_server = data_server

        self._handler_log = handler_log

        if stop_event is None:
            stop_event = asyncio.Event()
        self._stop_event = stop_event

    @property
    def stop_event(self) -> asyncio.Event:
        return self._stop_event

    async def run(self) -> None:
        # FIXME:
        #  - shared single server with updatable routes
        #  - get docker used ports with ns1
        #  - discover server port with get_available_port
        #  - discover relay port pair with get_available_ports
        # relay_port: ta.Optional[ta.Tuple[int, int]] = None

        relay_port: ta.Optional[int] = None
        if sys.platform == 'darwin':
            relay_port = self._port
            server_port = self._port + 1
        else:
            server_port = self._port

        #

        handler: HttpHandler = DataServerHttpHandler(self._data_server)

        if self._handler_log is not None:
            handler = LoggingHttpHandler(
                handler,
                self._handler_log,
            )

        #

        async with contextlib.AsyncExitStack() as es:
            if relay_port is not None:
                await es.enter_async_context(start_docker_port_relay(  # noqa
                    relay_port,
                    server_port,
                    intermediate_port=server_port + 1,
                ))

            async with AsyncioManagedSimpleHttpServer(
                    server_port,
                    handler,
                    temp_ssl=True,
            ) as server:
                server_run_task = asyncio.create_task(server.run())
                try:
                    await self._stop_event.wait()

                finally:
                    server.shutdown()
                    await server_run_task


########################################
# ../../../omlish/lite/timing.py


log = get_module_logger(globals())  # noqa


LogTimingContext.DEFAULT_LOG = log

log_timing_context = log_timing_context  # noqa


########################################
# ../docker/cache.py


##


@dc.dataclass(frozen=True)
class DockerCacheKey:
    prefixes: ta.Sequence[str]
    content: str

    def __post_init__(self) -> None:
        check.not_isinstance(self.prefixes, str)

    def append_prefix(self, *prefixes: str) -> 'DockerCacheKey':
        return dc.replace(self, prefixes=(*self.prefixes, *prefixes))

    SEPARATOR: ta.ClassVar[str] = '--'

    def __str__(self) -> str:
        return self.SEPARATOR.join([*self.prefixes, self.content])


##


class DockerCache(Abstract):
    @abc.abstractmethod
    def load_cache_docker_image(self, key: DockerCacheKey) -> ta.Awaitable[ta.Optional[str]]:
        raise NotImplementedError

    @abc.abstractmethod
    def save_cache_docker_image(self, key: DockerCacheKey, image: str) -> ta.Awaitable[None]:
        raise NotImplementedError


class DockerCacheImpl(DockerCache):
    def __init__(
            self,
            *,
            file_cache: ta.Optional[FileCache] = None,
    ) -> None:
        super().__init__()

        self._file_cache = file_cache

    async def load_cache_docker_image(self, key: DockerCacheKey) -> ta.Optional[str]:
        if self._file_cache is None:
            return None

        cache_file = await self._file_cache.get_file(str(key))
        if cache_file is None:
            return None

        get_cache_cmd = ShellCmd(f'cat {cache_file} | zstd -cd --long')

        return await load_docker_tar_cmd(get_cache_cmd)

    async def save_cache_docker_image(self, key: DockerCacheKey, image: str) -> None:
        if self._file_cache is None:
            return

        with temp_file_context() as tmp_file:
            write_tmp_cmd = ShellCmd(f'zstd > {tmp_file}')

            await save_docker_tar_cmd(image, write_tmp_cmd)

            await self._file_cache.put_file(str(key), tmp_file, steal=True)


########################################
# ../docker/repositories.py


##


class DockerImageRepositoryOpener(Abstract):
    @abc.abstractmethod
    def open_docker_image_repository(self, image: str) -> ta.AsyncContextManager[OciRepository]:
        raise NotImplementedError


#


class DockerImageRepositoryOpenerImpl(DockerImageRepositoryOpener):
    @contextlib.asynccontextmanager
    async def open_docker_image_repository(self, image: str) -> ta.AsyncGenerator[OciRepository, None]:
        with temp_dir_context() as save_dir:
            with log_timing_context(f'Saving docker image {image}'):
                await asyncio_subprocesses.check_call(
                    ' | '.join([
                        f'docker save {shlex.quote(image)}',
                        f'tar x -C {shlex.quote(save_dir)}',
                    ]),
                    shell=True,
                )

            yield DirectoryOciRepository(save_dir)


########################################
# ../github/api/clients.py


log = get_module_logger(globals())  # noqa


##


class GithubCacheClient(Abstract):
    @dc.dataclass(frozen=True)
    class Entry(Abstract):
        pass

    @abc.abstractmethod
    def get_entry(self, key: str) -> ta.Awaitable[ta.Optional[Entry]]:
        raise NotImplementedError

    def get_entry_url(self, entry: Entry) -> ta.Optional[str]:
        return None

    @abc.abstractmethod
    def download_file(self, entry: Entry, out_file: str) -> ta.Awaitable[None]:
        raise NotImplementedError

    @abc.abstractmethod
    def upload_file(self, key: str, in_file: str) -> ta.Awaitable[None]:
        raise NotImplementedError


##


class BaseGithubCacheClient(GithubCacheClient, Abstract):
    AUTH_TOKEN_ENV_VAR = register_github_env_var('ACTIONS_RUNTIME_TOKEN')  # noqa

    KEY_SUFFIX_ENV_VAR = register_github_env_var('GITHUB_RUN_ID')

    DEFAULT_CONCURRENCY = 4
    DEFAULT_CHUNK_SIZE = 64 * 1024 * 1024

    #

    def __init__(
            self,
            *,
            service_url: str,

            auth_token: ta.Optional[str] = None,

            key_prefix: ta.Optional[str] = None,
            key_suffix: ta.Optional[str] = None,

            cache_version: int = CI_CACHE_VERSION,

            loop: ta.Optional[asyncio.AbstractEventLoop] = None,

            concurrency: int = DEFAULT_CONCURRENCY,
            chunk_size: int = DEFAULT_CHUNK_SIZE,
    ) -> None:
        super().__init__()

        #

        self._service_url = check.non_empty_str(service_url)

        if auth_token is None:
            auth_token = self.AUTH_TOKEN_ENV_VAR()
        self._auth_token = auth_token

        #

        self._key_prefix = key_prefix

        if key_suffix is None:
            key_suffix = self.KEY_SUFFIX_ENV_VAR()
        self._key_suffix = check.non_empty_str(key_suffix)

        #

        self._cache_version = check.isinstance(cache_version, int)

        #

        self._given_loop = loop

        #

        check.arg(concurrency > 0)
        self._concurrency = concurrency

        check.arg(chunk_size > 0)
        self._chunk_size = chunk_size

    ##
    # misc

    def _get_loop(self) -> asyncio.AbstractEventLoop:
        if (loop := self._given_loop) is not None:
            return loop
        return asyncio.get_running_loop()

    #

    def _load_json_bytes(self, b: ta.Optional[bytes]) -> ta.Optional[ta.Any]:
        if not b:
            return None
        return json.loads(b.decode('utf-8-sig'))

    ##
    # requests

    def _build_request_headers(
            self,
            headers: ta.Optional[ta.Mapping[str, str]] = None,
            *,
            no_auth: bool = False,
            content_type: ta.Optional[str] = None,
            json_content: bool = False,
    ) -> ta.Dict[str, str]:
        dct = {}

        if not no_auth and (auth_token := self._auth_token):
            dct['Authorization'] = f'Bearer {auth_token}'

        if content_type is None and json_content:
            content_type = 'application/json'
        if content_type is not None:
            dct['Content-Type'] = content_type

        if headers:
            dct.update(headers)

        return dct

    #

    async def _send_urllib_request(
            self,
            req: urllib.request.Request,
    ) -> ta.Tuple[http.client.HTTPResponse, ta.Optional[bytes]]:
        def run_sync():
            opener = urllib.request.build_opener(NonRaisingUrllibErrorProcessor)
            with opener.open(req) as resp:  # noqa
                body = resp.read()
            return (resp, body)

        return await self._get_loop().run_in_executor(None, run_sync)  # noqa

    #

    @dc.dataclass()
    class ServiceRequestError(RuntimeError):
        status_code: int
        body: ta.Optional[bytes]

        def __str__(self) -> str:
            return repr(self)

    async def _send_request(
            self,
            *,
            url: ta.Optional[str] = None,
            path: ta.Optional[str] = None,

            method: ta.Optional[str] = None,

            headers: ta.Optional[ta.Mapping[str, str]] = None,
            no_auth: bool = False,
            content_type: ta.Optional[str] = None,

            content: ta.Optional[bytes] = None,
            json_content: ta.Optional[ta.Any] = None,

            success_status_codes: ta.Optional[ta.Container[int]] = None,

            retry_status_codes: ta.Optional[ta.Container[int]] = None,
            num_retries: int = 0,
            retry_sleep: ta.Optional[float] = None,
    ) -> ta.Optional[ta.Any]:
        if url is not None and path is not None:
            raise RuntimeError('Must not pass both url and path')
        elif path is not None:
            url = f'{self._service_url}/{path}'
        url = check.non_empty_str(url)

        if content is not None and json_content is not None:
            raise RuntimeError('Must not pass both content and json_content')
        elif json_content is not None:
            content = json_dumps_compact(json_content).encode('utf-8')
            header_json_content = True
        else:
            header_json_content = False

        if method is None:
            method = 'POST' if content is not None else 'GET'

        headers = self._build_request_headers(
            headers,
            no_auth=no_auth,
            content_type=content_type,
            json_content=header_json_content,
        )

        #

        for n in itertools.count():
            req = urllib.request.Request(  # noqa
                url,
                method=method,
                headers=headers,
                data=content,
            )

            resp, body = await self._send_urllib_request(req)

            #

            if success_status_codes is not None:
                is_success = resp.status in success_status_codes
            else:
                is_success = (200 <= resp.status < 300)
            if is_success:
                return self._load_json_bytes(body)

            #

            log.debug(f'Request to url {url} got unsuccessful status code {resp.status}')  # noqa

            if not (
                retry_status_codes is not None and
                resp.status in retry_status_codes and
                n < num_retries
            ):
                raise self.ServiceRequestError(resp.status, body)

            if retry_sleep is not None:
                await asyncio.sleep(retry_sleep)

        raise RuntimeError('Unreachable')

    ##
    # keys

    KEY_PART_SEPARATOR = '---'

    def fix_key(self, s: str, partial_suffix: bool = False) -> str:
        return self.KEY_PART_SEPARATOR.join([
            *([self._key_prefix] if self._key_prefix else []),
            s,
            ('' if partial_suffix else self._key_suffix),
        ])

    ##
    # downloading

    @dc.dataclass(frozen=True)
    class _DownloadChunk:
        key: str
        url: str
        out_file: str
        offset: int
        size: int

    async def _download_file_chunk_urllib(self, chunk: _DownloadChunk) -> None:
        req = urllib.request.Request(  # noqa
            chunk.url,
            headers={
                'Range': f'bytes={chunk.offset}-{chunk.offset + chunk.size - 1}',
            },
        )

        _, buf_ = await self._send_urllib_request(req)

        buf = check.not_none(buf_)
        check.equal(len(buf), chunk.size)

        #

        def write_sync():
            with open(chunk.out_file, 'r+b') as f:  # noqa
                f.seek(chunk.offset, os.SEEK_SET)
                f.write(buf)

        await self._get_loop().run_in_executor(None, write_sync)  # noqa

    # async def _download_file_chunk_curl(self, chunk: _DownloadChunk) -> None:
    #     async with contextlib.AsyncExitStack() as es:
    #         f = open(chunk.out_file, 'r+b')
    #         f.seek(chunk.offset, os.SEEK_SET)
    #
    #         tmp_file = es.enter_context(temp_file_context())  # noqa
    #
    #         proc = await es.enter_async_context(asyncio_subprocesses.popen(
    #             'curl',
    #             '-s',
    #             '-w', '%{json}',
    #             '-H', f'Range: bytes={chunk.offset}-{chunk.offset + chunk.size - 1}',
    #             chunk.url,
    #             output=subprocess.PIPE,
    #         ))
    #
    #         futs = asyncio.gather(
    #
    #         )
    #
    #         await proc.wait()
    #
    #         with open(tmp_file, 'r') as f:  # noqa
    #             curl_json = tmp_file.read()
    #
    #     curl_res = json.loads(curl_json.decode().strip())
    #
    #     status_code = check.isinstance(curl_res['response_code'], int)
    #
    #     if not (200 <= status_code < 300):
    #         raise RuntimeError(f'Curl chunk download {chunk} failed: {curl_res}')

    async def _download_file_chunk(self, chunk: _DownloadChunk) -> None:
        with log_timing_context(
                'Downloading github cache '
                f'key {chunk.key} '
                f'file {chunk.out_file} '
                f'chunk {chunk.offset} - {chunk.offset + chunk.size}',
        ):
            await self._download_file_chunk_urllib(chunk)

    async def _download_file_chunks(
            self,
            *,
            key: str,
            url: str,
            out_file: str,
    ) -> None:
        check.non_empty_str(key)
        check.non_empty_str(url)

        head_resp, _ = await self._send_urllib_request(urllib.request.Request(  # noqa
            url,
            method='HEAD',
        ))
        file_size = int(head_resp.headers['Content-Length'])

        #

        with open(out_file, 'xb') as f:  # noqa
            f.truncate(file_size)

        #

        download_tasks = []
        chunk_size = self._chunk_size
        for i in range((file_size // chunk_size) + (1 if file_size % chunk_size else 0)):
            offset = i * chunk_size
            size = min(chunk_size, file_size - offset)
            chunk = self._DownloadChunk(
                key,
                url,
                out_file,
                offset,
                size,
            )
            download_tasks.append(self._download_file_chunk(chunk))

        await asyncio_wait_concurrent(download_tasks, self._concurrency)

    ##
    # uploading

    @dc.dataclass(frozen=True)
    class _UploadChunk:
        url: str
        key: str
        in_file: str
        offset: int
        size: int

    UPLOAD_CHUNK_NUM_RETRIES = 10
    UPLOAD_CHUNK_RETRY_SLEEP = .5

    async def _upload_file_chunk_(self, chunk: _UploadChunk) -> None:
        with open(chunk.in_file, 'rb') as f:  # noqa
            f.seek(chunk.offset)
            buf = f.read(chunk.size)

        check.equal(len(buf), chunk.size)

        await self._send_request(
            url=chunk.url,

            method='PATCH',

            headers={
                'Content-Range': f'bytes {chunk.offset}-{chunk.offset + chunk.size - 1}/*',
            },
            no_auth=True,
            content_type='application/octet-stream',

            content=buf,

            success_status_codes=[204],

            # retry_status_codes=[405],
            num_retries=self.UPLOAD_CHUNK_NUM_RETRIES,
            retry_sleep=self.UPLOAD_CHUNK_RETRY_SLEEP,
        )

    async def _upload_file_chunk(self, chunk: _UploadChunk) -> None:
        with log_timing_context(
                f'Uploading github cache {chunk.key} '
                f'file {chunk.in_file} '
                f'chunk {chunk.offset} - {chunk.offset + chunk.size}',
        ):
            await self._upload_file_chunk_(chunk)

    def _generate_file_upload_chunks(
            self,
            *,
            in_file: str,
            url: str,
            key: str,

            file_size: ta.Optional[int] = None,
    ) -> ta.List[_UploadChunk]:
        check.state(os.path.isfile(in_file))

        if file_size is None:
            file_size = os.stat(in_file).st_size

        #

        upload_chunks: ta.List[BaseGithubCacheClient._UploadChunk] = []
        chunk_size = self._chunk_size
        for i in range((file_size // chunk_size) + (1 if file_size % chunk_size else 0)):
            offset = i * chunk_size
            size = min(chunk_size, file_size - offset)
            upload_chunks.append(self._UploadChunk(
                url=url,
                key=key,
                in_file=in_file,
                offset=offset,
                size=size,
            ))

        return upload_chunks

    async def _upload_file_chunks(
            self,
            *,
            in_file: str,
            url: str,
            key: str,

            file_size: ta.Optional[int] = None,
    ) -> None:
        upload_tasks = []
        for chunk in self._generate_file_upload_chunks(
            in_file=in_file,
            url=url,
            key=key,
            file_size=file_size,
        ):
            upload_tasks.append(self._upload_file_chunk(chunk))

        await asyncio_wait_concurrent(upload_tasks, self._concurrency)


########################################
# ../github/api/v2/azure.py
"""
TODO:
 - ominfra? no, circdep
"""


log = get_module_logger(globals())  # noqa


##


class AzureBlockBlobUploader:
    """
    https://learn.microsoft.com/en-us/rest/api/storageservices/put-block
    https://learn.microsoft.com/en-us/rest/api/storageservices/put-block-list
    """

    DEFAULT_CONCURRENCY = 4

    @dc.dataclass(frozen=True)
    class Request:
        method: str
        url: str
        headers: ta.Optional[ta.Dict[str, str]] = None
        body: ta.Optional[bytes] = None

    @dc.dataclass(frozen=True)
    class Response:
        status: int
        headers: ta.Optional[ta.Mapping[str, str]] = None
        data: ta.Optional[bytes] = None

        def get_header(self, name: str) -> ta.Optional[str]:
            for k, v in (self.headers or {}).items():
                if k.lower() == name.lower():
                    return v
            return None

    def __init__(
            self,
            blob_url_with_sas: str,
            make_request: ta.Callable[[Request], ta.Awaitable[Response]],
            *,
            api_version: str = '2020-10-02',
            concurrency: int = DEFAULT_CONCURRENCY,
    ) -> None:
        """
        blob_url_with_sas should be of the form:
           https://<account>.blob.core.windows.net/<container>/<blob>?<SAS-token>
        """

        super().__init__()

        self._make_request = make_request
        self._api_version = api_version
        check.arg(concurrency >= 1)
        self._concurrency = concurrency

        parsed = urllib.parse.urlparse(blob_url_with_sas)
        self._base_url = f'{parsed.scheme}://{parsed.netloc}'
        parts = parsed.path.lstrip('/').split('/', 1)
        self._container = parts[0]
        self._blob_name = parts[1]
        self._sas = parsed.query

    def _headers(self) -> ta.Dict[str, str]:
        """Standard headers for Azure Blob REST calls."""

        now = datetime.datetime.now(datetime.UTC).strftime('%a, %d %b %Y %H:%M:%S GMT')
        return {
            'x-ms-date': now,
            'x-ms-version': self._api_version,
        }

    @dc.dataclass(frozen=True)
    class FileChunk:
        in_file: str
        offset: int
        size: int

    async def _upload_file_chunk_(
            self,
            block_id: str,
            chunk: FileChunk,
    ) -> None:
        with open(chunk.in_file, 'rb') as f:  # noqa
            f.seek(chunk.offset)
            data = f.read(chunk.size)

        check.equal(len(data), chunk.size)

        params = {
            'comp': 'block',
            'blockid': block_id,
        }
        query = self._sas + '&' + urllib.parse.urlencode(params)
        url = f'{self._base_url}/{self._container}/{self._blob_name}?{query}'

        log.debug(f'Uploading azure blob chunk {chunk} with block id {block_id}')  # noqa

        resp = await self._make_request(self.Request(
            'PUT',
            url,
            headers=self._headers(),
            body=data,
        ))
        if resp.status not in (201, 202):
            raise RuntimeError(f'Put Block failed: {block_id=} {resp.status=}')

    async def _upload_file_chunk(
            self,
            block_id: str,
            chunk: FileChunk,
    ) -> None:
        with log_timing_context(f'Uploading azure blob chunk {chunk} with block id {block_id}'):
            await self._upload_file_chunk_(
                block_id,
                chunk,
            )

    async def upload_file(
            self,
            chunks: ta.List[FileChunk],
    ) -> ta.Dict[str, ta.Any]:
        block_ids = []

        # 1) Stage each block
        upload_tasks = []
        for idx, chunk in enumerate(chunks):
            # Generate a predictable block ID (must be URL-safe base64)
            raw_id = f'{idx:08d}'.encode()
            block_id = base64.b64encode(raw_id).decode('utf-8')
            block_ids.append(block_id)

            upload_tasks.append(self._upload_file_chunk(
                block_id,
                chunk,
            ))

        await asyncio_wait_concurrent(upload_tasks, self._concurrency)

        # 2) Commit block list
        root = ET.Element('BlockList')
        for bid in block_ids:
            elm = ET.SubElement(root, 'Latest')
            elm.text = bid
        body = ET.tostring(root, encoding='utf-8', method='xml')

        params = {'comp': 'blocklist'}
        query = self._sas + '&' + urllib.parse.urlencode(params)
        url = f'{self._base_url}/{self._container}/{self._blob_name}?{query}'

        log.debug(f'Putting azure blob chunk list block ids {block_ids}')  # noqa

        resp = await self._make_request(self.Request(
            'PUT',
            url,
            headers={
                **self._headers(),
                'Content-Type': 'application/xml',
            },
            body=body,
        ))
        if resp.status not in (200, 201):
            raise RuntimeError(f'Put Block List failed: {resp.status} {resp.data!r}')

        ret = {
            'status_code': resp.status,
            'etag': resp.get_header('ETag'),
        }

        log.debug(f'Uploaded azure blob chunk {ret}')  # noqa

        return ret


########################################
# ../../oci/pack/repositories.py


##


class OciPackedRepositoryBuilder(ExitStacked):
    def __init__(
            self,
            source_repo: OciRepository,
            *,
            temp_dir: ta.Optional[str] = None,

            num_packed_files: int = 3,  # GH actions have this set to 3, the default
            packed_compression: ta.Optional[OciCompression] = OciCompression.ZSTD,
    ) -> None:
        super().__init__()

        self._source_repo = source_repo

        self._given_temp_dir = temp_dir

        check.arg(num_packed_files > 0)
        self._num_packed_files = num_packed_files

        self._packed_compression = packed_compression

    @cached_nullary
    def _temp_dir(self) -> str:
        if (given := self._given_temp_dir) is not None:
            return given
        else:
            return self._enter_context(temp_dir_context())  # noqa

    #

    @cached_nullary
    def _source_image_index(self) -> OciImageIndex:
        image_index = read_oci_repository_root_index(self._source_repo)
        return get_single_leaf_oci_image_index(image_index)

    @cached_nullary
    def _source_image_manifest(self) -> OciImageManifest:
        return get_single_oci_image_manifest(self._source_image_index())

    #

    @cached_nullary
    def _extracted_layer_tar_files(self) -> ta.List[str]:
        image = self._source_image_manifest()

        layer_tar_files = []

        for i, layer in enumerate(image.layers):
            if isinstance(layer.data, FileOciDataRef):
                input_file_path = layer.data.path

            else:
                input_file_path = os.path.join(self._temp_dir(), f'save-layer-{i}.tar')
                with open(input_file_path, 'wb') as input_file:  # noqa
                    with open_oci_data_ref(layer.data) as layer_file:
                        shutil.copyfileobj(layer_file, input_file, length=1024 * 1024)  # noqa

            layer_tar_files.append(input_file_path)

        return layer_tar_files

    #

    @cached_nullary
    def _unpacked_tar_file(self) -> str:
        layer_tar_files = self._extracted_layer_tar_files()
        unpacked_file = os.path.join(self._temp_dir(), 'unpacked.tar')

        with log_timing_context(f'Unpacking docker image {self._source_repo}'):
            with OciLayerUnpacker(
                    layer_tar_files,
                    unpacked_file,
            ) as lu:
                lu.write()

        return unpacked_file

    #

    @cached_nullary
    def _packed_tar_files(self) -> ta.Mapping[str, WrittenOciDataTarFileInfo]:
        unpacked_tar_file = self._unpacked_tar_file()

        packed_tar_files = [
            os.path.join(self._temp_dir(), f'packed-{i}.tar')
            for i in range(self._num_packed_files)
        ]

        with log_timing_context(f'Packing docker image {self._source_repo}'):
            with OciLayerPacker(
                    unpacked_tar_file,
                    packed_tar_files,
                    compression=self._packed_compression,
            ) as lp:
                return lp.write()

    #

    @cached_nullary
    def _packed_image_index(self) -> OciImageIndex:
        image_index = copy.deepcopy(self._source_image_index())

        image = get_single_oci_image_manifest(image_index)

        image.config.history = None

        written = self._packed_tar_files()

        # FIXME: use prebuilt sha256
        image.layers = [
            OciImageLayer(
                kind=OciImageLayer.Kind.from_compression(self._packed_compression),
                data=FileOciDataRef(output_file),
            )
            for output_file, output_file_info in written.items()
        ]

        image.config.rootfs.diff_ids = [
            f'sha256:{output_file_info.tar_sha256}'
            for output_file_info in written.values()
        ]

        return image_index

    #

    @cached_nullary
    def build(self) -> BuiltOciImageIndexRepository:
        return build_oci_index_repository(self._packed_image_index())


########################################
# ../docker/buildcaching.py


##


class DockerBuildCaching(Abstract):
    @abc.abstractmethod
    def cached_build_docker_image(
            self,
            cache_key: DockerCacheKey,
            build_and_tag: ta.Callable[[str], ta.Awaitable[str]],  # image_tag -> image_id
    ) -> ta.Awaitable[str]:
        raise NotImplementedError


class DockerBuildCachingImpl(DockerBuildCaching):
    @dc.dataclass(frozen=True)
    class Config:
        service: str

        always_build: bool = False

    def __init__(
            self,
            *,
            config: Config,

            docker_cache: ta.Optional[DockerCache] = None,
    ) -> None:
        super().__init__()

        self._config = config

        self._docker_cache = docker_cache

    async def cached_build_docker_image(
            self,
            cache_key: DockerCacheKey,
            build_and_tag: ta.Callable[[str], ta.Awaitable[str]],
    ) -> str:
        image_tag = f'{self._config.service}:{cache_key!s}'

        if not self._config.always_build and (await is_docker_image_present(image_tag)):
            return image_tag

        if (
                self._docker_cache is not None and
                (cache_image_id := await self._docker_cache.load_cache_docker_image(cache_key)) is not None
        ):
            await tag_docker_image(
                cache_image_id,
                image_tag,
            )
            return image_tag

        image_id = await build_and_tag(image_tag)

        if self._docker_cache is not None:
            await self._docker_cache.save_cache_docker_image(cache_key, image_id)

        return image_tag


########################################
# ../docker/cacheserved/cache.py


log = get_module_logger(globals())  # noqa


##


class CacheServedDockerCache(DockerCache):
    @dc.dataclass(frozen=True)
    class Config:
        port: int = 5021

        repack: bool = True

        key_prefix: ta.Optional[str] = 'cs'

        #

        pull_run_cmd: ta.Optional[str] = 'true'

        #

        server_start_timeout: TimeoutLike = 5.
        server_start_sleep: float = .1

    def __init__(
            self,
            *,
            config: Config = Config(),

            image_repo_opener: DockerImageRepositoryOpener,
            data_cache: DataCache,
    ) -> None:
        super().__init__()

        self._config = config

        self._image_repo_opener = image_repo_opener
        self._data_cache = data_cache

    async def load_cache_docker_image(self, key: DockerCacheKey) -> ta.Optional[str]:
        if (kp := self._config.key_prefix) is not None:
            key = key.append_prefix(kp)

        if (manifest_data := await self._data_cache.get_data(str(key))) is None:
            return None

        manifest_bytes = await read_data_cache_data(manifest_data)

        manifest: CacheServedDockerImageManifest = unmarshal_obj(
            json.loads(manifest_bytes.decode('utf-8')),
            CacheServedDockerImageManifest,
        )

        async def make_cache_key_target(target_cache_key: str, **target_kwargs: ta.Any) -> DataServerTarget:  # noqa
            cache_data = check.not_none(await self._data_cache.get_data(target_cache_key))

            if isinstance(cache_data, DataCache.BytesData):
                return DataServerTarget.of(
                    cache_data.data,
                    **target_kwargs,
                )

            elif isinstance(cache_data, DataCache.FileData):
                return DataServerTarget.of(
                    file_path=cache_data.file_path,
                    **target_kwargs,
                )

            elif isinstance(cache_data, DataCache.UrlData):
                return DataServerTarget.of(
                    url=cache_data.url,
                    methods=['GET'],
                    **target_kwargs,
                )

            else:
                raise TypeError(cache_data)

        data_server_routes = await build_cache_served_docker_image_data_server_routes(
            manifest,
            make_cache_key_target,
        )

        data_server = DataServer(DataServer.HandlerRoute.of_(*data_server_routes))

        image_url = f'localhost:{self._config.port}/{key!s}'

        async with DockerDataServer(
                self._config.port,
                data_server,
                handler_log=log,
        ) as dds:
            dds_run_task = asyncio.create_task(dds.run())
            try:
                timeout = Timeout.of(self._config.server_start_timeout)

                await asyncio_wait_until_can_connect(
                    'localhost',
                    self._config.port,
                    timeout=timeout,
                    on_fail=lambda _: log.exception('Failed to connect to cache server - will try again'),
                    sleep_s=self._config.server_start_sleep,
                )

                if (prc := self._config.pull_run_cmd) is not None:
                    pull_cmd = [
                        'run',
                        '--rm',
                        image_url,
                        prc,
                    ]
                else:
                    pull_cmd = [
                        'pull',
                        image_url,
                    ]

                await asyncio_subprocesses.check_call(
                    'docker',
                    *pull_cmd,
                )

            finally:
                dds.stop_event.set()
                await dds_run_task

        return image_url

    async def save_cache_docker_image(self, key: DockerCacheKey, image: str) -> None:
        if (kp := self._config.key_prefix) is not None:
            key = key.append_prefix(kp)

        async with contextlib.AsyncExitStack() as es:
            image_repo: OciRepository = await es.enter_async_context(
                self._image_repo_opener.open_docker_image_repository(image),
            )

            root_image_index = read_oci_repository_root_index(image_repo)
            image_index = get_single_leaf_oci_image_index(root_image_index)

            if self._config.repack:
                prb: OciPackedRepositoryBuilder = es.enter_context(OciPackedRepositoryBuilder(
                    image_repo,
                ))
                built_repo = await asyncio.get_running_loop().run_in_executor(None, prb.build)  # noqa

            else:
                built_repo = build_oci_index_repository(image_index)

            data_server_routes = build_oci_repository_data_server_routes(
                str(key),
                built_repo,
            )

            async def make_file_cache_key(file_path: str) -> str:
                target_cache_key = f'{key!s}--{os.path.basename(file_path).split(".")[0]}'
                await self._data_cache.put_data(
                    target_cache_key,
                    DataCache.FileData(file_path),
                )
                return target_cache_key

            cache_served_manifest = await build_cache_served_docker_image_manifest(
                data_server_routes,
                make_file_cache_key,
            )

        manifest_data = json_dumps_compact(marshal_obj(cache_served_manifest)).encode('utf-8')

        await self._data_cache.put_data(
            str(key),
            DataCache.BytesData(manifest_data),
        )


########################################
# ../docker/imagepulling.py


##


class DockerImagePulling(Abstract):
    @abc.abstractmethod
    def pull_docker_image(self, image: str) -> ta.Awaitable[None]:
        raise NotImplementedError


class DockerImagePullingImpl(DockerImagePulling):
    @dc.dataclass(frozen=True)
    class Config:
        always_pull: bool = False

    def __init__(
            self,
            *,
            config: Config = Config(),

            file_cache: ta.Optional[FileCache] = None,
            docker_cache: ta.Optional[DockerCache] = None,
    ) -> None:
        super().__init__()

        self._config = config

        self._file_cache = file_cache
        self._docker_cache = docker_cache

    async def _pull_docker_image(self, image: str) -> None:
        if not self._config.always_pull and (await is_docker_image_present(image)):
            return

        key_content = StringMangler.of('-', '/:._').mangle(image)

        cache_key = DockerCacheKey(['docker'], key_content)
        if (
                self._docker_cache is not None and
                (await self._docker_cache.load_cache_docker_image(cache_key)) is not None
        ):
            return

        await pull_docker_image(image)

        if self._docker_cache is not None:
            await self._docker_cache.save_cache_docker_image(cache_key, image)

    async def pull_docker_image(self, image: str) -> None:
        with log_timing_context(f'Load docker image: {image}'):
            await self._pull_docker_image(image)


########################################
# ../github/api/v1/client.py


log = get_module_logger(globals())  # noqa


##


class GithubCacheServiceV1Client(BaseGithubCacheClient):
    BASE_URL_ENV_VAR = register_github_env_var('ACTIONS_CACHE_URL')

    def __init__(
            self,
            *,
            base_url: ta.Optional[str] = None,

            **kwargs: ta.Any,
    ) -> None:
        if base_url is None:
            base_url = check.non_empty_str(self.BASE_URL_ENV_VAR())
        service_url = GithubCacheServiceV1.get_service_url(base_url)

        super().__init__(
            service_url=service_url,
            **kwargs,
        )

    #

    def _build_request_headers(
            self,
            headers: ta.Optional[ta.Mapping[str, str]] = None,
            **kwargs: ta.Any,
    ) -> ta.Dict[str, str]:
        return super()._build_request_headers(
            {
                'Accept': ';'.join([
                    'application/json',
                    f'api-version={GithubCacheServiceV1.API_VERSION}',
                ]),
                **(headers or {}),
            },
            **kwargs,
        )

    #

    @dc.dataclass(frozen=True)
    class Entry(GithubCacheClient.Entry):
        artifact: GithubCacheServiceV1.ArtifactCacheEntry

    def get_entry_url(self, entry: GithubCacheClient.Entry) -> ta.Optional[str]:
        entry1 = check.isinstance(entry, self.Entry)
        return entry1.artifact.archive_location

    #

    def _build_get_entry_url_path(self, *keys: str) -> str:
        qp = dict(
            keys=','.join(urllib.parse.quote_plus(k) for k in keys),
            version=str(self._cache_version),
        )

        return '?'.join([
            'cache',
            '&'.join([
                f'{k}={v}'
                for k, v in qp.items()
            ]),
        ])

    GET_ENTRY_SUCCESS_STATUS_CODES = (200, 204)

    #

    async def get_entry(self, key: str) -> ta.Optional[GithubCacheClient.Entry]:
        obj = await self._send_request(
            path=self._build_get_entry_url_path(self.fix_key(key, partial_suffix=True)),
        )
        if obj is None:
            return None

        return self.Entry(GithubCacheServiceV1.dataclass_from_json(
            GithubCacheServiceV1.ArtifactCacheEntry,
            obj,
        ))

    #

    async def download_file(self, entry: GithubCacheClient.Entry, out_file: str) -> None:
        entry1 = check.isinstance(entry, self.Entry)
        with log_timing_context(
                'Downloading github cache '
                f'key {entry1.artifact.cache_key} '
                f'version {entry1.artifact.cache_version} '
                f'to {out_file}',
        ):
            await self._download_file_chunks(
                key=check.non_empty_str(entry1.artifact.cache_key),
                url=check.non_empty_str(entry1.artifact.archive_location),
                out_file=out_file,
            )

    #

    async def _upload_file(self, key: str, in_file: str) -> None:
        fixed_key = self.fix_key(key)

        check.state(os.path.isfile(in_file))
        file_size = os.stat(in_file).st_size

        #

        reserve_req = GithubCacheServiceV1.ReserveCacheRequest(
            key=fixed_key,
            cache_size=file_size,
            version=str(self._cache_version),
        )
        reserve_resp_obj = await self._send_request(
            path='caches',
            json_content=GithubCacheServiceV1.dataclass_to_json(reserve_req),
            success_status_codes=[201],
        )
        reserve_resp = GithubCacheServiceV1.dataclass_from_json(  # noqa
            GithubCacheServiceV1.ReserveCacheResponse,
            reserve_resp_obj,
        )
        cache_id = check.isinstance(reserve_resp.cache_id, int)

        log.debug(f'Github cache file {os.path.basename(in_file)} got id {cache_id}')  # noqa

        #

        url = f'{self._service_url}/caches/{cache_id}'

        await self._upload_file_chunks(
            in_file=in_file,
            url=url,
            key=fixed_key,
            file_size=file_size,
        )

        #

        commit_req = GithubCacheServiceV1.CommitCacheRequest(
            size=file_size,
        )
        await self._send_request(
            path=f'caches/{cache_id}',
            json_content=GithubCacheServiceV1.dataclass_to_json(commit_req),
            success_status_codes=[204],
        )

    async def upload_file(self, key: str, in_file: str) -> None:
        with log_timing_context(
                f'Uploading github cache file {os.path.basename(in_file)} '
                f'key {key}',
        ):
            await self._upload_file(key, in_file)


########################################
# ../github/api/v2/client.py


log = get_module_logger(globals())  # noqa


##


class GithubCacheServiceV2Client(BaseGithubCacheClient):
    BASE_URL_ENV_VAR = register_github_env_var('ACTIONS_RESULTS_URL')

    def __init__(
            self,
            *,
            base_url: ta.Optional[str] = None,

            **kwargs: ta.Any,
    ) -> None:
        if base_url is None:
            base_url = check.non_empty_str(self.BASE_URL_ENV_VAR())
        service_url = GithubCacheServiceV2.get_service_url(base_url)

        super().__init__(
            service_url=service_url,
            **kwargs,
        )

    #

    async def _send_method_request(
            self,
            method: GithubCacheServiceV2.Method[
                GithubCacheServiceV2RequestT,
                GithubCacheServiceV2ResponseT,
            ],
            request: GithubCacheServiceV2RequestT,
            **kwargs: ta.Any,
    ) -> ta.Optional[GithubCacheServiceV2ResponseT]:
        obj = await self._send_request(
            path=method.name,
            json_content=dc.asdict(request),  # type: ignore[call-overload]
            **kwargs,
        )

        if obj is None:
            return None
        return method.response(**obj)

    #

    @dc.dataclass(frozen=True)
    class Entry(GithubCacheClient.Entry):
        request: GithubCacheServiceV2.GetCacheEntryDownloadUrlRequest
        response: GithubCacheServiceV2.GetCacheEntryDownloadUrlResponse

        def __post_init__(self) -> None:
            check.state(self.response.ok)
            check.non_empty_str(self.response.signed_download_url)

    def get_entry_url(self, entry: GithubCacheClient.Entry) -> ta.Optional[str]:
        entry2 = check.isinstance(entry, self.Entry)
        return check.non_empty_str(entry2.response.signed_download_url)

    #

    async def get_entry(self, key: str) -> ta.Optional[GithubCacheClient.Entry]:
        version = str(self._cache_version).zfill(GithubCacheServiceV2.VERSION_LENGTH)

        req = GithubCacheServiceV2.GetCacheEntryDownloadUrlRequest(
            key=self.fix_key(key),
            restore_keys=[self.fix_key(key, partial_suffix=True)],
            version=version,
        )

        resp = await self._send_method_request(
            GithubCacheServiceV2.GET_CACHE_ENTRY_DOWNLOAD_URL_METHOD,
            req,
        )
        if resp is None or not resp.ok:
            return None

        return self.Entry(
            request=req,
            response=resp,
        )

    #

    async def download_file(self, entry: GithubCacheClient.Entry, out_file: str) -> None:
        entry2 = check.isinstance(entry, self.Entry)
        with log_timing_context(
                'Downloading github cache '
                f'key {entry2.response.matched_key} '
                f'version {entry2.request.version} '
                f'to {out_file}',
        ):
            await self._download_file_chunks(
                key=check.non_empty_str(entry2.response.matched_key),
                url=check.non_empty_str(entry2.response.signed_download_url),
                out_file=out_file,
            )

    #

    async def _upload_file(self, key: str, in_file: str) -> None:
        fixed_key = self.fix_key(key)

        check.state(os.path.isfile(in_file))
        file_size = os.stat(in_file).st_size

        #

        version = str(self._cache_version).zfill(GithubCacheServiceV2.VERSION_LENGTH)

        reserve_resp = check.not_none(await self._send_method_request(
            GithubCacheServiceV2.CREATE_CACHE_ENTRY_METHOD,  # type: ignore[arg-type]
            GithubCacheServiceV2.CreateCacheEntryRequest(
                key=fixed_key,
                version=version,
            ),
        ))
        check.state(reserve_resp.ok)

        log.debug(f'Github cache file {os.path.basename(in_file)} upload reserved for file size {file_size}')  # noqa

        #

        upload_chunks = self._generate_file_upload_chunks(
            in_file=in_file,
            url=reserve_resp.signed_upload_url,
            key=fixed_key,
            file_size=file_size,
        )

        az_chunks = [
            AzureBlockBlobUploader.FileChunk(
                in_file=in_file,
                offset=c.offset,
                size=c.size,
            )
            for c in upload_chunks
        ]

        async def az_make_request(req: AzureBlockBlobUploader.Request) -> AzureBlockBlobUploader.Response:
            u_req = urllib.request.Request(  # noqa
                req.url,
                method=req.method,
                headers=req.headers or {},
                data=req.body,
            )

            u_resp, u_body = await self._send_urllib_request(u_req)

            return AzureBlockBlobUploader.Response(
                status=u_resp.status,
                headers=dict(u_resp.headers),
                data=u_body,
            )

        az_uploader = AzureBlockBlobUploader(
            reserve_resp.signed_upload_url,
            az_make_request,
            concurrency=self._concurrency,
        )

        await az_uploader.upload_file(az_chunks)

        #

        commit_resp = check.not_none(await self._send_method_request(
            GithubCacheServiceV2.FINALIZE_CACHE_ENTRY_METHOD,  # type: ignore[arg-type]
            GithubCacheServiceV2.FinalizeCacheEntryUploadRequest(
                key=fixed_key,
                size_bytes=file_size,
                version=version,
            ),
        ))
        check.state(commit_resp.ok)

        log.debug(f'Github cache file {os.path.basename(in_file)} upload complete, entry id {commit_resp.entry_id}')  # noqa

    async def upload_file(self, key: str, in_file: str) -> None:
        with log_timing_context(
                f'Uploading github cache file {os.path.basename(in_file)} '
                f'key {key}',
        ):
            await self._upload_file(key, in_file)


########################################
# ../ci.py


##


class Ci(AsyncExitStacked):
    KEY_HASH_LEN = 16

    @dc.dataclass(frozen=True)
    class Config:
        project_dir: str

        docker_file: str

        compose_file: str
        service: str

        cmd: ShellCmd

        #

        requirements_txts: ta.Optional[ta.Sequence[str]] = None

        always_pull: bool = False
        always_build: bool = False

        setup_concurrency: ta.Optional[int] = None

        no_dependencies: bool = False

        setup_only: bool = False

        run_options: ta.Optional[ta.Sequence[str]] = None

        #

        def __post_init__(self) -> None:
            check.not_isinstance(self.requirements_txts, str)

    def __init__(
            self,
            config: Config,
            *,
            docker_build_caching: DockerBuildCaching,
            docker_image_pulling: DockerImagePulling,
    ) -> None:
        super().__init__()

        self._config = config

        self._docker_build_caching = docker_build_caching
        self._docker_image_pulling = docker_image_pulling

    #

    @cached_nullary
    def docker_file_hash(self) -> str:
        return build_docker_file_hash(self._config.docker_file)[:self.KEY_HASH_LEN]

    @cached_nullary
    def ci_base_image_cache_key(self) -> DockerCacheKey:
        return DockerCacheKey(['ci-base'], self.docker_file_hash())

    async def _resolve_ci_base_image(self) -> str:
        async def build_and_tag(image_tag: str) -> str:
            return await build_docker_image(
                self._config.docker_file,
                tag=image_tag,
                cwd=self._config.project_dir,
            )

        return await self._docker_build_caching.cached_build_docker_image(
            self.ci_base_image_cache_key(),
            build_and_tag,
        )

    @async_cached_nullary
    async def resolve_ci_base_image(self) -> str:
        with log_timing_context('Resolve ci base image') as ltc:
            image_id = await self._resolve_ci_base_image()
            ltc.set_description(f'Resolve ci base image: {image_id}')
            return image_id

    #

    @cached_nullary
    def requirements_txts(self) -> ta.Sequence[str]:
        return [
            os.path.join(self._config.project_dir, rf)
            for rf in check.not_none(self._config.requirements_txts)
        ]

    @cached_nullary
    def requirements_hash(self) -> str:
        return build_requirements_hash(self.requirements_txts())[:self.KEY_HASH_LEN]

    @cached_nullary
    def ci_image_cache_key(self) -> DockerCacheKey:
        return DockerCacheKey(['ci'], f'{self.docker_file_hash()}-{self.requirements_hash()}')

    async def _resolve_ci_image(self) -> str:
        async def build_and_tag(image_tag: str) -> str:
            base_image = await self.resolve_ci_base_image()

            setup_cmds = [
                ' '.join([
                    'pip install',
                    '--no-cache-dir',
                    '--root-user-action ignore',
                    'uv',
                ]),
                ' '.join([
                    'uv pip install',
                    '--no-cache',
                    '--index-strategy unsafe-best-match',
                    '--system',
                    *[f'-r /project/{rf}' for rf in self._config.requirements_txts or []],
                ]),
            ]
            setup_cmd = ' && '.join(setup_cmds)

            docker_file_lines = [
                f'FROM {base_image}',
                'RUN mkdir /project',
                *[f'COPY {rf} /project/{rf}' for rf in self._config.requirements_txts or []],
                f'RUN {setup_cmd}',
                'RUN rm /project/*',
                'WORKDIR /project',
            ]

            with temp_file_context() as docker_file:
                with open(docker_file, 'w') as f:  # noqa
                    f.write('\n'.join(docker_file_lines))

                return await build_docker_image(
                    docker_file,
                    tag=image_tag,
                    cwd=self._config.project_dir,
                )

        return await self._docker_build_caching.cached_build_docker_image(
            self.ci_image_cache_key(),
            build_and_tag,
        )

    @async_cached_nullary
    async def resolve_ci_image(self) -> str:
        with log_timing_context('Resolve ci image') as ltc:
            image_id = await self._resolve_ci_image()
            ltc.set_description(f'Resolve ci image: {image_id}')
            return image_id

    #

    @cached_nullary
    def get_dependency_images(self) -> ta.Sequence[str]:
        deps = get_compose_service_dependencies(
            self._config.compose_file,
            self._config.service,
        )
        return sorted(deps.values())

    @cached_nullary
    def pull_dependencies_funcs(self) -> ta.Sequence[ta.Callable[[], ta.Awaitable]]:
        return [
            async_cached_nullary(functools.partial(
                self._docker_image_pulling.pull_docker_image,
                dep_image,
            ))
            for dep_image in self.get_dependency_images()
        ]

    #

    @cached_nullary
    def setup_funcs(self) -> ta.Sequence[ta.Callable[[], ta.Awaitable]]:
        return [
            self.resolve_ci_image,

            *(self.pull_dependencies_funcs() if not self._config.no_dependencies else []),
        ]

    @async_cached_nullary
    async def setup(self) -> None:
        await asyncio_wait_maybe_concurrent(
            [fn() for fn in self.setup_funcs()],
            self._config.setup_concurrency,
        )

    #

    async def _run_compose_(self) -> None:
        async with DockerComposeRun(DockerComposeRun.Config(
            compose_file=self._config.compose_file,
            service=self._config.service,

            image=await self.resolve_ci_image(),

            cmd=self._config.cmd,

            run_options=[
                '-v', f'{os.path.abspath(self._config.project_dir)}:/project',
                *(self._config.run_options or []),
            ],

            cwd=self._config.project_dir,

            no_dependencies=self._config.no_dependencies,
        )) as ci_compose_run:
            await ci_compose_run.run()

    async def _run_compose(self) -> None:
        with log_timing_context('Run compose'):
            await self._run_compose_()

    #

    async def _run_setup_only(self) -> None:
        image_ids = [
            await self.resolve_ci_image(),

            *(self.get_dependency_images() if not self._config.no_dependencies else []),
        ]

        for image_id in image_ids:
            with log_timing_context(f'Run setup only: {image_id}'):
                await ensure_docker_image_setup(
                    image_id,
                    cwd=self._config.project_dir,
                )

    #

    async def run(self) -> None:
        await self.setup()

        if self._config.setup_only:
            await self._run_setup_only()
        else:
            await self._run_compose()


########################################
# ../docker/inject.py


##


def bind_docker(
        *,
        build_caching_config: DockerBuildCachingImpl.Config,
        cache_served_docker_cache_config: ta.Optional[CacheServedDockerCache.Config] = None,
        image_pulling_config: DockerImagePullingImpl.Config = DockerImagePullingImpl.Config(),
) -> InjectorBindings:
    lst: ta.List[InjectorBindingOrBindings] = []

    #

    lst.extend([
        inj.bind(build_caching_config),
        inj.bind(DockerBuildCachingImpl, singleton=True),
        inj.bind(DockerBuildCaching, to_key=DockerBuildCachingImpl),
    ])

    #

    if cache_served_docker_cache_config is not None:
        lst.extend([
            inj.bind(DockerImageRepositoryOpenerImpl, singleton=True),
            inj.bind(DockerImageRepositoryOpener, to_key=DockerImageRepositoryOpenerImpl),

            inj.bind(cache_served_docker_cache_config),
            inj.bind(CacheServedDockerCache, singleton=True),
            inj.bind(DockerCache, to_key=CacheServedDockerCache),
        ])

    else:
        lst.extend([
            inj.bind(DockerCacheImpl, singleton=True),
            inj.bind(DockerCache, to_key=DockerCacheImpl),
        ])

    #

    lst.extend([
        inj.bind(image_pulling_config),
        inj.bind(DockerImagePullingImpl, singleton=True),
        inj.bind(DockerImagePulling, to_key=DockerImagePullingImpl),
    ])

    #

    return inj.as_bindings(*lst)


########################################
# ../github/cache.py


##


class GithubCache(FileCache, DataCache):
    @dc.dataclass(frozen=True)
    class Config:
        pass

    DEFAULT_CLIENT_VERSION: ta.ClassVar[int] = 2

    DEFAULT_CLIENTS_BY_VERSION: ta.ClassVar[ta.Mapping[int, ta.Callable[..., GithubCacheClient]]] = {
        1: GithubCacheServiceV1Client,
        2: GithubCacheServiceV2Client,
    }

    def __init__(
            self,
            config: Config = Config(),
            *,
            client: ta.Optional[GithubCacheClient] = None,
            default_client_version: ta.Optional[int] = None,

            version: ta.Optional[CacheVersion] = None,

            local: DirectoryFileCache,
    ) -> None:
        super().__init__(
            version=version,
        )

        self._config = config

        if client is None:
            client_cls = self.DEFAULT_CLIENTS_BY_VERSION[default_client_version or self.DEFAULT_CLIENT_VERSION]
            client = client_cls(
                cache_version=self._version,
            )
        self._client: GithubCacheClient = client

        self._local = local

    #

    async def get_file(self, key: str) -> ta.Optional[str]:
        local_file = self._local.get_cache_file_path(key)
        if os.path.exists(local_file):
            return local_file

        if (entry := await self._client.get_entry(key)) is None:
            return None

        tmp_file = self._local.format_incomplete_file(local_file)
        with unlinking_if_exists(tmp_file):
            await self._client.download_file(entry, tmp_file)

            os.replace(tmp_file, local_file)

        return local_file

    async def put_file(
            self,
            key: str,
            file_path: str,
            *,
            steal: bool = False,
    ) -> str:
        cache_file_path = await self._local.put_file(
            key,
            file_path,
            steal=steal,
        )

        await self._client.upload_file(key, cache_file_path)

        return cache_file_path

    #

    async def get_data(self, key: str) -> ta.Optional[DataCache.Data]:
        local_file = self._local.get_cache_file_path(key)
        if os.path.exists(local_file):
            return DataCache.FileData(local_file)

        if (entry := await self._client.get_entry(key)) is None:
            return None

        return DataCache.UrlData(check.non_empty_str(self._client.get_entry_url(entry)))

    async def put_data(self, key: str, data: DataCache.Data) -> None:
        await FileCacheDataCache(self).put_data(key, data)


########################################
# ../github/cli.py
"""
See:
 - https://docs.github.com/en/rest/actions/cache?apiVersion=2022-11-28
"""


##


class GithubCli(ArgparseCli):
    @argparse_cmd()
    def list_referenced_env_vars(self) -> None:
        print('\n'.join(sorted(ev.k for ev in GITHUB_ENV_VARS)))

    @argparse_cmd(
        argparse_arg('key'),
    )
    async def get_cache_entry(self) -> None:
        client = GithubCacheServiceV1Client()
        entry = await client.get_entry(self.args.key)
        if entry is None:
            return
        print(json_dumps_pretty(dc.asdict(entry)))  # noqa

    @argparse_cmd(
        argparse_arg('repository-id'),
    )
    def list_cache_entries(self) -> None:
        raise NotImplementedError


########################################
# ../github/inject.py


##


def bind_github() -> InjectorBindings:
    lst: ta.List[InjectorBindingOrBindings] = [
        inj.bind(GithubCache, singleton=True),
        inj.bind(DataCache, to_key=GithubCache),
        inj.bind(FileCache, to_key=GithubCache),
    ]

    return inj.as_bindings(*lst)


########################################
# ../inject.py


##


def bind_ci(
        *,
        config: Ci.Config,

        directory_file_cache_config: ta.Optional[DirectoryFileCache.Config] = None,

        github: bool = False,

        cache_served_docker: bool = False,
) -> InjectorBindings:
    lst: ta.List[InjectorBindingOrBindings] = [  # noqa
        inj.bind(config),
        inj.bind(Ci, singleton=True),
    ]

    lst.append(bind_docker(
        build_caching_config=DockerBuildCachingImpl.Config(
            service=config.service,

            always_build=config.always_build,
        ),

        cache_served_docker_cache_config=CacheServedDockerCache.Config(
            #
        ) if cache_served_docker else None,

        image_pulling_config=DockerImagePullingImpl.Config(
            always_pull=config.always_pull,
        ),
    ))

    if directory_file_cache_config is not None:
        lst.extend([
            inj.bind(directory_file_cache_config),
            inj.bind(DirectoryFileCache, singleton=True),
        ])

        if github:
            lst.append(bind_github())

        else:
            lst.extend([
                inj.bind(FileCache, to_key=DirectoryFileCache),

                inj.bind(FileCacheDataCache, singleton=True),
                inj.bind(DataCache, to_key=FileCacheDataCache),
            ])

    return inj.as_bindings(*lst)


########################################
# cli.py


log = get_module_logger(globals())  # noqa


##


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
    async def github(self) -> ta.Optional[int]:
        return await GithubCli(self.unknown_args).async_cli_run()

    #

    DEFAULT_PURGE_MAX_AGE_S = 60 * 60 * 24 * 30
    DEFAULT_PURGE_MAX_SIZE_B = 1024 * 1024 * 1024 * 4

    @argparse_cmd(
        argparse_arg('project-dir'),
        argparse_arg('service'),
        argparse_arg('--docker-file'),
        argparse_arg('--compose-file'),
        argparse_arg('-r', '--requirements-txt', action='append'),

        argparse_arg('--cache-dir'),

        argparse_arg('--no-purge', action='store_true'),

        argparse_arg('--github', action='store_true'),
        argparse_arg('--github-detect', action='store_true'),

        argparse_arg('--cache-served-docker', action='store_true'),

        argparse_arg('--setup-concurrency', type=int),

        argparse_arg('--always-pull', action='store_true'),
        argparse_arg('--always-build', action='store_true'),

        argparse_arg('--no-dependencies', action='store_true'),

        argparse_arg('--setup-only', action='store_true'),

        argparse_arg('-e', '--env', action='append'),
        argparse_arg('-v', '--volume', action='append'),

        argparse_arg('cmd', nargs=argparse.REMAINDER),
    )
    async def run(self) -> None:
        project_dir = self.args.project_dir
        docker_file = self.args.docker_file
        compose_file = self.args.compose_file
        requirements_txts = self.args.requirements_txt
        cache_dir = self.args.cache_dir

        #

        cmd = ' '.join(self.args.cmd)
        check.non_empty_str(cmd)

        #

        check.state(os.path.isdir(project_dir))

        #

        def find_alt_file(*alts: str) -> ta.Optional[str]:
            for alt in alts:
                alt_file = os.path.abspath(os.path.join(project_dir, alt))
                if os.path.isfile(alt_file):
                    log.debug('Using %s', alt_file)
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
                    log.debug('Using %s', rf)
                    requirements_txts.append(rf)
        else:
            for rf in requirements_txts:
                check.state(os.path.isfile(rf))

        #

        github = self.args.github
        if not github and self.args.github_detect:
            github = is_in_github_actions()
            if github:
                log.debug('Github detected')

        #

        if cache_dir is not None:
            cache_dir = os.path.abspath(cache_dir)
            log.debug('Using cache dir %s', cache_dir)

        #

        run_options: ta.List[str] = []
        for run_arg, run_arg_vals in [
            ('-e', self.args.env or []),
            ('-v', self.args.volume or []),
        ]:
            run_options.extend(itertools.chain.from_iterable(
                [run_arg, run_arg_val]
                for run_arg_val in run_arg_vals
            ))

        #

        config = Ci.Config(
            project_dir=project_dir,

            docker_file=docker_file,

            compose_file=compose_file,
            service=self.args.service,

            requirements_txts=requirements_txts,

            cmd=ShellCmd(cmd),

            always_pull=self.args.always_pull,
            always_build=self.args.always_build,

            setup_concurrency=self.args.setup_concurrency,

            no_dependencies=self.args.no_dependencies,

            setup_only=self.args.setup_only,

            run_options=run_options,
        )

        directory_file_cache_config: ta.Optional[DirectoryFileCache.Config] = None
        if cache_dir is not None:
            directory_file_cache_config = DirectoryFileCache.Config(
                dir=cache_dir,

                no_purge=bool(self.args.no_purge),

                purge_max_age_s=self.DEFAULT_PURGE_MAX_AGE_S,
                purge_max_size_b=self.DEFAULT_PURGE_MAX_SIZE_B,
            )

        injector = inj.create_injector(bind_ci(
            config=config,

            directory_file_cache_config=directory_file_cache_config,

            github=github,

            cache_served_docker=self.args.cache_served_docker,
        ))

        async with injector[Ci] as ci:
            await ci.run()

        if directory_file_cache_config is not None and not directory_file_cache_config.no_purge:
            dfc = injector[DirectoryFileCache]
            dfc.purge()


async def _async_main() -> ta.Optional[int]:
    return await CiCli().async_cli_run()


def _main() -> None:
    configure_standard_logging('DEBUG')

    raise SystemExit(rc if isinstance(rc := asyncio.run(_async_main()), int) else 0)


if __name__ == '__main__':
    _main()
