#!/usr/bin/env python3
# noinspection DuplicatedCode
# @omlish-lite
# @omlish-script
# @omlish-generated
# @omlish-amalg-output ../../omlish/os/pidfiles/cli.py
# @omlish-git-diff-omit
# ruff: noqa: PYI034 UP006 UP007 UP036 UP037 UP045
"""
TODO:
 - F_SETLK mode
"""
import abc
import argparse
import base64
import collections
import collections.abc
import contextlib
import dataclasses as dc
import datetime
import decimal
import enum
import errno
import fcntl
import fractions
import functools
import inspect
import json
import logging
import operator
import os
import os.path
import shlex
import shutil
import signal
import subprocess
import sys
import threading
import time
import types
import typing as ta
import uuid
import weakref


########################################


if sys.version_info < (3, 8):
    raise OSError(f'Requires python (3, 8), got {sys.version_info} from {sys.executable}')  # noqa


def __omlish_amalg__():  # noqa
    return dict(
        src_files=[
            dict(path='../../lite/abstract.py', sha1='a2fc3f3697fa8de5247761e9d554e70176f37aac'),
            dict(path='../../lite/cached.py', sha1='0c33cf961ac8f0727284303c7a30c5ea98f714f2'),
            dict(path='../../lite/check.py', sha1='7088e41034dbdce7bdae200793aaa9d6838c79d8'),
            dict(path='../../lite/dataclasses.py', sha1='42ff344c22262193795c54929bfb90d0a3507bab'),
            dict(path='../../lite/objects.py', sha1='9566bbf3530fd71fcc56321485216b592fae21e9'),
            dict(path='../../lite/reflect.py', sha1='c4fec44bf144e9d93293c996af06f6c65fc5e63d'),
            dict(path='../../lite/strings.py', sha1='89831ecbc34ad80e118a865eceb390ed399dc4d6'),
            dict(path='../../lite/typing.py', sha1='9d6caabc7b31534109e3f2e249d21f8610c9c079'),
            dict(path='../../logs/levels.py', sha1='83f6cdd019675b52181422442e7d7541597d0df2'),
            dict(path='pidfile.py', sha1='4fedbf087d874b8f9b612cf0707ac82feb88deaa'),
            dict(path='../signals.py', sha1='0e05e92da535e84b6fef8ca7e3f3c9b3fd313710'),
            dict(path='../../argparse/parsers.py', sha1='f874eb5c45e22156b2e9a762cfb68a2311b6d1f8'),
            dict(path='../../lite/marshal.py', sha1='66bc88d705df274e9fa1168d2aab20c7e3935cf6'),
            dict(path='../../lite/maybes.py', sha1='5ac5f92e5610c6795b0a228c38e7bcd272bf6305'),
            dict(path='../../lite/runtime.py', sha1='2e752a27ae2bf89b1bb79b4a2da522a3ec360c70'),
            dict(path='../../lite/timeouts.py', sha1='2866f276bc45dafdd02a6daf2e8a8b4753e9fb9a'),
            dict(path='../../logs/protocols.py', sha1='05ca4d1d7feb50c4e3b9f22ee371aa7bf4b3dbd1'),
            dict(path='../../argparse/cli.py', sha1='aef500dd2d8f5a65c4c04ede11355ac8eb513f2e'),
            dict(path='../../lite/args.py', sha1='ae96b0baeb376617a63c0e64632ab2c5ff4171a8'),
            dict(path='../../subprocesses/run.py', sha1='1d2a78b18bcc601c8b28269d792cc38bbf25a078'),
            dict(path='../../subprocesses/wrap.py', sha1='8a9b7d2255481fae15c05f5624b0cdc0766f4b3f'),
            dict(path='../../diag/cmds/lslocks.py', sha1='b1e09c9374f9007cb19c2c5009937e7d2f4c0a7b'),
            dict(path='../../diag/cmds/lsof.py', sha1='0a58d3c05ce0038690ce8c5b64dd96e7b21b5853'),
            dict(path='../../subprocesses/base.py', sha1='483de755e9d090d8cae5a774e232e0965ea5713e'),
            dict(path='../../subprocesses/sync.py', sha1='8434919eba4da67825773d56918fdc0cb2f1883b'),
            dict(path='pinning.py', sha1='6f12d3300f89a2265a8df9602c70a11e485e7231'),
            dict(path='cli.py', sha1='5da3992cb0abb547f43f909c2d7c9092bb536f8a'),
        ],
    )


########################################


# ../../lite/abstract.py
T = ta.TypeVar('T')

# ../../lite/cached.py
CallableT = ta.TypeVar('CallableT', bound=ta.Callable)

# ../../lite/check.py
SizedT = ta.TypeVar('SizedT', bound=ta.Sized)
CheckMessage = ta.Union[str, ta.Callable[..., ta.Optional[str]], ta.Type[Exception], None]  # ta.TypeAlias
CheckLateConfigureFn = ta.Callable[['Checks'], None]  # ta.TypeAlias
CheckOnRaiseFn = ta.Callable[[Exception], None]  # ta.TypeAlias
CheckExceptionFactory = ta.Callable[..., Exception]  # ta.TypeAlias
CheckArgsRenderer = ta.Callable[..., ta.Optional[str]]  # ta.TypeAlias

# ../../lite/typing.py
A0 = ta.TypeVar('A0')
A1 = ta.TypeVar('A1')
A2 = ta.TypeVar('A2')

# ../../logs/levels.py
LogLevel = int  # ta.TypeAlias

# ../../argparse/parsers.py
ArgparseCmdFn = ta.Callable[[], ta.Union[ta.Optional[int], ta.Awaitable[ta.Optional[int]]]]  # ta.TypeAlias

# ../../lite/maybes.py
U = ta.TypeVar('U')

# ../../lite/timeouts.py
TimeoutLike = ta.Union['Timeout', ta.Type['Timeout.DEFAULT'], ta.Iterable['TimeoutLike'], 'CanFloat', float, int, bool, None]  # ta.TypeAlias  # noqa

# ../../subprocesses/base.py
SubprocessChannelOption = ta.Literal['pipe', 'stdout', 'devnull']  # ta.TypeAlias


