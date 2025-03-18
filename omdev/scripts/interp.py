#!/usr/bin/env python3
# noinspection DuplicatedCode
# @omlish-lite
# @omlish-script
# @omlish-amalg-output ../interp/cli.py
# @omlish-git-diff-omit
# ruff: noqa: N802 UP006 UP007 UP036
"""
TODO:
 - partial best-matches - '3.12'
 - https://github.com/asdf-vm/asdf support (instead of pyenv) ?
 - colon sep provider name prefix - pyenv:3.12
"""
import abc
import argparse
import asyncio
import asyncio.base_subprocess
import asyncio.subprocess
import collections
import contextlib
import contextvars
import dataclasses as dc
import datetime
import functools
import inspect
import itertools
import json
import logging
import os
import os.path
import re
import shlex
import shutil
import subprocess
import sys
import threading
import time
import types
import typing as ta
import weakref


########################################


if sys.version_info < (3, 8):
    raise OSError(f'Requires python (3, 8), got {sys.version_info} from {sys.executable}')  # noqa


########################################


# ../packaging/versions.py
VersionLocalType = ta.Tuple[ta.Union[int, str], ...]
VersionCmpPrePostDevType = ta.Union['InfinityVersionType', 'NegativeInfinityVersionType', ta.Tuple[str, int]]
_VersionCmpLocalType0 = ta.Tuple[ta.Union[ta.Tuple[int, str], ta.Tuple['NegativeInfinityVersionType', ta.Union[int, str]]], ...]  # noqa
VersionCmpLocalType = ta.Union['NegativeInfinityVersionType', _VersionCmpLocalType0]
VersionCmpKey = ta.Tuple[int, ta.Tuple[int, ...], VersionCmpPrePostDevType, VersionCmpPrePostDevType, VersionCmpPrePostDevType, VersionCmpLocalType]  # noqa
VersionComparisonMethod = ta.Callable[[VersionCmpKey, VersionCmpKey], bool]

# ../../omlish/lite/cached.py
T = ta.TypeVar('T')
CallableT = ta.TypeVar('CallableT', bound=ta.Callable)

# ../../omlish/lite/check.py
SizedT = ta.TypeVar('SizedT', bound=ta.Sized)
CheckMessage = ta.Union[str, ta.Callable[..., ta.Optional[str]], None]  # ta.TypeAlias
CheckLateConfigureFn = ta.Callable[['Checks'], None]  # ta.TypeAlias
CheckOnRaiseFn = ta.Callable[[Exception], None]  # ta.TypeAlias
CheckExceptionFactory = ta.Callable[..., Exception]  # ta.TypeAlias
CheckArgsRenderer = ta.Callable[..., ta.Optional[str]]  # ta.TypeAlias

# ../../omlish/lite/timeouts.py
TimeoutLike = ta.Union['Timeout', ta.Type['Timeout.Default'], ta.Iterable['TimeoutLike'], float]  # ta.TypeAlias

# ../packaging/specifiers.py
UnparsedVersion = ta.Union['Version', str]
UnparsedVersionVar = ta.TypeVar('UnparsedVersionVar', bound=UnparsedVersion)
CallableVersionOperator = ta.Callable[['Version', str], bool]

# ../../omlish/argparse/cli.py
ArgparseCmdFn = ta.Callable[[], ta.Optional[int]]  # ta.TypeAlias

# ../../omlish/asyncs/asyncio/timeouts.py
AwaitableT = ta.TypeVar('AwaitableT', bound=ta.Awaitable)

# ../../omlish/lite/inject.py
U = ta.TypeVar('U')
InjectorKeyCls = ta.Union[type, ta.NewType]
InjectorProviderFn = ta.Callable[['Injector'], ta.Any]
InjectorProviderFnMap = ta.Mapping['InjectorKey', 'InjectorProviderFn']
InjectorBindingOrBindings = ta.Union['InjectorBinding', 'InjectorBindings']

# ../../omlish/subprocesses/base.py
SubprocessChannelOption = ta.Literal['pipe', 'stdout', 'devnull']  # ta.TypeAlias


########################################
# ../../packaging/versions.py
# Copyright (c) Donald Stufft and individual contributors.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the
# following conditions are met:
#
#     1. Redistributions of source code must retain the above copyright notice, this list of conditions and the
#        following disclaimer.
#
#     2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the
#        following disclaimer in the documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES,
# INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
# WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE. This file is dual licensed under the terms of the
# Apache License, Version 2.0, and the BSD License. See the LICENSE file in the root of this repository for complete
# details.
# https://github.com/pypa/packaging/blob/2c885fe91a54559e2382902dce28428ad2887be5/src/packaging/version.py


##


class InfinityVersionType:
    def __repr__(self) -> str:
        return 'Infinity'

    def __hash__(self) -> int:
        return hash(repr(self))

    def __lt__(self, other: object) -> bool:
        return False

    def __le__(self, other: object) -> bool:
        return False

    def __eq__(self, other: object) -> bool:
        return isinstance(other, self.__class__)

    def __gt__(self, other: object) -> bool:
        return True

    def __ge__(self, other: object) -> bool:
        return True

    def __neg__(self: object) -> 'NegativeInfinityVersionType':
        return NegativeInfinityVersion


InfinityVersion = InfinityVersionType()


class NegativeInfinityVersionType:
    def __repr__(self) -> str:
        return '-Infinity'

    def __hash__(self) -> int:
        return hash(repr(self))

    def __lt__(self, other: object) -> bool:
        return True

    def __le__(self, other: object) -> bool:
        return True

    def __eq__(self, other: object) -> bool:
        return isinstance(other, self.__class__)

    def __gt__(self, other: object) -> bool:
        return False

    def __ge__(self, other: object) -> bool:
        return False

    def __neg__(self: object) -> InfinityVersionType:
        return InfinityVersion


NegativeInfinityVersion = NegativeInfinityVersionType()


##


class _Version(ta.NamedTuple):
    epoch: int
    release: ta.Tuple[int, ...]
    dev: ta.Optional[ta.Tuple[str, int]]
    pre: ta.Optional[ta.Tuple[str, int]]
    post: ta.Optional[ta.Tuple[str, int]]
    local: ta.Optional[VersionLocalType]


class InvalidVersion(ValueError):  # noqa
    pass


class _BaseVersion:
    _key: ta.Tuple[ta.Any, ...]

    def __hash__(self) -> int:
        return hash(self._key)

    def __lt__(self, other: '_BaseVersion') -> bool:
        if not isinstance(other, _BaseVersion):
            return NotImplemented  # type: ignore
        return self._key < other._key

    def __le__(self, other: '_BaseVersion') -> bool:
        if not isinstance(other, _BaseVersion):
            return NotImplemented  # type: ignore
        return self._key <= other._key

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, _BaseVersion):
            return NotImplemented
        return self._key == other._key

    def __ge__(self, other: '_BaseVersion') -> bool:
        if not isinstance(other, _BaseVersion):
            return NotImplemented  # type: ignore
        return self._key >= other._key

    def __gt__(self, other: '_BaseVersion') -> bool:
        if not isinstance(other, _BaseVersion):
            return NotImplemented  # type: ignore
        return self._key > other._key

    def __ne__(self, other: object) -> bool:
        if not isinstance(other, _BaseVersion):
            return NotImplemented
        return self._key != other._key


_VERSION_PATTERN = r"""
    v?
    (?:
        (?:(?P<epoch>[0-9]+)!)?
        (?P<release>[0-9]+(?:\.[0-9]+)*)
        (?P<pre>
            [-_\.]?
            (?P<pre_l>alpha|a|beta|b|preview|pre|c|rc)
            [-_\.]?
            (?P<pre_n>[0-9]+)?
        )?
        (?P<post>
            (?:-(?P<post_n1>[0-9]+))
            |
            (?:
                [-_\.]?
                (?P<post_l>post|rev|r)
                [-_\.]?
                (?P<post_n2>[0-9]+)?
            )
        )?
        (?P<dev>
            [-_\.]?
            (?P<dev_l>dev)
            [-_\.]?
            (?P<dev_n>[0-9]+)?
        )?
    )
    (?:\+(?P<local>[a-z0-9]+(?:[-_\.][a-z0-9]+)*))?
"""

