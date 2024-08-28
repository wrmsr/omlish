#!/usr/bin/env python3
# noinspection DuplicatedCode
# @omdev-amalg-output ../interp/cli.py
# ruff: noqa: UP007
"""
TODO:
 - partial best-matches - '3.12'
 - https://github.com/asdf-vm/asdf support (instead of pyenv) ?
 - colon sep provider name prefix - pyenv:3.12
"""
import abc
import argparse
import collections
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
import typing as ta


VersionLocalType = ta.Tuple[ta.Union[int, str], ...]
VersionCmpPrePostDevType = ta.Union['InfinityVersionType', 'NegativeInfinityVersionType', ta.Tuple[str, int]]
_VersionCmpLocalType0 = ta.Tuple[ta.Union[ta.Tuple[int, str], ta.Tuple['NegativeInfinityVersionType', ta.Union[int, str]]], ...]  # noqa
VersionCmpLocalType = ta.Union['NegativeInfinityVersionType', _VersionCmpLocalType0]
VersionCmpKey = ta.Tuple[int, ta.Tuple[int, ...], VersionCmpPrePostDevType, VersionCmpPrePostDevType, VersionCmpPrePostDevType, VersionCmpLocalType]  # noqa
VersionComparisonMethod = ta.Callable[[VersionCmpKey, VersionCmpKey], bool]
T = ta.TypeVar('T')
UnparsedVersion = ta.Union['Version', str]
UnparsedVersionVar = ta.TypeVar('UnparsedVersionVar', bound=UnparsedVersion)
CallableVersionOperator = ta.Callable[['Version', str], bool]


########################################
# ../../versioning/versions.py
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
# ruff: noqa: UP006 UP007


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


class cached_nullary:  # noqa
    def __init__(self, fn):
        super().__init__()
        self._fn = fn
        self._value = self._missing = object()
        functools.update_wrapper(self, fn)

    def __call__(self, *args, **kwargs):  # noqa
        if self._value is self._missing:
            self._value = self._fn()
        return self._value

    def __get__(self, instance, owner):  # noqa
        bound = instance.__dict__[self._fn.__name__] = self.__class__(self._fn.__get__(instance, owner))
        return bound


########################################
# ../../../omlish/lite/check.py
# ruff: noqa: UP006 UP007


def check_isinstance(v: T, spec: ta.Union[ta.Type[T], tuple]) -> T:
    if not isinstance(v, spec):
        raise TypeError(v)
    return v


def check_not_isinstance(v: T, spec: ta.Union[type, tuple]) -> T:
    if isinstance(v, spec):
        raise TypeError(v)
    return v


def check_not_none(v: ta.Optional[T]) -> T:
    if v is None:
        raise ValueError
    return v


def check_not(v: ta.Any) -> None:
    if v:
        raise ValueError(v)
    return v


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
# ../../../omlish/lite/reflect.py
# ruff: noqa: UP006


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


def camel_case(name: str) -> str:
    return ''.join(map(str.capitalize, name.split('_')))  # noqa


def snake_case(name: str) -> str:
    uppers: list[int | None] = [i for i, c in enumerate(name) if c.isupper()]
    return '_'.join([name[l:r].lower() for l, r in zip([None, *uppers], [*uppers, None])]).strip('_')


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


########################################
# ../../versioning/specifiers.py
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
# ruff: noqa: UP006 UP007


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
# ../../../omlish/lite/logs.py
"""
TODO:
 - translate json keys
 - debug
"""
# ruff: noqa: UP006 UP007 N802


log = logging.getLogger(__name__)


##


class TidLogFilter(logging.Filter):

    def filter(self, record):
        record.tid = threading.get_native_id()
        return True


##


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

    def format(self, record: logging.LogRecord) -> str:
        dct = {
            k: v
            for k, o in self.KEYS.items()
            for v in [getattr(record, k)]
            if not (o and v is None)
        }
        return json_dumps_compact(dct)


##