########################################
# ../../../lite/abstract.py


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
# ../../../lite/cached.py


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
# ../../../lite/check.py
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

    @staticmethod
    def default_exception_factory(exc_cls: ta.Type[Exception], *args, **kwargs) -> Exception:
        return exc_cls(*args, **kwargs)  # noqa

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
        self._late_configure()

        exc_args: tuple = ()

        if isinstance(message, type):
            exception_type = message

        else:
            if callable(message):
                message = ta.cast(ta.Callable, message)(*ak.args, **ak.kwargs)
                if isinstance(message, tuple):
                    message, *exc_args = message  # type: ignore

            if message is None:
                message = default_message

            if render_fmt is not None and (af := self._args_renderer) is not None:
                rendered_args = af(render_fmt, *ak.args)
                if rendered_args is not None:
                    message = f'{message} : {rendered_args}'

            exc_args = (message, *exc_args)

        exc = self._exception_factory(
            exception_type,
            *exc_args,
            *ak.args,
            **ak.kwargs,
        )

        for fn in self._on_raise_fns:
            fn(exc)

        raise exc

    #

    def _unpack_isinstance_spec(self, spec: ta.Any) -> ta.Any:
        if spec == ta.Any:
            return object
        if spec is None:
            return None.__class__
        if not isinstance(spec, tuple):
            return spec
        if ta.Any in spec:
            return object
        if None in spec:
            spec = tuple(filter(None, spec)) + (None.__class__,)  # noqa
        return spec

    @ta.overload
    def isinstance(self, v: ta.Any, spec: ta.Type[T], msg: CheckMessage = None, /) -> T:
        ...

    @ta.overload
    def isinstance(self, v: ta.Any, spec: ta.Any, msg: CheckMessage = None, /) -> ta.Any:
        ...

    def isinstance(self, v, spec, msg=None):
        if not isinstance(v, spec if (st := type(spec)) is type or (st is tuple and all(type(x) is type for x in spec)) else self._unpack_isinstance_spec(spec)):  # noqa
            self._raise(
                TypeError,
                'Must be instance',
                msg,
                Checks._ArgsKwargs(v, spec),
                render_fmt='not isinstance(%s, %s)',
            )

        return v

    @ta.overload
    def of_isinstance(self, spec: ta.Type[T], msg: CheckMessage = None, /) -> ta.Callable[[ta.Any], T]:
        ...

    @ta.overload
    def of_isinstance(self, spec: ta.Any, msg: CheckMessage = None, /) -> ta.Callable[[ta.Any], ta.Any]:
        ...

    def of_isinstance(self, spec, msg=None, /):
        spec = spec if (st := type(spec)) is type or (st is tuple and all(type(x) is type for x in spec)) else self._unpack_isinstance_spec(spec)  # noqa

        def inner(v):
            return self.isinstance(v, spec, msg)

        return inner

    def cast(self, v: ta.Any, cls: ta.Type[T], msg: CheckMessage = None, /) -> T:
        if not isinstance(v, cls):
            self._raise(
                TypeError,
                'Must be instance',
                msg,
                Checks._ArgsKwargs(v, cls),
            )

        return v

    def of_cast(self, cls: ta.Type[T], msg: CheckMessage = None, /) -> ta.Callable[[T], T]:
        def inner(v):
            return self.cast(v, cls, msg)

        return inner

    def not_isinstance(self, v: T, spec: ta.Any, msg: CheckMessage = None, /) -> T:  # noqa
        if isinstance(v, spec if (st := type(spec)) is type or (st is tuple and all(type(x) is type for x in spec)) else self._unpack_isinstance_spec(spec)):  # noqa
            self._raise(
                TypeError,
                'Must not be instance',
                msg,
                Checks._ArgsKwargs(v, spec),
                render_fmt='isinstance(%s, %s)',
            )

        return v

    def of_not_isinstance(self, spec: ta.Any, msg: CheckMessage = None, /) -> ta.Callable[[T], T]:
        spec = spec if (st := type(spec)) is type or (st is tuple and all(type(x) is type for x in spec)) else self._unpack_isinstance_spec(spec)  # noqa

        def inner(v):
            return self.not_isinstance(v, spec, msg)

        return inner

    ##

    def issubclass(self, v: ta.Type[T], spec: ta.Any, msg: CheckMessage = None, /) -> ta.Type[T]:  # noqa
        if not issubclass(v, spec):
            self._raise(
                TypeError,
                'Must be subclass',
                msg,
                Checks._ArgsKwargs(v, spec),
                render_fmt='not issubclass(%s, %s)',
            )

        return v

    def not_issubclass(self, v: ta.Type[T], spec: ta.Any, msg: CheckMessage = None, /) -> ta.Type[T]:
        if issubclass(v, spec):
            self._raise(
                TypeError,
                'Must not be subclass',
                msg,
                Checks._ArgsKwargs(v, spec),
                render_fmt='issubclass(%s, %s)',
            )

        return v

    def not_issubclass_except_nameerror(self, v: ta.Type[T], spec: ta.Callable[[], type], msg: CheckMessage = None, /) -> ta.Type[T]:  # noqa
        try:
            c = spec()
        except NameError:
            return v

        if issubclass(v, c):
            self._raise(
                TypeError,
                'Must not be subclass',
                msg,
                Checks._ArgsKwargs(v, c),
                render_fmt='issubclass(%s, %s)',
            )

        return v

    #

    def in_(self, v: T, c: ta.Container[T], msg: CheckMessage = None, /) -> T:
        if v not in c:
            self._raise(
                ValueError,
                'Must be in',
                msg,
                Checks._ArgsKwargs(v, c),
                render_fmt='%s not in %s',
            )

        return v

    def not_in(self, v: T, c: ta.Container[T], msg: CheckMessage = None, /) -> T:
        if v in c:
            self._raise(
                ValueError,
                'Must not be in',
                msg,
                Checks._ArgsKwargs(v, c),
                render_fmt='%s in %s',
            )

        return v

    def empty(self, v: SizedT, msg: CheckMessage = None, /) -> SizedT:
        if len(v) != 0:
            self._raise(
                ValueError,
                'Must be empty',
                msg,
                Checks._ArgsKwargs(v),
                render_fmt='%s',
            )

        return v

    def iterempty(self, v: ta.Iterable[T], msg: CheckMessage = None, /) -> ta.Iterable[T]:
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

    def not_empty(self, v: SizedT, msg: CheckMessage = None, /) -> SizedT:
        if len(v) == 0:
            self._raise(
                ValueError,
                'Must not be empty',
                msg,
                Checks._ArgsKwargs(v),
                render_fmt='%s',
            )

        return v

    def unique(self, it: ta.Iterable[T], msg: CheckMessage = None, /) -> ta.Iterable[T]:
        dupes = [e for e, c in collections.Counter(it).items() if c > 1]
        if dupes:
            self._raise(
                ValueError,
                'Must be unique',
                msg,
                Checks._ArgsKwargs(it, dupes),
            )

        return it

    def single(self, obj: ta.Iterable[T], msg: CheckMessage = None, /) -> T:
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

    def opt_single(self, obj: ta.Iterable[T], msg: CheckMessage = None, /) -> ta.Optional[T]:
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

    async def async_single(self, obj: ta.AsyncIterable[T], msg: CheckMessage = None, /) -> T:
        ait = obj.__aiter__()

        try:
            try:
                value = await ait.__anext__()
            except StopAsyncIteration:
                pass

            else:
                try:
                    await ait.__anext__()
                except StopAsyncIteration:
                    return value

        finally:
            if inspect.isasyncgen(ait):
                await ait.aclose()

        self._raise(
            ValueError,
            'Must be single',
            msg,
            Checks._ArgsKwargs(obj),
            render_fmt='%s',
        )

        raise RuntimeError  # noqa

    async def async_opt_single(self, obj: ta.AsyncIterable[T], msg: CheckMessage = None, /) -> ta.Optional[T]:
        ait = obj.__aiter__()

        try:
            try:
                value = await ait.__anext__()
            except StopAsyncIteration:
                return None

            try:
                await ait.__anext__()
            except StopAsyncIteration:
                return value  # noqa

        finally:
            if inspect.isasyncgen(ait):
                await ait.aclose()

        self._raise(
            ValueError,
            'Must be empty or single',
            msg,
            Checks._ArgsKwargs(obj),
            render_fmt='%s',
        )

        raise RuntimeError  # noqa

    #

    def none(self, v: ta.Any, msg: CheckMessage = None, /) -> None:
        if v is not None:
            self._raise(
                ValueError,
                'Must be None',
                msg,
                render_fmt='%s',
            )

    def not_none(self, v: ta.Optional[T], msg: CheckMessage = None, /) -> T:
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

    def equal(self, v: T, o: ta.Any, msg: CheckMessage = None, /) -> T:
        if o != v:
            self._raise(
                ValueError,
                'Must be equal',
                msg,
                Checks._ArgsKwargs(v, o),
                render_fmt='%s != %s',
            )

        return v

    def not_equal(self, v: T, o: ta.Any, msg: CheckMessage = None, /) -> T:
        if o == v:
            self._raise(
                ValueError,
                'Must not be equal',
                msg,
                Checks._ArgsKwargs(v, o),
                render_fmt='%s == %s',
            )

        return v

    def is_(self, v: T, o: ta.Any, msg: CheckMessage = None, /) -> T:
        if o is not v:
            self._raise(
                ValueError,
                'Must be the same',
                msg,
                Checks._ArgsKwargs(v, o),
                render_fmt='%s is not %s',
            )

        return v

    def is_not(self, v: T, o: ta.Any, msg: CheckMessage = None, /) -> T:
        if o is v:
            self._raise(
                ValueError,
                'Must not be the same',
                msg,
                Checks._ArgsKwargs(v, o),
                render_fmt='%s is %s',
            )

        return v

    def callable(self, v: T, msg: CheckMessage = None, /) -> T:  # noqa
        if not callable(v):
            self._raise(
                TypeError,
                'Must be callable',
                msg,
                Checks._ArgsKwargs(v),
                render_fmt='%s',
            )

        return v

    def non_empty_str(self, v: ta.Optional[str], msg: CheckMessage = None, /) -> str:
        if not isinstance(v, str) or not v:
            self._raise(
                ValueError,
                'Must be non-empty str',
                msg,
                Checks._ArgsKwargs(v),
                render_fmt='%s',
            )

        return v

    def replacing(self, expected: ta.Any, old: ta.Any, new: T, msg: CheckMessage = None, /) -> T:
        if old != expected:
            self._raise(
                ValueError,
                'Must be replacing',
                msg,
                Checks._ArgsKwargs(expected, old, new),
                render_fmt='%s -> %s -> %s',
            )

        return new

    def replacing_none(self, old: ta.Any, new: T, msg: CheckMessage = None, /) -> T:
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

    def arg(self, v: bool, msg: CheckMessage = None, /) -> None:
        if not v:
            self._raise(
                RuntimeError,
                'Argument condition not met',
                msg,
                render_fmt='%s',
            )

    def state(self, v: bool, msg: CheckMessage = None, /) -> None:
        if not v:
            self._raise(
                RuntimeError,
                'State condition not met',
                msg,
                render_fmt='%s',
            )

    def inline(self, v: T, c: bool, msg: CheckMessage = None, /) -> T:
        if not c:
            self._raise(
                RuntimeError,
                'State condition not met',
                msg,
                render_fmt='%s',
            )
        return v