VERSION_PATTERN = _VERSION_PATTERN


class Version(_BaseVersion):
    _regex = re.compile(r'^\s*' + VERSION_PATTERN + r'\s*$', re.VERBOSE | re.IGNORECASE)
    _key: VersionCmpKey

    def __init__(self, version: str) -> None:
        match = self._regex.search(version)
        if not match:
            raise InvalidVersion(f"Invalid version: '{version}'")

        self._version = _Version(
            epoch=int(match.group('epoch')) if match.group('epoch') else 0,
            release=tuple(int(i) for i in match.group('release').split('.')),
            pre=_parse_letter_version(match.group('pre_l'), match.group('pre_n')),
            post=_parse_letter_version(match.group('post_l'), match.group('post_n1') or match.group('post_n2')),
            dev=_parse_letter_version(match.group('dev_l'), match.group('dev_n')),
            local=_parse_local_version(match.group('local')),
        )

        self._key = _version_cmpkey(
            self._version.epoch,
            self._version.release,
            self._version.pre,
            self._version.post,
            self._version.dev,
            self._version.local,
        )

    def __repr__(self) -> str:
        return f"<Version('{self}')>"

    def __str__(self) -> str:
        parts = []

        if self.epoch != 0:
            parts.append(f'{self.epoch}!')

        parts.append('.'.join(str(x) for x in self.release))

        if self.pre is not None:
            parts.append(''.join(str(x) for x in self.pre))

        if self.post is not None:
            parts.append(f'.post{self.post}')

        if self.dev is not None:
            parts.append(f'.dev{self.dev}')

        if self.local is not None:
            parts.append(f'+{self.local}')

        return ''.join(parts)

    @property
    def epoch(self) -> int:
        return self._version.epoch

    @property
    def release(self) -> ta.Tuple[int, ...]:
        return self._version.release

    @property
    def pre(self) -> ta.Optional[ta.Tuple[str, int]]:
        return self._version.pre

    @property
    def post(self) -> ta.Optional[int]:
        return self._version.post[1] if self._version.post else None

    @property
    def dev(self) -> ta.Optional[int]:
        return self._version.dev[1] if self._version.dev else None

    @property
    def local(self) -> ta.Optional[str]:
        if self._version.local:
            return '.'.join(str(x) for x in self._version.local)
        else:
            return None

    @property
    def public(self) -> str:
        return str(self).split('+', 1)[0]

    @property
    def base_version(self) -> str:
        parts = []

        if self.epoch != 0:
            parts.append(f'{self.epoch}!')

        parts.append('.'.join(str(x) for x in self.release))

        return ''.join(parts)

    @property
    def is_prerelease(self) -> bool:
        return self.dev is not None or self.pre is not None

    @property
    def is_postrelease(self) -> bool:
        return self.post is not None

    @property
    def is_devrelease(self) -> bool:
        return self.dev is not None

    @property
    def major(self) -> int:
        return self.release[0] if len(self.release) >= 1 else 0

    @property
    def minor(self) -> int:
        return self.release[1] if len(self.release) >= 2 else 0

    @property
    def micro(self) -> int:
        return self.release[2] if len(self.release) >= 3 else 0


def _parse_letter_version(
        letter: ta.Optional[str],
        number: ta.Union[str, bytes, ta.SupportsInt, None],
) -> ta.Optional[ta.Tuple[str, int]]:
    if letter:
        if number is None:
            number = 0

        letter = letter.lower()
        if letter == 'alpha':
            letter = 'a'
        elif letter == 'beta':
            letter = 'b'
        elif letter in ['c', 'pre', 'preview']:
            letter = 'rc'
        elif letter in ['rev', 'r']:
            letter = 'post'

        return letter, int(number)
    if not letter and number:
        letter = 'post'
        return letter, int(number)

    return None


_local_version_separators = re.compile(r'[\._-]')


def _parse_local_version(local: ta.Optional[str]) -> ta.Optional[VersionLocalType]:
    if local is not None:
        return tuple(
            part.lower() if not part.isdigit() else int(part)
            for part in _local_version_separators.split(local)
        )
    return None


def _version_cmpkey(
    epoch: int,
    release: ta.Tuple[int, ...],
    pre: ta.Optional[ta.Tuple[str, int]],
    post: ta.Optional[ta.Tuple[str, int]],
    dev: ta.Optional[ta.Tuple[str, int]],
    local: ta.Optional[VersionLocalType],
) -> VersionCmpKey:
    _release = tuple(reversed(list(itertools.dropwhile(lambda x: x == 0, reversed(release)))))

    if pre is None and post is None and dev is not None:
        _pre: VersionCmpPrePostDevType = NegativeInfinityVersion
    elif pre is None:
        _pre = InfinityVersion
    else:
        _pre = pre

    if post is None:
        _post: VersionCmpPrePostDevType = NegativeInfinityVersion
    else:
        _post = post

    if dev is None:
        _dev: VersionCmpPrePostDevType = InfinityVersion
    else:
        _dev = dev

    if local is None:
        _local: VersionCmpLocalType = NegativeInfinityVersion
    else:
        _local = tuple((i, '') if isinstance(i, int) else (NegativeInfinityVersion, i) for i in local)

    return epoch, _release, _pre, _post, _dev, _local


##


def canonicalize_version(
        version: ta.Union[Version, str],
        *,
        strip_trailing_zero: bool = True,
) -> str:
    if isinstance(version, str):
        try:
            parsed = Version(version)
        except InvalidVersion:
            return version
    else:
        parsed = version

    parts = []

    if parsed.epoch != 0:
        parts.append(f'{parsed.epoch}!')

    release_segment = '.'.join(str(x) for x in parsed.release)
    if strip_trailing_zero:
        release_segment = re.sub(r'(\.0)+$', '', release_segment)
    parts.append(release_segment)

    if parsed.pre is not None:
        parts.append(''.join(str(x) for x in parsed.pre))

    if parsed.post is not None:
        parts.append(f'.post{parsed.post}')

    if parsed.dev is not None:
        parts.append(f'.dev{parsed.dev}')

    if parsed.local is not None:
        parts.append(f'+{parsed.local}')

    return ''.join(parts)


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
# ../../../omlish/lite/maybes.py


class Maybe(ta.Generic[T]):
    @property
    @abc.abstractmethod
    def present(self) -> bool:
        raise NotImplementedError

    @abc.abstractmethod
    def must(self) -> T:
        raise NotImplementedError

    @classmethod
    def just(cls, v: T) -> 'Maybe[T]':
        return tuple.__new__(_Maybe, (v,))  # noqa

    _empty: ta.ClassVar['Maybe']

    @classmethod
    def empty(cls) -> 'Maybe[T]':
        return Maybe._empty


class _Maybe(Maybe[T], tuple):
    __slots__ = ()

    def __init_subclass__(cls, **kwargs):
        raise TypeError

    @property
    def present(self) -> bool:
        return bool(self)

    def must(self) -> T:
        if not self:
            raise ValueError
        return self[0]


Maybe._empty = tuple.__new__(_Maybe, ())  # noqa


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
# ../../../omlish/lite/timeouts.py
"""
TODO:
 - Event (/ Predicate)
"""


##