STANDARD_LOG_FORMAT_PARTS = [
    ('asctime', '%(asctime)-15s'),
    ('process', 'pid=%(process)-6s'),
    ('thread', 'tid=%(thread)-16s'),
    ('levelname', '%(levelname)-8s'),
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
            t = ct.strftime("%Y-%m-%d %H:%M:%S")  # noqa
            return '%s.%03d' % (t, record.msecs)


##


def configure_standard_logging(
        level: ta.Union[int, str] = logging.INFO,
        *,
        json: bool = False,
) -> logging.Handler:
    handler = logging.StreamHandler()

    formatter: logging.Formatter
    if json:
        formatter = JsonLogFormatter()
    else:
        formatter = StandardLogFormatter(StandardLogFormatter.build_log_format(STANDARD_LOG_FORMAT_PARTS))
    handler.setFormatter(formatter)

    handler.addFilter(TidLogFilter())

    logging.root.addHandler(handler)

    if level is not None:
        logging.root.setLevel(level)

    return handler


########################################
# ../../../omlish/lite/runtime.py


@cached_nullary
def is_debugger_attached() -> bool:
    return any(frame[1].endswith('pydevd.py') for frame in inspect.stack())


REQUIRED_PYTHON_VERSION = (3, 8)


def check_runtime_version() -> None:
    if sys.version_info < REQUIRED_PYTHON_VERSION:
        raise OSError(
            f'Requires python {REQUIRED_PYTHON_VERSION}, got {sys.version_info} from {sys.executable}')  # noqa


########################################
# ../types.py
# ruff: noqa: UP006


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
        return cls(
            specifier=Specifier(s),
            opts=o,
        )

    def contains(self, iv: InterpVersion) -> bool:
        return self.specifier.contains(iv.version) and self.opts == iv.opts


@dc.dataclass(frozen=True)
class Interp:
    exe: str
    version: InterpVersion


########################################
# ../../../omlish/lite/subprocesses.py
# ruff: noqa: UP006 UP007


##


_SUBPROCESS_SHELL_WRAP_EXECS = False


def subprocess_shell_wrap_exec(*args: str) -> ta.Tuple[str, ...]:
    return ('sh', '-c', ' '.join(map(shlex.quote, args)))


def subprocess_maybe_shell_wrap_exec(*args: str) -> ta.Tuple[str, ...]:
    if _SUBPROCESS_SHELL_WRAP_EXECS or is_debugger_attached():
        return subprocess_shell_wrap_exec(*args)
    else:
        return args


def _prepare_subprocess_invocation(
        *args: str,
        env: ta.Optional[ta.Mapping[str, ta.Any]] = None,
        extra_env: ta.Optional[ta.Mapping[str, ta.Any]] = None,
        quiet: bool = False,
        shell: bool = False,
        **kwargs: ta.Any,
) -> ta.Tuple[ta.Tuple[ta.Any, ...], ta.Dict[str, ta.Any]]:
    log.debug(args)
    if extra_env:
        log.debug(extra_env)

    if extra_env:
        env = {**(env if env is not None else os.environ), **extra_env}

    if quiet and 'stderr' not in kwargs:
        if not log.isEnabledFor(logging.DEBUG):
            kwargs['stderr'] = subprocess.DEVNULL

    if not shell:
        args = subprocess_maybe_shell_wrap_exec(*args)

    return args, dict(
        env=env,
        shell=shell,
        **kwargs,
    )


def subprocess_check_call(*args: str, stdout=sys.stderr, **kwargs: ta.Any) -> None:
    args, kwargs = _prepare_subprocess_invocation(*args, stdout=stdout, **kwargs)
    return subprocess.check_call(args, **kwargs)  # type: ignore


def subprocess_check_output(*args: str, **kwargs: ta.Any) -> bytes:
    args, kwargs = _prepare_subprocess_invocation(*args, **kwargs)
    return subprocess.check_output(args, **kwargs)


def subprocess_check_output_str(*args: str, **kwargs: ta.Any) -> str:
    return subprocess_check_output(*args, **kwargs).decode().strip()


##


DEFAULT_SUBPROCESS_TRY_EXCEPTIONS: ta.Tuple[ta.Type[Exception], ...] = (
    FileNotFoundError,
    subprocess.CalledProcessError,
)


def subprocess_try_call(
        *args: str,
        try_exceptions: ta.Tuple[ta.Type[Exception], ...] = DEFAULT_SUBPROCESS_TRY_EXCEPTIONS,
        **kwargs: ta.Any,
) -> bool:
    try:
        subprocess_check_call(*args, **kwargs)
    except try_exceptions as e:  # noqa
        if log.isEnabledFor(logging.DEBUG):
            log.exception('command failed')
        return False
    else:
        return True


def subprocess_try_output(
        *args: str,
        try_exceptions: ta.Tuple[ta.Type[Exception], ...] = DEFAULT_SUBPROCESS_TRY_EXCEPTIONS,
        **kwargs: ta.Any,
) -> ta.Optional[bytes]:
    try:
        return subprocess_check_output(*args, **kwargs)
    except try_exceptions as e:  # noqa
        if log.isEnabledFor(logging.DEBUG):
            log.exception('command failed')
        return None


def subprocess_try_output_str(*args: str, **kwargs: ta.Any) -> ta.Optional[str]:
    out = subprocess_try_output(*args, **kwargs)
    return out.decode().strip() if out is not None else None


########################################
# ../inspect.py
# ruff: noqa: UP006 UP007


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

    def __init__(self) -> None:
        super().__init__()

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

    def _inspect(self, exe: str) -> InterpInspection:
        output = subprocess_check_output(exe, '-c', f'print({self._INSPECTION_CODE})', quiet=True)
        return self._build_inspection(exe, output.decode())

    def inspect(self, exe: str) -> ta.Optional[InterpInspection]:
        try:
            return self._cache[exe]
        except KeyError:
            ret: ta.Optional[InterpInspection]
            try:
                ret = self._inspect(exe)
            except Exception as e:  # noqa
                if log.isEnabledFor(logging.DEBUG):
                    log.exception('Failed to inspect interp: %s', exe)
                ret = None
            self._cache[exe] = ret
            return ret


INTERP_INSPECTOR = InterpInspector()


########################################
# ../providers.py
"""
TODO:
 - backends
  - local builds
  - deadsnakes?
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
    def get_installed_versions(self, spec: InterpSpecifier) -> ta.Sequence[InterpVersion]:
        raise NotImplementedError

    @abc.abstractmethod
    def get_installed_version(self, version: InterpVersion) -> Interp:
        raise NotImplementedError

    def get_installable_versions(self, spec: InterpSpecifier) -> ta.Sequence[InterpVersion]:
        return []

    def install_version(self, version: InterpVersion) -> Interp:
        raise TypeError


##


class RunningInterpProvider(InterpProvider):
    @cached_nullary
    def version(self) -> InterpVersion:
        return InterpInspector.running().iv

    def get_installed_versions(self, spec: InterpSpecifier) -> ta.Sequence[InterpVersion]:
        return [self.version()]

    def get_installed_version(self, version: InterpVersion) -> Interp:
        if version != self.version():
            raise KeyError(version)
        return Interp(
            exe=sys.executable,
            version=self.version(),
        )


########################################
# ../pyenv.py
"""
TODO:
 - custom tags
 - optionally install / upgrade pyenv itself
 - new vers dont need these custom mac opts, only run on old vers
"""
# ruff: noqa: UP006 UP007


##


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

    @cached_nullary
    def root(self) -> ta.Optional[str]:
        if self._root_kw is not None:
            return self._root_kw

        if shutil.which('pyenv'):
            return subprocess_check_output_str('pyenv', 'root')

        d = os.path.expanduser('~/.pyenv')
        if os.path.isdir(d) and os.path.isfile(os.path.join(d, 'bin', 'pyenv')):
            return d

        return None

    @cached_nullary
    def exe(self) -> str:
        return os.path.join(check_not_none(self.root()), 'bin', 'pyenv')

    def version_exes(self) -> ta.List[ta.Tuple[str, str]]:
        if (root := self.root()) is None:
            return []
        ret = []
        vp = os.path.join(root, 'versions')
        for dn in os.listdir(vp):
            ep = os.path.join(vp, dn, 'bin', 'python')
            if not os.path.isfile(ep):
                continue
            ret.append((dn, ep))
        return ret

    def installable_versions(self) -> ta.List[str]:
        if self.root() is None:
            return []
        ret = []
        s = subprocess_check_output_str(self.exe(), 'install', '--list')
        for l in s.splitlines():
            if not l.startswith('  '):
                continue
            l = l.strip()
            if not l:
                continue
            ret.append(l)
        return ret


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


DEFAULT_PYENV_INSTALL_OPTS = PyenvInstallOpts(opts=['-s', '-v'])
DEBUG_PYENV_INSTALL_OPTS = PyenvInstallOpts(opts=['-g'])


#


class PyenvInstallOptsProvider(abc.ABC):
    @abc.abstractmethod
    def opts(self) -> PyenvInstallOpts:
        raise NotImplementedError


class LinuxPyenvInstallOpts(PyenvInstallOptsProvider):
    def opts(self) -> PyenvInstallOpts:
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

    @cached_nullary
    def brew_deps_opts(self) -> PyenvInstallOpts:
        cflags = []
        ldflags = []
        for dep in self.BREW_DEPS:
            dep_prefix = subprocess_check_output_str('brew', '--prefix', dep)
            cflags.append(f'-I{dep_prefix}/include')
            ldflags.append(f'-L{dep_prefix}/lib')
        return PyenvInstallOpts(
            cflags=cflags,
            ldflags=ldflags,
        )

    @cached_nullary
    def brew_tcl_opts(self) -> PyenvInstallOpts:
        if subprocess_try_output('brew', '--prefix', 'tcl-tk') is None:
            return PyenvInstallOpts()

        tcl_tk_prefix = subprocess_check_output_str('brew', '--prefix', 'tcl-tk')
        tcl_tk_ver_str = subprocess_check_output_str('brew', 'ls', '--versions', 'tcl-tk')
        tcl_tk_ver = '.'.join(tcl_tk_ver_str.split()[1].split('.')[:2])

        return PyenvInstallOpts(conf_opts=[
            f"--with-tcltk-includes='-I{tcl_tk_prefix}/include'",
            f"--with-tcltk-libs='-L{tcl_tk_prefix}/lib -ltcl{tcl_tk_ver} -ltk{tcl_tk_ver}'",
        ])

    @cached_nullary
    def brew_ssl_opts(self) -> PyenvInstallOpts:
        pkg_config_path = subprocess_check_output_str('brew', '--prefix', 'openssl')
        if 'PKG_CONFIG_PATH' in os.environ:
            pkg_config_path += ':' + os.environ['PKG_CONFIG_PATH']
        return PyenvInstallOpts(env={'PKG_CONFIG_PATH': pkg_config_path})

    def opts(self) -> PyenvInstallOpts:
        return PyenvInstallOpts().merge(
            self.framework_opts(),
            self.brew_deps_opts(),
            self.brew_tcl_opts(),
            self.brew_ssl_opts(),
        )


PLATFORM_PYENV_INSTALL_OPTS: ta.Dict[str, PyenvInstallOptsProvider] = {
    'darwin': DarwinPyenvInstallOpts(),
    'linux': LinuxPyenvInstallOpts(),
}


##


class PyenvVersionInstaller:

    def __init__(
            self,
            version: str,
            opts: ta.Optional[PyenvInstallOpts] = None,
            *,
            debug: bool = False,
            pyenv: Pyenv = Pyenv(),
    ) -> None:
        super().__init__()

        if opts is None:
            lst = [DEFAULT_PYENV_INSTALL_OPTS]
            if debug:
                lst.append(DEBUG_PYENV_INSTALL_OPTS)
            lst.append(PLATFORM_PYENV_INSTALL_OPTS[sys.platform].opts())
            opts = PyenvInstallOpts().merge(*lst)

        self._version = version
        self._opts = opts
        self._debug = debug
        self._pyenv = pyenv

    @property
    def version(self) -> str:
        return self._version

    @property
    def opts(self) -> PyenvInstallOpts:
        return self._opts

    @cached_nullary
    def install_name(self) -> str:
        return self._version + ('-debug' if self._debug else '')

    @cached_nullary
    def install_dir(self) -> str:
        return str(os.path.join(check_not_none(self._pyenv.root()), 'versions', self.install_name()))

    @cached_nullary
    def install(self) -> str:
        env = dict(self._opts.env)
        for k, l in [
            ('CFLAGS', self._opts.cflags),
            ('LDFLAGS', self._opts.ldflags),
            ('PYTHON_CONFIGURE_OPTS', self._opts.conf_opts),
        ]:
            v = ' '.join(l)
            if k in os.environ:
                v += ' ' + os.environ[k]
            env[k] = v

        subprocess_check_call(self._pyenv.exe(), 'install', *self._opts.opts, self._version, env=env)

        exe = os.path.join(self.install_dir(), 'bin', 'python')
        if not os.path.isfile(exe):
            raise RuntimeError(f'Interpreter not found: {exe}')
        return exe


##


class PyenvInterpProvider(InterpProvider):

    def __init__(
            self,
            pyenv: Pyenv = Pyenv(),

            inspect: bool = False,
            inspector: InterpInspector = INTERP_INSPECTOR,
    ) -> None:
        super().__init__()

        self._pyenv = pyenv

        self._inspect = inspect
        self._inspector = inspector

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

    def _make_installed(self, vn: str, ep: str) -> ta.Optional[Installed]:
        iv: ta.Optional[InterpVersion]
        if self._inspect:
            try:
                iv = check_not_none(self._inspector.inspect(ep)).iv
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

    def installed(self) -> ta.Sequence[Installed]:
        ret: ta.List[PyenvInterpProvider.Installed] = []
        for vn, ep in self._pyenv.version_exes():
            if (i := self._make_installed(vn, ep)) is None:
                log.debug('Invalid pyenv version: %s', vn)
                continue
            ret.append(i)
        return ret

    #

    def get_installed_versions(self, spec: InterpSpecifier) -> ta.Sequence[InterpVersion]:
        return [i.version for i in self.installed()]

    def get_installed_version(self, version: InterpVersion) -> Interp:
        for i in self.installed():
            if i.version == version:
                return Interp(
                    exe=i.exe,
                    version=i.version,
                )
        raise KeyError(version)

    #

    def get_installable_versions(self, spec: InterpSpecifier) -> ta.Sequence[InterpVersion]:
        lst = []
        for vs in self._pyenv.installable_versions():
            if (iv := self.guess_version(vs)) is None:
                continue
            if iv.opts.debug:
                raise Exception('Pyenv installable versions not expected to have debug suffix')
            for d in [False, True]:
                lst.append(dc.replace(iv, opts=dc.replace(iv.opts, debug=d)))
        return lst


########################################
# ../system.py
"""
TODO:
 - python, python3, python3.12, ...
 - check if path py's are venvs: sys.prefix != sys.base_prefix
"""
# ruff: noqa: UP006 UP007


##


@dc.dataclass(frozen=True)
class SystemInterpProvider(InterpProvider):
    cmd: str = 'python3'
    path: ta.Optional[str] = None

    inspect: bool = False
    inspector: InterpInspector = INTERP_INSPECTOR

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
            path=self.path,
        )

    #

    def get_exe_version(self, exe: str) -> ta.Optional[InterpVersion]:
        if not self.inspect:
            s = os.path.basename(exe)
            if s.startswith('python'):
                s = s[len('python'):]
            if '.' in s:
                try:
                    return InterpVersion.parse(s)
                except InvalidVersion:
                    pass
        ii = self.inspector.inspect(exe)
        return ii.iv if ii is not None else None

    def exe_versions(self) -> ta.Sequence[ta.Tuple[str, InterpVersion]]:
        lst = []
        for e in self.exes():
            if (ev := self.get_exe_version(e)) is None:
                log.debug('Invalid system version: %s', e)
                continue
            lst.append((e, ev))
        return lst

    #

    def get_installed_versions(self, spec: InterpSpecifier) -> ta.Sequence[InterpVersion]:
        return [ev for e, ev in self.exe_versions()]

    def get_installed_version(self, version: InterpVersion) -> Interp:
        for e, ev in self.exe_versions():
            if ev != version:
                continue
            return Interp(
                exe=e,
                version=ev,
            )
        raise KeyError(version)


########################################
# ../resolvers.py
# ruff: noqa: UP006


INTERP_PROVIDER_TYPES_BY_NAME: ta.Mapping[str, ta.Type[InterpProvider]] = {
    cls.name: cls for cls in deep_subclasses(InterpProvider) if abc.ABC not in cls.__bases__  # type: ignore
}


class InterpResolver:
    def __init__(
            self,
            providers: ta.Sequence[ta.Tuple[str, InterpProvider]],
    ) -> None:
        super().__init__()
        self._providers: ta.Mapping[str, InterpProvider] = collections.OrderedDict(providers)

    def resolve(self, spec: InterpSpecifier) -> Interp:
        lst = [
            (i, si)
            for i, p in enumerate(self._providers.values())
            for si in p.get_installed_versions(spec)
            if spec.contains(si)
        ]
        best = sorted(lst, key=lambda t: (-t[0], t[1]))[-1]
        bi, bv = best
        bp = list(self._providers.values())[bi]
        return bp.get_installed_version(bv)

    def list(self, spec: InterpSpecifier) -> None:
        print('installed:')
        for n, p in self._providers.items():
            lst = [
                si
                for si in p.get_installed_versions(spec)
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
                for si in p.get_installable_versions(spec)
                if spec.contains(si)
            ]
            if lst:
                print(f'  {n}')
                for si in lst:
                    print(f'    {si}')


DEFAULT_INTERP_RESOLVER = InterpResolver([(p.name, p) for p in [
    # pyenv is preferred to system interpreters as it tends to have more support for things like tkinter
    PyenvInterpProvider(),

    RunningInterpProvider(),

    SystemInterpProvider(),
]])


########################################
# cli.py


def _list_cmd(args) -> None:
    r = DEFAULT_INTERP_RESOLVER
    s = InterpSpecifier.parse(args.version)
    r.list(s)


def _resolve_cmd(args) -> None:
    r = DEFAULT_INTERP_RESOLVER
    s = InterpSpecifier.parse(args.version)
    print(r.resolve(s).exe)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()

    subparsers = parser.add_subparsers()

    parser_list = subparsers.add_parser('list')
    parser_list.add_argument('version')
    parser_list.add_argument('--debug', action='store_true')
    parser_list.set_defaults(func=_list_cmd)

    parser_resolve = subparsers.add_parser('resolve')
    parser_resolve.add_argument('version')
    parser_resolve.add_argument('--debug', action='store_true')
    parser_resolve.set_defaults(func=_resolve_cmd)

    return parser


def _main(argv: ta.Optional[ta.Sequence[str]] = None) -> None:
    check_runtime_version()
    configure_standard_logging()

    parser = _build_parser()
    args = parser.parse_args(argv)
    if not getattr(args, 'func', None):
        parser.print_help()
    else:
        args.func(args)


if __name__ == '__main__':
    _main()