check = Checks()


########################################
# ../../../lite/dataclasses.py


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


def _install_dataclass_fn(cls: type, fn: ta.Any, fn_name: ta.Optional[str] = None) -> None:
    if fn_name is None:
        fn_name = fn.__name__
    setattr(cls, fn_name, fn)
    fn.__qualname__ = f'{cls.__qualname__}.{fn_name}'


##


def install_dataclass_cache_hash(
        *,
        cached_hash_attr: str = '__dataclass_hash__',
):
    def inner(cls):
        if not (isinstance(cls, type) and dc.is_dataclass(cls)):
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
                object.__setattr__(self, cached_hash_attr, h := real_hash(self))
            return h

        _install_dataclass_fn(cls, cached_hash, '__hash__')

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


def dataclass_filtered_repr(
        obj: ta.Any,
        fn: ta.Union[ta.Callable[[ta.Any, dc.Field, ta.Any], bool], ta.Literal['omit_none', 'omit_falsey']],
) -> str:
    if fn == 'omit_none':
        fn = lambda o, f, v: v is not None  # noqa
    elif fn == 'omit_falsey':
        fn = lambda o, f, v: bool(v)

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
    return dataclass_filtered_repr(obj, 'omit_none')


def dataclass_repr_omit_falsey(obj: ta.Any) -> str:
    return dataclass_filtered_repr(obj, 'omit_falsey')


def install_dataclass_filtered_repr(
        fn: ta.Union[ta.Callable[[ta.Any, dc.Field, ta.Any], bool], ta.Literal['omit_none', 'omit_falsey']],
):
    def inner(cls):
        if not (isinstance(cls, type) and dc.is_dataclass(cls)):
            raise TypeError(cls)

        def filtered_repr(self) -> str:
            return dataclass_filtered_repr(self, fn)

        _install_dataclass_fn(cls, filtered_repr, '__repr__')

        return cls

    return inner


#


def dataclass_terse_repr(obj: ta.Any) -> str:
    return f'{obj.__class__.__qualname__}({", ".join(repr(getattr(obj, f.name)) for f in dc.fields(obj))})'


def install_dataclass_terse_repr():
    def inner(cls):
        if not (isinstance(cls, type) and dc.is_dataclass(cls)):
            raise TypeError(cls)

        def terse_repr(self) -> str:
            return dataclass_terse_repr(self)

        _install_dataclass_fn(cls, terse_repr, '__repr__')

        return cls

    return inner


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