class Timeout(abc.ABC):
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

    class Default:
        def __new__(cls, *args, **kwargs):  # noqa
            raise TypeError

    class _NOT_SPECIFIED:  # noqa
        def __new__(cls, *args, **kwargs):  # noqa
            raise TypeError

    @classmethod
    def of(
            cls,
            obj: ta.Optional[TimeoutLike],
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

        elif obj is Timeout.Default:
            if default is Timeout._NOT_SPECIFIED or default is Timeout.Default:
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
# ../../packaging/specifiers.py
# Copyright (c) Donald Stufft and individual contributors.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the
# following conditions are met:
#
#     1. Redistributions of source code must retain the above copyright notice, this list of conditions and the
#        following disclaimer.
#
#     2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the
#        following disclaimer in the documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES,
# INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
# WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE. This file is dual licensed under the terms of the
# Apache License, Version 2.0, and the BSD License. See the LICENSE file in the root of this repository for complete
# details.
# https://github.com/pypa/packaging/blob/2c885fe91a54559e2382902dce28428ad2887be5/src/packaging/specifiers.py


##


def _coerce_version(version: UnparsedVersion) -> Version:
    if not isinstance(version, Version):
        version = Version(version)
    return version


class InvalidSpecifier(ValueError):  # noqa
    pass


class BaseSpecifier(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def __str__(self) -> str:
        raise NotImplementedError

    @abc.abstractmethod
    def __hash__(self) -> int:
        raise NotImplementedError

    @abc.abstractmethod
    def __eq__(self, other: object) -> bool:
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def prereleases(self) -> ta.Optional[bool]:
        raise NotImplementedError

    @prereleases.setter
    def prereleases(self, value: bool) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def contains(self, item: str, prereleases: ta.Optional[bool] = None) -> bool:
        raise NotImplementedError

    @abc.abstractmethod
    def filter(
            self,
            iterable: ta.Iterable[UnparsedVersionVar],
            prereleases: ta.Optional[bool] = None,
    ) -> ta.Iterator[UnparsedVersionVar]:
        raise NotImplementedError


class Specifier(BaseSpecifier):
    _operator_regex_str = r"""
        (?P<operator>(~=|==|!=|<=|>=|<|>|===))
        """

    _version_regex_str = r"""
        (?P<version>
            (?:
                (?<====)
                \s*
                [^\s;)]*
            )
            |
            (?:
                (?<===|!=)
                \s*
                v?
                (?:[0-9]+!)?
                [0-9]+(?:\.[0-9]+)*
                (?:
                    \.\*
                    |
                    (?:
                        [-_\.]?
                        (alpha|beta|preview|pre|a|b|c|rc)
                        [-_\.]?
                        [0-9]*
                    )?
                    (?:
                        (?:-[0-9]+)|(?:[-_\.]?(post|rev|r)[-_\.]?[0-9]*)
                    )?
                    (?:[-_\.]?dev[-_\.]?[0-9]*)?
                    (?:\+[a-z0-9]+(?:[-_\.][a-z0-9]+)*)?
                )?
            )
            |
            (?:
                (?<=~=)
                \s*
                v?
                (?:[0-9]+!)?
                [0-9]+(?:\.[0-9]+)+
                (?:
                    [-_\.]?
                    (alpha|beta|preview|pre|a|b|c|rc)
                    [-_\.]?
                    [0-9]*
                )?
                (?:
                    (?:-[0-9]+)|(?:[-_\.]?(post|rev|r)[-_\.]?[0-9]*)
                )?
                (?:[-_\.]?dev[-_\.]?[0-9]*)?
            )
            |
            (?:
                (?<!==|!=|~=)
                \s*
                v?
                (?:[0-9]+!)?
                [0-9]+(?:\.[0-9]+)*
                (?:
                    [-_\.]?
                    (alpha|beta|preview|pre|a|b|c|rc)
                    [-_\.]?
                    [0-9]*
                )?
                (?:
                    (?:-[0-9]+)|(?:[-_\.]?(post|rev|r)[-_\.]?[0-9]*)
                )?
                (?:[-_\.]?dev[-_\.]?[0-9]*)?
            )
        )
        """

    _regex = re.compile(
        r'^\s*' + _operator_regex_str + _version_regex_str + r'\s*$',
        re.VERBOSE | re.IGNORECASE,
    )

    OPERATORS: ta.ClassVar[ta.Mapping[str, str]] = {
        '~=': 'compatible',
        '==': 'equal',
        '!=': 'not_equal',
        '<=': 'less_than_equal',
        '>=': 'greater_than_equal',
        '<': 'less_than',
        '>': 'greater_than',
        '===': 'arbitrary',
    }

    def __init__(
            self,
            spec: str = '',
            prereleases: ta.Optional[bool] = None,
    ) -> None:
        match = self._regex.search(spec)
        if not match:
            raise InvalidSpecifier(f"Invalid specifier: '{spec}'")

        self._spec: ta.Tuple[str, str] = (
            match.group('operator').strip(),
            match.group('version').strip(),
        )

        self._prereleases = prereleases

    @property  # type: ignore
    def prereleases(self) -> bool:
        if self._prereleases is not None:
            return self._prereleases

        operator, version = self._spec
        if operator in ['==', '>=', '<=', '~=', '===']:
            if operator == '==' and version.endswith('.*'):
                version = version[:-2]

            if Version(version).is_prerelease:
                return True

        return False

    @prereleases.setter
    def prereleases(self, value: bool) -> None:
        self._prereleases = value

    @property
    def operator(self) -> str:
        return self._spec[0]

    @property
    def version(self) -> str:
        return self._spec[1]

    def __repr__(self) -> str:
        pre = (
            f', prereleases={self.prereleases!r}'
            if self._prereleases is not None
            else ''
        )

        return f'<{self.__class__.__name__}({str(self)!r}{pre})>'

    def __str__(self) -> str:
        return '{}{}'.format(*self._spec)

    @property
    def _canonical_spec(self) -> ta.Tuple[str, str]:
        canonical_version = canonicalize_version(
            self._spec[1],
            strip_trailing_zero=(self._spec[0] != '~='),
        )
        return self._spec[0], canonical_version

    def __hash__(self) -> int:
        return hash(self._canonical_spec)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, str):
            try:
                other = self.__class__(str(other))
            except InvalidSpecifier:
                return NotImplemented
        elif not isinstance(other, self.__class__):
            return NotImplemented

        return self._canonical_spec == other._canonical_spec

    def _get_operator(self, op: str) -> CallableVersionOperator:
        operator_callable: CallableVersionOperator = getattr(self, f'_compare_{self.OPERATORS[op]}')
        return operator_callable

    def _compare_compatible(self, prospective: Version, spec: str) -> bool:
        prefix = _version_join(list(itertools.takewhile(_is_not_version_suffix, _version_split(spec)))[:-1])
        prefix += '.*'
        return self._get_operator('>=')(prospective, spec) and self._get_operator('==')(prospective, prefix)

    def _compare_equal(self, prospective: Version, spec: str) -> bool:
        if spec.endswith('.*'):
            normalized_prospective = canonicalize_version(prospective.public, strip_trailing_zero=False)
            normalized_spec = canonicalize_version(spec[:-2], strip_trailing_zero=False)
            split_spec = _version_split(normalized_spec)

            split_prospective = _version_split(normalized_prospective)
            padded_prospective, _ = _pad_version(split_prospective, split_spec)
            shortened_prospective = padded_prospective[: len(split_spec)]

            return shortened_prospective == split_spec

        else:
            spec_version = Version(spec)
            if not spec_version.local:
                prospective = Version(prospective.public)
            return prospective == spec_version

    def _compare_not_equal(self, prospective: Version, spec: str) -> bool:
        return not self._compare_equal(prospective, spec)

    def _compare_less_than_equal(self, prospective: Version, spec: str) -> bool:
        return Version(prospective.public) <= Version(spec)

    def _compare_greater_than_equal(self, prospective: Version, spec: str) -> bool:
        return Version(prospective.public) >= Version(spec)

    def _compare_less_than(self, prospective: Version, spec_str: str) -> bool:
        spec = Version(spec_str)

        if not prospective < spec:
            return False

        if not spec.is_prerelease and prospective.is_prerelease:
            if Version(prospective.base_version) == Version(spec.base_version):
                return False

        return True

    def _compare_greater_than(self, prospective: Version, spec_str: str) -> bool:
        spec = Version(spec_str)

        if not prospective > spec:
            return False

        if not spec.is_postrelease and prospective.is_postrelease:
            if Version(prospective.base_version) == Version(spec.base_version):
                return False

        if prospective.local is not None:
            if Version(prospective.base_version) == Version(spec.base_version):
                return False

        return True

    def _compare_arbitrary(self, prospective: Version, spec: str) -> bool:
        return str(prospective).lower() == str(spec).lower()

    def __contains__(self, item: ta.Union[str, Version]) -> bool:
        return self.contains(item)

    def contains(self, item: UnparsedVersion, prereleases: ta.Optional[bool] = None) -> bool:
        if prereleases is None:
            prereleases = self.prereleases

        normalized_item = _coerce_version(item)

        if normalized_item.is_prerelease and not prereleases:
            return False

        operator_callable: CallableVersionOperator = self._get_operator(self.operator)
        return operator_callable(normalized_item, self.version)

    def filter(
            self,
            iterable: ta.Iterable[UnparsedVersionVar],
            prereleases: ta.Optional[bool] = None,
    ) -> ta.Iterator[UnparsedVersionVar]:
        yielded = False
        found_prereleases = []

        kw = {'prereleases': prereleases if prereleases is not None else True}

        for version in iterable:
            parsed_version = _coerce_version(version)

            if self.contains(parsed_version, **kw):
                if parsed_version.is_prerelease and not (prereleases or self.prereleases):
                    found_prereleases.append(version)
                else:
                    yielded = True
                    yield version

        if not yielded and found_prereleases:
            for version in found_prereleases:
                yield version


_version_prefix_regex = re.compile(r'^([0-9]+)((?:a|b|c|rc)[0-9]+)$')


def _version_split(version: str) -> ta.List[str]:
    result: ta.List[str] = []

    epoch, _, rest = version.rpartition('!')
    result.append(epoch or '0')

    for item in rest.split('.'):
        match = _version_prefix_regex.search(item)
        if match:
            result.extend(match.groups())
        else:
            result.append(item)
    return result


def _version_join(components: ta.List[str]) -> str:
    epoch, *rest = components
    return f"{epoch}!{'.'.join(rest)}"


def _is_not_version_suffix(segment: str) -> bool:
    return not any(segment.startswith(prefix) for prefix in ('dev', 'a', 'b', 'rc', 'post'))


def _pad_version(left: ta.List[str], right: ta.List[str]) -> ta.Tuple[ta.List[str], ta.List[str]]:
    left_split, right_split = [], []

    left_split.append(list(itertools.takewhile(lambda x: x.isdigit(), left)))
    right_split.append(list(itertools.takewhile(lambda x: x.isdigit(), right)))

    left_split.append(left[len(left_split[0]):])
    right_split.append(right[len(right_split[0]):])

    left_split.insert(1, ['0'] * max(0, len(right_split[0]) - len(left_split[0])))
    right_split.insert(1, ['0'] * max(0, len(left_split[0]) - len(right_split[0])))

    return (
        list(itertools.chain.from_iterable(left_split)),
        list(itertools.chain.from_iterable(right_split)),
    )


class SpecifierSet(BaseSpecifier):
    def __init__(
            self,
            specifiers: str = '',
            prereleases: ta.Optional[bool] = None,
    ) -> None:
        split_specifiers = [s.strip() for s in specifiers.split(',') if s.strip()]

        self._specs = frozenset(map(Specifier, split_specifiers))
        self._prereleases = prereleases

    @property
    def prereleases(self) -> ta.Optional[bool]:
        if self._prereleases is not None:
            return self._prereleases

        if not self._specs:
            return None

        return any(s.prereleases for s in self._specs)

    @prereleases.setter
    def prereleases(self, value: bool) -> None:
        self._prereleases = value

    def __repr__(self) -> str:
        pre = (
            f', prereleases={self.prereleases!r}'
            if self._prereleases is not None
            else ''
        )

        return f'<SpecifierSet({str(self)!r}{pre})>'

    def __str__(self) -> str:
        return ','.join(sorted(str(s) for s in self._specs))

    def __hash__(self) -> int:
        return hash(self._specs)

    def __and__(self, other: ta.Union['SpecifierSet', str]) -> 'SpecifierSet':
        if isinstance(other, str):
            other = SpecifierSet(other)
        elif not isinstance(other, SpecifierSet):
            return NotImplemented  # type: ignore

        specifier = SpecifierSet()
        specifier._specs = frozenset(self._specs | other._specs)

        if self._prereleases is None and other._prereleases is not None:
            specifier._prereleases = other._prereleases
        elif self._prereleases is not None and other._prereleases is None:
            specifier._prereleases = self._prereleases
        elif self._prereleases == other._prereleases:
            specifier._prereleases = self._prereleases
        else:
            raise ValueError('Cannot combine SpecifierSets with True and False prerelease overrides.')

        return specifier

    def __eq__(self, other: object) -> bool:
        if isinstance(other, (str, Specifier)):
            other = SpecifierSet(str(other))
        elif not isinstance(other, SpecifierSet):
            return NotImplemented

        return self._specs == other._specs

    def __len__(self) -> int:
        return len(self._specs)

    def __iter__(self) -> ta.Iterator[Specifier]:
        return iter(self._specs)

    def __contains__(self, item: UnparsedVersion) -> bool:
        return self.contains(item)

    def contains(
        self,
        item: UnparsedVersion,
        prereleases: ta.Optional[bool] = None,
        installed: ta.Optional[bool] = None,
    ) -> bool:
        if not isinstance(item, Version):
            item = Version(item)

        if prereleases is None:
            prereleases = self.prereleases

        if not prereleases and item.is_prerelease:
            return False

        if installed and item.is_prerelease:
            item = Version(item.base_version)

        return all(s.contains(item, prereleases=prereleases) for s in self._specs)

    def filter(
            self,
            iterable: ta.Iterable[UnparsedVersionVar],
            prereleases: ta.Optional[bool] = None,
    ) -> ta.Iterator[UnparsedVersionVar]:
        if prereleases is None:
            prereleases = self.prereleases

        if self._specs:
            for spec in self._specs:
                iterable = spec.filter(iterable, prereleases=bool(prereleases))
            return iter(iterable)

        else:
            filtered: ta.List[UnparsedVersionVar] = []
            found_prereleases: ta.List[UnparsedVersionVar] = []

            for item in iterable:
                parsed_version = _coerce_version(item)

                if parsed_version.is_prerelease and not prereleases:
                    if not filtered:
                        found_prereleases.append(item)
                else:
                    filtered.append(item)

            if not filtered and found_prereleases and prereleases is None:
                return iter(found_prereleases)

            return iter(filtered)


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
# ../../../omlish/asyncs/asyncio/timeouts.py


def asyncio_maybe_timeout(
        fut: AwaitableT,
        timeout: ta.Optional[TimeoutLike] = None,
) -> AwaitableT:
    if timeout is not None:
        fut = asyncio.wait_for(fut, Timeout.of(timeout)())  # type: ignore
    return fut


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


class InjectorProvider(abc.ABC):
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


class InjectorBindings(abc.ABC):
    @abc.abstractmethod
    def bindings(self) -> ta.Iterator[InjectorBinding]:
        raise NotImplementedError

##


class Injector(abc.ABC):
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


class InjectorScope(abc.ABC):  # noqa
    def __init__(
            self,
            *,
            _i: Injector,
    ) -> None:
        check.not_in(abc.ABC, type(self).__bases__)

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


class ExclusiveInjectorScope(InjectorScope, abc.ABC):
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


class ContextvarInjectorScope(InjectorScope, abc.ABC):
    _cv: contextvars.ContextVar

    def __init_subclass__(cls, **kwargs: ta.Any) -> None:
        super().__init_subclass__(**kwargs)
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
            check.not_in(abc.ABC, in_.__bases__)
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
    timeout: ta.Optional[TimeoutLike] = None
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
            timeout: ta.Optional[TimeoutLike] = None,
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
        return check.not_none(subprocesses).run_(self.replace(**kwargs))  # type: ignore[attr-defined]

    _DEFAULT_ASYNC_SUBPROCESSES: ta.ClassVar[ta.Optional[ta.Any]] = None  # AbstractAsyncSubprocesses

    async def async_run(
            self,
            async_subprocesses: ta.Optional[ta.Any] = None,  # AbstractAsyncSubprocesses
            **kwargs: ta.Any,
    ) -> SubprocessRunOutput:
        if async_subprocesses is None:
            async_subprocesses = self._DEFAULT_ASYNC_SUBPROCESSES
        return await check.not_none(async_subprocesses).run_(self.replace(**kwargs))  # type: ignore[attr-defined]


SubprocessRun._FIELD_NAMES = frozenset(fld.name for fld in dc.fields(SubprocessRun))  # noqa


##


class SubprocessRunnable(abc.ABC, ta.Generic[T]):
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


########################################
# ../types.py


##


# See https://peps.python.org/pep-3149/
INTERP_OPT_GLYPHS_BY_ATTR: ta.Mapping[str, str] = collections.OrderedDict([
    ('debug', 'd'),
    ('threaded', 't'),
])

INTERP_OPT_ATTRS_BY_GLYPH: ta.Mapping[str, str] = collections.OrderedDict(
    (g, a) for a, g in INTERP_OPT_GLYPHS_BY_ATTR.items()
)


@dc.dataclass(frozen=True)
class InterpOpts:
    threaded: bool = False
    debug: bool = False

    def __str__(self) -> str:
        return ''.join(g for a, g in INTERP_OPT_GLYPHS_BY_ATTR.items() if getattr(self, a))

    @classmethod
    def parse(cls, s: str) -> 'InterpOpts':
        return cls(**{INTERP_OPT_ATTRS_BY_GLYPH[g]: True for g in s})

    @classmethod
    def parse_suffix(cls, s: str) -> ta.Tuple[str, 'InterpOpts']:
        kw = {}
        while s and (a := INTERP_OPT_ATTRS_BY_GLYPH.get(s[-1])):
            s, kw[a] = s[:-1], True
        return s, cls(**kw)


##


@dc.dataclass(frozen=True)
class InterpVersion:
    version: Version
    opts: InterpOpts

    def __str__(self) -> str:
        return str(self.version) + str(self.opts)

    @classmethod
    def parse(cls, s: str) -> 'InterpVersion':
        s, o = InterpOpts.parse_suffix(s)
        v = Version(s)
        return cls(
            version=v,
            opts=o,
        )

    @classmethod
    def try_parse(cls, s: str) -> ta.Optional['InterpVersion']:
        try:
            return cls.parse(s)
        except (KeyError, InvalidVersion):
            return None


##


@dc.dataclass(frozen=True)
class InterpSpecifier:
    specifier: Specifier
    opts: InterpOpts

    def __str__(self) -> str:
        return str(self.specifier) + str(self.opts)

    @classmethod
    def parse(cls, s: str) -> 'InterpSpecifier':
        s, o = InterpOpts.parse_suffix(s)
        if not any(s.startswith(o) for o in Specifier.OPERATORS):
            s = '~=' + s
            if s.count('.') < 2:
                s += '.0'
        return cls(
            specifier=Specifier(s),
            opts=o,
        )

    def contains(self, iv: InterpVersion) -> bool:
        return self.specifier.contains(iv.version) and self.opts == iv.opts

    def __contains__(self, iv: InterpVersion) -> bool:
        return self.contains(iv)


##


@dc.dataclass(frozen=True)
class Interp:
    exe: str
    version: InterpVersion


########################################
# ../uv/inject.py


def bind_interp_uv() -> InjectorBindings:
    lst: ta.List[InjectorBindingOrBindings] = []

    return inj.as_bindings(*lst)


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
    ('process', 'pid=%(process)s'),
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
# ../providers/base.py
"""
TODO:
 - backends
  - local builds
  - deadsnakes?
  - uv
 - loose versions
"""


##


class InterpProvider(abc.ABC):
    name: ta.ClassVar[str]

    def __init_subclass__(cls, **kwargs: ta.Any) -> None:
        super().__init_subclass__(**kwargs)
        if abc.ABC not in cls.__bases__ and 'name' not in cls.__dict__:
            sfx = 'InterpProvider'
            if not cls.__name__.endswith(sfx):
                raise NameError(cls)
            setattr(cls, 'name', snake_case(cls.__name__[:-len(sfx)]))

    @abc.abstractmethod
    def get_installed_versions(self, spec: InterpSpecifier) -> ta.Awaitable[ta.Sequence[InterpVersion]]:
        raise NotImplementedError

    @abc.abstractmethod
    def get_installed_version(self, version: InterpVersion) -> ta.Awaitable[Interp]:
        raise NotImplementedError

    async def get_installable_versions(self, spec: InterpSpecifier) -> ta.Sequence[InterpVersion]:
        return []

    async def install_version(self, version: InterpVersion) -> Interp:
        raise TypeError


InterpProviders = ta.NewType('InterpProviders', ta.Sequence[InterpProvider])


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
# ../resolvers.py


@dc.dataclass(frozen=True)
class InterpResolverProviders:
    providers: ta.Sequence[ta.Tuple[str, InterpProvider]]


class InterpResolver:
    def __init__(
            self,
            providers: InterpResolverProviders,
    ) -> None:
        super().__init__()

        self._providers: ta.Mapping[str, InterpProvider] = collections.OrderedDict(providers.providers)

    async def _resolve_installed(self, spec: InterpSpecifier) -> ta.Optional[ta.Tuple[InterpProvider, InterpVersion]]:
        lst = [
            (i, si)
            for i, p in enumerate(self._providers.values())
            for si in await p.get_installed_versions(spec)
            if spec.contains(si)
        ]

        slst = sorted(lst, key=lambda t: (-t[0], t[1].version))
        if not slst:
            return None

        bi, bv = slst[-1]
        bp = list(self._providers.values())[bi]
        return (bp, bv)

    async def resolve(
            self,
            spec: InterpSpecifier,
            *,
            install: bool = False,
    ) -> ta.Optional[Interp]:
        tup = await self._resolve_installed(spec)
        if tup is not None:
            bp, bv = tup
            return await bp.get_installed_version(bv)

        if not install:
            return None

        tp = list(self._providers.values())[0]  # noqa

        sv = sorted(
            [s for s in await tp.get_installable_versions(spec) if s in spec],
            key=lambda s: s.version,
        )
        if not sv:
            return None

        bv = sv[-1]
        return await tp.install_version(bv)

    async def list(self, spec: InterpSpecifier) -> None:
        print('installed:')
        for n, p in self._providers.items():
            lst = [
                si
                for si in await p.get_installed_versions(spec)
                if spec.contains(si)
            ]
            if lst:
                print(f'  {n}')
                for si in lst:
                    print(f'    {si}')

        print()

        print('installable:')
        for n, p in self._providers.items():
            lst = [
                si
                for si in await p.get_installable_versions(spec)
                if spec.contains(si)
            ]
            if lst:
                print(f'  {n}')
                for si in lst:
                    print(f'    {si}')


########################################
# ../../../omlish/subprocesses/async_.py


##


class AbstractAsyncSubprocesses(BaseSubprocesses):
    @abc.abstractmethod
    async def run_(self, run: SubprocessRun) -> SubprocessRunOutput:
        raise NotImplementedError

    def run(
            self,
            *cmd: str,
            input: ta.Any = None,  # noqa
            timeout: ta.Optional[TimeoutLike] = None,
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
            timeout: ta.Optional[TimeoutLike] = None,
    ) -> Communication:
        return await asyncio_maybe_timeout(self._communicate(input), timeout)


##


class AsyncioSubprocesses(AbstractAsyncSubprocesses):
    async def communicate(
            self,
            proc: asyncio.subprocess.Process,
            input: ta.Any = None,  # noqa
            timeout: ta.Optional[TimeoutLike] = None,
    ) -> ta.Tuple[ta.Optional[bytes], ta.Optional[bytes]]:
        return await AsyncioProcessCommunicator(proc).communicate(input, timeout)  # noqa

    #

    @contextlib.asynccontextmanager
    async def popen(
            self,
            *cmd: str,
            shell: bool = False,
            timeout: ta.Optional[TimeoutLike] = None,
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

        if check and proc.returncode:
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
# ../inspect.py


@dc.dataclass(frozen=True)
class InterpInspection:
    exe: str
    version: Version

    version_str: str
    config_vars: ta.Mapping[str, str]
    prefix: str
    base_prefix: str

    @property
    def opts(self) -> InterpOpts:
        return InterpOpts(
            threaded=bool(self.config_vars.get('Py_GIL_DISABLED')),
            debug=bool(self.config_vars.get('Py_DEBUG')),
        )

    @property
    def iv(self) -> InterpVersion:
        return InterpVersion(
            version=self.version,
            opts=self.opts,
        )

    @property
    def is_venv(self) -> bool:
        return self.prefix != self.base_prefix


class InterpInspector:
    def __init__(
            self,
            *,
            log: ta.Optional[logging.Logger] = None,
    ) -> None:
        super().__init__()

        self._log = log

        self._cache: ta.Dict[str, ta.Optional[InterpInspection]] = {}

    _RAW_INSPECTION_CODE = """
    __import__('json').dumps(dict(
        version_str=__import__('sys').version,
        prefix=__import__('sys').prefix,
        base_prefix=__import__('sys').base_prefix,
        config_vars=__import__('sysconfig').get_config_vars(),
    ))"""

    _INSPECTION_CODE = ''.join(l.strip() for l in _RAW_INSPECTION_CODE.splitlines())

    @staticmethod
    def _build_inspection(
            exe: str,
            output: str,
    ) -> InterpInspection:
        dct = json.loads(output)

        version = Version(dct['version_str'].split()[0])

        return InterpInspection(
            exe=exe,
            version=version,
            **{k: dct[k] for k in (
                'version_str',
                'prefix',
                'base_prefix',
                'config_vars',
            )},
        )

    @classmethod
    def running(cls) -> 'InterpInspection':
        return cls._build_inspection(sys.executable, eval(cls._INSPECTION_CODE))  # noqa

    async def _inspect(self, exe: str) -> InterpInspection:
        output = await asyncio_subprocesses.check_output(exe, '-c', f'print({self._INSPECTION_CODE})', quiet=True)
        return self._build_inspection(exe, output.decode())

    async def inspect(self, exe: str) -> ta.Optional[InterpInspection]:
        try:
            return self._cache[exe]
        except KeyError:
            ret: ta.Optional[InterpInspection]
            try:
                ret = await self._inspect(exe)
            except Exception as e:  # noqa
                if self._log is not None and self._log.isEnabledFor(logging.DEBUG):
                    self._log.exception('Failed to inspect interp: %s', exe)
                ret = None
            self._cache[exe] = ret
            return ret


########################################
# ../pyenv/pyenv.py
"""
TODO:
 - custom tags
  - 'aliases'
  - https://github.com/pyenv/pyenv/pull/2966
  - https://github.com/pyenv/pyenv/issues/218 (lol)
  - probably need custom (temp?) definition file
  - *or* python-build directly just into the versions dir?
 - optionally install / upgrade pyenv itself
 - new vers dont need these custom mac opts, only run on old vers
"""


class Pyenv:
    def __init__(
            self,
            *,
            root: ta.Optional[str] = None,
    ) -> None:
        if root is not None and not (isinstance(root, str) and root):
            raise ValueError(f'pyenv_root: {root!r}')

        super().__init__()

        self._root_kw = root

    @async_cached_nullary
    async def root(self) -> ta.Optional[str]:
        if self._root_kw is not None:
            return self._root_kw

        if shutil.which('pyenv'):
            return await asyncio_subprocesses.check_output_str('pyenv', 'root')

        d = os.path.expanduser('~/.pyenv')
        if os.path.isdir(d) and os.path.isfile(os.path.join(d, 'bin', 'pyenv')):
            return d

        return None

    @async_cached_nullary
    async def exe(self) -> str:
        return os.path.join(check.not_none(await self.root()), 'bin', 'pyenv')

    async def version_exes(self) -> ta.List[ta.Tuple[str, str]]:
        if (root := await self.root()) is None:
            return []
        ret = []
        vp = os.path.join(root, 'versions')
        if os.path.isdir(vp):
            for dn in os.listdir(vp):
                ep = os.path.join(vp, dn, 'bin', 'python')
                if not os.path.isfile(ep):
                    continue
                ret.append((dn, ep))
        return ret

    async def installable_versions(self) -> ta.List[str]:
        if await self.root() is None:
            return []
        ret = []
        s = await asyncio_subprocesses.check_output_str(await self.exe(), 'install', '--list')
        for l in s.splitlines():
            if not l.startswith('  '):
                continue
            l = l.strip()
            if not l:
                continue
            ret.append(l)
        return ret

    async def update(self) -> bool:
        if (root := await self.root()) is None:
            return False
        if not os.path.isdir(os.path.join(root, '.git')):
            return False
        await asyncio_subprocesses.check_call('git', 'pull', cwd=root)
        return True


########################################
# ../providers/running.py


class RunningInterpProvider(InterpProvider):
    @cached_nullary
    def version(self) -> InterpVersion:
        return InterpInspector.running().iv

    async def get_installed_versions(self, spec: InterpSpecifier) -> ta.Sequence[InterpVersion]:
        return [self.version()]

    async def get_installed_version(self, version: InterpVersion) -> Interp:
        if version != self.version():
            raise KeyError(version)
        return Interp(
            exe=sys.executable,
            version=self.version(),
        )


########################################
# ../providers/system.py
"""
TODO:
 - python, python3, python3.12, ...
 - check if path py's are venvs: sys.prefix != sys.base_prefix
"""


##


class SystemInterpProvider(InterpProvider):
    @dc.dataclass(frozen=True)
    class Options:
        cmd: str = 'python3'  # FIXME: unused lol
        path: ta.Optional[str] = None

        inspect: bool = False

    def __init__(
            self,
            options: Options = Options(),
            *,
            inspector: ta.Optional[InterpInspector] = None,
            log: ta.Optional[logging.Logger] = None,
    ) -> None:
        super().__init__()

        self._options = options

        self._inspector = inspector
        self._log = log

    #

    @staticmethod
    def _re_which(
            pat: re.Pattern,
            *,
            mode: int = os.F_OK | os.X_OK,
            path: ta.Optional[str] = None,
    ) -> ta.List[str]:
        if path is None:
            path = os.environ.get('PATH', None)
            if path is None:
                try:
                    path = os.confstr('CS_PATH')
                except (AttributeError, ValueError):
                    path = os.defpath

        if not path:
            return []

        path = os.fsdecode(path)
        pathlst = path.split(os.pathsep)

        def _access_check(fn: str, mode: int) -> bool:
            return os.path.exists(fn) and os.access(fn, mode)

        out = []
        seen = set()
        for d in pathlst:
            normdir = os.path.normcase(d)
            if normdir not in seen:
                seen.add(normdir)
                if not _access_check(normdir, mode):
                    continue
                for thefile in os.listdir(d):
                    name = os.path.join(d, thefile)
                    if not (
                            os.path.isfile(name) and
                            pat.fullmatch(thefile) and
                            _access_check(name, mode)
                    ):
                        continue
                    out.append(name)

        return out

    @cached_nullary
    def exes(self) -> ta.List[str]:
        return self._re_which(
            re.compile(r'python3(\.\d+)?'),
            path=self._options.path,
        )

    #

    async def get_exe_version(self, exe: str) -> ta.Optional[InterpVersion]:
        if not self._options.inspect:
            s = os.path.basename(exe)
            if s.startswith('python'):  # noqa
                s = s[len('python'):]
            if '.' in s:
                try:
                    return InterpVersion.parse(s)
                except InvalidVersion:
                    pass
        ii = await check.not_none(self._inspector).inspect(exe)
        return ii.iv if ii is not None else None

    async def exe_versions(self) -> ta.Sequence[ta.Tuple[str, InterpVersion]]:
        lst = []
        for e in self.exes():
            if (ev := await self.get_exe_version(e)) is None:
                if self._log is not None:
                    self._log.debug('Invalid system version: %s', e)
                continue
            lst.append((e, ev))
        return lst

    #

    async def get_installed_versions(self, spec: InterpSpecifier) -> ta.Sequence[InterpVersion]:
        return [ev for e, ev in await self.exe_versions()]

    async def get_installed_version(self, version: InterpVersion) -> Interp:
        for e, ev in await self.exe_versions():
            if ev != version:
                continue
            return Interp(
                exe=e,
                version=ev,
            )
        raise KeyError(version)


########################################
# ../pyenv/install.py


##


@dc.dataclass(frozen=True)
class PyenvInstallOpts:
    opts: ta.Sequence[str] = ()
    conf_opts: ta.Sequence[str] = ()
    cflags: ta.Sequence[str] = ()
    ldflags: ta.Sequence[str] = ()
    env: ta.Mapping[str, str] = dc.field(default_factory=dict)

    def merge(self, *others: 'PyenvInstallOpts') -> 'PyenvInstallOpts':
        return PyenvInstallOpts(
            opts=list(itertools.chain.from_iterable(o.opts for o in [self, *others])),
            conf_opts=list(itertools.chain.from_iterable(o.conf_opts for o in [self, *others])),
            cflags=list(itertools.chain.from_iterable(o.cflags for o in [self, *others])),
            ldflags=list(itertools.chain.from_iterable(o.ldflags for o in [self, *others])),
            env=dict(itertools.chain.from_iterable(o.env.items() for o in [self, *others])),
        )


# TODO: https://github.com/pyenv/pyenv/blob/master/plugins/python-build/README.md#building-for-maximum-performance
DEFAULT_PYENV_INSTALL_OPTS = PyenvInstallOpts(
    opts=[
        '-s',
        '-v',
        '-k',
    ],
    conf_opts=[
        # FIXME: breaks on mac for older py's
        '--enable-loadable-sqlite-extensions',

        # '--enable-shared',

        '--enable-optimizations',
        '--with-lto',

        # '--enable-profiling', # ?

        # '--enable-ipv6', # ?
    ],
    cflags=[
        # '-march=native',
        # '-mtune=native',
    ],
)

DEBUG_PYENV_INSTALL_OPTS = PyenvInstallOpts(opts=['-g'])

THREADED_PYENV_INSTALL_OPTS = PyenvInstallOpts(conf_opts=['--disable-gil'])


#


class PyenvInstallOptsProvider(abc.ABC):
    @abc.abstractmethod
    def opts(self) -> ta.Awaitable[PyenvInstallOpts]:
        raise NotImplementedError


class LinuxPyenvInstallOpts(PyenvInstallOptsProvider):
    async def opts(self) -> PyenvInstallOpts:
        return PyenvInstallOpts()


class DarwinPyenvInstallOpts(PyenvInstallOptsProvider):
    @cached_nullary
    def framework_opts(self) -> PyenvInstallOpts:
        return PyenvInstallOpts(conf_opts=['--enable-framework'])

    @cached_nullary
    def has_brew(self) -> bool:
        return shutil.which('brew') is not None

    BREW_DEPS: ta.Sequence[str] = [
        'openssl',
        'readline',
        'sqlite3',
        'zlib',
    ]

    @async_cached_nullary
    async def brew_deps_opts(self) -> PyenvInstallOpts:
        cflags = []
        ldflags = []
        for dep in self.BREW_DEPS:
            dep_prefix = await asyncio_subprocesses.check_output_str('brew', '--prefix', dep)
            cflags.append(f'-I{dep_prefix}/include')
            ldflags.append(f'-L{dep_prefix}/lib')
        return PyenvInstallOpts(
            cflags=cflags,
            ldflags=ldflags,
        )

    @async_cached_nullary
    async def brew_tcl_opts(self) -> PyenvInstallOpts:
        if await asyncio_subprocesses.try_output('brew', '--prefix', 'tcl-tk') is None:
            return PyenvInstallOpts()

        tcl_tk_prefix = await asyncio_subprocesses.check_output_str('brew', '--prefix', 'tcl-tk')
        tcl_tk_ver_str = await asyncio_subprocesses.check_output_str('brew', 'ls', '--versions', 'tcl-tk')
        tcl_tk_ver = '.'.join(tcl_tk_ver_str.split()[1].split('.')[:2])

        return PyenvInstallOpts(conf_opts=[
            f"--with-tcltk-includes='-I{tcl_tk_prefix}/include'",
            f"--with-tcltk-libs='-L{tcl_tk_prefix}/lib -ltcl{tcl_tk_ver} -ltk{tcl_tk_ver}'",
        ])

    # @cached_nullary
    # def brew_ssl_opts(self) -> PyenvInstallOpts:
    #     pkg_config_path = subprocess_check_output_str('brew', '--prefix', 'openssl')
    #     if 'PKG_CONFIG_PATH' in os.environ:
    #         pkg_config_path += ':' + os.environ['PKG_CONFIG_PATH']
    #     return PyenvInstallOpts(env={'PKG_CONFIG_PATH': pkg_config_path})

    async def opts(self) -> PyenvInstallOpts:
        return PyenvInstallOpts().merge(
            self.framework_opts(),
            await self.brew_deps_opts(),
            await self.brew_tcl_opts(),
            # self.brew_ssl_opts(),
        )


PLATFORM_PYENV_INSTALL_OPTS: ta.Dict[str, PyenvInstallOptsProvider] = {
    'darwin': DarwinPyenvInstallOpts(),
    'linux': LinuxPyenvInstallOpts(),
}


##


class PyenvVersionInstaller:
    """
    Messy: can install freethreaded build with a 't' suffixed version str _or_ by THREADED_PYENV_INSTALL_OPTS - need
    latter to build custom interp with ft, need former to use canned / blessed interps. Muh.
    """

    def __init__(
            self,
            version: str,
            opts: ta.Optional[PyenvInstallOpts] = None,
            interp_opts: InterpOpts = InterpOpts(),
            *,
            pyenv: Pyenv,

            install_name: ta.Optional[str] = None,
            no_default_opts: bool = False,
    ) -> None:
        super().__init__()

        self._version = version
        self._given_opts = opts
        self._interp_opts = interp_opts
        self._given_install_name = install_name

        self._no_default_opts = no_default_opts
        self._pyenv = pyenv

    @property
    def version(self) -> str:
        return self._version

    @async_cached_nullary
    async def opts(self) -> PyenvInstallOpts:
        opts = self._given_opts
        if self._no_default_opts:
            if opts is None:
                opts = PyenvInstallOpts()
        else:
            lst = [self._given_opts if self._given_opts is not None else DEFAULT_PYENV_INSTALL_OPTS]
            if self._interp_opts.debug:
                lst.append(DEBUG_PYENV_INSTALL_OPTS)
            if self._interp_opts.threaded:
                lst.append(THREADED_PYENV_INSTALL_OPTS)
            lst.append(await PLATFORM_PYENV_INSTALL_OPTS[sys.platform].opts())
            opts = PyenvInstallOpts().merge(*lst)
        return opts

    @cached_nullary
    def install_name(self) -> str:
        if self._given_install_name is not None:
            return self._given_install_name
        return self._version + ('-debug' if self._interp_opts.debug else '')

    @async_cached_nullary
    async def install_dir(self) -> str:
        return str(os.path.join(check.not_none(await self._pyenv.root()), 'versions', self.install_name()))

    @async_cached_nullary
    async def install(self) -> str:
        opts = await self.opts()
        env = {**os.environ, **opts.env}
        for k, l in [
            ('CFLAGS', opts.cflags),
            ('LDFLAGS', opts.ldflags),
            ('PYTHON_CONFIGURE_OPTS', opts.conf_opts),
        ]:
            v = ' '.join(l)
            if k in os.environ:
                v += ' ' + os.environ[k]
            env[k] = v

        conf_args = [
            *opts.opts,
            self._version,
        ]

        full_args: ta.List[str]
        if self._given_install_name is not None:
            full_args = [
                os.path.join(check.not_none(await self._pyenv.root()), 'plugins', 'python-build', 'bin', 'python-build'),  # noqa
                *conf_args,
                await self.install_dir(),
            ]
        else:
            full_args = [
                await self._pyenv.exe(),
                'install',
                *conf_args,
            ]

        await asyncio_subprocesses.check_call(
            *full_args,
            env=env,
        )

        exe = os.path.join(await self.install_dir(), 'bin', 'python')
        if not os.path.isfile(exe):
            raise RuntimeError(f'Interpreter not found: {exe}')
        return exe


########################################
# ../providers/inject.py


def bind_interp_providers() -> InjectorBindings:
    lst: ta.List[InjectorBindingOrBindings] = [
        inj.bind_array(InterpProvider),
        inj.bind_array_type(InterpProvider, InterpProviders),

        inj.bind(RunningInterpProvider, singleton=True),
        inj.bind(InterpProvider, to_key=RunningInterpProvider, array=True),

        inj.bind(SystemInterpProvider, singleton=True),
        inj.bind(InterpProvider, to_key=SystemInterpProvider, array=True),
    ]

    return inj.as_bindings(*lst)


########################################
# ../pyenv/provider.py


class PyenvInterpProvider(InterpProvider):
    @dc.dataclass(frozen=True)
    class Options:
        inspect: bool = False

        try_update: bool = False

    def __init__(
            self,
            options: Options = Options(),
            *,
            pyenv: Pyenv,
            inspector: InterpInspector,
            log: ta.Optional[logging.Logger] = None,
    ) -> None:
        super().__init__()

        self._options = options

        self._pyenv = pyenv
        self._inspector = inspector
        self._log = log

    #

    @staticmethod
    def guess_version(s: str) -> ta.Optional[InterpVersion]:
        def strip_sfx(s: str, sfx: str) -> ta.Tuple[str, bool]:
            if s.endswith(sfx):
                return s[:-len(sfx)], True
            return s, False
        ok = {}
        s, ok['debug'] = strip_sfx(s, '-debug')
        s, ok['threaded'] = strip_sfx(s, 't')
        try:
            v = Version(s)
        except InvalidVersion:
            return None
        return InterpVersion(v, InterpOpts(**ok))

    class Installed(ta.NamedTuple):
        name: str
        exe: str
        version: InterpVersion

    async def _make_installed(self, vn: str, ep: str) -> ta.Optional[Installed]:
        iv: ta.Optional[InterpVersion]
        if self._options.inspect:
            try:
                iv = check.not_none(await self._inspector.inspect(ep)).iv
            except Exception as e:  # noqa
                return None
        else:
            iv = self.guess_version(vn)
        if iv is None:
            return None
        return PyenvInterpProvider.Installed(
            name=vn,
            exe=ep,
            version=iv,
        )

    async def installed(self) -> ta.Sequence[Installed]:
        ret: ta.List[PyenvInterpProvider.Installed] = []
        for vn, ep in await self._pyenv.version_exes():
            if (i := await self._make_installed(vn, ep)) is None:
                if self._log is not None:
                    self._log.debug('Invalid pyenv version: %s', vn)
                continue
            ret.append(i)
        return ret

    #

    async def get_installed_versions(self, spec: InterpSpecifier) -> ta.Sequence[InterpVersion]:
        return [i.version for i in await self.installed()]

    async def get_installed_version(self, version: InterpVersion) -> Interp:
        for i in await self.installed():
            if i.version == version:
                return Interp(
                    exe=i.exe,
                    version=i.version,
                )
        raise KeyError(version)

    #

    async def _get_installable_versions(self, spec: InterpSpecifier) -> ta.Sequence[InterpVersion]:
        lst = []

        for vs in await self._pyenv.installable_versions():
            if (iv := self.guess_version(vs)) is None:
                continue
            if iv.opts.debug:
                raise Exception('Pyenv installable versions not expected to have debug suffix')
            for d in [False, True]:
                lst.append(dc.replace(iv, opts=dc.replace(iv.opts, debug=d)))

        return lst

    async def get_installable_versions(self, spec: InterpSpecifier) -> ta.Sequence[InterpVersion]:
        lst = await self._get_installable_versions(spec)

        if self._options.try_update and not any(v in spec for v in lst):
            if self._pyenv.update():
                lst = await self._get_installable_versions(spec)

        return lst

    async def install_version(self, version: InterpVersion) -> Interp:
        inst_version = str(version.version)
        inst_opts = version.opts
        if inst_opts.threaded:
            inst_version += 't'
            inst_opts = dc.replace(inst_opts, threaded=False)

        installer = PyenvVersionInstaller(
            inst_version,
            interp_opts=inst_opts,
            pyenv=self._pyenv,
        )

        exe = await installer.install()
        return Interp(exe, version)


########################################
# ../pyenv/inject.py


def bind_interp_pyenv() -> InjectorBindings:
    lst: ta.List[InjectorBindingOrBindings] = [
        inj.bind(Pyenv, singleton=True),

        inj.bind(PyenvInterpProvider, singleton=True),
        inj.bind(InterpProvider, to_key=PyenvInterpProvider, array=True),
    ]

    return inj.as_bindings(*lst)


########################################
# ../inject.py


def bind_interp() -> InjectorBindings:
    lst: ta.List[InjectorBindingOrBindings] = [
        bind_interp_providers(),

        bind_interp_pyenv(),

        bind_interp_uv(),

        inj.bind(InterpInspector, singleton=True),
    ]

    #

    def provide_interp_resolver_providers(injector: Injector) -> InterpResolverProviders:
        # FIXME: lol
        rps: ta.List[ta.Any] = [
            injector.provide(c)
            for c in [
                PyenvInterpProvider,
                RunningInterpProvider,
                SystemInterpProvider,
            ]
        ]

        return InterpResolverProviders([(rp.name, rp) for rp in rps])

    lst.append(inj.bind(provide_interp_resolver_providers, singleton=True))

    lst.extend([
        inj.bind(InterpResolver, singleton=True),
    ])

    #

    return inj.as_bindings(*lst)


########################################
# cli.py


class InterpCli(ArgparseCli):
    @cached_nullary
    def injector(self) -> Injector:
        return inj.create_injector(bind_interp())

    @cached_nullary
    def providers(self) -> InterpResolverProviders:
        return self.injector()[InterpResolverProviders]

    #

    @argparse_cmd(
        argparse_arg('version'),
        argparse_arg('-d', '--debug', action='store_true'),
    )
    async def list(self) -> None:
        r = InterpResolver(self.providers())
        s = InterpSpecifier.parse(self.args.version)
        await r.list(s)

    @argparse_cmd(
        argparse_arg('version'),
        argparse_arg('-p', '--provider'),
        argparse_arg('-d', '--debug', action='store_true'),
        argparse_arg('-i', '--install', action='store_true'),
    )
    async def resolve(self) -> None:
        if self.args.provider:
            p = check.single([p for n, p in self.providers().providers if n == self.args.provider])
            r = InterpResolver(InterpResolverProviders([(p.name, p)]))
        else:
            r = InterpResolver(self.providers())
        s = InterpSpecifier.parse(self.args.version)
        print(check.not_none(await r.resolve(s, install=bool(self.args.install))).exe)


async def _async_main(argv: ta.Optional[ta.Sequence[str]] = None) -> None:
    check_lite_runtime_version()
    configure_standard_logging()

    cli = InterpCli(argv)
    await cli.async_cli_run()


def _main(argv: ta.Optional[ta.Sequence[str]] = None) -> None:
    asyncio.run(_async_main(argv))


if __name__ == '__main__':
    _main()