def install_dataclass_kw_only_init():
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

        _install_dataclass_fn(cls, kw_only_init, '__init__')

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
# ../../../lite/objects.py


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
# ../../../lite/reflect.py


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
# ../../../lite/strings.py


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
# ../../../lite/typing.py


##
# A workaround for typing deficiencies (like `Argument 2 to NewType(...) must be subclassable`).
#
# Note that this problem doesn't happen at runtime - it happens in mypy:
#
#   mypy <(echo "import typing as ta; MyCallback = ta.NewType('MyCallback', ta.Callable[[], None])")
#   /dev/fd/11:1:22: error: Argument 2 to NewType(...) must be subclassable (got "Callable[[], None]")  [valid-newtype]
#


@dc.dataclass(frozen=True)
class AnyFunc(ta.Generic[T]):
    fn: ta.Callable[..., T]

    def __call__(self, *args: ta.Any, **kwargs: ta.Any) -> T:
        return self.fn(*args, **kwargs)


@dc.dataclass(frozen=True)
class Func0(ta.Generic[T]):
    fn: ta.Callable[[], T]

    def __call__(self) -> T:
        return self.fn()


@dc.dataclass(frozen=True)
class Func1(ta.Generic[A0, T]):
    fn: ta.Callable[[A0], T]

    def __call__(self, a0: A0) -> T:
        return self.fn(a0)


@dc.dataclass(frozen=True)
class Func2(ta.Generic[A0, A1, T]):
    fn: ta.Callable[[A0, A1], T]

    def __call__(self, a0: A0, a1: A1) -> T:
        return self.fn(a0, a1)


@dc.dataclass(frozen=True)
class Func3(ta.Generic[A0, A1, A2, T]):
    fn: ta.Callable[[A0, A1, A2], T]

    def __call__(self, a0: A0, a1: A1, a2: A2) -> T:
        return self.fn(a0, a1, a2)


##


@dc.dataclass(frozen=True)
class CachedFunc0(ta.Generic[T]):
    fn: ta.Callable[[], T]

    def __call__(self) -> T:
        try:
            return object.__getattribute__(self, '_value')
        except AttributeError:
            pass

        value = self.fn()
        object.__setattr__(self, '_value', value)
        return value


@dc.dataclass(frozen=True)
class AsyncCachedFunc0(ta.Generic[T]):
    fn: ta.Callable[[], ta.Awaitable[T]]

    async def __call__(self) -> T:
        try:
            return object.__getattribute__(self, '_value')
        except AttributeError:
            pass

        value = await self.fn()
        object.__setattr__(self, '_value', value)
        return value


##


_TYPING_ANNOTATIONS_ATTR = '__annotate__' if sys.version_info >= (3, 14) else '__annotations__'


def typing_annotations_attr() -> str:
    return _TYPING_ANNOTATIONS_ATTR


##


@ta.runtime_checkable
class CanInt(ta.Protocol):
    def __int__(self) -> int:
        ...


@ta.runtime_checkable
class CanFloat(ta.Protocol):
    def __float__(self) -> float:
        ...


########################################
# ../../../logs/levels.py


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
# ../pidfile.py
"""
TODO:
 - 'json pids', with code version? '.json.pid'? '.jpid'?
  - json*L* pidfiles - first line is bare int, following may be json - now `head -n1 foo.pid` not cat
"""


##


class Pidfile:
    def __init__(
            self,
            path: str,
            *,
            inheritable: bool = True,
            no_create: bool = False,
    ) -> None:
        super().__init__()

        self._path = path
        self._inheritable = inheritable
        self._no_create = no_create

    @property
    def path(self) -> str:
        return self._path

    @property
    def inheritable(self) -> bool:
        return self._inheritable

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({self._path!r})'

    #

    _f: ta.TextIO

    def fileno(self) -> ta.Optional[int]:
        if hasattr(self, '_f'):
            return self._f.fileno()
        else:
            return None

    #

    _fd_to_dup: int

    def dup(self) -> 'Pidfile':
        fd = self._f.fileno()
        dup = Pidfile(
            self._path,
            inheritable=self._inheritable,
        )
        dup._fd_to_dup = fd  # noqa
        return dup

    #

    def __enter__(self) -> 'Pidfile':
        if hasattr(self, '_fd_to_dup'):
            fd = os.dup(self._fd_to_dup)
            del self._fd_to_dup

        else:
            ofl = os.O_RDWR
            if not self._no_create:
                ofl |= os.O_CREAT
            fd = os.open(self._path, ofl, 0o600)

        try:
            if self._inheritable:
                os.set_inheritable(fd, True)

            f = os.fdopen(fd, 'r+')

        except BaseException:
            os.close(fd)
            raise

        self._f = f
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    #

    def __getstate__(self):
        state = self.__dict__.copy()

        if '_f' in state:
            # self._inheritable may be decoupled from actual file inheritability - for example when using the manager.
            if os.get_inheritable(fd := state.pop('_f').fileno()):
                state['__fd'] = fd

        return state

    def __setstate__(self, state):
        if '_f' in state:
            raise RuntimeError

        if '__fd' in state:
            state['_f'] = os.fdopen(state.pop('__fd'), 'r+')

        self.__dict__.update(state)

    #

    def close(self) -> bool:
        if not hasattr(self, '_f'):
            return False

        self._f.close()
        del self._f
        return True

    def try_acquire_lock(self) -> bool:
        try:
            fcntl.flock(self._f, fcntl.LOCK_EX | fcntl.LOCK_NB)
            return True

        except BlockingIOError as e:
            if e.errno == errno.EAGAIN:
                return False
            else:
                raise

    #

    class Error(Exception):
        pass

    class LockedError(Error):
        pass

    def acquire_lock(self) -> None:
        if not self.try_acquire_lock():
            raise self.LockedError

    class NotLockedError(Error):
        pass

    def ensure_cannot_lock(self) -> None:
        if self.try_acquire_lock():
            raise self.NotLockedError

    #

    def write(
            self,
            pid: ta.Optional[int] = None,
            *,
            suffix: ta.Optional[str] = None,
    ) -> None:
        self.acquire_lock()

        if pid is None:
            pid = os.getpid()

        self._f.seek(0)
        self._f.truncate()
        self._f.write('\n'.join([
            str(pid),
            *([suffix] if suffix is not None else []),
            '',
        ]))
        self._f.flush()

    def clear(self) -> None:
        self.acquire_lock()

        self._f.seek(0)
        self._f.truncate()

    #

    def read_raw(self) -> ta.Optional[str]:
        self.ensure_cannot_lock()

        self._f.seek(0)
        buf = self._f.read()
        if not buf:
            return None
        return buf

    def read(self) -> ta.Optional[int]:
        buf = self.read_raw()
        if not buf:
            return None
        return int(buf.splitlines()[0].strip())

    def kill(self, sig: int = signal.SIGTERM) -> None:
        if (pid := self.read()) is None:
            raise self.Error(f'Pidfile locked but empty')
        os.kill(pid, sig)


########################################
# ../../signals.py


##


def parse_signal(s: ta.Union[int, str]) -> int:
    if isinstance(s, int):
        return s

    try:
        return int(s)
    except ValueError:
        pass

    s = s.upper()
    if not s.startswith('SIG'):
        s = 'SIG' + s
    return signal.Signals[s]  # noqa


########################################
# ../../../argparse/parsers.py


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
    default: bool = False

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

    def __call__(self, *args, **kwargs) -> ta.Union[ta.Optional[int], ta.Awaitable[ta.Optional[int]]]:
        return self.fn(*args, **kwargs)


def argparse_cmd(
        *args: ArgparseArg,
        name: ta.Optional[str] = None,
        aliases: ta.Optional[ta.Iterable[str]] = None,
        parent: ta.Optional[ArgparseCmd] = None,
        accepts_unknown: bool = False,
        default: bool = False,
) -> ta.Any:  # ta.Callable[[ArgparseCmdFn], ArgparseCmd]:  # FIXME
    for arg in args:
        check.isinstance(arg, ArgparseArg)
    check.isinstance(name, (str, type(None)))
    check.isinstance(parent, (ArgparseCmd, type(None)))
    check.not_isinstance(aliases, str)
    check.isinstance(default, bool)

    def inner(fn):
        return ArgparseCmd(
            (name if name is not None else fn.__name__).replace('_', '-'),
            fn,
            args,
            aliases=tuple(aliases) if aliases is not None else None,
            parent=parent,
            accepts_unknown=accepts_unknown,
            default=default,
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


class _ArgparseParserClassAnnotationBox:
    def __init__(self, annotations: ta.Mapping[str, ta.Any]) -> None:
        super().__init__()

        self.__annotations__ = annotations  # type: ignore


def configure_argparse_parser_class_parser(
        cls: type,
        parser: ta.Optional[argparse.ArgumentParser] = None,
) -> argparse.ArgumentParser:
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

    anns = ta.get_type_hints(_ArgparseParserClassAnnotationBox({
        **{k: v for bcls in reversed(mro) for k, v in getattr(bcls, '__annotations__', {}).items()},
        **ns.get('__annotations__', {}),
    }), globalns=ns.get('__globals__', {}))

    #

    if parser is None:
        parser = argparse.ArgumentParser()

    #

    subparsers = parser.add_subparsers()

    default_cmd: ta.Optional[ArgparseCmd] = None

    for att, obj in objs.items():
        if isinstance(obj, ArgparseCmd):
            if obj.parent is not None:
                raise NotImplementedError

            if obj.default:
                if default_cmd:
                    raise TypeError(f'Already have a default command: {default_cmd}, {obj}')
                default_cmd = obj

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

    if default_cmd is not None:
        parser.set_defaults(_cmd=default_cmd)

    return parser


##


class ArgparseParserClass(Abstract):
    def __init_subclass__(cls, **kwargs: ta.Any) -> None:
        super().__init_subclass__(**kwargs)

        ns = cls.__dict__

        if '_parser' in ns:
            parser = check.isinstance(ns['_parser'], argparse.ArgumentParser)
        else:
            parser = argparse.ArgumentParser()

        configure_argparse_parser_class_parser(cls, parser)

        setattr(cls, '_parser', parser)

    #

    _parser: ta.ClassVar[argparse.ArgumentParser]

    @classmethod
    def get_parser(cls) -> argparse.ArgumentParser:
        return cls._parser


########################################
# ../../../lite/marshal.py
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
# ../../../lite/maybes.py


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
    def or_none(self) -> ta.Optional[T]:
        if self.present:
            return self.must()
        else:
            return None

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
# ../../../lite/runtime.py


##


@cached_nullary
def is_debugger_attached() -> bool:
    return any(frame[1].endswith('pydevd.py') for frame in inspect.stack())


LITE_REQUIRED_PYTHON_VERSION = (3, 8)


def check_lite_runtime_version() -> None:
    if sys.version_info < LITE_REQUIRED_PYTHON_VERSION:
        raise OSError(f'Requires python {LITE_REQUIRED_PYTHON_VERSION}, got {sys.version_info} from {sys.executable}')  # noqa


########################################
# ../../../lite/timeouts.py
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
        if isinstance(obj, bool):
            if obj:
                obj = Timeout.DEFAULT
            else:
                obj = None

        if obj is None:
            return InfiniteTimeout()

        if isinstance(obj, Timeout):
            return obj

        if isinstance(obj, (float, int)):
            return DeadlineTimeout(cls._now() + obj)

        # if isinstance(obj, CanInt):
        #     return DeadlineTimeout(cls._now() + int(obj))

        if isinstance(obj, CanFloat):
            return DeadlineTimeout(cls._now() + float(obj))

        if isinstance(obj, ta.Iterable):
            return CompositeTimeout(*[Timeout.of(c) for c in obj])

        if obj is Timeout.DEFAULT:
            if default is Timeout._NOT_SPECIFIED or default is Timeout.DEFAULT:
                raise RuntimeError('Must specify a default timeout')

            else:
                return Timeout.of(default)  # type: ignore[arg-type]

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

    def __repr__(self) -> str:
        return f'{type(self).__name__}({self.deadline!r}, {self.exc!r})'

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
    def __repr__(self) -> str:
        return f'{type(self).__name__}()'

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

    def __repr__(self) -> str:
        return f'{type(self).__name__}({self.children!r})'

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

    def __repr__(self) -> str:
        return f'{type(self).__name__}({self.expired_fn!r}, {self.exc!r})'

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
# ../../../logs/protocols.py


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
# ../../../argparse/cli.py
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


class ArgparseCli(ArgparseParserClass, Abstract):
    def __init__(self, argv: ta.Optional[ta.Sequence[str]] = None) -> None:
        super().__init__()

        self._argv = argv if argv is not None else sys.argv[1:]

        self._args, self._unknown_args = self.get_parser().parse_known_args(self._argv)

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

        return check.isinstance(fn(), (int, None))

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
# ../../../lite/args.py


##


@dc.dataclass(init=False)
class Args:
    args: ta.Sequence[ta.Any]
    kwargs: ta.Mapping[str, ta.Any]

    def __init__(self, *args: ta.Any, **kwargs: ta.Any) -> None:
        super().__init__()

        self.args = args
        self.kwargs = kwargs

    def __bool__(self) -> bool:
        return bool(self.args) or bool(self.kwargs)

    def update(self, *args: ta.Any, **kwargs: ta.Any) -> 'Args':
        return Args(
            *self.args,
            *args,
            **{
                **self.kwargs,
                **kwargs,
            },
        )

    def map(self, fn: ta.Callable[[ta.Any], ta.Any]) -> 'Args':
        return Args(
            *[fn(a) for a in self.args],
            **{k: fn(v) for k, v in self.kwargs.items()},
        )

    def map_maybe(self, fn: ta.Callable[[ta.Any], Maybe[ta.Any]]) -> 'Args':
        return Args(
            *[n.must() for a in self.args if (n := fn(a)).present],
            **{k: n.must() for k, v in self.kwargs.items() if (n := fn(v)).present},
        )

    def __call__(self, fn: ta.Callable[..., T]) -> T:
        return fn(*self.args, **self.kwargs)

    @staticmethod
    def call(fn: ta.Callable[..., T], args: ta.Optional['Args']) -> T:
        if args is not None:
            return args(fn)
        else:
            return fn()

    EMPTY: ta.ClassVar['Args']


Args.EMPTY = Args()


########################################
# ../../../subprocesses/run.py


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
# ../../../subprocesses/wrap.py
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
# ../../../diag/cmds/lslocks.py
"""https://github.com/util-linux/util-linux/blob/a4436c7bf07f98a6381c7dfa2ab3f9a415f9c479/misc-utils/lslocks.c"""


##


@dc.dataclass(frozen=True)
class LslocksItem:
    """https://manpages.ubuntu.com/manpages/lunar/man8/lslocks.8.html"""

    command: str
    pid: int
    type: str  # POSIX | FLOCK | OFDLCK
    size: ta.Optional[int]
    mode: str  # READ | WRITE
    mandatory: bool = dc.field(metadata={OBJ_MARSHALER_FIELD_KEY: 'm'})
    start: int
    end: int
    path: str
    blocker: ta.Optional[int] = None


##


@dc.dataclass(frozen=True)
class LslocksCommand(SubprocessRunnable[ta.List[LslocksItem]]):
    pid: ta.Optional[int] = None
    no_inaccessible: bool = False

    def make_run(self) -> SubprocessRun:
        return SubprocessRun.of(
            'lslocks',
            '--json',
            '--bytes',
            '--notruncate',
            *(['--pid', str(self.pid)] if self.pid is not None else []),
            *(['--noinaccessible'] if self.no_inaccessible else []),

            check=True,
            stdout='pipe',
            stderr='devnull',
        )

    def handle_run_output(self, output: SubprocessRunOutput) -> ta.List[LslocksItem]:
        buf = check.not_none(output.stdout).decode().strip()
        if not buf:
            return []
        obj = json.loads(buf)
        return unmarshal_obj(obj['locks'], ta.List[LslocksItem])


########################################
# ../../../diag/cmds/lsof.py
"""https://man7.org/linux/man-pages/man8/lsof.8.html"""


##


# FIXME: ??
# https://unix.stackexchange.com/a/86011
class LsofItemMode(enum.Enum):
    SOLARIS_NFS_LOCK = 'N'
    READ_LOCK_PARTIAL = 'r'
    READ_LOCK_FULL = 'R'
    WRITE_LOCK_PARTIAL = 'w'
    WRITE_LOCK_FULL = 'W'
    READ_WRITE_LOCK = 'u'
    UNKNOWN_LOCK_TYPE = 'U'
    XENIX_LOCK_PARTIAL = 'x'
    XENIX_LOCK_FULL = 'X'


@dc.dataclass(frozen=True)
class _LsofFieldMeta:
    prefix: str
    process: bool = False
    variadic: bool = False

    @classmethod
    def make(cls, *args, **kwargs):
        return {
            cls: cls(*args, **kwargs),
            OBJ_MARSHALER_OMIT_IF_NONE: True,
        }


@dc.dataclass(frozen=True)
class LsofItem:
    __repr__ = dataclass_repr_omit_falsey

    class _PREFIX:
        def __new__(cls, *args, **kwargs):  # noqa
            raise TypeError

    class _PROCESS:
        def __new__(cls, *args, **kwargs):  # noqa
            raise TypeError

    pid: ta.Optional[str] = dc.field(default=None, metadata=_LsofFieldMeta.make('p', process=True))
    pgid: ta.Optional[str] = dc.field(default=None, metadata=_LsofFieldMeta.make('g', process=True))
    ppid: ta.Optional[str] = dc.field(default=None, metadata=_LsofFieldMeta.make('R', process=True))
    cmd: ta.Optional[str] = dc.field(default=None, metadata=_LsofFieldMeta.make('c', process=True))

    uid: ta.Optional[str] = dc.field(default=None, metadata=_LsofFieldMeta.make('u', process=True))
    login_name: ta.Optional[str] = dc.field(default=None, metadata=_LsofFieldMeta.make('L', process=True))

    # FD is the File Descriptor number of the file or:
    #   cwd  current working directory;
    #   Lnn  library references (AIX);
    #   ctty character tty;
    #   DEL  deleted file;
    #   err  FD information error (see NAME column);
    #   fp.  Fileport (Darwin);
    #   jld  jail directory (FreeBSD);
    #   ltx  shared library text (code and data);
    #   Mxx  hex memory-mapped type number xx.
    #   m86  DOS Merge mapped file;
    #   mem  memory-mapped file;
    #   mmap memory-mapped device;
    #   NOFD for a Linux /proc/<PID>/fd directory that can't be opened -- the directory path appears in the NAME column,
    #     followed by an error message;
    #   pd   parent directory;
    #   Rnn  unknown pregion number (HP-UX);
    #   rtd  root directory;
    #   twd  per task current working directory;
    #   txt  program text (code and data);
    #   v86  VP/ix mapped file;
    #
    # FD is followed by one of these characters, describing the mode under which the file is open:
    #   r for read access;
    #   w for write access;
    #   u for read and write access;
    #   space if mode unknown and no lock
    #   character follows;
    #   `-' if mode unknown and lock
    #   character follows.
    #
    # The mode character is followed by one of these lock characters, describing the type of lock applied to the file:
    #   N for a Solaris NFS lock of unknown type;
    #   r for read lock on part of the file;
    #   R for a read lock on the entire file;
    #   w for a write lock on part of the file;
    #   W for a write lock on the entire file;
    #   u for a read and write lock of any length;
    #   U for a lock of unknown type;
    #   x for an SCO OpenServer Xenix lock on part of the file;
    #   X for an SCO OpenServer Xenix lock on the entire file;
    #   space if there is no lock.
    #
    fd: ta.Optional[str] = dc.field(default=None, metadata=_LsofFieldMeta.make('f'))

    inode: ta.Optional[str] = dc.field(default=None, metadata=_LsofFieldMeta.make('i'))
    name: ta.Optional[str] = dc.field(default=None, metadata=_LsofFieldMeta.make('n'))

    # r = read; w = write; u = read/write
    access: ta.Optional[str] = dc.field(default=None, metadata=_LsofFieldMeta.make('a'))

    # r/R = read; w/W = write; u = read/write
    lock: ta.Optional[str] = dc.field(default=None, metadata=_LsofFieldMeta.make('l'))

    file_flags: ta.Optional[str] = dc.field(default=None, metadata=_LsofFieldMeta.make('G'))
    file_type: ta.Optional[str] = dc.field(default=None, metadata=_LsofFieldMeta.make('t'))
    file_size: ta.Optional[str] = dc.field(default=None, metadata=_LsofFieldMeta.make('s'))
    file_offset: ta.Optional[str] = dc.field(default=None, metadata=_LsofFieldMeta.make('o'))  # as 0t<dec> or 0x<hex>

    device_character_code: ta.Optional[str] = dc.field(default=None, metadata=_LsofFieldMeta.make('d'))
    device_number: ta.Optional[str] = dc.field(default=None, metadata=_LsofFieldMeta.make('D'))  # as 0x<hex>
    raw_device_number: ta.Optional[str] = dc.field(default=None, metadata=_LsofFieldMeta.make('r'))  # as 0x<hex>

    share_count: ta.Optional[str] = dc.field(default=None, metadata=_LsofFieldMeta.make('C'))
    link_count: ta.Optional[str] = dc.field(default=None, metadata=_LsofFieldMeta.make('k'))

    stream_info: ta.Optional[str] = dc.field(default=None, metadata=_LsofFieldMeta.make('S'))
    protocol_name: ta.Optional[str] = dc.field(default=None, metadata=_LsofFieldMeta.make('P'))

    tcp_tpi_info: ta.Optional[ta.Sequence[str]] = dc.field(
        default=None,
        metadata=_LsofFieldMeta.make('T', variadic=True),
    )

    # 'K':  'task_id',  # unknown field
    # 'M':  'task_command_name',  # unknown field

    _FIELDS_BY_PREFIX: ta.ClassVar[ta.Mapping[str, dc.Field]]
    _DEFAULT_PREFIXES: ta.ClassVar[str]

    @classmethod
    def from_prefixes(cls, dct: ta.Mapping[str, ta.Any]) -> 'LsofItem':
        kw: ta.Dict[str, ta.Any] = {
            fld.name: val
            for pfx, val in dct.items()
            if (fld := cls._FIELDS_BY_PREFIX.get(pfx)) is not None
        }

        return cls(**kw)

    @classmethod
    def from_prefix_lines(cls, lines: ta.Iterable[str]) -> ta.List['LsofItem']:
        proc_dct: ta.Dict[str, ta.Any] = {}
        file_dct: ta.Dict[str, ta.Any] = {}
        out: ta.List[LsofItem] = []

        def emit() -> None:
            if file_dct:
                out.append(cls.from_prefixes({**proc_dct, **file_dct}))

        for line in lines:
            pfx, val = line[0], line[1:]
            try:
                fld = cls._FIELDS_BY_PREFIX[pfx]
            except KeyError:
                continue
            meta: _LsofFieldMeta = fld.metadata[_LsofFieldMeta]

            if pfx == 'p':
                emit()
                proc_dct = {}
                file_dct = {}
            elif pfx == 'f':
                emit()
                file_dct = {}

            if meta.process:
                dct = proc_dct
            else:
                dct = file_dct

            if meta.variadic:
                dct.setdefault(pfx, []).append(val)
            else:
                if pfx in dct:
                    raise KeyError(pfx)
                dct[pfx] = val

        emit()

        return out


LsofItem._FIELDS_BY_PREFIX = {  # noqa
    meta.prefix: fld
    for fld in dc.fields(LsofItem)  # noqa
    if (meta := fld.metadata.get(_LsofFieldMeta)) is not None  # noqa
}

LsofItem._DEFAULT_PREFIXES = ''.join(LsofItem._FIELDS_BY_PREFIX)  # noqa


##


@dc.dataclass(frozen=True)
class LsofCommand(SubprocessRunnable[ta.List[LsofItem]]):
    pid: ta.Optional[int] = None
    file: ta.Optional[str] = None

    prefixes: ta.Optional[ta.Sequence[str]] = None

    def make_run(self) -> SubprocessRun:
        if (prefixes := self.prefixes) is None:
            prefixes = LsofItem._DEFAULT_PREFIXES  # noqa

        return SubprocessRun.of(
            'lsof',
            '-F', ''.join(prefixes),
            *(['-p', str(self.pid)] if self.pid is not None else []),
            *([self.file] if self.file is not None else []),

            stdout='pipe',
            stderr='devnull',
            check=True,
        )

    def handle_run_output(self, output: SubprocessRunOutput) -> ta.List[LsofItem]:
        lines = [s for l in check.not_none(output.stdout).decode().splitlines() if (s := l.strip())]
        return LsofItem.from_prefix_lines(lines)


##


########################################
# ../../../subprocesses/base.py


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

    PIPE: ta.ClassVar[int] = subprocess.PIPE
    STDOUT: ta.ClassVar[int] = subprocess.STDOUT
    DEVNULL: ta.ClassVar[int] = subprocess.DEVNULL

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
# ../../../subprocesses/sync.py
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
# ../pinning.py
"""
Notes:
 - still racy as to if it's a different actual process as initial check, just with same pid, but due to 'identity' /
   semantic meaning of the named pidfile the processes are considered equivalent

Strategies:
 - linux
  - get pid of owner (lslocks or F_GETLK)
  - open pidfd to owner pid
  - re-check pid of owner
 - darwin
  - get pids of referrers (lsof)
  - read pid from file
  - ensure pid is in referrers
  - optionally loop
  - ? setup pid death watcher? still a race
"""


##


class PidfilePinner(Abstract):
    def __init__(
            self,
            *,
            sleep_s: float = .1,
    ) -> None:
        super().__init__()

        self._sleep_s = sleep_s

    @classmethod
    @abc.abstractmethod
    def is_available(cls) -> bool:
        raise NotImplementedError

    class NoOwnerError(Exception):
        pass

    @abc.abstractmethod
    def _pin_pidfile_owner(self, pidfile: Pidfile, timeout: Timeout) -> ta.ContextManager[int]:
        raise NotImplementedError

    @contextlib.contextmanager
    def pin_pidfile_owner(
            self,
            path: str,
            *,
            timeout: TimeoutLike = None,
            inheritable: bool = False,  # Present to match Pidfile kwargs for convenience, but enforced to be False.
            **kwargs: ta.Any,
    ) -> ta.Iterator[int]:
        check.arg(not inheritable)

        timeout = Timeout.of(timeout)

        if not os.path.isfile(path):
            raise self.NoOwnerError

        with Pidfile(
                path,
                inheritable=False,
                **kwargs,
        ) as pf:
            try:
                with self._pin_pidfile_owner(pf, timeout) as pid:
                    yield pid

            except Pidfile.NotLockedError:
                raise self.NoOwnerError from None

    @classmethod
    def default_impl(cls) -> ta.Type['PidfilePinner']:
        for impl in [
            LslocksPidfdPidfilePinner,
            LsofPidfilePinner,
        ]:
            if impl.is_available():
                return impl
        return UnverifiedPidfilePinner


##


class UnverifiedPidfilePinner(PidfilePinner):
    @classmethod
    def is_available(cls) -> bool:
        return True

    @contextlib.contextmanager
    def _pin_pidfile_owner(self, pidfile: Pidfile, timeout: Timeout) -> ta.Iterator[int]:
        while (pid := pidfile.read()) is None:
            time.sleep(self._sleep_s)
            timeout()

        yield pid


##


class LsofPidfilePinner(PidfilePinner):
    """
    Fundamentally wrong, but still better than nothing. Simply reads the file contents and ensures a valid contained pid
    has the file open via `lsof`.
    """

    @classmethod
    def is_available(cls) -> bool:
        return shutil.which('lsof') is not None

    def _try_read_and_verify(self, pf: Pidfile, timeout: Timeout) -> ta.Optional[int]:
        if (initial_pid := pf.read()) is None:
            return None

        lsof_output = LsofCommand(
            # pid=initial_pid,
            file=os.path.abspath(pf.path),
        ).run(
            timeout=timeout,
        )

        lsof_pids: ta.Set[int] = set()
        for li in lsof_output:
            if li.pid is None:
                continue
            try:
                li_pid = int(li.pid)
            except ValueError:
                continue
            lsof_pids.add(li_pid)

        if initial_pid not in lsof_pids:
            return None

        if (reread_pid := pf.read()) is None or reread_pid != initial_pid:
            return None

        return reread_pid

    @contextlib.contextmanager
    def _pin_pidfile_owner(self, pidfile: Pidfile, timeout: Timeout) -> ta.Iterator[int]:
        while (pid := self._try_read_and_verify(pidfile, timeout)) is None:
            time.sleep(self._sleep_s)
            timeout()

        yield pid


##


class LslocksPidfdPidfilePinner(PidfilePinner):
    """
    Finds the locking pid via `lslocks`, opens a pidfd, then re-runs `lslocks` and rechecks the locking pid is the same.
    """

    @classmethod
    def is_available(cls) -> bool:
        return sys.platform == 'linux' and shutil.which('lslocks') is not None

    def _read_locking_pid(self, path: str, timeout: Timeout) -> int:
        lsl_output = LslocksCommand().run(timeout=timeout)

        lsl_pids = {
            li.pid
            for li in lsl_output
            if li.path == path
            and li.type == 'FLOCK'
        }
        if not lsl_pids:
            raise self.NoOwnerError
        if len(lsl_pids) != 1:
            raise RuntimeError(f'Multiple locks on file: {path}')

        [pid] = lsl_pids
        return pid

    class _Result(ta.NamedTuple):
        pid: int
        pidfd: int

    def _try_read_and_verify(
            self,
            pidfile: Pidfile,
            timeout: Timeout,
    ) -> ta.Optional[_Result]:
        path = os.path.abspath(pidfile.path)
        initial_pid = self._read_locking_pid(path, timeout)

        try:
            pidfd = os.open(f'/proc/{initial_pid}', os.O_RDONLY)
        except FileNotFoundError:
            raise self.NoOwnerError from None

        try:
            reread_pid = self._read_locking_pid(path, timeout)
            if reread_pid != initial_pid:
                os.close(pidfd)
                return None

            return self._Result(initial_pid, pidfd)

        except BaseException:
            os.close(pidfd)
            raise

    @contextlib.contextmanager
    def _pin_pidfile_owner(
            self,
            pidfile: Pidfile,
            timeout: Timeout,
    ) -> ta.Iterator[int]:
        while (res := self._try_read_and_verify(pidfile, timeout)) is None:
            time.sleep(self._sleep_s)
            timeout()

        try:
            yield res.pid
        finally:
            os.close(res.pidfd)


##


########################################
# cli.py


##


class Cli(ArgparseCli):
    _PIDFILE_ARGS: ta.ClassVar[ta.Sequence[ArgparseArg]] = [
        argparse_arg('pid-file'),
        argparse_arg('--create', action='store_true'),
    ]

    def _pidfile_args(self) -> Args:
        return Args(
            self.args.pid_file,
            inheritable=False,
            no_create=not self._args.create,
        )

    def _args_pidfile(self) -> Pidfile:
        return self._pidfile_args()(Pidfile)

    #

    @argparse_cmd(*_PIDFILE_ARGS)
    def read_no_verify(self) -> None:
        with self._args_pidfile() as pidfile:
            print(pidfile.read())

    @argparse_cmd(*_PIDFILE_ARGS)
    def lock(self) -> None:
        with self._args_pidfile() as pidfile:
            pidfile.acquire_lock()
            print(os.getpid())
            input()

    #

    _PIDFILE_PINNER_ARGS: ta.ClassVar[ta.Sequence[ArgparseArg]] = [
        *_PIDFILE_ARGS,
        argparse_arg('--timeout', type=float),
    ]

    def _pidfile_pinner_args(self) -> Args:
        return self._pidfile_args().update(
            timeout=self._args.timeout,
        )

    def _args_pidfile_pinner(self) -> ta.ContextManager[int]:
        return self._pidfile_pinner_args()(PidfilePinner.default_impl()().pin_pidfile_owner)

    #

    @argparse_cmd(*_PIDFILE_PINNER_ARGS)
    def read(self) -> None:
        with self._args_pidfile_pinner() as pid:
            print(pid)

    @argparse_cmd(*_PIDFILE_PINNER_ARGS)
    def pin(self) -> None:
        with self._args_pidfile_pinner() as pid:
            print(pid)
            input()

    @argparse_cmd(
        *_PIDFILE_PINNER_ARGS,
        argparse_arg('signal'),
    )
    def kill(self) -> None:
        sig = parse_signal(self._args.signal)
        with self._args_pidfile_pinner() as pid:
            os.kill(pid, sig)


def _main() -> None:
    Cli().cli_run_and_exit()


if __name__ == '__main__':
    _main()
