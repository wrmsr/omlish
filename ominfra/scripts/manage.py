#!/usr/bin/env python3
# noinspection DuplicatedCode
# @omlish-lite
# @omlish-script
# @omlish-amalg-output ../manage/main.py
# ruff: noqa: N802 TC003 UP006 UP007 UP036
"""
manage.py -s 'docker run -i python:3.12'
manage.py -s 'ssh -i /foo/bar.pem foo@bar.baz' -q --python=python3.8
"""
import abc
import argparse
import asyncio
import asyncio.base_subprocess
import asyncio.subprocess
import base64
import collections
import collections.abc
import contextlib
import ctypes as ct
import dataclasses as dc
import datetime
import decimal
import enum
import fractions
import functools
import hashlib
import inspect
import io
import itertools
import json
import logging
import os
import os.path
import platform
import pwd
import re
import shlex
import shutil
import signal
import site
import string
import struct
import subprocess
import sys
import tempfile
import threading
import time
import traceback
import types
import typing as ta
import uuid
import weakref  # noqa
import zlib


########################################


if sys.version_info < (3, 8):
    raise OSError(f'Requires python (3, 8), got {sys.version_info} from {sys.executable}')  # noqa


########################################


# ../../omdev/packaging/versions.py
VersionLocalType = ta.Tuple[ta.Union[int, str], ...]
VersionCmpPrePostDevType = ta.Union['InfinityVersionType', 'NegativeInfinityVersionType', ta.Tuple[str, int]]
_VersionCmpLocalType0 = ta.Tuple[ta.Union[ta.Tuple[int, str], ta.Tuple['NegativeInfinityVersionType', ta.Union[int, str]]], ...]  # noqa
VersionCmpLocalType = ta.Union['NegativeInfinityVersionType', _VersionCmpLocalType0]
VersionCmpKey = ta.Tuple[int, ta.Tuple[int, ...], VersionCmpPrePostDevType, VersionCmpPrePostDevType, VersionCmpPrePostDevType, VersionCmpLocalType]  # noqa
VersionComparisonMethod = ta.Callable[[VersionCmpKey, VersionCmpKey], bool]

# ../../omdev/toml/parser.py
TomlParseFloat = ta.Callable[[str], ta.Any]
TomlKey = ta.Tuple[str, ...]
TomlPos = int  # ta.TypeAlias

# deploy/paths/types.py
DeployPathKind = ta.Literal['dir', 'file']  # ta.TypeAlias

# ../../omlish/asyncs/asyncio/timeouts.py
AwaitableT = ta.TypeVar('AwaitableT', bound=ta.Awaitable)

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

# ../../omlish/lite/typing.py
A0 = ta.TypeVar('A0')
A1 = ta.TypeVar('A1')
A2 = ta.TypeVar('A2')

# ../../omdev/packaging/specifiers.py
UnparsedVersion = ta.Union['Version', str]
UnparsedVersionVar = ta.TypeVar('UnparsedVersionVar', bound=UnparsedVersion)
CallableVersionOperator = ta.Callable[['Version', str], bool]

# commands/base.py
CommandT = ta.TypeVar('CommandT', bound='Command')
CommandOutputT = ta.TypeVar('CommandOutputT', bound='Command.Output')

# ../../omlish/argparse/cli.py
ArgparseCommandFn = ta.Callable[[], ta.Optional[int]]  # ta.TypeAlias

# ../../omlish/lite/contextmanagers.py
ExitStackedT = ta.TypeVar('ExitStackedT', bound='ExitStacked')

# ../../omlish/lite/inject.py
U = ta.TypeVar('U')
InjectorKeyCls = ta.Union[type, ta.NewType]
InjectorProviderFn = ta.Callable[['Injector'], ta.Any]
InjectorProviderFnMap = ta.Mapping['InjectorKey', 'InjectorProviderFn']
InjectorBindingOrBindings = ta.Union['InjectorBinding', 'InjectorBindings']

# ../../omlish/os/atomics.py
AtomicPathSwapKind = ta.Literal['dir', 'file']
AtomicPathSwapState = ta.Literal['open', 'committed', 'aborted']  # ta.TypeAlias

# ../configs.py
ConfigMapping = ta.Mapping[str, ta.Any]

# ../../omlish/subprocesses.py
SubprocessChannelOption = ta.Literal['pipe', 'stdout', 'devnull']  # ta.TypeAlias

# deploy/specs.py
KeyDeployTagT = ta.TypeVar('KeyDeployTagT', bound='KeyDeployTag')

# system/packages.py
SystemPackageOrStr = ta.Union['SystemPackage', str]


########################################
# ../../../omdev/packaging/versions.py
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
# ../../../omdev/toml/parser.py
# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2021 Taneli Hukkinen
# Licensed to PSF under a Contributor Agreement.
#
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
# 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023 Python Software Foundation; All
# Rights Reserved" are retained in Python alone or in any derivative version prepared by Licensee.
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
#
# https://github.com/python/cpython/blob/9ce90206b7a4649600218cf0bd4826db79c9a312/Lib/tomllib/_parser.py


##


_TOML_TIME_RE_STR = r'([01][0-9]|2[0-3]):([0-5][0-9]):([0-5][0-9])(?:\.([0-9]{1,6})[0-9]*)?'

TOML_RE_NUMBER = re.compile(
    r"""
0
(?:
    x[0-9A-Fa-f](?:_?[0-9A-Fa-f])*   # hex
    |
    b[01](?:_?[01])*                 # bin
    |
    o[0-7](?:_?[0-7])*               # oct
)
|
[+-]?(?:0|[1-9](?:_?[0-9])*)         # dec, integer part
(?P<floatpart>
    (?:\.[0-9](?:_?[0-9])*)?         # optional fractional part
    (?:[eE][+-]?[0-9](?:_?[0-9])*)?  # optional exponent part
)
""",
    flags=re.VERBOSE,
)
TOML_RE_LOCALTIME = re.compile(_TOML_TIME_RE_STR)
TOML_RE_DATETIME = re.compile(
    rf"""
([0-9]{{4}})-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])  # date, e.g. 1988-10-27
(?:
    [Tt ]
    {_TOML_TIME_RE_STR}
    (?:([Zz])|([+-])([01][0-9]|2[0-3]):([0-5][0-9]))?  # optional time offset
)?
""",
    flags=re.VERBOSE,
)


def toml_match_to_datetime(match: re.Match) -> ta.Union[datetime.datetime, datetime.date]:
    """Convert a `RE_DATETIME` match to `datetime.datetime` or `datetime.date`.

    Raises ValueError if the match does not correspond to a valid date or datetime.
    """
    (
        year_str,
        month_str,
        day_str,
        hour_str,
        minute_str,
        sec_str,
        micros_str,
        zulu_time,
        offset_sign_str,
        offset_hour_str,
        offset_minute_str,
    ) = match.groups()
    year, month, day = int(year_str), int(month_str), int(day_str)
    if hour_str is None:
        return datetime.date(year, month, day)
    hour, minute, sec = int(hour_str), int(minute_str), int(sec_str)
    micros = int(micros_str.ljust(6, '0')) if micros_str else 0
    if offset_sign_str:
        tz: ta.Optional[datetime.tzinfo] = toml_cached_tz(
            offset_hour_str, offset_minute_str, offset_sign_str,
        )
    elif zulu_time:
        tz = datetime.UTC
    else:  # local date-time
        tz = None
    return datetime.datetime(year, month, day, hour, minute, sec, micros, tzinfo=tz)


@functools.lru_cache()  # noqa
def toml_cached_tz(hour_str: str, minute_str: str, sign_str: str) -> datetime.timezone:
    sign = 1 if sign_str == '+' else -1
    return datetime.timezone(
        datetime.timedelta(
            hours=sign * int(hour_str),
            minutes=sign * int(minute_str),
        ),
    )


def toml_match_to_localtime(match: re.Match) -> datetime.time:
    hour_str, minute_str, sec_str, micros_str = match.groups()
    micros = int(micros_str.ljust(6, '0')) if micros_str else 0
    return datetime.time(int(hour_str), int(minute_str), int(sec_str), micros)


def toml_match_to_number(match: re.Match, parse_float: TomlParseFloat) -> ta.Any:
    if match.group('floatpart'):
        return parse_float(match.group())
    return int(match.group(), 0)


TOML_ASCII_CTRL = frozenset(chr(i) for i in range(32)) | frozenset(chr(127))

# Neither of these sets include quotation mark or backslash. They are currently handled as separate cases in the parser
# functions.
TOML_ILLEGAL_BASIC_STR_CHARS = TOML_ASCII_CTRL - frozenset('\t')
TOML_ILLEGAL_MULTILINE_BASIC_STR_CHARS = TOML_ASCII_CTRL - frozenset('\t\n')

TOML_ILLEGAL_LITERAL_STR_CHARS = TOML_ILLEGAL_BASIC_STR_CHARS
TOML_ILLEGAL_MULTILINE_LITERAL_STR_CHARS = TOML_ILLEGAL_MULTILINE_BASIC_STR_CHARS

TOML_ILLEGAL_COMMENT_CHARS = TOML_ILLEGAL_BASIC_STR_CHARS

TOML_WS = frozenset(' \t')
TOML_WS_AND_NEWLINE = TOML_WS | frozenset('\n')
TOML_BARE_KEY_CHARS = frozenset(string.ascii_letters + string.digits + '-_')
TOML_KEY_INITIAL_CHARS = TOML_BARE_KEY_CHARS | frozenset("\"'")
TOML_HEXDIGIT_CHARS = frozenset(string.hexdigits)

TOML_BASIC_STR_ESCAPE_REPLACEMENTS = types.MappingProxyType(
    {
        '\\b': '\u0008',  # backspace
        '\\t': '\u0009',  # tab
        '\\n': '\u000A',  # linefeed
        '\\f': '\u000C',  # form feed
        '\\r': '\u000D',  # carriage return
        '\\"': '\u0022',  # quote
        '\\\\': '\u005C',  # backslash
    },
)


class TomlDecodeError(ValueError):
    """An error raised if a document is not valid TOML."""


def toml_load(fp: ta.BinaryIO, /, *, parse_float: TomlParseFloat = float) -> ta.Dict[str, ta.Any]:
    """Parse TOML from a binary file object."""
    b = fp.read()
    try:
        s = b.decode()
    except AttributeError:
        raise TypeError("File must be opened in binary mode, e.g. use `open('foo.toml', 'rb')`") from None
    return toml_loads(s, parse_float=parse_float)


def toml_loads(s: str, /, *, parse_float: TomlParseFloat = float) -> ta.Dict[str, ta.Any]:  # noqa: C901
    """Parse TOML from a string."""

    # The spec allows converting "\r\n" to "\n", even in string literals. Let's do so to simplify parsing.
    try:
        src = s.replace('\r\n', '\n')
    except (AttributeError, TypeError):
        raise TypeError(f"Expected str object, not '{type(s).__qualname__}'") from None
    pos = 0
    out = TomlOutput(TomlNestedDict(), TomlFlags())
    header: TomlKey = ()
    parse_float = toml_make_safe_parse_float(parse_float)

    # Parse one statement at a time (typically means one line in TOML source)
    while True:
        # 1. Skip line leading whitespace
        pos = toml_skip_chars(src, pos, TOML_WS)

        # 2. Parse rules. Expect one of the following:
        #    - end of file
        #    - end of line
        #    - comment
        #    - key/value pair
        #    - append dict to list (and move to its namespace)
        #    - create dict (and move to its namespace)
        # Skip trailing whitespace when applicable.
        try:
            char = src[pos]
        except IndexError:
            break
        if char == '\n':
            pos += 1
            continue
        if char in TOML_KEY_INITIAL_CHARS:
            pos = toml_key_value_rule(src, pos, out, header, parse_float)
            pos = toml_skip_chars(src, pos, TOML_WS)
        elif char == '[':
            try:
                second_char: ta.Optional[str] = src[pos + 1]
            except IndexError:
                second_char = None
            out.flags.finalize_pending()
            if second_char == '[':
                pos, header = toml_create_list_rule(src, pos, out)
            else:
                pos, header = toml_create_dict_rule(src, pos, out)
            pos = toml_skip_chars(src, pos, TOML_WS)
        elif char != '#':
            raise toml_suffixed_err(src, pos, 'Invalid statement')

        # 3. Skip comment
        pos = toml_skip_comment(src, pos)

        # 4. Expect end of line or end of file
        try:
            char = src[pos]
        except IndexError:
            break
        if char != '\n':
            raise toml_suffixed_err(
                src, pos, 'Expected newline or end of document after a statement',
            )
        pos += 1

    return out.data.dict


class TomlFlags:
    """Flags that map to parsed keys/namespaces."""

    # Marks an immutable namespace (inline array or inline table).
    FROZEN = 0
    # Marks a nest that has been explicitly created and can no longer be opened using the "[table]" syntax.
    EXPLICIT_NEST = 1

    def __init__(self) -> None:
        self._flags: ta.Dict[str, dict] = {}
        self._pending_flags: ta.Set[ta.Tuple[TomlKey, int]] = set()

    def add_pending(self, key: TomlKey, flag: int) -> None:
        self._pending_flags.add((key, flag))

    def finalize_pending(self) -> None:
        for key, flag in self._pending_flags:
            self.set(key, flag, recursive=False)
        self._pending_flags.clear()

    def unset_all(self, key: TomlKey) -> None:
        cont = self._flags
        for k in key[:-1]:
            if k not in cont:
                return
            cont = cont[k]['nested']
        cont.pop(key[-1], None)

    def set(self, key: TomlKey, flag: int, *, recursive: bool) -> None:  # noqa: A003
        cont = self._flags
        key_parent, key_stem = key[:-1], key[-1]
        for k in key_parent:
            if k not in cont:
                cont[k] = {'flags': set(), 'recursive_flags': set(), 'nested': {}}
            cont = cont[k]['nested']
        if key_stem not in cont:
            cont[key_stem] = {'flags': set(), 'recursive_flags': set(), 'nested': {}}
        cont[key_stem]['recursive_flags' if recursive else 'flags'].add(flag)

    def is_(self, key: TomlKey, flag: int) -> bool:
        if not key:
            return False  # document root has no flags
        cont = self._flags
        for k in key[:-1]:
            if k not in cont:
                return False
            inner_cont = cont[k]
            if flag in inner_cont['recursive_flags']:
                return True
            cont = inner_cont['nested']
        key_stem = key[-1]
        if key_stem in cont:
            cont = cont[key_stem]
            return flag in cont['flags'] or flag in cont['recursive_flags']
        return False


class TomlNestedDict:
    def __init__(self) -> None:
        # The parsed content of the TOML document
        self.dict: ta.Dict[str, ta.Any] = {}

    def get_or_create_nest(
            self,
            key: TomlKey,
            *,
            access_lists: bool = True,
    ) -> dict:
        cont: ta.Any = self.dict
        for k in key:
            if k not in cont:
                cont[k] = {}
            cont = cont[k]
            if access_lists and isinstance(cont, list):
                cont = cont[-1]
            if not isinstance(cont, dict):
                raise KeyError('There is no nest behind this key')
        return cont

    def append_nest_to_list(self, key: TomlKey) -> None:
        cont = self.get_or_create_nest(key[:-1])
        last_key = key[-1]
        if last_key in cont:
            list_ = cont[last_key]
            if not isinstance(list_, list):
                raise KeyError('An object other than list found behind this key')
            list_.append({})
        else:
            cont[last_key] = [{}]


class TomlOutput(ta.NamedTuple):
    data: TomlNestedDict
    flags: TomlFlags


def toml_skip_chars(src: str, pos: TomlPos, chars: ta.Iterable[str]) -> TomlPos:
    try:
        while src[pos] in chars:
            pos += 1
    except IndexError:
        pass
    return pos


def toml_skip_until(
        src: str,
        pos: TomlPos,
        expect: str,
        *,
        error_on: ta.FrozenSet[str],
        error_on_eof: bool,
) -> TomlPos:
    try:
        new_pos = src.index(expect, pos)
    except ValueError:
        new_pos = len(src)
        if error_on_eof:
            raise toml_suffixed_err(src, new_pos, f'Expected {expect!r}') from None

    if not error_on.isdisjoint(src[pos:new_pos]):
        while src[pos] not in error_on:
            pos += 1
        raise toml_suffixed_err(src, pos, f'Found invalid character {src[pos]!r}')
    return new_pos


def toml_skip_comment(src: str, pos: TomlPos) -> TomlPos:
    try:
        char: ta.Optional[str] = src[pos]
    except IndexError:
        char = None
    if char == '#':
        return toml_skip_until(
            src, pos + 1, '\n', error_on=TOML_ILLEGAL_COMMENT_CHARS, error_on_eof=False,
        )
    return pos


def toml_skip_comments_and_array_ws(src: str, pos: TomlPos) -> TomlPos:
    while True:
        pos_before_skip = pos
        pos = toml_skip_chars(src, pos, TOML_WS_AND_NEWLINE)
        pos = toml_skip_comment(src, pos)
        if pos == pos_before_skip:
            return pos


def toml_create_dict_rule(src: str, pos: TomlPos, out: TomlOutput) -> ta.Tuple[TomlPos, TomlKey]:
    pos += 1  # Skip "["
    pos = toml_skip_chars(src, pos, TOML_WS)
    pos, key = toml_parse_key(src, pos)

    if out.flags.is_(key, TomlFlags.EXPLICIT_NEST) or out.flags.is_(key, TomlFlags.FROZEN):
        raise toml_suffixed_err(src, pos, f'Cannot declare {key} twice')
    out.flags.set(key, TomlFlags.EXPLICIT_NEST, recursive=False)
    try:
        out.data.get_or_create_nest(key)
    except KeyError:
        raise toml_suffixed_err(src, pos, 'Cannot overwrite a value') from None

    if not src.startswith(']', pos):
        raise toml_suffixed_err(src, pos, "Expected ']' at the end of a table declaration")
    return pos + 1, key


def toml_create_list_rule(src: str, pos: TomlPos, out: TomlOutput) -> ta.Tuple[TomlPos, TomlKey]:
    pos += 2  # Skip "[["
    pos = toml_skip_chars(src, pos, TOML_WS)
    pos, key = toml_parse_key(src, pos)

    if out.flags.is_(key, TomlFlags.FROZEN):
        raise toml_suffixed_err(src, pos, f'Cannot mutate immutable namespace {key}')
    # Free the namespace now that it points to another empty list item...
    out.flags.unset_all(key)
    # ...but this key precisely is still prohibited from table declaration
    out.flags.set(key, TomlFlags.EXPLICIT_NEST, recursive=False)
    try:
        out.data.append_nest_to_list(key)
    except KeyError:
        raise toml_suffixed_err(src, pos, 'Cannot overwrite a value') from None

    if not src.startswith(']]', pos):
        raise toml_suffixed_err(src, pos, "Expected ']]' at the end of an array declaration")
    return pos + 2, key


def toml_key_value_rule(
        src: str,
        pos: TomlPos,
        out: TomlOutput,
        header: TomlKey,
        parse_float: TomlParseFloat,
) -> TomlPos:
    pos, key, value = toml_parse_key_value_pair(src, pos, parse_float)
    key_parent, key_stem = key[:-1], key[-1]
    abs_key_parent = header + key_parent

    relative_path_cont_keys = (header + key[:i] for i in range(1, len(key)))
    for cont_key in relative_path_cont_keys:
        # Check that dotted key syntax does not redefine an existing table
        if out.flags.is_(cont_key, TomlFlags.EXPLICIT_NEST):
            raise toml_suffixed_err(src, pos, f'Cannot redefine namespace {cont_key}')
        # Containers in the relative path can't be opened with the table syntax or dotted key/value syntax in following
        # table sections.
        out.flags.add_pending(cont_key, TomlFlags.EXPLICIT_NEST)

    if out.flags.is_(abs_key_parent, TomlFlags.FROZEN):
        raise toml_suffixed_err(
            src,
            pos,
            f'Cannot mutate immutable namespace {abs_key_parent}',
        )

    try:
        nest = out.data.get_or_create_nest(abs_key_parent)
    except KeyError:
        raise toml_suffixed_err(src, pos, 'Cannot overwrite a value') from None
    if key_stem in nest:
        raise toml_suffixed_err(src, pos, 'Cannot overwrite a value')
    # Mark inline table and array namespaces recursively immutable
    if isinstance(value, (dict, list)):
        out.flags.set(header + key, TomlFlags.FROZEN, recursive=True)
    nest[key_stem] = value
    return pos


def toml_parse_key_value_pair(
        src: str,
        pos: TomlPos,
        parse_float: TomlParseFloat,
) -> ta.Tuple[TomlPos, TomlKey, ta.Any]:
    pos, key = toml_parse_key(src, pos)
    try:
        char: ta.Optional[str] = src[pos]
    except IndexError:
        char = None
    if char != '=':
        raise toml_suffixed_err(src, pos, "Expected '=' after a key in a key/value pair")
    pos += 1
    pos = toml_skip_chars(src, pos, TOML_WS)
    pos, value = toml_parse_value(src, pos, parse_float)
    return pos, key, value


def toml_parse_key(src: str, pos: TomlPos) -> ta.Tuple[TomlPos, TomlKey]:
    pos, key_part = toml_parse_key_part(src, pos)
    key: TomlKey = (key_part,)
    pos = toml_skip_chars(src, pos, TOML_WS)
    while True:
        try:
            char: ta.Optional[str] = src[pos]
        except IndexError:
            char = None
        if char != '.':
            return pos, key
        pos += 1
        pos = toml_skip_chars(src, pos, TOML_WS)
        pos, key_part = toml_parse_key_part(src, pos)
        key += (key_part,)
        pos = toml_skip_chars(src, pos, TOML_WS)


def toml_parse_key_part(src: str, pos: TomlPos) -> ta.Tuple[TomlPos, str]:
    try:
        char: ta.Optional[str] = src[pos]
    except IndexError:
        char = None
    if char in TOML_BARE_KEY_CHARS:
        start_pos = pos
        pos = toml_skip_chars(src, pos, TOML_BARE_KEY_CHARS)
        return pos, src[start_pos:pos]
    if char == "'":
        return toml_parse_literal_str(src, pos)
    if char == '"':
        return toml_parse_one_line_basic_str(src, pos)
    raise toml_suffixed_err(src, pos, 'Invalid initial character for a key part')


def toml_parse_one_line_basic_str(src: str, pos: TomlPos) -> ta.Tuple[TomlPos, str]:
    pos += 1
    return toml_parse_basic_str(src, pos, multiline=False)


def toml_parse_array(src: str, pos: TomlPos, parse_float: TomlParseFloat) -> ta.Tuple[TomlPos, list]:
    pos += 1
    array: list = []

    pos = toml_skip_comments_and_array_ws(src, pos)
    if src.startswith(']', pos):
        return pos + 1, array
    while True:
        pos, val = toml_parse_value(src, pos, parse_float)
        array.append(val)
        pos = toml_skip_comments_and_array_ws(src, pos)

        c = src[pos:pos + 1]
        if c == ']':
            return pos + 1, array
        if c != ',':
            raise toml_suffixed_err(src, pos, 'Unclosed array')
        pos += 1

        pos = toml_skip_comments_and_array_ws(src, pos)
        if src.startswith(']', pos):
            return pos + 1, array


def toml_parse_inline_table(src: str, pos: TomlPos, parse_float: TomlParseFloat) -> ta.Tuple[TomlPos, dict]:
    pos += 1
    nested_dict = TomlNestedDict()
    flags = TomlFlags()

    pos = toml_skip_chars(src, pos, TOML_WS)
    if src.startswith('}', pos):
        return pos + 1, nested_dict.dict
    while True:
        pos, key, value = toml_parse_key_value_pair(src, pos, parse_float)
        key_parent, key_stem = key[:-1], key[-1]
        if flags.is_(key, TomlFlags.FROZEN):
            raise toml_suffixed_err(src, pos, f'Cannot mutate immutable namespace {key}')
        try:
            nest = nested_dict.get_or_create_nest(key_parent, access_lists=False)
        except KeyError:
            raise toml_suffixed_err(src, pos, 'Cannot overwrite a value') from None
        if key_stem in nest:
            raise toml_suffixed_err(src, pos, f'Duplicate inline table key {key_stem!r}')
        nest[key_stem] = value
        pos = toml_skip_chars(src, pos, TOML_WS)
        c = src[pos:pos + 1]
        if c == '}':
            return pos + 1, nested_dict.dict
        if c != ',':
            raise toml_suffixed_err(src, pos, 'Unclosed inline table')
        if isinstance(value, (dict, list)):
            flags.set(key, TomlFlags.FROZEN, recursive=True)
        pos += 1
        pos = toml_skip_chars(src, pos, TOML_WS)


def toml_parse_basic_str_escape(
        src: str,
        pos: TomlPos,
        *,
        multiline: bool = False,
) -> ta.Tuple[TomlPos, str]:
    escape_id = src[pos:pos + 2]
    pos += 2
    if multiline and escape_id in {'\\ ', '\\\t', '\\\n'}:
        # Skip whitespace until next non-whitespace character or end of the doc. Error if non-whitespace is found before
        # newline.
        if escape_id != '\\\n':
            pos = toml_skip_chars(src, pos, TOML_WS)
            try:
                char = src[pos]
            except IndexError:
                return pos, ''
            if char != '\n':
                raise toml_suffixed_err(src, pos, "Unescaped '\\' in a string")
            pos += 1
        pos = toml_skip_chars(src, pos, TOML_WS_AND_NEWLINE)
        return pos, ''
    if escape_id == '\\u':
        return toml_parse_hex_char(src, pos, 4)
    if escape_id == '\\U':
        return toml_parse_hex_char(src, pos, 8)
    try:
        return pos, TOML_BASIC_STR_ESCAPE_REPLACEMENTS[escape_id]
    except KeyError:
        raise toml_suffixed_err(src, pos, "Unescaped '\\' in a string") from None


def toml_parse_basic_str_escape_multiline(src: str, pos: TomlPos) -> ta.Tuple[TomlPos, str]:
    return toml_parse_basic_str_escape(src, pos, multiline=True)


def toml_parse_hex_char(src: str, pos: TomlPos, hex_len: int) -> ta.Tuple[TomlPos, str]:
    hex_str = src[pos:pos + hex_len]
    if len(hex_str) != hex_len or not TOML_HEXDIGIT_CHARS.issuperset(hex_str):
        raise toml_suffixed_err(src, pos, 'Invalid hex value')
    pos += hex_len
    hex_int = int(hex_str, 16)
    if not toml_is_unicode_scalar_value(hex_int):
        raise toml_suffixed_err(src, pos, 'Escaped character is not a Unicode scalar value')
    return pos, chr(hex_int)


def toml_parse_literal_str(src: str, pos: TomlPos) -> ta.Tuple[TomlPos, str]:
    pos += 1  # Skip starting apostrophe
    start_pos = pos
    pos = toml_skip_until(
        src, pos, "'", error_on=TOML_ILLEGAL_LITERAL_STR_CHARS, error_on_eof=True,
    )
    return pos + 1, src[start_pos:pos]  # Skip ending apostrophe


def toml_parse_multiline_str(src: str, pos: TomlPos, *, literal: bool) -> ta.Tuple[TomlPos, str]:
    pos += 3
    if src.startswith('\n', pos):
        pos += 1

    if literal:
        delim = "'"
        end_pos = toml_skip_until(
            src,
            pos,
            "'''",
            error_on=TOML_ILLEGAL_MULTILINE_LITERAL_STR_CHARS,
            error_on_eof=True,
        )
        result = src[pos:end_pos]
        pos = end_pos + 3
    else:
        delim = '"'
        pos, result = toml_parse_basic_str(src, pos, multiline=True)

    # Add at maximum two extra apostrophes/quotes if the end sequence is 4 or 5 chars long instead of just 3.
    if not src.startswith(delim, pos):
        return pos, result
    pos += 1
    if not src.startswith(delim, pos):
        return pos, result + delim
    pos += 1
    return pos, result + (delim * 2)


def toml_parse_basic_str(src: str, pos: TomlPos, *, multiline: bool) -> ta.Tuple[TomlPos, str]:
    if multiline:
        error_on = TOML_ILLEGAL_MULTILINE_BASIC_STR_CHARS
        parse_escapes = toml_parse_basic_str_escape_multiline
    else:
        error_on = TOML_ILLEGAL_BASIC_STR_CHARS
        parse_escapes = toml_parse_basic_str_escape
    result = ''
    start_pos = pos
    while True:
        try:
            char = src[pos]
        except IndexError:
            raise toml_suffixed_err(src, pos, 'Unterminated string') from None
        if char == '"':
            if not multiline:
                return pos + 1, result + src[start_pos:pos]
            if src.startswith('"""', pos):
                return pos + 3, result + src[start_pos:pos]
            pos += 1
            continue
        if char == '\\':
            result += src[start_pos:pos]
            pos, parsed_escape = parse_escapes(src, pos)
            result += parsed_escape
            start_pos = pos
            continue
        if char in error_on:
            raise toml_suffixed_err(src, pos, f'Illegal character {char!r}')
        pos += 1


def toml_parse_value(  # noqa: C901
        src: str,
        pos: TomlPos,
        parse_float: TomlParseFloat,
) -> ta.Tuple[TomlPos, ta.Any]:
    try:
        char: ta.Optional[str] = src[pos]
    except IndexError:
        char = None

    # IMPORTANT: order conditions based on speed of checking and likelihood

    # Basic strings
    if char == '"':
        if src.startswith('"""', pos):
            return toml_parse_multiline_str(src, pos, literal=False)
        return toml_parse_one_line_basic_str(src, pos)

    # Literal strings
    if char == "'":
        if src.startswith("'''", pos):
            return toml_parse_multiline_str(src, pos, literal=True)
        return toml_parse_literal_str(src, pos)

    # Booleans
    if char == 't':
        if src.startswith('true', pos):
            return pos + 4, True
    if char == 'f':
        if src.startswith('false', pos):
            return pos + 5, False

    # Arrays
    if char == '[':
        return toml_parse_array(src, pos, parse_float)

    # Inline tables
    if char == '{':
        return toml_parse_inline_table(src, pos, parse_float)

    # Dates and times
    datetime_match = TOML_RE_DATETIME.match(src, pos)
    if datetime_match:
        try:
            datetime_obj = toml_match_to_datetime(datetime_match)
        except ValueError as e:
            raise toml_suffixed_err(src, pos, 'Invalid date or datetime') from e
        return datetime_match.end(), datetime_obj
    localtime_match = TOML_RE_LOCALTIME.match(src, pos)
    if localtime_match:
        return localtime_match.end(), toml_match_to_localtime(localtime_match)

    # Integers and "normal" floats. The regex will greedily match any type starting with a decimal char, so needs to be
    # located after handling of dates and times.
    number_match = TOML_RE_NUMBER.match(src, pos)
    if number_match:
        return number_match.end(), toml_match_to_number(number_match, parse_float)

    # Special floats
    first_three = src[pos:pos + 3]
    if first_three in {'inf', 'nan'}:
        return pos + 3, parse_float(first_three)
    first_four = src[pos:pos + 4]
    if first_four in {'-inf', '+inf', '-nan', '+nan'}:
        return pos + 4, parse_float(first_four)

    raise toml_suffixed_err(src, pos, 'Invalid value')


def toml_suffixed_err(src: str, pos: TomlPos, msg: str) -> TomlDecodeError:
    """Return a `TomlDecodeError` where error message is suffixed with coordinates in source."""

    def coord_repr(src: str, pos: TomlPos) -> str:
        if pos >= len(src):
            return 'end of document'
        line = src.count('\n', 0, pos) + 1
        if line == 1:
            column = pos + 1
        else:
            column = pos - src.rindex('\n', 0, pos)
        return f'line {line}, column {column}'

    return TomlDecodeError(f'{msg} (at {coord_repr(src, pos)})')


def toml_is_unicode_scalar_value(codepoint: int) -> bool:
    return (0 <= codepoint <= 55295) or (57344 <= codepoint <= 1114111)


def toml_make_safe_parse_float(parse_float: TomlParseFloat) -> TomlParseFloat:
    """A decorator to make `parse_float` safe.

    `parse_float` must not return dicts or lists, because these types would be mixed with parsed TOML tables and arrays,
    thus confusing the parser. The returned decorated callable raises `ValueError` instead of returning illegal types.
    """
    # The default `float` callable never returns illegal types. Optimize it.
    if parse_float is float:
        return float

    def safe_parse_float(float_str: str) -> ta.Any:
        float_value = parse_float(float_str)
        if isinstance(float_value, (dict, list)):
            raise ValueError('parse_float must not return dicts or lists')  # noqa
        return float_value

    return safe_parse_float


########################################
# ../config.py


@dc.dataclass(frozen=True)
class MainConfig:
    log_level: ta.Optional[str] = 'INFO'

    debug: bool = False


########################################
# ../deploy/config.py


##


@dc.dataclass(frozen=True)
class DeployConfig:
    pass


########################################
# ../deploy/paths/types.py


##


########################################
# ../deploy/types.py


##


DeployHome = ta.NewType('DeployHome', str)

DeployRev = ta.NewType('DeployRev', str)


########################################
# ../../pyremote.py
"""
Basically this: https://mitogen.networkgenomics.com/howitworks.html

TODO:
 - log: ta.Optional[logging.Logger] = None + log.debug's
"""


##


@dc.dataclass(frozen=True)
class PyremoteBootstrapOptions:
    debug: bool = False

    DEFAULT_MAIN_NAME_OVERRIDE: ta.ClassVar[str] = '__pyremote__'
    main_name_override: ta.Optional[str] = DEFAULT_MAIN_NAME_OVERRIDE


##


@dc.dataclass(frozen=True)
class PyremoteEnvInfo:
    sys_base_prefix: str
    sys_byteorder: str
    sys_defaultencoding: str
    sys_exec_prefix: str
    sys_executable: str
    sys_implementation_name: str
    sys_path: ta.List[str]
    sys_platform: str
    sys_prefix: str
    sys_version: str
    sys_version_info: ta.List[ta.Union[int, str]]

    platform_architecture: ta.List[str]
    platform_machine: str
    platform_platform: str
    platform_processor: str
    platform_system: str
    platform_release: str
    platform_version: str

    site_userbase: str

    os_cwd: str
    os_gid: int
    os_loadavg: ta.List[float]
    os_login: ta.Optional[str]
    os_pgrp: int
    os_pid: int
    os_ppid: int
    os_uid: int

    pw_name: str
    pw_uid: int
    pw_gid: int
    pw_gecos: str
    pw_dir: str
    pw_shell: str

    env_path: ta.Optional[str]


def _get_pyremote_env_info() -> PyremoteEnvInfo:
    os_uid = os.getuid()

    pw = pwd.getpwuid(os_uid)

    os_login: ta.Optional[str]
    try:
        os_login = os.getlogin()
    except OSError:
        os_login = None

    return PyremoteEnvInfo(
        sys_base_prefix=sys.base_prefix,
        sys_byteorder=sys.byteorder,
        sys_defaultencoding=sys.getdefaultencoding(),
        sys_exec_prefix=sys.exec_prefix,
        sys_executable=sys.executable,
        sys_implementation_name=sys.implementation.name,
        sys_path=sys.path,
        sys_platform=sys.platform,
        sys_prefix=sys.prefix,
        sys_version=sys.version,
        sys_version_info=list(sys.version_info),

        platform_architecture=list(platform.architecture()),
        platform_machine=platform.machine(),
        platform_platform=platform.platform(),
        platform_processor=platform.processor(),
        platform_system=platform.system(),
        platform_release=platform.release(),
        platform_version=platform.version(),

        site_userbase=site.getuserbase(),

        os_cwd=os.getcwd(),
        os_gid=os.getgid(),
        os_loadavg=list(os.getloadavg()),
        os_login=os_login,
        os_pgrp=os.getpgrp(),
        os_pid=os.getpid(),
        os_ppid=os.getppid(),
        os_uid=os_uid,

        pw_name=pw.pw_name,
        pw_uid=pw.pw_uid,
        pw_gid=pw.pw_gid,
        pw_gecos=pw.pw_gecos,
        pw_dir=pw.pw_dir,
        pw_shell=pw.pw_shell,

        env_path=os.environ.get('PATH'),
    )


##


_PYREMOTE_BOOTSTRAP_INPUT_FD = 100
_PYREMOTE_BOOTSTRAP_SRC_FD = 101

_PYREMOTE_BOOTSTRAP_CHILD_PID_VAR = '_OPYR_CHILD_PID'
_PYREMOTE_BOOTSTRAP_ARGV0_VAR = '_OPYR_ARGV0'
_PYREMOTE_BOOTSTRAP_CONTEXT_NAME_VAR = '_OPYR_CONTEXT_NAME'
_PYREMOTE_BOOTSTRAP_SRC_FILE_VAR = '_OPYR_SRC_FILE'
_PYREMOTE_BOOTSTRAP_OPTIONS_JSON_VAR = '_OPYR_OPTIONS_JSON'

_PYREMOTE_BOOTSTRAP_ACK0 = b'OPYR000\n'
_PYREMOTE_BOOTSTRAP_ACK1 = b'OPYR001\n'
_PYREMOTE_BOOTSTRAP_ACK2 = b'OPYR002\n'
_PYREMOTE_BOOTSTRAP_ACK3 = b'OPYR003\n'

_PYREMOTE_BOOTSTRAP_PROC_TITLE_FMT = '(pyremote:%s)'

_PYREMOTE_BOOTSTRAP_IMPORTS = [
    'base64',
    'os',
    'struct',
    'sys',
    'zlib',
]


def _pyremote_bootstrap_main(context_name: str) -> None:
    # Get pid
    pid = os.getpid()

    # Two copies of payload src to be sent to parent
    r0, w0 = os.pipe()
    r1, w1 = os.pipe()

    if (cp := os.fork()):
        # Parent process

        # Dup original stdin to comm_fd for use as comm channel
        os.dup2(0, _PYREMOTE_BOOTSTRAP_INPUT_FD)

        # Overwrite stdin (fed to python repl) with first copy of src
        os.dup2(r0, 0)

        # Dup second copy of src to src_fd to recover after launch
        os.dup2(r1, _PYREMOTE_BOOTSTRAP_SRC_FD)

        # Close remaining fd's
        for f in [r0, w0, r1, w1]:
            os.close(f)

        # Save vars
        env = os.environ
        exe = sys.executable
        env[_PYREMOTE_BOOTSTRAP_CHILD_PID_VAR] = str(cp)
        env[_PYREMOTE_BOOTSTRAP_ARGV0_VAR] = exe
        env[_PYREMOTE_BOOTSTRAP_CONTEXT_NAME_VAR] = context_name

        # Start repl reading stdin from r0
        os.execl(exe, exe + (_PYREMOTE_BOOTSTRAP_PROC_TITLE_FMT % (context_name,)))

    else:
        # Child process

        # Write first ack
        os.write(1, _PYREMOTE_BOOTSTRAP_ACK0)

        # Write pid
        os.write(1, struct.pack('<Q', pid))

        # Read payload src from stdin
        payload_z_len = struct.unpack('<I', os.read(0, 4))[0]
        if len(payload_z := os.fdopen(0, 'rb').read(payload_z_len)) != payload_z_len:
            raise EOFError
        payload_src = zlib.decompress(payload_z)

        # Write both copies of payload src. Must write to w0 (parent stdin) before w1 (copy pipe) as pipe will likely
        # fill and block and need to be drained by pyremote_bootstrap_finalize running in parent.
        for w in [w0, w1]:
            fp = os.fdopen(w, 'wb', 0)
            fp.write(payload_src)
            fp.close()

        # Write second ack
        os.write(1, _PYREMOTE_BOOTSTRAP_ACK1)

        # Exit child
        sys.exit(0)


##


def pyremote_build_bootstrap_cmd(context_name: str) -> str:
    if any(c in context_name for c in '\'"'):
        raise NameError(context_name)

    import inspect
    import textwrap
    bs_src = textwrap.dedent(inspect.getsource(_pyremote_bootstrap_main))

    for gl in [
        '_PYREMOTE_BOOTSTRAP_INPUT_FD',
        '_PYREMOTE_BOOTSTRAP_SRC_FD',

        '_PYREMOTE_BOOTSTRAP_CHILD_PID_VAR',
        '_PYREMOTE_BOOTSTRAP_ARGV0_VAR',
        '_PYREMOTE_BOOTSTRAP_CONTEXT_NAME_VAR',

        '_PYREMOTE_BOOTSTRAP_ACK0',
        '_PYREMOTE_BOOTSTRAP_ACK1',

        '_PYREMOTE_BOOTSTRAP_PROC_TITLE_FMT',
    ]:
        bs_src = bs_src.replace(gl, repr(globals()[gl]))

    bs_src = '\n'.join(
        cl
        for l in bs_src.splitlines()
        if (cl := (l.split('#')[0]).rstrip())
        if cl.strip()
    )

    bs_z = zlib.compress(bs_src.encode('utf-8'), 9)
    bs_z85 = base64.b85encode(bs_z).replace(b'\n', b'')
    if b'"' in bs_z85:
        raise ValueError(bs_z85)

    stmts = [
        f'import {", ".join(_PYREMOTE_BOOTSTRAP_IMPORTS)}',
        f'exec(zlib.decompress(base64.b85decode(b"{bs_z85.decode("ascii")}")))',
        f'_pyremote_bootstrap_main("{context_name}")',
    ]

    cmd = '; '.join(stmts)
    return cmd


##


@dc.dataclass(frozen=True)
class PyremotePayloadRuntime:
    input: ta.BinaryIO
    output: ta.BinaryIO
    context_name: str
    payload_src: str
    options: PyremoteBootstrapOptions
    env_info: PyremoteEnvInfo


def pyremote_bootstrap_finalize() -> PyremotePayloadRuntime:
    # If src file var is not present we need to do initial finalization
    if _PYREMOTE_BOOTSTRAP_SRC_FILE_VAR not in os.environ:
        # Read second copy of payload src
        r1 = os.fdopen(_PYREMOTE_BOOTSTRAP_SRC_FD, 'rb', 0)
        payload_src = r1.read().decode('utf-8')
        r1.close()

        # Reap boostrap child. Must be done after reading second copy of source because source may be too big to fit in
        # a pipe at once.
        os.waitpid(int(os.environ.pop(_PYREMOTE_BOOTSTRAP_CHILD_PID_VAR)), 0)

        # Read options
        options_json_len = struct.unpack('<I', os.read(_PYREMOTE_BOOTSTRAP_INPUT_FD, 4))[0]
        if len(options_json := os.read(_PYREMOTE_BOOTSTRAP_INPUT_FD, options_json_len)) != options_json_len:
            raise EOFError
        options = PyremoteBootstrapOptions(**json.loads(options_json.decode('utf-8')))

        # If debugging, re-exec as file
        if options.debug:
            # Write temp source file
            import tempfile
            tfd, tfn = tempfile.mkstemp('-pyremote.py')
            os.write(tfd, payload_src.encode('utf-8'))
            os.close(tfd)

            # Set vars
            os.environ[_PYREMOTE_BOOTSTRAP_SRC_FILE_VAR] = tfn
            os.environ[_PYREMOTE_BOOTSTRAP_OPTIONS_JSON_VAR] = options_json.decode('utf-8')

            # Re-exec temp file
            exe = os.environ[_PYREMOTE_BOOTSTRAP_ARGV0_VAR]
            context_name = os.environ[_PYREMOTE_BOOTSTRAP_CONTEXT_NAME_VAR]
            os.execl(exe, exe + (_PYREMOTE_BOOTSTRAP_PROC_TITLE_FMT % (context_name,)), tfn)

    else:
        # Load options json var
        options_json_str = os.environ.pop(_PYREMOTE_BOOTSTRAP_OPTIONS_JSON_VAR)
        options = PyremoteBootstrapOptions(**json.loads(options_json_str))

        # Read temp source file
        with open(os.environ.pop(_PYREMOTE_BOOTSTRAP_SRC_FILE_VAR)) as sf:
            payload_src = sf.read()

    # Restore vars
    sys.executable = os.environ.pop(_PYREMOTE_BOOTSTRAP_ARGV0_VAR)
    context_name = os.environ.pop(_PYREMOTE_BOOTSTRAP_CONTEXT_NAME_VAR)

    # Write third ack
    os.write(1, _PYREMOTE_BOOTSTRAP_ACK2)

    # Write env info
    env_info = _get_pyremote_env_info()
    env_info_json = json.dumps(dc.asdict(env_info), indent=None, separators=(',', ':'))  # noqa
    os.write(1, struct.pack('<I', len(env_info_json)))
    os.write(1, env_info_json.encode('utf-8'))

    # Setup IO
    input = os.fdopen(_PYREMOTE_BOOTSTRAP_INPUT_FD, 'rb', 0)  # noqa
    output = os.fdopen(os.dup(1), 'wb', 0)  # noqa
    os.dup2(nfd := os.open('/dev/null', os.O_WRONLY), 1)
    os.close(nfd)

    if (mn := options.main_name_override) is not None:
        # Inspections like typing.get_type_hints need an entry in sys.modules.
        sys.modules[mn] = sys.modules['__main__']

    # Write fourth ack
    output.write(_PYREMOTE_BOOTSTRAP_ACK3)

    # Return
    return PyremotePayloadRuntime(
        input=input,
        output=output,
        context_name=context_name,
        payload_src=payload_src,
        options=options,
        env_info=env_info,
    )


##


class PyremoteBootstrapDriver:
    def __init__(
            self,
            payload_src: ta.Union[str, ta.Sequence[str]],
            options: PyremoteBootstrapOptions = PyremoteBootstrapOptions(),
    ) -> None:
        super().__init__()

        self._payload_src = payload_src
        self._options = options

        self._prepared_payload_src = self._prepare_payload_src(payload_src, options)
        self._payload_z = zlib.compress(self._prepared_payload_src.encode('utf-8'))

        self._options_json = json.dumps(dc.asdict(options), indent=None, separators=(',', ':')).encode('utf-8')  # noqa
    #

    @classmethod
    def _prepare_payload_src(
            cls,
            payload_src: ta.Union[str, ta.Sequence[str]],
            options: PyremoteBootstrapOptions,
    ) -> str:
        parts: ta.List[str]
        if isinstance(payload_src, str):
            parts = [payload_src]
        else:
            parts = list(payload_src)

        if (mn := options.main_name_override) is not None:
            parts.insert(0, f'__name__ = {mn!r}')

        if len(parts) == 1:
            return parts[0]
        else:
            return '\n\n'.join(parts)

    #

    @dc.dataclass(frozen=True)
    class Read:
        sz: int

    @dc.dataclass(frozen=True)
    class Write:
        d: bytes

    class ProtocolError(Exception):
        pass

    @dc.dataclass(frozen=True)
    class Result:
        pid: int
        env_info: PyremoteEnvInfo

    def gen(self) -> ta.Generator[ta.Union[Read, Write], ta.Optional[bytes], Result]:
        # Read first ack (after fork)
        yield from self._expect(_PYREMOTE_BOOTSTRAP_ACK0)

        # Read pid
        d = yield from self._read(8)
        pid = struct.unpack('<Q', d)[0]

        # Write payload src
        yield from self._write(struct.pack('<I', len(self._payload_z)))
        yield from self._write(self._payload_z)

        # Read second ack (after writing src copies)
        yield from self._expect(_PYREMOTE_BOOTSTRAP_ACK1)

        # Write options
        yield from self._write(struct.pack('<I', len(self._options_json)))
        yield from self._write(self._options_json)

        # Read third ack (after reaping child process)
        yield from self._expect(_PYREMOTE_BOOTSTRAP_ACK2)

        # Read env info
        d = yield from self._read(4)
        env_info_json_len = struct.unpack('<I', d)[0]
        d = yield from self._read(env_info_json_len)
        env_info_json = d.decode('utf-8')
        env_info = PyremoteEnvInfo(**json.loads(env_info_json))

        # Read fourth ack (after finalization completed)
        yield from self._expect(_PYREMOTE_BOOTSTRAP_ACK3)

        # Return
        return self.Result(
            pid=pid,
            env_info=env_info,
        )

    def _read(self, sz: int) -> ta.Generator[Read, bytes, bytes]:
        d = yield self.Read(sz)
        if not isinstance(d, bytes):
            raise self.ProtocolError(f'Expected bytes after read, got {d!r}')
        if len(d) != sz:
            raise self.ProtocolError(f'Read {len(d)} bytes, expected {sz}')
        return d

    def _expect(self, e: bytes) -> ta.Generator[Read, bytes, None]:
        d = yield from self._read(len(e))
        if d != e:
            raise self.ProtocolError(f'Read {d!r}, expected {e!r}')

    def _write(self, d: bytes) -> ta.Generator[Write, ta.Optional[bytes], None]:
        i = yield self.Write(d)
        if i is not None:
            raise self.ProtocolError('Unexpected input after write')

    #

    def run(self, input: ta.IO, output: ta.IO) -> Result:  # noqa
        gen = self.gen()

        gi: ta.Optional[bytes] = None
        while True:
            try:
                if gi is not None:
                    go = gen.send(gi)
                else:
                    go = next(gen)
            except StopIteration as e:
                return e.value

            if isinstance(go, self.Read):
                if len(gi := input.read(go.sz)) != go.sz:
                    raise EOFError
            elif isinstance(go, self.Write):
                gi = None
                output.write(go.d)
                output.flush()
            else:
                raise TypeError(go)

    async def async_run(
            self,
            input: ta.Any,  # asyncio.StreamWriter  # noqa
            output: ta.Any,  # asyncio.StreamReader
    ) -> Result:
        gen = self.gen()

        gi: ta.Optional[bytes] = None
        while True:
            try:
                if gi is not None:
                    go = gen.send(gi)
                else:
                    go = next(gen)
            except StopIteration as e:
                return e.value

            if isinstance(go, self.Read):
                if len(gi := await input.read(go.sz)) != go.sz:
                    raise EOFError
            elif isinstance(go, self.Write):
                gi = None
                output.write(go.d)
                await output.drain()
            else:
                raise TypeError(go)


########################################
# ../../../omlish/asyncs/asyncio/channels.py


class AsyncioBytesChannelTransport(asyncio.Transport):
    def __init__(self, reader: asyncio.StreamReader) -> None:
        super().__init__()

        self.reader = reader
        self.closed: asyncio.Future = asyncio.Future()

    # @ta.override
    def write(self, data: bytes) -> None:
        self.reader.feed_data(data)

    # @ta.override
    def close(self) -> None:
        self.reader.feed_eof()
        if not self.closed.done():
            self.closed.set_result(True)

    # @ta.override
    def is_closing(self) -> bool:
        return self.closed.done()


def asyncio_create_bytes_channel(
        loop: ta.Any = None,
) -> ta.Tuple[asyncio.StreamReader, asyncio.StreamWriter]:
    if loop is None:
        loop = asyncio.get_running_loop()

    reader = asyncio.StreamReader()
    protocol = asyncio.StreamReaderProtocol(reader)
    transport = AsyncioBytesChannelTransport(reader)
    writer = asyncio.StreamWriter(transport, protocol, reader, loop)

    return reader, writer


########################################
# ../../../omlish/asyncs/asyncio/streams.py


ASYNCIO_DEFAULT_BUFFER_LIMIT = 2 ** 16


async def asyncio_open_stream_reader(
        f: ta.IO,
        loop: ta.Any = None,
        *,
        limit: int = ASYNCIO_DEFAULT_BUFFER_LIMIT,
) -> asyncio.StreamReader:
    if loop is None:
        loop = asyncio.get_running_loop()

    reader = asyncio.StreamReader(limit=limit, loop=loop)
    await loop.connect_read_pipe(
        lambda: asyncio.StreamReaderProtocol(reader, loop=loop),
        f,
    )

    return reader


async def asyncio_open_stream_writer(
        f: ta.IO,
        loop: ta.Any = None,
) -> asyncio.StreamWriter:
    if loop is None:
        loop = asyncio.get_running_loop()

    writer_transport, writer_protocol = await loop.connect_write_pipe(
        lambda: asyncio.streams.FlowControlMixin(loop=loop),
        f,
    )

    return asyncio.streams.StreamWriter(
        writer_transport,
        writer_protocol,
        None,
        loop,
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
# ../../../omlish/lite/pycharm.py


DEFAULT_PYCHARM_VERSION = '242.23726.102'


@dc.dataclass(frozen=True)
class PycharmRemoteDebug:
    port: int
    host: ta.Optional[str] = 'localhost'
    install_version: ta.Optional[str] = DEFAULT_PYCHARM_VERSION


def pycharm_debug_connect(prd: PycharmRemoteDebug) -> None:
    if prd.install_version is not None:
        import subprocess
        import sys
        subprocess.check_call([
            sys.executable,
            '-mpip',
            'install',
            f'pydevd-pycharm~={prd.install_version}',
        ])

    pydevd_pycharm = __import__('pydevd_pycharm')  # noqa
    pydevd_pycharm.settrace(
        prd.host,
        port=prd.port,
        stdoutToServer=True,
        stderrToServer=True,
    )


def pycharm_debug_preamble(prd: PycharmRemoteDebug) -> str:
    import inspect
    import textwrap
    return textwrap.dedent(f"""
        {inspect.getsource(pycharm_debug_connect)}

        pycharm_debug_connect(PycharmRemoteDebug(
            {prd.port!r},
            host={prd.host!r},
            install_version={prd.install_version!r},
        ))
    """)


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
# ../../../omlish/lite/resources.py


def read_package_resource_binary(package: str, resource: str) -> bytes:
    import importlib.resources
    return importlib.resources.read_binary(package, resource)


def read_package_resource_text(package: str, resource: str) -> str:
    import importlib.resources
    return importlib.resources.read_text(package, resource)


########################################
# ../../../omlish/lite/shlex.py


def shlex_needs_quote(s: str) -> bool:
    return bool(s) and len(list(shlex.shlex(s))) > 1


def shlex_maybe_quote(s: str) -> str:
    if shlex_needs_quote(s):
        return shlex.quote(s)
    else:
        return s


########################################
# ../../../omlish/lite/strings.py


##


def camel_case(name: str, lower: bool = False) -> str:
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
# ../../../omlish/lite/typing.py


##
# A workaround for typing deficiencies (like `Argument 2 to NewType(...) must be subclassable`).


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
# ../../../omlish/os/deathsig.py


LINUX_PR_SET_PDEATHSIG = 1  # Second arg is a signal
LINUX_PR_GET_PDEATHSIG = 2  # Second arg is a ptr to return the signal


def set_process_deathsig(sig: int) -> bool:
    if sys.platform == 'linux':
        libc = ct.CDLL('libc.so.6')

        # int prctl(int option, unsigned long arg2, unsigned long arg3, unsigned long arg4, unsigned long arg5);
        libc.prctl.restype = ct.c_int
        libc.prctl.argtypes = [ct.c_int, ct.c_ulong, ct.c_ulong, ct.c_ulong, ct.c_ulong]

        libc.prctl(LINUX_PR_SET_PDEATHSIG, sig, 0, 0, 0, 0)

        return True

    else:
        return False


########################################
# ../../../omlish/os/linux.py
"""
➜  ~ cat /etc/os-release
NAME="Amazon Linux"
VERSION="2"
ID="amzn"
ID_LIKE="centos rhel fedora"
VERSION_ID="2"
PRETTY_NAME="Amazon Linux 2"

➜  ~ cat /etc/os-release
PRETTY_NAME="Ubuntu 22.04.5 LTS"
NAME="Ubuntu"
VERSION_ID="22.04"
VERSION="22.04.5 LTS (Jammy Jellyfish)"
VERSION_CODENAME=jammy
ID=ubuntu
ID_LIKE=debian
UBUNTU_CODENAME=jammy

➜  omlish git:(master) docker run -i python:3.12 cat /etc/os-release
PRETTY_NAME="Debian GNU/Linux 12 (bookworm)"
NAME="Debian GNU/Linux"
VERSION_ID="12"
VERSION="12 (bookworm)"
VERSION_CODENAME=bookworm
ID=debian
"""


@dc.dataclass(frozen=True)
class LinuxOsRelease:
    """
    https://man7.org/linux/man-pages/man5/os-release.5.html
    """

    raw: ta.Mapping[str, str]

    # General information identifying the operating system

    @property
    def name(self) -> str:
        """
        A string identifying the operating system, without a version component, and suitable for presentation to the
        user. If not set, a default of "NAME=Linux" may be used.

        Examples: "NAME=Fedora", "NAME="Debian GNU/Linux"".
        """

        return self.raw['NAME']

    @property
    def id(self) -> str:
        """
        A lower-case string (no spaces or other characters outside of 0-9, a-z, ".", "_" and "-") identifying the
        operating system, excluding any version information and suitable for processing by scripts or usage in generated
        filenames. If not set, a default of "ID=linux" may be used. Note that even though this string may not include
        characters that require shell quoting, quoting may nevertheless be used.

        Examples: "ID=fedora", "ID=debian".
        """

        return self.raw['ID']

    @property
    def id_like(self) -> str:
        """
        A space-separated list of operating system identifiers in the same syntax as the ID= setting. It should list
        identifiers of operating systems that are closely related to the local operating system in regards to packaging
        and programming interfaces, for example listing one or more OS identifiers the local OS is a derivative from. An
        OS should generally only list other OS identifiers it itself is a derivative of, and not any OSes that are
        derived from it, though symmetric relationships are possible. Build scripts and similar should check this
        variable if they need to identify the local operating system and the value of ID= is not recognized. Operating
        systems should be listed in order of how closely the local operating system relates to the listed ones, starting
        with the closest. This field is optional.

        Examples: for an operating system with "ID=centos", an assignment of "ID_LIKE="rhel fedora"" would be
        appropriate. For an operating system with "ID=ubuntu", an assignment of "ID_LIKE=debian" is appropriate.
        """

        return self.raw['ID_LIKE']

    @property
    def pretty_name(self) -> str:
        """
        A pretty operating system name in a format suitable for presentation to the user. May or may not contain a
        release code name or OS version of some kind, as suitable. If not set, a default of "PRETTY_NAME="Linux"" may be
        used

        Example: "PRETTY_NAME="Fedora 17 (Beefy Miracle)"".
        """

        return self.raw['PRETTY_NAME']

    @property
    def cpe_name(self) -> str:
        """
        A CPE name for the operating system, in URI binding syntax, following the Common Platform Enumeration
        Specification[4] as proposed by the NIST. This field is optional.

        Example: "CPE_NAME="cpe:/o:fedoraproject:fedora:17""
        """

        return self.raw['CPE_NAME']

    @property
    def variant(self) -> str:
        """
        A string identifying a specific variant or edition of the operating system suitable for presentation to the
        user. This field may be used to inform the user that the configuration of this system is subject to a specific
        divergent set of rules or default configuration settings. This field is optional and may not be implemented on
        all systems.

        Examples: "VARIANT="Server Edition"", "VARIANT="Smart Refrigerator Edition"".

        Note: this field is for display purposes only. The VARIANT_ID field should be used for making programmatic
        decisions.

        Added in version 220.
        """

        return self.raw['VARIANT']

    @property
    def variant_id(self) -> str:
        """
        A lower-case string (no spaces or other characters outside of 0-9, a-z, ".", "_" and "-"), identifying a
        specific variant or edition of the operating system. This may be interpreted by other packages in order to
        determine a divergent default configuration. This field is optional and may not be implemented on all systems.

        Examples: "VARIANT_ID=server", "VARIANT_ID=embedded".

        Added in version 220.
        """

        return self.raw['variant_id']

    # Information about the version of the operating system

    @property
    def version(self) -> str:
        """
        A string identifying the operating system version, excluding any OS name information, possibly including a
        release code name, and suitable for presentation to the user. This field is optional.

        Examples: "VERSION=17", "VERSION="17 (Beefy Miracle)"".
        """

        return self.raw['VERSION']

    @property
    def version_id(self) -> str:
        """
        A lower-case string (mostly numeric, no spaces or other characters outside of 0-9, a-z, ".", "_" and "-")
        identifying the operating system version, excluding any OS name information or release code name, and suitable
        for processing by scripts or usage in generated filenames. This field is optional.

        Examples: "VERSION_ID=17", "VERSION_ID=11.04".
        """

        return self.raw['VERSION_ID']

    @property
    def version_codename(self) -> str:
        """
        A lower-case string (no spaces or other characters outside of 0-9, a-z, ".", "_" and "-") identifying the
        operating system release code name, excluding any OS name information or release version, and suitable for
        processing by scripts or usage in generated filenames. This field is optional and may not be implemented on all
        systems.

        Examples: "VERSION_CODENAME=buster", "VERSION_CODENAME=xenial".

        Added in version 231.
        """

        return self.raw['VERSION_CODENAME']

    @property
    def build_id(self) -> str:
        """
        A string uniquely identifying the system image originally used as the installation base. In most cases,
        VERSION_ID or IMAGE_ID+IMAGE_VERSION are updated when the entire system image is replaced during an update.
        BUILD_ID may be used in distributions where the original installation image version is important: VERSION_ID
        would change during incremental system updates, but BUILD_ID would not. This field is optional.

        Examples: "BUILD_ID="2013-03-20.3"", "BUILD_ID=201303203".

        Added in version 200.
        """

        return self.raw['BUILD_ID']

    @property
    def image_id(self) -> str:
        """
        A lower-case string (no spaces or other characters outside of 0-9, a-z, ".", "_" and "-"), identifying a
        specific image of the operating system. This is supposed to be used for environments where OS images are
        prepared, built, shipped and updated as comprehensive, consistent OS images. This field is optional and may not
        be implemented on all systems, in particularly not on those that are not managed via images but put together and
        updated from individual packages and on the local system.

        Examples: "IMAGE_ID=vendorx-cashier-system", "IMAGE_ID=netbook-image".

        Added in version 249.
        """

        return self.raw['IMAGE_ID']

    @property
    def image_version(self) -> str:
        """
        A lower-case string (mostly numeric, no spaces or other characters outside of 0-9, a-z, ".", "_" and "-")
        identifying the OS image version. This is supposed to be used together with IMAGE_ID described above, to discern
        different versions of the same image.

        Examples: "IMAGE_VERSION=33", "IMAGE_VERSION=47.1rc1".

        Added in version 249.
        """

        return self.raw['IMAGE_VERSION']

    # To summarize: if the image updates are built and shipped as comprehensive units, IMAGE_ID+IMAGE_VERSION is the
    # best fit. Otherwise, if updates eventually completely replace previously installed contents, as in a typical
    # binary distribution, VERSION_ID should be used to identify major releases of the operating system.  BUILD_ID may
    # be used instead or in addition to VERSION_ID when the original system image version is important.

    #

    # Presentation information and links

    # Links to resources on the Internet related to the operating system.  HOME_URL= should refer to the homepage of the
    # operating system, or alternatively some homepage of the specific version of the operating system.
    # DOCUMENTATION_URL= should refer to the main documentation page for this operating system.  SUPPORT_URL= should
    # refer to the main support page for the operating system, if there is any. This is primarily intended for operating
    # systems which vendors provide support for.  BUG_REPORT_URL= should refer to the main bug reporting page for the
    # operating system, if there is any. This is primarily intended for operating systems that rely on community QA.
    # PRIVACY_POLICY_URL= should refer to the main privacy policy page for the operating system, if there is any. These
    # settings are optional, and providing only some of these settings is common. These URLs are intended to be exposed
    # in "About this system" UIs behind links with captions such as "About this Operating System", "Obtain Support",
    # "Report a Bug", or "Privacy Policy". The values should be in RFC3986 format[5], and should be "http:" or "https:"
    # URLs, and possibly "mailto:" or "tel:". Only one URL shall be listed in each setting. If multiple resources need
    # to be referenced, it is recommended to provide an online landing page linking all available resources.

    # Examples: "HOME_URL="https://fedoraproject.org/"", "BUG_REPORT_URL="https://bugzilla.redhat.com/"".

    @property
    def home_url(self) -> str:
        return self.raw['HOME_URL']

    @property
    def documentation_url(self) -> str:
        return self.raw['DOCUMENTATION_URL']

    @property
    def support_url(self) -> str:
        return self.raw['SUPPORT_URL']

    @property
    def bug_report_url(self) -> str:
        return self.raw['BUG_REPORT_URL']

    @property
    def privacy_policy_url(self) -> str:
        return self.raw['PRIVACY_POLICY_URL']

    @property
    def support_end(self) -> str:
        """
        The date at which support for this version of the OS ends. (What exactly "lack of support" means varies between
        vendors, but generally users should assume that updates, including security fixes, will not be provided.) The
        value is a date in the ISO 8601 format "YYYY-MM-DD", and specifies the first day on which support is not
        provided.

        For example, "SUPPORT_END=2001-01-01" means that the system was supported until the end of the last day of the
        previous millennium.

        Added in version 252.
        """

        return self.raw['SUPPORT_END']

    @property
    def logo(self) -> str:
        """
        A string, specifying the name of an icon as defined by freedesktop.org Icon Theme Specification[6]. This can be
        used by graphical applications to display an operating system's or distributor's logo. This field is optional
        and may not necessarily be implemented on all systems.

        Examples: "LOGO=fedora-logo", "LOGO=distributor-logo-opensuse"

        Added in version 240.
        """

        return self.raw['LOGO']

    @property
    def ansi_color(self) -> str:
        """
        A suggested presentation color when showing the OS name on the console. This should be specified as string
        suitable for inclusion in the ESC [ m ANSI/ECMA-48 escape code for setting graphical rendition. This field is
        optional.

        Examples: "ANSI_COLOR="0;31"" for red, "ANSI_COLOR="1;34"" for light blue, or "ANSI_COLOR="0;38;2;60;110;180""
        for Fedora blue.
        """

        return self.raw['ANSI_COLOR']

    @property
    def vendor_name(self) -> str:
        """
        The name of the OS vendor. This is the name of the organization or company which produces the OS. This field is
        optional.

        This name is intended to be exposed in "About this system" UIs or software update UIs when needed to distinguish
        the OS vendor from the OS itself. It is intended to be human readable.

        Examples: "VENDOR_NAME="Fedora Project"" for Fedora Linux, "VENDOR_NAME="Canonical"" for Ubuntu.

        Added in version 254.
        """

        return self.raw['VENDOR_NAME']

    @property
    def vendor_url(self) -> str:
        """
        The homepage of the OS vendor. This field is optional. The VENDOR_NAME= field should be set if this one is,
        although clients must be robust against either field not being set.

        The value should be in RFC3986 format[5], and should be "http:" or "https:" URLs. Only one URL shall be listed
        in the setting.

        Examples: "VENDOR_URL="https://fedoraproject.org/"", "VENDOR_URL="https://canonical.com/"".

        Added in version 254.
        """

        return self.raw['VENDOR_URL']

    # Distribution-level defaults and metadata

    @property
    def default_hostname(self) -> str:
        """
        A string specifying the hostname if hostname(5) is not present and no other configuration source specifies the
        hostname. Must be either a single DNS label (a string composed of 7-bit ASCII lower-case characters and no
        spaces or dots, limited to the format allowed for DNS domain name labels), or a sequence of such labels
        separated by single dots that forms a valid DNS FQDN. The hostname must be at most 64 characters, which is a
        Linux limitation (DNS allows longer names).

        See org.freedesktop.hostname1(5) for a description of how systemd-hostnamed.service(8) determines the fallback
        hostname.

        Added in version 248.
        """

        return self.raw['DEFAULT_HOSTNAME']

    @property
    def architecture(self) -> str:
        """
        A string that specifies which CPU architecture the userspace binaries require. The architecture identifiers are
        the same as for ConditionArchitecture= described in systemd.unit(5). The field is optional and should only be
        used when just single architecture is supported. It may provide redundant information when used in a GPT
        partition with a GUID type that already encodes the architecture. If this is not the case, the architecture
        should be specified in e.g., an extension image, to prevent an incompatible host from loading it.

        Added in version 252.
        """

        return self.raw['ARCHITECTURE']

    @property
    def sysext_level(self) -> str:
        """
        A lower-case string (mostly numeric, no spaces or other characters outside of 0-9, a-z, ".", "_" and "-")
        identifying the operating system extensions support level, to indicate which extension images are supported. See
        /usr/lib/extension-release.d/extension-release.IMAGE, initrd[2] and systemd-sysext(8)) for more information.

        Examples: "SYSEXT_LEVEL=2", "SYSEXT_LEVEL=15.14".

        Added in version 248.
        """

        return self.raw['SYSEXT_LEVEL']

    @property
    def confext_level(self) -> str:
        """
        Semantically the same as SYSEXT_LEVEL= but for confext images. See
        /etc/extension-release.d/extension-release.IMAGE for more information.

        Examples: "CONFEXT_LEVEL=2", "CONFEXT_LEVEL=15.14".

        Added in version 254.
        """

        return self.raw['CONFEXT_LEVEL']

    @property
    def sysext_scope(self) -> str:
        """
        Takes a space-separated list of one or more of the strings "system", "initrd" and "portable". This field is only
        supported in extension-release.d/ files and indicates what environments the system extension is applicable to:
        i.e. to regular systems, to initrds, or to portable service images. If unspecified, "SYSEXT_SCOPE=system
        portable" is implied, i.e. any system extension without this field is applicable to regular systems and to
        portable service environments, but not to initrd environments.

        Added in version 250.
        """

        return self.raw['SYSEXT_SCOPE']

    @property
    def confext_scope(self) -> str:
        """
        Semantically the same as SYSEXT_SCOPE= but for confext images.

        Added in version 254.
        """

        return self.raw['CONFEXT_SCOPE']

    @property
    def portable_prefixes(self) -> str:
        """
        Takes a space-separated list of one or more valid prefix match strings for the Portable Services[3] logic. This
        field serves two purposes: it is informational, identifying portable service images as such (and thus allowing
        them to be distinguished from other OS images, such as bootable system images). It is also used when a portable
        service image is attached: the specified or implied portable service prefix is checked against the list
        specified here, to enforce restrictions how images may be attached to a system.

        Added in version 250.
        """

        return self.raw['PORTABLE_PREFIXES']

    #

    DEFAULT_PATHS: ta.ClassVar[ta.Sequence[str]] = [
        '/etc/os-release',
        '/usr/lib/os-release',
    ]

    @classmethod
    def read(cls, *paths: str) -> ta.Optional['LinuxOsRelease']:
        for fp in (paths or cls.DEFAULT_PATHS):
            if not os.path.isfile(fp):
                continue
            with open(fp) as f:
                src = f.read()
            break
        else:
            return None

        raw = cls._parse_os_release(src)

        return cls(raw)

    @classmethod
    def _parse_os_release(cls, src: str) -> ta.Mapping[str, str]:
        dct: ta.Dict[str, str] = {}

        for l in src.splitlines():
            if not (l := l.strip()):
                continue
            if l.startswith('#') or '=' not in l:
                continue

            k, _, v = l.partition('=')
            if k.startswith('"'):
                k = k[1:-1]
            if v.startswith('"'):
                v = v[1:-1]

            dct[k] = v

        return dct


########################################
# ../../../omlish/os/paths.py


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
# ../../../omdev/packaging/specifiers.py
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
# ../commands/base.py


##


@dc.dataclass(frozen=True)
class Command(abc.ABC, ta.Generic[CommandOutputT]):
    @dc.dataclass(frozen=True)
    class Output(abc.ABC):  # noqa
        pass

    @ta.final
    async def execute(self, executor: 'CommandExecutor') -> CommandOutputT:
        return check.isinstance(await executor.execute(self), self.Output)  # type: ignore[return-value]


##


@dc.dataclass(frozen=True)
class CommandException:
    name: str
    repr: str

    traceback: ta.Optional[str] = None

    exc: ta.Optional[ta.Any] = None  # Exception

    cmd: ta.Optional[Command] = None

    @classmethod
    def of(
            cls,
            exc: Exception,
            *,
            omit_exc_object: bool = False,

            cmd: ta.Optional[Command] = None,
    ) -> 'CommandException':
        return CommandException(
            name=type(exc).__qualname__,
            repr=repr(exc),

            traceback=(
                ''.join(traceback.format_tb(exc.__traceback__))
                if getattr(exc, '__traceback__', None) is not None else None
            ),

            exc=None if omit_exc_object else exc,

            cmd=cmd,
        )


class CommandOutputOrException(abc.ABC, ta.Generic[CommandOutputT]):
    @property
    @abc.abstractmethod
    def output(self) -> ta.Optional[CommandOutputT]:
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def exception(self) -> ta.Optional[CommandException]:
        raise NotImplementedError


@dc.dataclass(frozen=True)
class CommandOutputOrExceptionData(CommandOutputOrException):
    output: ta.Optional[Command.Output] = None
    exception: ta.Optional[CommandException] = None


class CommandExecutor(abc.ABC, ta.Generic[CommandT, CommandOutputT]):
    @abc.abstractmethod
    def execute(self, cmd: CommandT) -> ta.Awaitable[CommandOutputT]:
        raise NotImplementedError

    async def try_execute(
            self,
            cmd: CommandT,
            *,
            log: ta.Optional[logging.Logger] = None,
            omit_exc_object: bool = False,
    ) -> CommandOutputOrException[CommandOutputT]:
        try:
            o = await self.execute(cmd)

        except Exception as e:  # noqa
            if log is not None:
                log.exception('Exception executing command: %r', type(cmd))

            return CommandOutputOrExceptionData(exception=CommandException.of(
                e,
                omit_exc_object=omit_exc_object,
                cmd=cmd,
            ))

        else:
            return CommandOutputOrExceptionData(output=o)


##


@dc.dataclass(frozen=True)
class CommandRegistration:
    command_cls: ta.Type[Command]

    name: ta.Optional[str] = None

    @property
    def name_or_default(self) -> str:
        if not (cls_name := self.command_cls.__name__).endswith('Command'):
            raise NameError(cls_name)
        return snake_case(cls_name[:-len('Command')])


CommandRegistrations = ta.NewType('CommandRegistrations', ta.Sequence[CommandRegistration])


##


@dc.dataclass(frozen=True)
class CommandExecutorRegistration:
    command_cls: ta.Type[Command]
    executor_cls: ta.Type[CommandExecutor]


CommandExecutorRegistrations = ta.NewType('CommandExecutorRegistrations', ta.Sequence[CommandExecutorRegistration])


##


CommandNameMap = ta.NewType('CommandNameMap', ta.Mapping[str, ta.Type[Command]])


def build_command_name_map(crs: CommandRegistrations) -> CommandNameMap:
    dct: ta.Dict[str, ta.Type[Command]] = {}
    cr: CommandRegistration
    for cr in crs:
        if (name := cr.name_or_default) in dct:
            raise NameError(name)
        dct[name] = cr.command_cls
    return CommandNameMap(dct)


########################################
# ../remote/config.py


@dc.dataclass(frozen=True)
class RemoteConfig:
    payload_file: ta.Optional[str] = None

    set_pgid: bool = True

    deathsig: ta.Optional[str] = 'KILL'

    pycharm_remote_debug: ta.Optional[PycharmRemoteDebug] = None

    forward_logging: bool = True

    timebomb_delay_s: ta.Optional[float] = 60 * 60.

    heartbeat_interval_s: float = 3.


########################################
# ../remote/payload.py


RemoteExecutionPayloadFile = ta.NewType('RemoteExecutionPayloadFile', str)


@cached_nullary
def _get_self_src() -> str:
    return inspect.getsource(sys.modules[__name__])


def _is_src_amalg(src: str) -> bool:
    for l in src.splitlines():  # noqa
        if l.startswith('# @omlish-amalg-output '):
            return True
    return False


@cached_nullary
def _is_self_amalg() -> bool:
    return _is_src_amalg(_get_self_src())


def get_remote_payload_src(
        *,
        file: ta.Optional[RemoteExecutionPayloadFile],
) -> str:
    if file is not None:
        with open(file) as f:
            return f.read()

    if _is_self_amalg():
        return _get_self_src()

    import importlib.resources
    return importlib.resources.files(__package__.split('.')[0] + '.scripts').joinpath('manage.py').read_text()


########################################
# ../system/platforms.py


##


@dc.dataclass(frozen=True)
class Platform(abc.ABC):  # noqa
    pass


class LinuxPlatform(Platform, abc.ABC):
    pass


class UbuntuPlatform(LinuxPlatform):
    pass


class AmazonLinuxPlatform(LinuxPlatform):
    pass


class GenericLinuxPlatform(LinuxPlatform):
    pass


class DarwinPlatform(Platform):
    pass


class UnknownPlatform(Platform):
    pass


##


def _detect_system_platform() -> Platform:
    plat = sys.platform

    if plat == 'linux':
        if (osr := LinuxOsRelease.read()) is None:
            return GenericLinuxPlatform()

        if osr.id == 'amzn':
            return AmazonLinuxPlatform()

        elif osr.id == 'ubuntu':
            return UbuntuPlatform()

        else:
            return GenericLinuxPlatform()

    elif plat == 'darwin':
        return DarwinPlatform()

    else:
        return UnknownPlatform()


@cached_nullary
def detect_system_platform() -> Platform:
    platform = _detect_system_platform()
    log.info('Detected platform: %r', platform)
    return platform


########################################
# ../targets/bestpython.py


BEST_PYTHON_SH = """\
bv=""
bx=""

for v in "" 3 3.{8..13}; do
    x="python$v"
    v=$($x -c "import sys; print((\\"%02d\\" * 3) % sys.version_info[:3])" 2>/dev/null)
    if [ $? -eq 0 ] && ([ -z "$bv" ] || [ "$v" \\> "$bv" ]); then
        bv=$v
        bx=$x
    fi
done

if [ -z "$bx" ]; then
    echo "no python" >&2
    exit 1
fi

exec "$bx" "$@"
"""  # noqa


@cached_nullary
def get_best_python_sh() -> str:
    buf = io.StringIO()

    for l in BEST_PYTHON_SH.strip().splitlines():
        if not (l := l.strip()):
            continue

        buf.write(l)

        if l.split()[-1] not in ('do', 'then', 'else'):
            buf.write(';')

        buf.write(' ')

    return buf.getvalue().strip(' ;')


########################################
# ../targets/targets.py
"""
It's desugaring. Subprocess and locals are only leafs. Retain an origin?
** TWO LAYERS ** - ManageTarget is user-facing, ConnectorTarget is bound, internal
"""


##


class ManageTarget(abc.ABC):  # noqa
    def __init_subclass__(cls, **kwargs: ta.Any) -> None:
        super().__init_subclass__(**kwargs)

        check.state(cls.__name__.endswith('ManageTarget'))


#


@dc.dataclass(frozen=True)
class PythonRemoteManageTarget:
    DEFAULT_PYTHON: ta.ClassVar[ta.Optional[ta.Sequence[str]]] = None
    python: ta.Optional[ta.Sequence[str]] = DEFAULT_PYTHON

    def __post_init__(self) -> None:
        check.not_isinstance(self.python, str)


#


class RemoteManageTarget(ManageTarget, abc.ABC):
    pass


class PhysicallyRemoteManageTarget(RemoteManageTarget, abc.ABC):
    pass


class LocalManageTarget(ManageTarget, abc.ABC):
    pass


##


@dc.dataclass(frozen=True)
class SshManageTarget(PhysicallyRemoteManageTarget, PythonRemoteManageTarget):
    host: ta.Optional[str] = None
    username: ta.Optional[str] = None
    key_file: ta.Optional[str] = None

    def __post_init__(self) -> None:
        check.non_empty_str(self.host)


##


@dc.dataclass(frozen=True)
class DockerManageTarget(RemoteManageTarget, PythonRemoteManageTarget):  # noqa
    image: ta.Optional[str] = None
    container_id: ta.Optional[str] = None

    def __post_init__(self) -> None:
        check.arg(bool(self.image) ^ bool(self.container_id))


##


@dc.dataclass(frozen=True)
class InProcessManageTarget(LocalManageTarget):
    class Mode(enum.Enum):
        DIRECT = enum.auto()
        FAKE_REMOTE = enum.auto()

    mode: Mode = Mode.DIRECT


@dc.dataclass(frozen=True)
class SubprocessManageTarget(LocalManageTarget, PythonRemoteManageTarget):
    pass


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
class ArgparseCommand:
    name: str
    fn: ArgparseCommandFn
    args: ta.Sequence[ArgparseArg] = ()  # noqa

    # _: dc.KW_ONLY

    aliases: ta.Optional[ta.Sequence[str]] = None
    parent: ta.Optional['ArgparseCommand'] = None
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
        check.isinstance(self.parent, (ArgparseCommand, type(None)))
        check.isinstance(self.accepts_unknown, bool)

        functools.update_wrapper(self, self.fn)

    def __get__(self, instance, owner=None):
        if instance is None:
            return self
        return dc.replace(self, fn=self.fn.__get__(instance, owner))  # noqa

    def __call__(self, *args, **kwargs) -> ta.Optional[int]:
        return self.fn(*args, **kwargs)


def argparse_command(
        *args: ArgparseArg,
        name: ta.Optional[str] = None,
        aliases: ta.Optional[ta.Iterable[str]] = None,
        parent: ta.Optional[ArgparseCommand] = None,
        accepts_unknown: bool = False,
) -> ta.Any:  # ta.Callable[[ArgparseCommandFn], ArgparseCommand]:  # FIXME
    for arg in args:
        check.isinstance(arg, ArgparseArg)
    check.isinstance(name, (str, type(None)))
    check.isinstance(parent, (ArgparseCommand, type(None)))
    check.not_isinstance(aliases, str)

    def inner(fn):
        return ArgparseCommand(
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
                if isinstance(v, (ArgparseCommand, ArgparseArg)):
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
            if isinstance(obj, ArgparseCommand):
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

    def _bind_cli_cmd(self, cmd: ArgparseCommand) -> ta.Callable:
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

    async def async_cli_run(self) -> ta.Optional[int]:
        if (fn := self.prepare_cli_run()) is None:
            return 0

        return await fn()


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


##


@contextlib.contextmanager
def defer(fn: ta.Callable) -> ta.Generator[ta.Callable, None, None]:
    try:
        yield fn
    finally:
        fn()


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
# inspection


class _InjectionInspection(ta.NamedTuple):
    signature: inspect.Signature
    type_hints: ta.Mapping[str, ta.Any]
    args_offset: int


_INJECTION_INSPECTION_CACHE: ta.MutableMapping[ta.Any, _InjectionInspection] = weakref.WeakKeyDictionary()


def _do_injection_inspect(obj: ta.Any) -> _InjectionInspection:
    tgt = obj
    if isinstance(tgt, type) and tgt.__init__ is not object.__init__:  # type: ignore[misc]
        # Python 3.8's inspect.signature can't handle subclasses overriding __new__, always generating *args/**kwargs.
        #  - https://bugs.python.org/issue40897
        #  - https://github.com/python/cpython/commit/df7c62980d15acd3125dfbd81546dad359f7add7
        tgt = tgt.__init__  # type: ignore[misc]
        has_generic_base = True
    else:
        has_generic_base = False

    # inspect.signature(eval_str=True) was added in 3.10 and we have to support 3.8, so we have to get_type_hints to
    # eval str annotations *in addition to* getting the signature for parameter information.
    uw = tgt
    has_partial = False
    while True:
        if isinstance(uw, functools.partial):
            has_partial = True
            uw = uw.func
        else:
            if (uw2 := inspect.unwrap(uw)) is uw:
                break
            uw = uw2

    if has_generic_base and has_partial:
        raise InjectorError(
            'Injector inspection does not currently support both a typing.Generic base and a functools.partial: '
            f'{obj}',
        )

    return _InjectionInspection(
        inspect.signature(tgt),
        ta.get_type_hints(uw),
        1 if has_generic_base else 0,
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
    def __init__(self, bs: InjectorBindings, p: ta.Optional[Injector] = None) -> None:
        super().__init__()

        self._bs = check.isinstance(bs, InjectorBindings)
        self._p: ta.Optional[Injector] = check.isinstance(p, (Injector, type(None)))

        self._pfm = {k: v.provider_fn() for k, v in build_injector_provider_map(bs).items()}

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

            singleton: bool = False,

            eager: bool = False,
    ) -> InjectorBindingOrBindings:
        if obj is None or obj is inspect.Parameter.empty:
            raise TypeError(obj)
        if isinstance(obj, cls._BANNED_BIND_TYPES):
            raise TypeError(obj)

        ##

        if key is not None:
            key = as_injector_key(key)

        ##

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

        ##

        if tag is not None:
            if key.tag is not None:
                raise TypeError('Tag already set')
            key = dc.replace(key, tag=tag)

        if array is not None:
            key = dc.replace(key, array=array)

        ##

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
        provider, = providers

        ##

        if singleton:
            provider = SingletonInjectorProvider(provider)

        binding = InjectorBinding(key, provider)

        ##

        extras: ta.List[InjectorBinding] = []

        if eager:
            extras.append(bind_injector_eager_key(key))

        ##

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


##


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

    def override(self, p: InjectorBindings, *args: InjectorBindingOrBindings) -> InjectorBindings:
        return injector_override(p, *args)

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
# ../../../omlish/lite/marshal.py
"""
TODO:
 - pickle stdlib objs? have to pin to 3.8 pickle protocol, will be cross-version
 - literals
"""


##


@dc.dataclass(frozen=True)
class ObjMarshalOptions:
    raw_bytes: bool = False
    non_strict_fields: bool = False


class ObjMarshaler(abc.ABC):
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


@dc.dataclass()
class ProxyObjMarshaler(ObjMarshaler):
    m: ta.Optional[ObjMarshaler] = None

    def marshal(self, o: ta.Any, ctx: 'ObjMarshalContext') -> ta.Any:
        return check.not_none(self.m).marshal(o, ctx)

    def unmarshal(self, o: ta.Any, ctx: 'ObjMarshalContext') -> ta.Any:
        return check.not_none(self.m).unmarshal(o, ctx)


@dc.dataclass(frozen=True)
class CastObjMarshaler(ObjMarshaler):
    ty: type

    def marshal(self, o: ta.Any, ctx: 'ObjMarshalContext') -> ta.Any:
        return o

    def unmarshal(self, o: ta.Any, ctx: 'ObjMarshalContext') -> ta.Any:
        return self.ty(o)


class DynamicObjMarshaler(ObjMarshaler):
    def marshal(self, o: ta.Any, ctx: 'ObjMarshalContext') -> ta.Any:
        return ctx.manager.marshal_obj(o, opts=ctx.options)

    def unmarshal(self, o: ta.Any, ctx: 'ObjMarshalContext') -> ta.Any:
        return o


@dc.dataclass(frozen=True)
class Base64ObjMarshaler(ObjMarshaler):
    ty: type

    def marshal(self, o: ta.Any, ctx: 'ObjMarshalContext') -> ta.Any:
        return base64.b64encode(o).decode('ascii')

    def unmarshal(self, o: ta.Any, ctx: 'ObjMarshalContext') -> ta.Any:
        return self.ty(base64.b64decode(o))


@dc.dataclass(frozen=True)
class BytesSwitchedObjMarshaler(ObjMarshaler):
    m: ObjMarshaler

    def marshal(self, o: ta.Any, ctx: 'ObjMarshalContext') -> ta.Any:
        if ctx.options.raw_bytes:
            return o
        return self.m.marshal(o, ctx)

    def unmarshal(self, o: ta.Any, ctx: 'ObjMarshalContext') -> ta.Any:
        if ctx.options.raw_bytes:
            return o
        return self.m.unmarshal(o, ctx)


@dc.dataclass(frozen=True)
class EnumObjMarshaler(ObjMarshaler):
    ty: type

    def marshal(self, o: ta.Any, ctx: 'ObjMarshalContext') -> ta.Any:
        return o.name

    def unmarshal(self, o: ta.Any, ctx: 'ObjMarshalContext') -> ta.Any:
        return self.ty.__members__[o]  # type: ignore


@dc.dataclass(frozen=True)
class OptionalObjMarshaler(ObjMarshaler):
    item: ObjMarshaler

    def marshal(self, o: ta.Any, ctx: 'ObjMarshalContext') -> ta.Any:
        if o is None:
            return None
        return self.item.marshal(o, ctx)

    def unmarshal(self, o: ta.Any, ctx: 'ObjMarshalContext') -> ta.Any:
        if o is None:
            return None
        return self.item.unmarshal(o, ctx)


@dc.dataclass(frozen=True)
class LiteralObjMarshaler(ObjMarshaler):
    item: ObjMarshaler
    vs: frozenset

    def marshal(self, o: ta.Any, ctx: 'ObjMarshalContext') -> ta.Any:
        return self.item.marshal(check.in_(o, self.vs), ctx)

    def unmarshal(self, o: ta.Any, ctx: 'ObjMarshalContext') -> ta.Any:
        return check.in_(self.item.unmarshal(o, ctx), self.vs)


@dc.dataclass(frozen=True)
class MappingObjMarshaler(ObjMarshaler):
    ty: type
    km: ObjMarshaler
    vm: ObjMarshaler

    def marshal(self, o: ta.Any, ctx: 'ObjMarshalContext') -> ta.Any:
        return {self.km.marshal(k, ctx): self.vm.marshal(v, ctx) for k, v in o.items()}

    def unmarshal(self, o: ta.Any, ctx: 'ObjMarshalContext') -> ta.Any:
        return self.ty((self.km.unmarshal(k, ctx), self.vm.unmarshal(v, ctx)) for k, v in o.items())


@dc.dataclass(frozen=True)
class IterableObjMarshaler(ObjMarshaler):
    ty: type
    item: ObjMarshaler

    def marshal(self, o: ta.Any, ctx: 'ObjMarshalContext') -> ta.Any:
        return [self.item.marshal(e, ctx) for e in o]

    def unmarshal(self, o: ta.Any, ctx: 'ObjMarshalContext') -> ta.Any:
        return self.ty(self.item.unmarshal(e, ctx) for e in o)


@dc.dataclass(frozen=True)
class FieldsObjMarshaler(ObjMarshaler):
    ty: type
    fs: ta.Mapping[str, ObjMarshaler]
    non_strict: bool = False

    def marshal(self, o: ta.Any, ctx: 'ObjMarshalContext') -> ta.Any:
        return {
            k: m.marshal(getattr(o, k), ctx)
            for k, m in self.fs.items()
        }

    def unmarshal(self, o: ta.Any, ctx: 'ObjMarshalContext') -> ta.Any:
        return self.ty(**{
            k: self.fs[k].unmarshal(v, ctx)
            for k, v in o.items()
            if not (self.non_strict or ctx.options.non_strict_fields) or k in self.fs
        })


@dc.dataclass(frozen=True)
class SingleFieldObjMarshaler(ObjMarshaler):
    ty: type
    fld: str

    def marshal(self, o: ta.Any, ctx: 'ObjMarshalContext') -> ta.Any:
        return getattr(o, self.fld)

    def unmarshal(self, o: ta.Any, ctx: 'ObjMarshalContext') -> ta.Any:
        return self.ty(**{self.fld: o})


@dc.dataclass(frozen=True)
class PolymorphicObjMarshaler(ObjMarshaler):
    class Impl(ta.NamedTuple):
        ty: type
        tag: str
        m: ObjMarshaler

    impls_by_ty: ta.Mapping[type, Impl]
    impls_by_tag: ta.Mapping[str, Impl]

    @classmethod
    def of(cls, impls: ta.Iterable[Impl]) -> 'PolymorphicObjMarshaler':
        return cls(
            {i.ty: i for i in impls},
            {i.tag: i for i in impls},
        )

    def marshal(self, o: ta.Any, ctx: 'ObjMarshalContext') -> ta.Any:
        impl = self.impls_by_ty[type(o)]
        return {impl.tag: impl.m.marshal(o, ctx)}

    def unmarshal(self, o: ta.Any, ctx: 'ObjMarshalContext') -> ta.Any:
        [(t, v)] = o.items()
        impl = self.impls_by_tag[t]
        return impl.m.unmarshal(v, ctx)


@dc.dataclass(frozen=True)
class DatetimeObjMarshaler(ObjMarshaler):
    ty: type

    def marshal(self, o: ta.Any, ctx: 'ObjMarshalContext') -> ta.Any:
        return o.isoformat()

    def unmarshal(self, o: ta.Any, ctx: 'ObjMarshalContext') -> ta.Any:
        return self.ty.fromisoformat(o)  # type: ignore


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
    **{t: dict for t in (collections.abc.Mapping, collections.abc.MutableMapping)},
}

_OBJ_MARSHALER_GENERIC_ITERABLE_TYPES: ta.Dict[ta.Any, type] = {
    **{t: t for t in (list, tuple, set, frozenset)},
    collections.abc.Set: frozenset,
    collections.abc.MutableSet: set,
    collections.abc.Sequence: tuple,
    collections.abc.MutableSequence: list,
}


##


_REGISTERED_OBJ_MARSHALERS_BY_TYPE: ta.MutableMapping[type, ObjMarshaler] = weakref.WeakKeyDictionary()


def register_type_obj_marshaler(ty: type, om: ObjMarshaler) -> None:
    _REGISTERED_OBJ_MARSHALERS_BY_TYPE[ty] = om


##


class ObjMarshalerManager:
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

            if abc.ABC in ty.__bases__:
                impls = [ity for ity in deep_subclasses(ty) if abc.ABC not in ity.__bases__]  # type: ignore
                if all(ity.__qualname__.endswith(ty.__name__) for ity in impls):
                    ins = {ity: snake_case(ity.__qualname__[:-len(ty.__name__)]) for ity in impls}
                else:
                    ins = {ity: ity.__qualname__ for ity in impls}
                return PolymorphicObjMarshaler.of([
                    PolymorphicObjMarshaler.Impl(
                        ity,
                        itn,
                        rec(ity),
                    )
                    for ity, itn in ins.items()
                ])

            if issubclass(ty, enum.Enum):
                return EnumObjMarshaler(ty)

            if dc.is_dataclass(ty):
                return FieldsObjMarshaler(
                    ty,
                    {f.name: rec(f.type) for f in dc.fields(ty)},
                    non_strict=non_strict_fields,
                )

            if issubclass(ty, tuple) and hasattr(ty, '_fields'):
                return FieldsObjMarshaler(
                    ty,
                    {p.name: rec(p.annotation) for p in inspect.signature(ty).parameters.values()},
                    non_strict=non_strict_fields,
                )

        if is_new_type(ty):
            return rec(get_new_type_supertype(ty))

        if is_literal_type(ty):
            lvs = frozenset(get_literal_type_args(ty))
            lty = check.single(set(map(type, lvs)))
            return LiteralObjMarshaler(rec(lty), lvs)

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
                return OptionalObjMarshaler(rec(get_optional_alias_arg(ty)))

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
            p.m = m

            if not no_cache:
                self._obj_marshalers[ty] = m
            return m

    #

    def _make_context(self, opts: ta.Optional[ObjMarshalOptions]) -> 'ObjMarshalContext':
        return ObjMarshalContext(
            options=opts or self._default_options,
            manager=self,
        )

    def marshal_obj(
            self,
            o: ta.Any,
            ty: ta.Any = None,
            opts: ta.Optional[ObjMarshalOptions] = None,
    ) -> ta.Any:
        m = self.get_obj_marshaler(ty if ty is not None else type(o))
        return m.marshal(o, self._make_context(opts))

    def unmarshal_obj(
            self,
            o: ta.Any,
            ty: ta.Union[ta.Type[T], ta.Any],
            opts: ta.Optional[ObjMarshalOptions] = None,
    ) -> T:
        m = self.get_obj_marshaler(ty)
        return m.unmarshal(o, self._make_context(opts))

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


@dc.dataclass(frozen=True)
class ObjMarshalContext:
    options: ObjMarshalOptions
    manager: ObjMarshalerManager


##


OBJ_MARSHALER_MANAGER = ObjMarshalerManager()

set_obj_marshaler = OBJ_MARSHALER_MANAGER.set_obj_marshaler
get_obj_marshaler = OBJ_MARSHALER_MANAGER.get_obj_marshaler

marshal_obj = OBJ_MARSHALER_MANAGER.marshal_obj
unmarshal_obj = OBJ_MARSHALER_MANAGER.unmarshal_obj


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
# ../../../omlish/os/atomics.py


##


class AtomicPathSwap(abc.ABC):
    def __init__(
            self,
            kind: AtomicPathSwapKind,
            dst_path: str,
            *,
            auto_commit: bool = False,
    ) -> None:
        super().__init__()

        self._kind = kind
        self._dst_path = dst_path
        self._auto_commit = auto_commit

        self._state: AtomicPathSwapState = 'open'

    def __repr__(self) -> str:
        return attr_repr(self, 'kind', 'dst_path', 'tmp_path')

    @property
    def kind(self) -> AtomicPathSwapKind:
        return self._kind

    @property
    def dst_path(self) -> str:
        return self._dst_path

    @property
    @abc.abstractmethod
    def tmp_path(self) -> str:
        raise NotImplementedError

    #

    @property
    def state(self) -> AtomicPathSwapState:
        return self._state

    def _check_state(self, *states: AtomicPathSwapState) -> None:
        if self._state not in states:
            raise RuntimeError(f'Atomic path swap not in correct state: {self._state}, {states}')

    #

    @abc.abstractmethod
    def _commit(self) -> None:
        raise NotImplementedError

    def commit(self) -> None:
        if self._state == 'committed':
            return
        self._check_state('open')
        try:
            self._commit()
        except Exception:  # noqa
            self._abort()
            raise
        else:
            self._state = 'committed'

    #

    @abc.abstractmethod
    def _abort(self) -> None:
        raise NotImplementedError

    def abort(self) -> None:
        if self._state == 'aborted':
            return
        self._abort()
        self._state = 'aborted'

    #

    def __enter__(self) -> 'AtomicPathSwap':
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if (
                exc_type is None and
                self._auto_commit and
                self._state == 'open'
        ):
            self.commit()
        else:
            self.abort()


class AtomicPathSwapping(abc.ABC):
    @abc.abstractmethod
    def begin_atomic_path_swap(
            self,
            kind: AtomicPathSwapKind,
            dst_path: str,
            *,
            name_hint: ta.Optional[str] = None,
            make_dirs: bool = False,
            **kwargs: ta.Any,
    ) -> AtomicPathSwap:
        raise NotImplementedError


##


class OsReplaceAtomicPathSwap(AtomicPathSwap):
    def __init__(
            self,
            kind: AtomicPathSwapKind,
            dst_path: str,
            tmp_path: str,
            **kwargs: ta.Any,
    ) -> None:
        if kind == 'dir':
            check.state(os.path.isdir(tmp_path))
        elif kind == 'file':
            check.state(os.path.isfile(tmp_path))
        else:
            raise TypeError(kind)

        super().__init__(
            kind,
            dst_path,
            **kwargs,
        )

        self._tmp_path = tmp_path

    @property
    def tmp_path(self) -> str:
        return self._tmp_path

    def _commit(self) -> None:
        os.replace(self._tmp_path, self._dst_path)

    def _abort(self) -> None:
        shutil.rmtree(self._tmp_path, ignore_errors=True)


class TempDirAtomicPathSwapping(AtomicPathSwapping):
    def __init__(
            self,
            *,
            temp_dir: ta.Optional[str] = None,
            root_dir: ta.Optional[str] = None,
    ) -> None:
        super().__init__()

        if root_dir is not None:
            root_dir = os.path.abspath(root_dir)
        self._root_dir = root_dir
        self._temp_dir = temp_dir

    def begin_atomic_path_swap(
            self,
            kind: AtomicPathSwapKind,
            dst_path: str,
            *,
            name_hint: ta.Optional[str] = None,
            make_dirs: bool = False,
            **kwargs: ta.Any,
    ) -> AtomicPathSwap:
        dst_path = os.path.abspath(dst_path)
        if self._root_dir is not None and not dst_path.startswith(check.non_empty_str(self._root_dir)):
            raise RuntimeError(f'Atomic path swap dst must be in root dir: {dst_path}, {self._root_dir}')

        dst_dir = os.path.dirname(dst_path)
        if make_dirs:
            os.makedirs(dst_dir, exist_ok=True)
        if not os.path.isdir(dst_dir):
            raise RuntimeError(f'Atomic path swap dst dir does not exist: {dst_dir}')

        if kind == 'dir':
            tmp_path = tempfile.mkdtemp(prefix=name_hint, dir=self._temp_dir)
        elif kind == 'file':
            fd, tmp_path = tempfile.mkstemp(prefix=name_hint, dir=self._temp_dir)
            os.close(fd)
        else:
            raise TypeError(kind)

        return OsReplaceAtomicPathSwap(
            kind,
            dst_path,
            tmp_path,
            **kwargs,
        )


########################################
# ../../../omdev/interp/types.py


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


@dc.dataclass(frozen=True)
class Interp:
    exe: str
    version: InterpVersion


########################################
# ../../configs.py


def parse_config_file(
        name: str,
        f: ta.TextIO,
) -> ConfigMapping:
    if name.endswith('.toml'):
        return toml_loads(f.read())

    elif any(name.endswith(e) for e in ('.yml', '.yaml')):
        yaml = __import__('yaml')
        return yaml.safe_load(f)

    elif name.endswith('.ini'):
        import configparser
        cp = configparser.ConfigParser()
        cp.read_file(f)
        config_dct: ta.Dict[str, ta.Any] = {}
        for sec in cp.sections():
            cd = config_dct
            for k in sec.split('.'):
                cd = cd.setdefault(k, {})
            cd.update(cp.items(sec))
        return config_dct

    else:
        return json.loads(f.read())


def read_config_file(
        path: str,
        cls: ta.Type[T],
        *,
        prepare: ta.Optional[ta.Callable[[ConfigMapping], ConfigMapping]] = None,
        msh: ObjMarshalerManager = OBJ_MARSHALER_MANAGER,
) -> T:
    with open(path) as cf:
        config_dct = parse_config_file(os.path.basename(path), cf)

    if prepare is not None:
        config_dct = prepare(config_dct)

    return msh.unmarshal_obj(config_dct, cls)


def build_config_named_children(
        o: ta.Union[
            ta.Sequence[ConfigMapping],
            ta.Mapping[str, ConfigMapping],
            None,
        ],
        *,
        name_key: str = 'name',
) -> ta.Optional[ta.Sequence[ConfigMapping]]:
    if o is None:
        return None

    lst: ta.List[ConfigMapping] = []
    if isinstance(o, ta.Mapping):
        for k, v in o.items():
            check.isinstance(v, ta.Mapping)
            if name_key in v:
                n = v[name_key]
                if k != n:
                    raise KeyError(f'Given names do not match: {n} != {k}')
                lst.append(v)
            else:
                lst.append({name_key: k, **v})

    else:
        check.not_isinstance(o, str)
        lst.extend(o)

    seen = set()
    for d in lst:
        n = d['name']
        if n in d:
            raise KeyError(f'Duplicate name: {n}')
        seen.add(n)

    return lst


########################################
# ../commands/marshal.py


def install_command_marshaling(
        cmds: CommandNameMap,
        msh: ObjMarshalerManager,
) -> None:
    for fn in [
        lambda c: c,
        lambda c: c.Output,
    ]:
        msh.set_obj_marshaler(
            fn(Command),
            PolymorphicObjMarshaler.of([
                PolymorphicObjMarshaler.Impl(
                    fn(cmd),
                    name,
                    msh.get_obj_marshaler(fn(cmd)),
                )
                for name, cmd in cmds.items()
            ]),
        )


########################################
# ../commands/ping.py


##


@dc.dataclass(frozen=True)
class PingCommand(Command['PingCommand.Output']):
    time: float = dc.field(default_factory=time.time)

    @dc.dataclass(frozen=True)
    class Output(Command.Output):
        time: float


class PingCommandExecutor(CommandExecutor[PingCommand, PingCommand.Output]):
    async def execute(self, cmd: PingCommand) -> PingCommand.Output:
        return PingCommand.Output(cmd.time)


########################################
# ../commands/types.py


CommandExecutorMap = ta.NewType('CommandExecutorMap', ta.Mapping[ta.Type[Command], CommandExecutor])


########################################
# ../deploy/tags.py


##


DEPLOY_TAG_SIGIL = '@'

DEPLOY_TAG_SEPARATOR = '--'

DEPLOY_TAG_DELIMITERS: ta.AbstractSet[str] = frozenset([
    DEPLOY_TAG_SEPARATOR,
    '.',
])

DEPLOY_TAG_ILLEGAL_STRS: ta.AbstractSet[str] = frozenset([
    DEPLOY_TAG_SIGIL,
    *DEPLOY_TAG_DELIMITERS,
    '/',
])


##


@dc.dataclass(frozen=True)
class DeployTag(abc.ABC):  # noqa
    s: str

    def __post_init__(self) -> None:
        check.not_in(abc.ABC, type(self).__bases__)
        check.non_empty_str(self.s)
        for ch in DEPLOY_TAG_ILLEGAL_STRS:
            check.state(ch not in self.s)

    #

    tag_name: ta.ClassVar[str]
    tag_kwarg: ta.ClassVar[str]

    def __init_subclass__(cls, **kwargs: ta.Any) -> None:
        super().__init_subclass__(**kwargs)

        if abc.ABC in cls.__bases__:
            return

        for b in cls.__bases__:
            if issubclass(b, DeployTag):
                check.in_(abc.ABC, b.__bases__)

        check.non_empty_str(tn := cls.tag_name)
        check.equal(tn, tn.lower().strip())
        check.not_in('_', tn)

        check.state(not hasattr(cls, 'tag_kwarg'))
        cls.tag_kwarg = tn.replace('-', '_')


##


_DEPLOY_TAGS: ta.Set[ta.Type[DeployTag]] = set()
DEPLOY_TAGS: ta.AbstractSet[ta.Type[DeployTag]] = _DEPLOY_TAGS

_DEPLOY_TAGS_BY_NAME: ta.Dict[str, ta.Type[DeployTag]] = {}
DEPLOY_TAGS_BY_NAME: ta.Mapping[str, ta.Type[DeployTag]] = _DEPLOY_TAGS_BY_NAME

_DEPLOY_TAGS_BY_KWARG: ta.Dict[str, ta.Type[DeployTag]] = {}
DEPLOY_TAGS_BY_KWARG: ta.Mapping[str, ta.Type[DeployTag]] = _DEPLOY_TAGS_BY_KWARG


def _register_deploy_tag(cls):
    check.not_in(cls.tag_name, _DEPLOY_TAGS_BY_NAME)
    check.not_in(cls.tag_kwarg, _DEPLOY_TAGS_BY_KWARG)

    _DEPLOY_TAGS.add(cls)
    _DEPLOY_TAGS_BY_NAME[cls.tag_name] = cls
    _DEPLOY_TAGS_BY_KWARG[cls.tag_kwarg] = cls

    register_type_obj_marshaler(cls, SingleFieldObjMarshaler(cls, 's'))

    return cls


##


@_register_deploy_tag
class DeployTime(DeployTag):
    tag_name: ta.ClassVar[str] = 'time'


##


class NameDeployTag(DeployTag, abc.ABC):  # noqa
    pass


@_register_deploy_tag
class DeployApp(NameDeployTag):
    tag_name: ta.ClassVar[str] = 'app'


@_register_deploy_tag
class DeployConf(NameDeployTag):
    tag_name: ta.ClassVar[str] = 'conf'


##


class KeyDeployTag(DeployTag, abc.ABC):  # noqa
    pass


@_register_deploy_tag
class DeployKey(KeyDeployTag):
    tag_name: ta.ClassVar[str] = 'deploy-key'


@_register_deploy_tag
class DeployAppKey(KeyDeployTag):
    tag_name: ta.ClassVar[str] = 'app-key'


##


class RevDeployTag(DeployTag, abc.ABC):  # noqa
    pass


@_register_deploy_tag
class DeployAppRev(RevDeployTag):
    tag_name: ta.ClassVar[str] = 'app-rev'


##


class DeployTagMap:
    def __init__(
            self,
            *args: DeployTag,
            **kwargs: str,
    ) -> None:
        super().__init__()

        dct: ta.Dict[ta.Type[DeployTag], DeployTag] = {}

        for a in args:
            c = type(check.isinstance(a, DeployTag))
            check.not_in(c, dct)
            dct[c] = a

        for k, v in kwargs.items():
            c = DEPLOY_TAGS_BY_KWARG[k]
            check.not_in(c, dct)
            dct[c] = c(v)

        self._dct = dct
        self._tup = tuple(sorted((type(t).tag_kwarg, t.s) for t in dct.values()))

    #

    def add(self, *args: ta.Any, **kwargs: ta.Any) -> 'DeployTagMap':
        return DeployTagMap(
            *self,
            *args,
            **kwargs,
        )

    def remove(self, *tags_or_names: ta.Union[ta.Type[DeployTag], str]) -> 'DeployTagMap':
        dcs = {
            check.issubclass(a, DeployTag) if isinstance(a, type) else DEPLOY_TAGS_BY_NAME[a]
            for a in tags_or_names
        }

        return DeployTagMap(*[
            t
            for t in self._dct.values()
            if t not in dcs
        ])

    #

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({", ".join(f"{k}={v!r}" for k, v in self._tup)})'

    def __hash__(self) -> int:
        return hash(self._tup)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, DeployTagMap):
            return self._tup == other._tup
        else:
            return NotImplemented

    #

    def __len__(self) -> int:
        return len(self._dct)

    def __iter__(self) -> ta.Iterator[DeployTag]:
        return iter(self._dct.values())

    def __getitem__(self, key: ta.Union[ta.Type[DeployTag], str]) -> DeployTag:
        if isinstance(key, str):
            return self._dct[DEPLOY_TAGS_BY_NAME[key]]
        elif isinstance(key, type):
            return self._dct[key]
        else:
            raise TypeError(key)

    def __contains__(self, key: ta.Union[ta.Type[DeployTag], str]) -> bool:
        if isinstance(key, str):
            return DEPLOY_TAGS_BY_NAME[key] in self._dct
        elif isinstance(key, type):
            return key in self._dct
        else:
            raise TypeError(key)


########################################
# ../marshal.py


@dc.dataclass(frozen=True)
class ObjMarshalerInstaller:
    fn: ta.Callable[[ObjMarshalerManager], None]


ObjMarshalerInstallers = ta.NewType('ObjMarshalerInstallers', ta.Sequence[ObjMarshalerInstaller])


########################################
# ../remote/channel.py


##


class RemoteChannel(abc.ABC):
    @abc.abstractmethod
    def send_obj(self, o: ta.Any, ty: ta.Any = None) -> ta.Awaitable[None]:
        raise NotImplementedError

    @abc.abstractmethod
    def recv_obj(self, ty: ta.Type[T]) -> ta.Awaitable[ta.Optional[T]]:
        raise NotImplementedError

    def set_marshaler(self, msh: ObjMarshalerManager) -> None:  # noqa
        pass


##


class RemoteChannelImpl(RemoteChannel):
    def __init__(
            self,
            input: asyncio.StreamReader,  # noqa
            output: asyncio.StreamWriter,
            *,
            msh: ObjMarshalerManager = OBJ_MARSHALER_MANAGER,
    ) -> None:
        super().__init__()

        self._input = input
        self._output = output
        self._msh = msh

        self._input_lock = asyncio.Lock()
        self._output_lock = asyncio.Lock()

    def set_marshaler(self, msh: ObjMarshalerManager) -> None:
        self._msh = msh

    #

    async def _send_obj(self, o: ta.Any, ty: ta.Any = None) -> None:
        j = json_dumps_compact(self._msh.marshal_obj(o, ty))
        d = j.encode('utf-8')

        self._output.write(struct.pack('<I', len(d)))
        self._output.write(d)
        await self._output.drain()

    async def send_obj(self, o: ta.Any, ty: ta.Any = None) -> None:
        async with self._output_lock:
            return await self._send_obj(o, ty)

    #

    async def _recv_obj(self, ty: ta.Type[T]) -> ta.Optional[T]:
        d = await self._input.read(4)
        if not d:
            return None
        if len(d) != 4:
            raise EOFError

        sz = struct.unpack('<I', d)[0]
        d = await self._input.read(sz)
        if len(d) != sz:
            raise EOFError

        j = json.loads(d.decode('utf-8'))
        return self._msh.unmarshal_obj(j, ty)

    async def recv_obj(self, ty: ta.Type[T]) -> ta.Optional[T]:
        async with self._input_lock:
            return await self._recv_obj(ty)


########################################
# ../system/config.py


@dc.dataclass(frozen=True)
class SystemConfig:
    platform: ta.Optional[Platform] = None


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
# ../bootstrap.py


@dc.dataclass(frozen=True)
class MainBootstrap:
    main_config: MainConfig = MainConfig()

    deploy_config: DeployConfig = DeployConfig()

    remote_config: RemoteConfig = RemoteConfig()

    system_config: SystemConfig = SystemConfig()


########################################
# ../commands/local.py


class LocalCommandExecutor(CommandExecutor):
    def __init__(
            self,
            *,
            command_executors: CommandExecutorMap,
    ) -> None:
        super().__init__()

        self._command_executors = command_executors

    async def execute(self, cmd: Command) -> Command.Output:
        ce: CommandExecutor = self._command_executors[type(cmd)]
        return await ce.execute(cmd)


########################################
# ../deploy/paths/paths.py
"""
TODO:
 - run/{.pid,.sock}
 - logs/...
 - current symlink
 - conf/{nginx,supervisor}
 - env/?
 - apps/<app>/shared
"""


##


class DeployPathError(Exception):
    pass


class DeployPathRenderable(abc.ABC):
    @abc.abstractmethod
    def render(self, tags: ta.Optional[DeployTagMap] = None) -> str:
        raise NotImplementedError


##


class DeployPathNamePart(DeployPathRenderable, abc.ABC):
    @classmethod
    def parse(cls, s: str) -> 'DeployPathNamePart':
        check.non_empty_str(s)
        if s.startswith(DEPLOY_TAG_SIGIL):
            return TagDeployPathNamePart(s[1:])
        elif s in DEPLOY_TAG_DELIMITERS:
            return DelimiterDeployPathNamePart(s)
        else:
            return ConstDeployPathNamePart(s)


@dc.dataclass(frozen=True)
class TagDeployPathNamePart(DeployPathNamePart):
    name: str

    def __post_init__(self) -> None:
        check.in_(self.name, DEPLOY_TAGS_BY_NAME)

    @property
    def tag(self) -> ta.Type[DeployTag]:
        return DEPLOY_TAGS_BY_NAME[self.name]

    def render(self, tags: ta.Optional[DeployTagMap] = None) -> str:
        if tags is not None:
            return tags[self.tag].s
        else:
            return DEPLOY_TAG_SIGIL + self.name


@dc.dataclass(frozen=True)
class DelimiterDeployPathNamePart(DeployPathNamePart):
    delimiter: str

    def __post_init__(self) -> None:
        check.in_(self.delimiter, DEPLOY_TAG_DELIMITERS)

    def render(self, tags: ta.Optional[DeployTagMap] = None) -> str:
        return self.delimiter


@dc.dataclass(frozen=True)
class ConstDeployPathNamePart(DeployPathNamePart):
    const: str

    def __post_init__(self) -> None:
        check.non_empty_str(self.const)
        for c in [*DEPLOY_TAG_DELIMITERS, DEPLOY_TAG_SIGIL, '/']:
            check.not_in(c, self.const)

    def render(self, tags: ta.Optional[DeployTagMap] = None) -> str:
        return self.const


@dc.dataclass(frozen=True)
class DeployPathName(DeployPathRenderable):
    parts: ta.Sequence[DeployPathNamePart]

    def __post_init__(self) -> None:
        hash(self)
        check.not_empty(self.parts)
        for k, g in itertools.groupby(self.parts, type):
            if len(gl := list(g)) > 1:
                raise DeployPathError(f'May not have consecutive path name part types: {k} {gl}')

    def render(self, tags: ta.Optional[DeployTagMap] = None) -> str:
        return ''.join(p.render(tags) for p in self.parts)

    @classmethod
    def parse(cls, s: str) -> 'DeployPathName':
        check.non_empty_str(s)
        check.not_in('/', s)

        i = 0
        ps = []
        while i < len(s):
            ns = [(n, d) for d in DEPLOY_TAG_DELIMITERS if (n := s.find(d, i)) >= 0]
            if not ns:
                ps.append(s[i:])
                break
            n, d = min(ns)
            ps.append(check.non_empty_str(s[i:n]))
            ps.append(s[n:n + len(d)])
            i = n + len(d)

        return cls(tuple(DeployPathNamePart.parse(p) for p in ps))


##


@dc.dataclass(frozen=True)
class DeployPathPart(DeployPathRenderable, abc.ABC):  # noqa
    name: DeployPathName

    @property
    @abc.abstractmethod
    def kind(self) -> DeployPathKind:
        raise NotImplementedError

    def render(self, tags: ta.Optional[DeployTagMap] = None) -> str:
        return self.name.render(tags) + ('/' if self.kind == 'dir' else '')

    @classmethod
    def parse(cls, s: str) -> 'DeployPathPart':
        if (is_dir := s.endswith('/')):
            s = s[:-1]
        check.non_empty_str(s)
        check.not_in('/', s)

        n = DeployPathName.parse(s)
        if is_dir:
            return DirDeployPathPart(n)
        else:
            return FileDeployPathPart(n)


class DirDeployPathPart(DeployPathPart):
    @property
    def kind(self) -> DeployPathKind:
        return 'dir'


class FileDeployPathPart(DeployPathPart):
    @property
    def kind(self) -> DeployPathKind:
        return 'file'


##


@dc.dataclass(frozen=True)
class DeployPath:
    parts: ta.Sequence[DeployPathPart]

    @property
    def name_parts(self) -> ta.Iterator[DeployPathNamePart]:
        for p in self.parts:
            yield from p.name.parts

    def __post_init__(self) -> None:
        hash(self)
        check.not_empty(self.parts)
        for p in self.parts[:-1]:
            check.equal(p.kind, 'dir')

    @cached_nullary
    def tag_indices(self) -> ta.Mapping[ta.Type[DeployTag], ta.Sequence[int]]:
        pd: ta.Dict[ta.Type[DeployTag], ta.List[int]] = {}
        for i, np in enumerate(self.name_parts):
            if isinstance(np, TagDeployPathNamePart):
                pd.setdefault(np.tag, []).append(i)
        return pd

    @property
    def kind(self) -> DeployPathKind:
        return self.parts[-1].kind

    def render(self, tags: ta.Optional[DeployTagMap] = None) -> str:
        return ''.join([p.render(tags) for p in self.parts])

    @classmethod
    def parse(cls, s: str) -> 'DeployPath':
        check.non_empty_str(s)
        ps = split_keep_delimiter(s, '/')
        return cls(tuple(DeployPathPart.parse(p) for p in ps))


########################################
# ../deploy/specs.py


##


def check_valid_deploy_spec_path(s: str) -> str:
    check.non_empty_str(s)
    for c in ['..', '//']:
        check.not_in(c, s)
    check.arg(not s.startswith('/'))
    return s


class DeploySpecKeyed(ta.Generic[KeyDeployTagT]):
    @cached_nullary
    def _key_str(self) -> str:
        return hashlib.sha256(repr(self).encode('utf-8')).hexdigest()[:8]

    @abc.abstractmethod
    def key(self) -> KeyDeployTagT:
        raise NotImplementedError


##


@dc.dataclass(frozen=True)
class DeployGitRepo:
    host: ta.Optional[str] = None
    username: ta.Optional[str] = None
    path: ta.Optional[str] = None

    def __post_init__(self) -> None:
        check.not_in('..', check.non_empty_str(self.host))
        check.not_in('.', check.non_empty_str(self.path))


@dc.dataclass(frozen=True)
class DeployGitSpec:
    repo: DeployGitRepo
    rev: DeployRev

    subtrees: ta.Optional[ta.Sequence[str]] = None

    def __post_init__(self) -> None:
        check.non_empty_str(self.rev)
        if self.subtrees is not None:
            for st in self.subtrees:
                check.non_empty_str(st)


##


@dc.dataclass(frozen=True)
class DeployVenvSpec:
    interp: ta.Optional[str] = None

    requirements_files: ta.Optional[ta.Sequence[str]] = None
    extra_dependencies: ta.Optional[ta.Sequence[str]] = None

    use_uv: bool = False


##


@dc.dataclass(frozen=True)
class DeployAppConfFile:
    path: str
    body: str

    def __post_init__(self) -> None:
        check_valid_deploy_spec_path(self.path)


#


@dc.dataclass(frozen=True)
class DeployAppConfLink:  # noqa
    """
    May be either:
     - @conf(.ext)* - links a single file in root of app conf dir to conf/@conf/@dst(.ext)*
     - @conf/file - links a single file in a single subdir to conf/@conf/@dst--file
     - @conf/ - links a directory in root of app conf dir to conf/@conf/@dst/
    """

    src: str

    kind: ta.Literal['current_only', 'all_active'] = 'current_only'

    def __post_init__(self) -> None:
        check_valid_deploy_spec_path(self.src)
        if '/' in self.src:
            check.equal(self.src.count('/'), 1)


#


@dc.dataclass(frozen=True)
class DeployAppConfSpec:
    files: ta.Optional[ta.Sequence[DeployAppConfFile]] = None

    links: ta.Optional[ta.Sequence[DeployAppConfLink]] = None

    def __post_init__(self) -> None:
        if self.files:
            seen: ta.Set[str] = set()
            for f in self.files:
                check.not_in(f.path, seen)
                seen.add(f.path)


##


@dc.dataclass(frozen=True)
class DeployAppSpec(DeploySpecKeyed[DeployAppKey]):
    app: DeployApp

    git: DeployGitSpec

    venv: ta.Optional[DeployVenvSpec] = None

    conf: ta.Optional[DeployAppConfSpec] = None

    # @ta.override
    def key(self) -> DeployAppKey:
        return DeployAppKey(self._key_str())


##


@dc.dataclass(frozen=True)
class DeploySpec(DeploySpecKeyed[DeployKey]):
    home: DeployHome

    apps: ta.Sequence[DeployAppSpec]

    def __post_init__(self) -> None:
        check.non_empty_str(self.home)

        seen: ta.Set[DeployApp] = set()
        for a in self.apps:
            if a.app in seen:
                raise KeyError(a.app)
            seen.add(a.app)

    # @ta.override
    def key(self) -> DeployKey:
        return DeployKey(self._key_str())


########################################
# ../remote/execution.py
"""
TODO:
 - sequence all messages
"""


##


class _RemoteProtocol:
    class Message(abc.ABC):  # noqa
        async def send(self, chan: RemoteChannel) -> None:
            await chan.send_obj(self, _RemoteProtocol.Message)

        @classmethod
        async def recv(cls: ta.Type[T], chan: RemoteChannel) -> ta.Optional[T]:
            return await chan.recv_obj(cls)

    #

    class Request(Message, abc.ABC):  # noqa
        pass

    @dc.dataclass(frozen=True)
    class CommandRequest(Request):
        seq: int
        cmd: Command

    @dc.dataclass(frozen=True)
    class PingRequest(Request):
        time: float

    #

    class Response(Message, abc.ABC):  # noqa
        pass

    @dc.dataclass(frozen=True)
    class LogResponse(Response):
        s: str

    @dc.dataclass(frozen=True)
    class CommandResponse(Response):
        seq: int
        res: CommandOutputOrExceptionData

    @dc.dataclass(frozen=True)
    class PingResponse(Response):
        time: float


##


class _RemoteLogHandler(logging.Handler):
    def __init__(
            self,
            chan: RemoteChannel,
            loop: ta.Any = None,
    ) -> None:
        super().__init__()

        self._chan = chan
        self._loop = loop

    def emit(self, record):
        msg = self.format(record)

        async def inner():
            await _RemoteProtocol.LogResponse(msg).send(self._chan)

        loop = self._loop
        if loop is None:
            loop = asyncio.get_running_loop()
        if loop is not None:
            asyncio.run_coroutine_threadsafe(inner(), loop)


##


class _RemoteCommandHandler:
    DEFAULT_PING_INTERVAL_S: float = 3.

    def __init__(
            self,
            chan: RemoteChannel,
            executor: CommandExecutor,
            *,
            stop: ta.Optional[asyncio.Event] = None,
            ping_interval_s: float = DEFAULT_PING_INTERVAL_S,
    ) -> None:
        super().__init__()

        self._chan = chan
        self._executor = executor
        self._stop = stop if stop is not None else asyncio.Event()
        self._ping_interval_s = ping_interval_s

        self._cmds_by_seq: ta.Dict[int, _RemoteCommandHandler._Command] = {}

        self._last_ping_send: float = 0.
        self._ping_in_flight: bool = False
        self._last_ping_recv: ta.Optional[float] = None

    def stop(self) -> None:
        self._stop.set()

    @dc.dataclass(frozen=True)
    class _Command:
        req: _RemoteProtocol.CommandRequest
        fut: asyncio.Future

    async def run(self) -> None:
        log.debug('_RemoteCommandHandler loop start: %r', self)

        stop_task = asyncio.create_task(self._stop.wait())
        recv_task: ta.Optional[asyncio.Task] = None

        while not self._stop.is_set():
            if recv_task is None:
                recv_task = asyncio.create_task(_RemoteProtocol.Message.recv(self._chan))

            if not self._ping_in_flight:
                if not self._last_ping_recv:
                    ping_wait_time = 0.
                else:
                    ping_wait_time = self._ping_interval_s - (time.time() - self._last_ping_recv)
            else:
                ping_wait_time = float('inf')
            wait_time = min(self._ping_interval_s, ping_wait_time)
            log.debug('_RemoteCommandHandler loop wait: %f', wait_time)

            done, pending = await asyncio.wait(
                [
                    stop_task,
                    recv_task,
                ],
                return_when=asyncio.FIRST_COMPLETED,
                timeout=wait_time,
            )

            #

            if (
                    (time.time() - self._last_ping_send >= self._ping_interval_s) and
                    not self._ping_in_flight
            ):
                now = time.time()
                self._last_ping_send = now
                self._ping_in_flight = True
                await _RemoteProtocol.PingRequest(
                    time=now,
                ).send(self._chan)

            #

            if recv_task in done:
                msg: ta.Optional[_RemoteProtocol.Message] = check.isinstance(
                    recv_task.result(),
                    (_RemoteProtocol.Message, type(None)),
                )
                recv_task = None

                if msg is None:
                    break

                await self._handle_message(msg)

        log.debug('_RemoteCommandHandler loop stopping: %r', self)

        for task in [
            stop_task,
            recv_task,
        ]:
            if task is not None and not task.done():
                task.cancel()

        for cmd in self._cmds_by_seq.values():
            cmd.fut.cancel()

        log.debug('_RemoteCommandHandler loop exited: %r', self)

    async def _handle_message(self, msg: _RemoteProtocol.Message) -> None:
        if isinstance(msg, _RemoteProtocol.PingRequest):
            log.debug('Ping: %r', msg)
            await _RemoteProtocol.PingResponse(
                time=msg.time,
            ).send(self._chan)

        elif isinstance(msg, _RemoteProtocol.PingResponse):
            latency_s = time.time() - msg.time
            log.debug('Pong: %0.2f ms %r', latency_s * 1000., msg)
            self._last_ping_recv = time.time()
            self._ping_in_flight = False

        elif isinstance(msg, _RemoteProtocol.CommandRequest):
            fut = asyncio.create_task(self._handle_command_request(msg))
            self._cmds_by_seq[msg.seq] = _RemoteCommandHandler._Command(
                req=msg,
                fut=fut,
            )

        else:
            raise TypeError(msg)

    async def _handle_command_request(self, req: _RemoteProtocol.CommandRequest) -> None:
        res = await self._executor.try_execute(
            req.cmd,
            log=log,
            omit_exc_object=True,
        )

        await _RemoteProtocol.CommandResponse(
            seq=req.seq,
            res=CommandOutputOrExceptionData(
                output=res.output,
                exception=res.exception,
            ),
        ).send(self._chan)

        self._cmds_by_seq.pop(req.seq)  # noqa


##


@dc.dataclass()
class RemoteCommandError(Exception):
    e: CommandException


class RemoteCommandExecutor(CommandExecutor):
    def __init__(self, chan: RemoteChannel) -> None:
        super().__init__()

        self._chan = chan

        self._cmd_seq = itertools.count()
        self._queue: asyncio.Queue = asyncio.Queue()  # asyncio.Queue[RemoteCommandExecutor._Request]
        self._stop = asyncio.Event()
        self._loop_task: ta.Optional[asyncio.Task] = None
        self._reqs_by_seq: ta.Dict[int, RemoteCommandExecutor._Request] = {}

    #

    async def start(self) -> None:
        check.none(self._loop_task)
        check.state(not self._stop.is_set())
        self._loop_task = asyncio.create_task(self._loop())

    async def aclose(self) -> None:
        self._stop.set()
        if self._loop_task is not None:
            await self._loop_task

    #

    @dc.dataclass(frozen=True)
    class _Request:
        seq: int
        cmd: Command
        fut: asyncio.Future

    async def _loop(self) -> None:
        log.debug('RemoteCommandExecutor loop start: %r', self)

        stop_task = asyncio.create_task(self._stop.wait())
        queue_task: ta.Optional[asyncio.Task] = None
        recv_task: ta.Optional[asyncio.Task] = None

        while not self._stop.is_set():
            if queue_task is None:
                queue_task = asyncio.create_task(self._queue.get())
            if recv_task is None:
                recv_task = asyncio.create_task(_RemoteProtocol.Message.recv(self._chan))

            done, pending = await asyncio.wait(
                [
                    stop_task,
                    queue_task,
                    recv_task,
                ],
                return_when=asyncio.FIRST_COMPLETED,
            )

            #

            if queue_task in done:
                req = check.isinstance(queue_task.result(), RemoteCommandExecutor._Request)
                queue_task = None
                await self._handle_queued_request(req)

            #

            if recv_task in done:
                msg: ta.Optional[_RemoteProtocol.Message] = check.isinstance(
                    recv_task.result(),
                    (_RemoteProtocol.Message, type(None)),
                )
                recv_task = None

                if msg is None:
                    log.debug('RemoteCommandExecutor got eof: %r', self)
                    break

                await self._handle_message(msg)

        log.debug('RemoteCommandExecutor loop stopping: %r', self)

        for task in [
            stop_task,
            queue_task,
            recv_task,
        ]:
            if task is not None and not task.done():
                task.cancel()

        for req in self._reqs_by_seq.values():
            req.fut.cancel()

        log.debug('RemoteCommandExecutor loop exited: %r', self)

    async def _handle_queued_request(self, req: _Request) -> None:
        self._reqs_by_seq[req.seq] = req
        await _RemoteProtocol.CommandRequest(
            seq=req.seq,
            cmd=req.cmd,
        ).send(self._chan)

    async def _handle_message(self, msg: _RemoteProtocol.Message) -> None:
        if isinstance(msg, _RemoteProtocol.PingRequest):
            log.debug('Ping: %r', msg)
            await _RemoteProtocol.PingResponse(
                time=msg.time,
            ).send(self._chan)

        elif isinstance(msg, _RemoteProtocol.PingResponse):
            latency_s = time.time() - msg.time
            log.debug('Pong: %0.2f ms %r', latency_s * 1000., msg)

        elif isinstance(msg, _RemoteProtocol.LogResponse):
            log.info(msg.s)

        elif isinstance(msg, _RemoteProtocol.CommandResponse):
            req = self._reqs_by_seq.pop(msg.seq)
            req.fut.set_result(msg.res)

        else:
            raise TypeError(msg)

    #

    async def _remote_execute(self, cmd: Command) -> CommandOutputOrException:
        req = RemoteCommandExecutor._Request(
            seq=next(self._cmd_seq),
            cmd=cmd,
            fut=asyncio.Future(),
        )
        await self._queue.put(req)
        return await req.fut

    # @ta.override
    async def execute(self, cmd: Command) -> Command.Output:
        r = await self._remote_execute(cmd)
        if (e := r.exception) is not None:
            raise RemoteCommandError(e)
        else:
            return check.not_none(r.output)

    # @ta.override
    async def try_execute(
            self,
            cmd: Command,
            *,
            log: ta.Optional[logging.Logger] = None,  # noqa
            omit_exc_object: bool = False,
    ) -> CommandOutputOrException:
        try:
            r = await self._remote_execute(cmd)

        except Exception as e:  # noqa
            if log is not None:
                log.exception('Exception executing remote command: %r', type(cmd))

            return CommandOutputOrExceptionData(exception=CommandException.of(
                e,
                omit_exc_object=omit_exc_object,
                cmd=cmd,
            ))

        else:
            return r


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
# ../../../omdev/interp/inspect.py


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
                if log.isEnabledFor(logging.DEBUG):
                    log.exception('Failed to inspect interp: %s', exe)
                ret = None
            self._cache[exe] = ret
            return ret


INTERP_INSPECTOR = InterpInspector()


########################################
# ../commands/subprocess.py


##


@dc.dataclass(frozen=True)
class SubprocessCommand(Command['SubprocessCommand.Output']):
    cmd: ta.Sequence[str]

    shell: bool = False
    cwd: ta.Optional[str] = None
    env: ta.Optional[ta.Mapping[str, str]] = None

    stdout: str = 'pipe'  # SubprocessChannelOption
    stderr: str = 'pipe'  # SubprocessChannelOption

    input: ta.Optional[bytes] = None
    timeout: ta.Optional[float] = None

    def __post_init__(self) -> None:
        check.not_isinstance(self.cmd, str)

    @dc.dataclass(frozen=True)
    class Output(Command.Output):
        rc: int
        pid: int

        elapsed_s: float

        stdout: ta.Optional[bytes] = None
        stderr: ta.Optional[bytes] = None


class SubprocessCommandExecutor(CommandExecutor[SubprocessCommand, SubprocessCommand.Output]):
    async def execute(self, cmd: SubprocessCommand) -> SubprocessCommand.Output:
        proc: asyncio.subprocess.Process
        async with asyncio_subprocesses.popen(
            *subprocess_maybe_shell_wrap_exec(*cmd.cmd),

            shell=cmd.shell,
            cwd=cmd.cwd,
            env={**os.environ, **(cmd.env or {})},

            stdin=subprocess.PIPE if cmd.input is not None else None,
            stdout=SUBPROCESS_CHANNEL_OPTION_VALUES[ta.cast(SubprocessChannelOption, cmd.stdout)],
            stderr=SUBPROCESS_CHANNEL_OPTION_VALUES[ta.cast(SubprocessChannelOption, cmd.stderr)],

            timeout=cmd.timeout,
        ) as proc:
            start_time = time.time()
            stdout, stderr = await asyncio_subprocesses.communicate(
                proc,
                input=cmd.input,
                timeout=cmd.timeout,
            )
            end_time = time.time()

        return SubprocessCommand.Output(
            rc=check.not_none(proc.returncode),
            pid=proc.pid,

            elapsed_s=end_time - start_time,

            stdout=stdout,  # noqa
            stderr=stderr,  # noqa
        )


########################################
# ../deploy/conf.py
"""
TODO:
 - @conf DeployPathPlaceholder? :|
 - post-deploy: remove any dir_links not present in new spec
  - * only if succeeded * - otherwise, remove any dir_links present in new spec but not previously present?
   - no such thing as 'previously present'.. build a 'deploy state' and pass it back?
 - ** whole thing can be atomic **
  - 1) new atomic temp dir
  - 2) for each subdir not needing modification, hardlink into temp dir
  - 3) for each subdir needing modification, new subdir, hardlink all files not needing modification
  - 4) write (or if deleting, omit) new files
  - 5) swap top level
 - ** whole deploy can be atomic(-ish) - do this for everything **
  - just a '/deploy/current' dir
  - some things (venvs) cannot be moved, thus the /deploy/venvs dir
  - ** ensure (enforce) equivalent relpath nesting
"""


class DeployConfManager:
    async def _write_app_conf_file(
            self,
            acf: DeployAppConfFile,
            app_conf_dir: str,
    ) -> None:
        conf_file = os.path.join(app_conf_dir, acf.path)
        check.arg(is_path_in_dir(app_conf_dir, conf_file))

        os.makedirs(os.path.dirname(conf_file), exist_ok=True)

        with open(conf_file, 'w') as f:  # noqa
            f.write(acf.body)

    #

    class _ComputedConfLink(ta.NamedTuple):
        conf: DeployConf
        is_dir: bool
        link_src: str
        link_dst: str

    _UNIQUE_LINK_NAME_STR = '@app--@time--@app-key'
    _UNIQUE_LINK_NAME = DeployPath.parse(_UNIQUE_LINK_NAME_STR)

    @classmethod
    def _compute_app_conf_link_dst(
            cls,
            link: DeployAppConfLink,
            tags: DeployTagMap,
            app_conf_dir: str,
            conf_link_dir: str,
    ) -> _ComputedConfLink:
        link_src = os.path.join(app_conf_dir, link.src)
        check.arg(is_path_in_dir(app_conf_dir, link_src))

        #

        if (is_dir := link.src.endswith('/')):
            # @conf/ - links a directory in root of app conf dir to conf/@conf/@dst/
            check.arg(link.src.count('/') == 1)
            conf = DeployConf(link.src.split('/')[0])
            link_dst_pfx = link.src
            link_dst_sfx = ''

        elif '/' in link.src:
            # @conf/file - links a single file in a single subdir to conf/@conf/@dst--file
            d, f = os.path.split(link.src)
            # TODO: check filename :|
            conf = DeployConf(d)
            link_dst_pfx = d + '/'
            link_dst_sfx = DEPLOY_TAG_SEPARATOR + f

        else:  # noqa
            # @conf(.ext)* - links a single file in root of app conf dir to conf/@conf/@dst(.ext)*
            if '.' in link.src:
                l, _, r = link.src.partition('.')
                conf = DeployConf(l)
                link_dst_pfx = l + '/'
                link_dst_sfx = '.' + r
            else:
                conf = DeployConf(link.src)
                link_dst_pfx = link.src + '/'
                link_dst_sfx = ''

        #

        if link.kind == 'current_only':
            link_dst_mid = str(tags[DeployApp].s)
        elif link.kind == 'all_active':
            link_dst_mid = cls._UNIQUE_LINK_NAME.render(tags)
        else:
            raise TypeError(link)

        #

        link_dst_name = ''.join([
            link_dst_pfx,
            link_dst_mid,
            link_dst_sfx,
        ])
        link_dst = os.path.join(conf_link_dir, link_dst_name)

        return DeployConfManager._ComputedConfLink(
            conf=conf,
            is_dir=is_dir,
            link_src=link_src,
            link_dst=link_dst,
        )

    async def _make_app_conf_link(
            self,
            link: DeployAppConfLink,
            tags: DeployTagMap,
            app_conf_dir: str,
            conf_link_dir: str,
    ) -> None:
        comp = self._compute_app_conf_link_dst(
            link,
            tags,
            app_conf_dir,
            conf_link_dir,
        )

        #

        check.arg(is_path_in_dir(app_conf_dir, comp.link_src))
        check.arg(is_path_in_dir(conf_link_dir, comp.link_dst))

        if comp.is_dir:
            check.arg(os.path.isdir(comp.link_src))
        else:
            check.arg(os.path.isfile(comp.link_src))

        #

        relative_symlink(  # noqa
            comp.link_src,
            comp.link_dst,
            target_is_directory=comp.is_dir,
            make_dirs=True,
        )

    #

    async def write_app_conf(
            self,
            spec: DeployAppConfSpec,
            tags: DeployTagMap,
            app_conf_dir: str,
            conf_link_dir: str,
    ) -> None:
        for acf in spec.files or []:
            await self._write_app_conf_file(
                acf,
                app_conf_dir,
            )

        #

        for link in spec.links or []:
            await self._make_app_conf_link(
                link,
                tags,
                app_conf_dir,
                conf_link_dir,
            )


########################################
# ../deploy/paths/owners.py


class DeployPathOwner(abc.ABC):
    @abc.abstractmethod
    def get_owned_deploy_paths(self) -> ta.AbstractSet[DeployPath]:
        raise NotImplementedError


DeployPathOwners = ta.NewType('DeployPathOwners', ta.Sequence[DeployPathOwner])


class SingleDirDeployPathOwner(DeployPathOwner, abc.ABC):
    def __init__(
            self,
            *args: ta.Any,
            owned_dir: str,
            **kwargs: ta.Any,
    ) -> None:
        super().__init__(*args, **kwargs)

        check.not_in('/', owned_dir)
        self._owned_dir: str = check.non_empty_str(owned_dir)

        self._owned_deploy_paths = frozenset([DeployPath.parse(self._owned_dir + '/')])

    def _dir(self, home: DeployHome) -> str:
        return os.path.join(check.non_empty_str(home), self._owned_dir)

    def _make_dir(self, home: DeployHome) -> str:
        if not os.path.isdir(d := self._dir(home)):
            os.makedirs(d, exist_ok=True)
        return d

    def get_owned_deploy_paths(self) -> ta.AbstractSet[DeployPath]:
        return self._owned_deploy_paths


########################################
# ../remote/_main.py


##


class _RemoteExecutionLogHandler(logging.Handler):
    def __init__(self, fn: ta.Callable[[str], None]) -> None:
        super().__init__()
        self._fn = fn

    def emit(self, record):
        msg = self.format(record)
        self._fn(msg)


##


class _RemoteExecutionMain:
    def __init__(
            self,
            chan: RemoteChannel,
    ) -> None:
        super().__init__()

        self._chan = chan

        self.__bootstrap: ta.Optional[MainBootstrap] = None
        self.__injector: ta.Optional[Injector] = None

    @property
    def _bootstrap(self) -> MainBootstrap:
        return check.not_none(self.__bootstrap)

    @property
    def _injector(self) -> Injector:
        return check.not_none(self.__injector)

    #

    def _timebomb_main(
            self,
            delay_s: float,
            *,
            sig: int = signal.SIGINT,
            code: int = 1,
    ) -> None:
        time.sleep(delay_s)

        if (pgid := os.getpgid(0)) == os.getpid():
            os.killpg(pgid, sig)

        os._exit(code)  # noqa

    @cached_nullary
    def _timebomb_thread(self) -> ta.Optional[threading.Thread]:
        if (tbd := self._bootstrap.remote_config.timebomb_delay_s) is None:
            return None

        thr = threading.Thread(
            target=functools.partial(self._timebomb_main, tbd),
            name=f'{self.__class__.__name__}.timebomb',
            daemon=True,
        )

        thr.start()

        log.debug('Started timebomb thread: %r', thr)

        return thr

    #

    @cached_nullary
    def _log_handler(self) -> _RemoteLogHandler:
        return _RemoteLogHandler(self._chan)

    #

    async def _setup(self) -> None:
        check.none(self.__bootstrap)
        check.none(self.__injector)

        # Bootstrap

        self.__bootstrap = check.not_none(await self._chan.recv_obj(MainBootstrap))

        if (prd := self._bootstrap.remote_config.pycharm_remote_debug) is not None:
            pycharm_debug_connect(prd)

        self.__injector = main_bootstrap(self._bootstrap)

        self._chan.set_marshaler(self._injector[ObjMarshalerManager])

        # Post-bootstrap

        if self._bootstrap.remote_config.set_pgid:
            if os.getpgid(0) != os.getpid():
                log.debug('Setting pgid')
                os.setpgid(0, 0)

        if (ds := self._bootstrap.remote_config.deathsig) is not None:
            log.debug('Setting deathsig: %s', ds)
            set_process_deathsig(int(signal.Signals[f'SIG{ds.upper()}']))

        self._timebomb_thread()

        if self._bootstrap.remote_config.forward_logging:
            log.debug('Installing log forwarder')
            logging.root.addHandler(self._log_handler())

    #

    async def run(self) -> None:
        await self._setup()

        executor = self._injector[LocalCommandExecutor]

        handler = _RemoteCommandHandler(self._chan, executor)

        await handler.run()


def _remote_execution_main() -> None:
    rt = pyremote_bootstrap_finalize()  # noqa

    async def inner() -> None:
        input = await asyncio_open_stream_reader(rt.input)  # noqa
        output = await asyncio_open_stream_writer(rt.output)

        chan = RemoteChannelImpl(
            input,
            output,
        )

        await _RemoteExecutionMain(chan).run()

    asyncio.run(inner())


########################################
# ../remote/spawning.py


##


class RemoteSpawning(abc.ABC):
    @dc.dataclass(frozen=True)
    class Target:
        shell: ta.Optional[str] = None
        shell_quote: bool = False

        DEFAULT_PYTHON: ta.ClassVar[ta.Sequence[str]] = ('python3',)
        python: ta.Sequence[str] = DEFAULT_PYTHON

        stderr: ta.Optional[str] = None  # SubprocessChannelOption

        def __post_init__(self) -> None:
            check.not_isinstance(self.python, str)

    @dc.dataclass(frozen=True)
    class Spawned:
        stdin: asyncio.StreamWriter
        stdout: asyncio.StreamReader
        stderr: ta.Optional[asyncio.StreamReader]

    @abc.abstractmethod
    def spawn(
            self,
            tgt: Target,
            src: str,
            *,
            timeout: ta.Optional[float] = None,
            debug: bool = False,
    ) -> ta.AsyncContextManager[Spawned]:
        raise NotImplementedError


##


class SubprocessRemoteSpawning(RemoteSpawning):
    class _PreparedCmd(ta.NamedTuple):  # noqa
        cmd: ta.Sequence[str]
        shell: bool

    def _prepare_cmd(
            self,
            tgt: RemoteSpawning.Target,
            src: str,
    ) -> _PreparedCmd:
        if tgt.shell is not None:
            sh_src = ' '.join([
                *map(shlex_maybe_quote, tgt.python),
                '-c',
                shlex_maybe_quote(src),
            ])
            if tgt.shell_quote:
                sh_src = shlex.quote(sh_src)
            sh_cmd = f'{tgt.shell} {sh_src}'
            return SubprocessRemoteSpawning._PreparedCmd([sh_cmd], shell=True)

        else:
            return SubprocessRemoteSpawning._PreparedCmd([*tgt.python, '-c', src], shell=False)

    #

    @contextlib.asynccontextmanager
    async def spawn(
            self,
            tgt: RemoteSpawning.Target,
            src: str,
            *,
            timeout: ta.Optional[float] = None,
            debug: bool = False,
    ) -> ta.AsyncGenerator[RemoteSpawning.Spawned, None]:
        pc = self._prepare_cmd(tgt, src)

        async with asyncio_subprocesses.popen(
                *pc.cmd,
                shell=pc.shell,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=(
                    SUBPROCESS_CHANNEL_OPTION_VALUES[ta.cast(SubprocessChannelOption, tgt.stderr)]
                    if tgt.stderr is not None else None
                ),
                timeout=timeout,
        ) as proc:
            stdin = check.not_none(proc.stdin)
            stdout = check.not_none(proc.stdout)

            try:
                yield RemoteSpawning.Spawned(
                    stdin=stdin,
                    stdout=stdout,
                    stderr=proc.stderr,
                )

            finally:
                try:
                    stdin.close()
                except BrokenPipeError:
                    pass


########################################
# ../system/packages.py
"""
TODO:
 - yum/rpm
"""


@dc.dataclass(frozen=True)
class SystemPackage:
    name: str
    version: ta.Optional[str] = None


class SystemPackageManager(abc.ABC):
    @abc.abstractmethod
    def update(self) -> ta.Awaitable[None]:
        raise NotImplementedError

    @abc.abstractmethod
    def upgrade(self) -> ta.Awaitable[None]:
        raise NotImplementedError

    @abc.abstractmethod
    def install(self, *packages: SystemPackageOrStr) -> ta.Awaitable[None]:
        raise NotImplementedError

    @abc.abstractmethod
    def query(self, *packages: SystemPackageOrStr) -> ta.Awaitable[ta.Mapping[str, SystemPackage]]:
        raise NotImplementedError


class BrewSystemPackageManager(SystemPackageManager):
    async def update(self) -> None:
        await asyncio_subprocesses.check_call('brew', 'update')

    async def upgrade(self) -> None:
        await asyncio_subprocesses.check_call('brew', 'upgrade')

    async def install(self, *packages: SystemPackageOrStr) -> None:
        es: ta.List[str] = []
        for p in packages:
            if isinstance(p, SystemPackage):
                es.append(p.name + (f'@{p.version}' if p.version is not None else ''))
            else:
                es.append(p)
        await asyncio_subprocesses.check_call('brew', 'install', *es)

    async def query(self, *packages: SystemPackageOrStr) -> ta.Mapping[str, SystemPackage]:
        pns = [p.name if isinstance(p, SystemPackage) else p for p in packages]
        o = await asyncio_subprocesses.check_output('brew', 'info', '--json', *pns)
        j = json.loads(o.decode())
        d: ta.Dict[str, SystemPackage] = {}
        for e in j:
            if not e['installed']:
                continue
            d[e['name']] = SystemPackage(
                name=e['name'],
                version=e['installed'][0]['version'],
            )
        return d


class AptSystemPackageManager(SystemPackageManager):
    _APT_ENV: ta.ClassVar[ta.Mapping[str, str]] = {
        'DEBIAN_FRONTEND': 'noninteractive',
    }

    async def update(self) -> None:
        await asyncio_subprocesses.check_call('sudo', 'apt', 'update', env={**os.environ, **self._APT_ENV})

    async def upgrade(self) -> None:
        await asyncio_subprocesses.check_call('sudo', 'apt', 'upgrade', '-y', env={**os.environ, **self._APT_ENV})

    async def install(self, *packages: SystemPackageOrStr) -> None:
        pns = [p.name if isinstance(p, SystemPackage) else p for p in packages]  # FIXME: versions
        await asyncio_subprocesses.check_call('sudo', 'apt', 'install', '-y', *pns, env={**os.environ, **self._APT_ENV})

    async def query(self, *packages: SystemPackageOrStr) -> ta.Mapping[str, SystemPackage]:
        pns = [p.name if isinstance(p, SystemPackage) else p for p in packages]
        out = await asyncio_subprocesses.run(
            'dpkg-query', '-W', '-f=${Package}=${Version}\n', *pns,
            capture_output=True,
            check=False,
        )
        d: ta.Dict[str, SystemPackage] = {}
        for l in check.not_none(out.stdout).decode('utf-8').strip().splitlines():
            n, v = l.split('=', 1)
            d[n] = SystemPackage(
                name=n,
                version=v,
            )
        return d


class YumSystemPackageManager(SystemPackageManager):
    async def update(self) -> None:
        await asyncio_subprocesses.check_call('sudo', 'yum', 'check-update')

    async def upgrade(self) -> None:
        await asyncio_subprocesses.check_call('sudo', 'yum', 'update')

    async def install(self, *packages: SystemPackageOrStr) -> None:
        pns = [p.name if isinstance(p, SystemPackage) else p for p in packages]  # FIXME: versions
        await asyncio_subprocesses.check_call('sudo', 'yum', 'install', *pns)

    async def query(self, *packages: SystemPackageOrStr) -> ta.Mapping[str, SystemPackage]:
        pns = [p.name if isinstance(p, SystemPackage) else p for p in packages]
        d: ta.Dict[str, SystemPackage] = {}
        for pn in pns:
            out = await asyncio_subprocesses.run(
                'rpm', '-q', pn,
                capture_output=True,
            )
            if not out.proc.returncode:
                d[pn] = SystemPackage(
                    pn,
                    check.not_none(out.stdout).decode().strip(),
                )
        return d


########################################
# ../../../omdev/interp/providers.py
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


##


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
# ../commands/inject.py


##


def bind_command(
        command_cls: ta.Type[Command],
        executor_cls: ta.Optional[ta.Type[CommandExecutor]],
) -> InjectorBindings:
    lst: ta.List[InjectorBindingOrBindings] = [
        inj.bind(CommandRegistration(command_cls), array=True),
    ]

    if executor_cls is not None:
        lst.extend([
            inj.bind(executor_cls, singleton=True),
            inj.bind(CommandExecutorRegistration(command_cls, executor_cls), array=True),
        ])

    return inj.as_bindings(*lst)


##


@dc.dataclass(frozen=True)
class _FactoryCommandExecutor(CommandExecutor):
    factory: ta.Callable[[], CommandExecutor]

    def execute(self, i: Command) -> ta.Awaitable[Command.Output]:
        return self.factory().execute(i)


##


def bind_commands(
        *,
        main_config: MainConfig,
) -> InjectorBindings:
    lst: ta.List[InjectorBindingOrBindings] = [
        inj.bind_array(CommandRegistration),
        inj.bind_array_type(CommandRegistration, CommandRegistrations),

        inj.bind_array(CommandExecutorRegistration),
        inj.bind_array_type(CommandExecutorRegistration, CommandExecutorRegistrations),

        inj.bind(build_command_name_map, singleton=True),
    ]

    #

    def provide_obj_marshaler_installer(cmds: CommandNameMap) -> ObjMarshalerInstaller:
        return ObjMarshalerInstaller(functools.partial(install_command_marshaling, cmds))

    lst.append(inj.bind(provide_obj_marshaler_installer, array=True))

    #

    def provide_command_executor_map(
            injector: Injector,
            crs: CommandExecutorRegistrations,
    ) -> CommandExecutorMap:
        dct: ta.Dict[ta.Type[Command], CommandExecutor] = {}

        cr: CommandExecutorRegistration
        for cr in crs:
            if cr.command_cls in dct:
                raise KeyError(cr.command_cls)

            factory = functools.partial(injector.provide, cr.executor_cls)
            if main_config.debug:
                ce = factory()
            else:
                ce = _FactoryCommandExecutor(factory)

            dct[cr.command_cls] = ce

        return CommandExecutorMap(dct)

    lst.extend([
        inj.bind(provide_command_executor_map, singleton=True),

        inj.bind(LocalCommandExecutor, singleton=True, eager=main_config.debug),
    ])

    #

    lst.extend([
        bind_command(PingCommand, PingCommandExecutor),
        bind_command(SubprocessCommand, SubprocessCommandExecutor),
    ])

    #

    return inj.as_bindings(*lst)


########################################
# ../deploy/paths/manager.py


class DeployPathsManager:
    def __init__(
            self,
            *,
            deploy_path_owners: DeployPathOwners,
    ) -> None:
        super().__init__()

        self._deploy_path_owners = deploy_path_owners

    @cached_nullary
    def owners_by_path(self) -> ta.Mapping[DeployPath, DeployPathOwner]:
        dct: ta.Dict[DeployPath, DeployPathOwner] = {}
        for o in self._deploy_path_owners:
            for p in o.get_owned_deploy_paths():
                if p in dct:
                    raise DeployPathError(f'Duplicate deploy path owner: {p}')
                dct[p] = o
        return dct

    def validate_deploy_paths(self) -> None:
        self.owners_by_path()


########################################
# ../deploy/tmp.py


class DeployHomeAtomics(Func1[DeployHome, AtomicPathSwapping]):
    pass


class DeployTmpManager(
    SingleDirDeployPathOwner,
):
    def __init__(self) -> None:
        super().__init__(
            owned_dir='tmp',
        )

    def get_swapping(self, home: DeployHome) -> AtomicPathSwapping:
        return TempDirAtomicPathSwapping(
            temp_dir=self._make_dir(home),
            root_dir=check.non_empty_str(home),
        )


########################################
# ../remote/connection.py


##


class PyremoteRemoteExecutionConnector:
    def __init__(
            self,
            *,
            spawning: RemoteSpawning,
            msh: ObjMarshalerManager,
            payload_file: ta.Optional[RemoteExecutionPayloadFile] = None,
    ) -> None:
        super().__init__()

        self._spawning = spawning
        self._msh = msh
        self._payload_file = payload_file

    #

    @cached_nullary
    def _payload_src(self) -> str:
        return get_remote_payload_src(file=self._payload_file)

    @cached_nullary
    def _remote_src(self) -> ta.Sequence[str]:
        return [
            self._payload_src(),
            '_remote_execution_main()',
        ]

    @cached_nullary
    def _spawn_src(self) -> str:
        return pyremote_build_bootstrap_cmd(__package__ or 'manage')

    #

    @contextlib.asynccontextmanager
    async def connect(
            self,
            tgt: RemoteSpawning.Target,
            bs: MainBootstrap,
    ) -> ta.AsyncGenerator[RemoteCommandExecutor, None]:
        spawn_src = self._spawn_src()
        remote_src = self._remote_src()

        async with self._spawning.spawn(
                tgt,
                spawn_src,
                debug=bs.main_config.debug,
        ) as proc:
            res = await PyremoteBootstrapDriver(  # noqa
                remote_src,
                PyremoteBootstrapOptions(
                    debug=bs.main_config.debug,
                ),
            ).async_run(
                proc.stdout,
                proc.stdin,
            )

            chan = RemoteChannelImpl(
                proc.stdout,
                proc.stdin,
                msh=self._msh,
            )

            await chan.send_obj(bs)

            rce: RemoteCommandExecutor
            async with aclosing(RemoteCommandExecutor(chan)) as rce:
                await rce.start()

                yield rce


##


class InProcessRemoteExecutionConnector:
    def __init__(
            self,
            *,
            msh: ObjMarshalerManager,
            local_executor: LocalCommandExecutor,
    ) -> None:
        super().__init__()

        self._msh = msh
        self._local_executor = local_executor

    @contextlib.asynccontextmanager
    async def connect(self) -> ta.AsyncGenerator[RemoteCommandExecutor, None]:
        r0, w0 = asyncio_create_bytes_channel()
        r1, w1 = asyncio_create_bytes_channel()

        remote_chan = RemoteChannelImpl(r0, w1, msh=self._msh)
        local_chan = RemoteChannelImpl(r1, w0, msh=self._msh)

        rch = _RemoteCommandHandler(
            remote_chan,
            self._local_executor,
        )
        rch_task = asyncio.create_task(rch.run())  # noqa
        try:
            rce: RemoteCommandExecutor
            async with aclosing(RemoteCommandExecutor(local_chan)) as rce:
                await rce.start()

                yield rce

        finally:
            rch.stop()
            await rch_task


########################################
# ../system/commands.py


##


@dc.dataclass(frozen=True)
class CheckSystemPackageCommand(Command['CheckSystemPackageCommand.Output']):
    pkgs: ta.Sequence[str] = ()

    def __post_init__(self) -> None:
        check.not_isinstance(self.pkgs, str)

    @dc.dataclass(frozen=True)
    class Output(Command.Output):
        pkgs: ta.Sequence[SystemPackage]


class CheckSystemPackageCommandExecutor(CommandExecutor[CheckSystemPackageCommand, CheckSystemPackageCommand.Output]):
    def __init__(
            self,
            *,
            mgr: SystemPackageManager,
    ) -> None:
        super().__init__()

        self._mgr = mgr

    async def execute(self, cmd: CheckSystemPackageCommand) -> CheckSystemPackageCommand.Output:
        log.info('Checking system package!')

        ret = await self._mgr.query(*cmd.pkgs)

        return CheckSystemPackageCommand.Output(list(ret.values()))


########################################
# ../../../omdev/interp/pyenv.py
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
            install_name: ta.Optional[str] = None,
            no_default_opts: bool = False,
            pyenv: Pyenv = Pyenv(),
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


##


class PyenvInterpProvider(InterpProvider):
    def __init__(
            self,
            pyenv: Pyenv = Pyenv(),

            inspect: bool = False,
            inspector: InterpInspector = INTERP_INSPECTOR,

            *,

            try_update: bool = False,
    ) -> None:
        super().__init__()

        self._pyenv = pyenv

        self._inspect = inspect
        self._inspector = inspector

        self._try_update = try_update

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
        if self._inspect:
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
                log.debug('Invalid pyenv version: %s', vn)
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

        if self._try_update and not any(v in spec for v in lst):
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
        )

        exe = await installer.install()
        return Interp(exe, version)


########################################
# ../../../omdev/interp/system.py
"""
TODO:
 - python, python3, python3.12, ...
 - check if path py's are venvs: sys.prefix != sys.base_prefix
"""


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

    async def get_exe_version(self, exe: str) -> ta.Optional[InterpVersion]:
        if not self.inspect:
            s = os.path.basename(exe)
            if s.startswith('python'):
                s = s[len('python'):]
            if '.' in s:
                try:
                    return InterpVersion.parse(s)
                except InvalidVersion:
                    pass
        ii = await self.inspector.inspect(exe)
        return ii.iv if ii is not None else None

    async def exe_versions(self) -> ta.Sequence[ta.Tuple[str, InterpVersion]]:
        lst = []
        for e in self.exes():
            if (ev := await self.get_exe_version(e)) is None:
                log.debug('Invalid system version: %s', e)
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
# ../deploy/git.py
"""
TODO:
 - 'repos'?

git/github.com/wrmsr/omlish <- bootstrap repo
 - shallow clone off bootstrap into /apps

github.com/wrmsr/omlish@rev
"""


##


class DeployGitManager(SingleDirDeployPathOwner):
    def __init__(
            self,
            *,
            atomics: DeployHomeAtomics,
    ) -> None:
        super().__init__(
            owned_dir='git',
        )

        self._atomics = atomics

        self._repo_dirs: ta.Dict[DeployGitRepo, DeployGitManager.RepoDir] = {}

    class RepoDir:
        def __init__(
                self,
                git: 'DeployGitManager',
                repo: DeployGitRepo,
                home: DeployHome,
        ) -> None:
            super().__init__()

            self._git = git
            self._repo = repo
            self._home = home
            self._dir = os.path.join(
                self._git._make_dir(home),  # noqa
                check.non_empty_str(repo.host),
                check.non_empty_str(repo.path),
            )

        @property
        def repo(self) -> DeployGitRepo:
            return self._repo

        @property
        def url(self) -> str:
            if self._repo.username is not None:
                return f'{self._repo.username}@{self._repo.host}:{self._repo.path}'
            else:
                return f'https://{self._repo.host}/{self._repo.path}'

        #

        async def _call(self, *cmd: str) -> None:
            await asyncio_subprocesses.check_call(
                *cmd,
                cwd=self._dir,
            )

        #

        @async_cached_nullary
        async def init(self) -> None:
            os.makedirs(self._dir, exist_ok=True)
            if os.path.exists(os.path.join(self._dir, '.git')):
                return

            await self._call('git', 'init')
            await self._call('git', 'remote', 'add', 'origin', self.url)

        async def fetch(self, rev: DeployRev) -> None:
            await self.init()
            await self._call('git', 'fetch', '--depth=1', 'origin', rev)

        #

        async def checkout(self, spec: DeployGitSpec, dst_dir: str) -> None:
            check.state(not os.path.exists(dst_dir))
            with self._git._atomics(self._home).begin_atomic_path_swap(  # noqa
                    'dir',
                    dst_dir,
                    auto_commit=True,
                    make_dirs=True,
            ) as dst_swap:
                await self.fetch(spec.rev)

                dst_call = functools.partial(asyncio_subprocesses.check_call, cwd=dst_swap.tmp_path)
                await dst_call('git', 'init')

                await dst_call('git', 'remote', 'add', 'local', self._dir)
                await dst_call('git', 'fetch', '--depth=1', 'local', spec.rev)
                await dst_call('git', 'checkout', spec.rev, *(spec.subtrees or []))

    def get_repo_dir(
            self,
            repo: DeployGitRepo,
            home: DeployHome,
    ) -> RepoDir:
        try:
            return self._repo_dirs[repo]
        except KeyError:
            repo_dir = self._repo_dirs[repo] = DeployGitManager.RepoDir(
                self,
                repo,
                home,
            )
            return repo_dir

    async def checkout(
            self,
            spec: DeployGitSpec,
            home: DeployHome,
            dst_dir: str,
    ) -> None:
        await self.get_repo_dir(
            spec.repo,
            home,
        ).checkout(
            spec,
            dst_dir,
        )


########################################
# ../deploy/paths/inject.py


def bind_deploy_paths() -> InjectorBindings:
    lst: ta.List[InjectorBindingOrBindings] = [
        inj.bind_array(DeployPathOwner),
        inj.bind_array_type(DeployPathOwner, DeployPathOwners),

        inj.bind(DeployPathsManager, singleton=True),
    ]

    return inj.as_bindings(*lst)


########################################
# ../remote/inject.py


def bind_remote(
        *,
        remote_config: RemoteConfig,
) -> InjectorBindings:
    lst: ta.List[InjectorBindingOrBindings] = [
        inj.bind(remote_config),

        inj.bind(SubprocessRemoteSpawning, singleton=True),
        inj.bind(RemoteSpawning, to_key=SubprocessRemoteSpawning),

        inj.bind(PyremoteRemoteExecutionConnector, singleton=True),
        inj.bind(InProcessRemoteExecutionConnector, singleton=True),
    ]

    #

    if (pf := remote_config.payload_file) is not None:
        lst.append(inj.bind(pf, key=RemoteExecutionPayloadFile))

    #

    return inj.as_bindings(*lst)


########################################
# ../system/inject.py


def bind_system(
        *,
        system_config: SystemConfig,
) -> InjectorBindings:
    lst: ta.List[InjectorBindingOrBindings] = [
        inj.bind(system_config),
    ]

    #

    platform = system_config.platform or detect_system_platform()
    lst.append(inj.bind(platform, key=Platform))

    #

    if isinstance(platform, AmazonLinuxPlatform):
        lst.extend([
            inj.bind(YumSystemPackageManager, singleton=True),
            inj.bind(SystemPackageManager, to_key=YumSystemPackageManager),
        ])

    elif isinstance(platform, LinuxPlatform):
        lst.extend([
            inj.bind(AptSystemPackageManager, singleton=True),
            inj.bind(SystemPackageManager, to_key=AptSystemPackageManager),
        ])

    elif isinstance(platform, DarwinPlatform):
        lst.extend([
            inj.bind(BrewSystemPackageManager, singleton=True),
            inj.bind(SystemPackageManager, to_key=BrewSystemPackageManager),
        ])

    #

    lst.extend([
        bind_command(CheckSystemPackageCommand, CheckSystemPackageCommandExecutor),
    ])

    #

    return inj.as_bindings(*lst)


########################################
# ../targets/connection.py


##


class ManageTargetConnector(abc.ABC):
    @abc.abstractmethod
    def connect(self, tgt: ManageTarget) -> ta.AsyncContextManager[CommandExecutor]:
        raise NotImplementedError

    def _default_python(self, python: ta.Optional[ta.Sequence[str]]) -> ta.Sequence[str]:
        check.not_isinstance(python, str)
        if python is not None:
            return python
        else:
            return ['sh', '-c', get_best_python_sh(), '--']


##


ManageTargetConnectorMap = ta.NewType('ManageTargetConnectorMap', ta.Mapping[ta.Type[ManageTarget], ManageTargetConnector])  # noqa


@dc.dataclass(frozen=True)
class TypeSwitchedManageTargetConnector(ManageTargetConnector):
    connectors: ManageTargetConnectorMap

    def get_connector(self, ty: ta.Type[ManageTarget]) -> ManageTargetConnector:
        for k, v in self.connectors.items():
            if issubclass(ty, k):
                return v
        raise KeyError(ty)

    def connect(self, tgt: ManageTarget) -> ta.AsyncContextManager[CommandExecutor]:
        return self.get_connector(type(tgt)).connect(tgt)


##


@dc.dataclass(frozen=True)
class LocalManageTargetConnector(ManageTargetConnector):
    _local_executor: LocalCommandExecutor
    _in_process_connector: InProcessRemoteExecutionConnector
    _pyremote_connector: PyremoteRemoteExecutionConnector
    _bootstrap: MainBootstrap

    @contextlib.asynccontextmanager
    async def connect(self, tgt: ManageTarget) -> ta.AsyncGenerator[CommandExecutor, None]:
        lmt = check.isinstance(tgt, LocalManageTarget)

        if isinstance(lmt, InProcessManageTarget):
            imt = check.isinstance(lmt, InProcessManageTarget)

            if imt.mode == InProcessManageTarget.Mode.DIRECT:
                yield self._local_executor

            elif imt.mode == InProcessManageTarget.Mode.FAKE_REMOTE:
                async with self._in_process_connector.connect() as rce:
                    yield rce

            else:
                raise TypeError(imt.mode)

        elif isinstance(lmt, SubprocessManageTarget):
            async with self._pyremote_connector.connect(
                    RemoteSpawning.Target(
                        python=self._default_python(lmt.python),
                    ),
                    self._bootstrap,
            ) as rce:
                yield rce

        else:
            raise TypeError(lmt)


##


@dc.dataclass(frozen=True)
class DockerManageTargetConnector(ManageTargetConnector):
    _pyremote_connector: PyremoteRemoteExecutionConnector
    _bootstrap: MainBootstrap

    @contextlib.asynccontextmanager
    async def connect(self, tgt: ManageTarget) -> ta.AsyncGenerator[CommandExecutor, None]:
        dmt = check.isinstance(tgt, DockerManageTarget)

        sh_parts: ta.List[str] = ['docker']
        if dmt.image is not None:
            sh_parts.extend(['run', '-i', dmt.image])
        elif dmt.container_id is not None:
            sh_parts.extend(['exec', '-i', dmt.container_id])
        else:
            raise ValueError(dmt)

        async with self._pyremote_connector.connect(
                RemoteSpawning.Target(
                    shell=' '.join(sh_parts),
                    python=self._default_python(dmt.python),
                ),
                self._bootstrap,
        ) as rce:
            yield rce


##


@dc.dataclass(frozen=True)
class SshManageTargetConnector(ManageTargetConnector):
    _pyremote_connector: PyremoteRemoteExecutionConnector
    _bootstrap: MainBootstrap

    @contextlib.asynccontextmanager
    async def connect(self, tgt: ManageTarget) -> ta.AsyncGenerator[CommandExecutor, None]:
        smt = check.isinstance(tgt, SshManageTarget)

        sh_parts: ta.List[str] = ['ssh']
        if smt.key_file is not None:
            sh_parts.extend(['-i', smt.key_file])
        addr = check.not_none(smt.host)
        if smt.username is not None:
            addr = f'{smt.username}@{addr}'
        sh_parts.append(addr)

        async with self._pyremote_connector.connect(
                RemoteSpawning.Target(
                    shell=' '.join(sh_parts),
                    shell_quote=True,
                    python=self._default_python(smt.python),
                ),
                self._bootstrap,
        ) as rce:
            yield rce


########################################
# ../../../omdev/interp/resolvers.py


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


DEFAULT_INTERP_RESOLVER = InterpResolver([(p.name, p) for p in [
    # pyenv is preferred to system interpreters as it tends to have more support for things like tkinter
    PyenvInterpProvider(try_update=True),

    RunningInterpProvider(),

    SystemInterpProvider(),
]])


########################################
# ../targets/inject.py


def bind_targets() -> InjectorBindings:
    lst: ta.List[InjectorBindingOrBindings] = [
        inj.bind(LocalManageTargetConnector, singleton=True),
        inj.bind(DockerManageTargetConnector, singleton=True),
        inj.bind(SshManageTargetConnector, singleton=True),

        inj.bind(TypeSwitchedManageTargetConnector, singleton=True),
        inj.bind(ManageTargetConnector, to_key=TypeSwitchedManageTargetConnector),
    ]

    #

    def provide_manage_target_connector_map(injector: Injector) -> ManageTargetConnectorMap:
        return ManageTargetConnectorMap({
            LocalManageTarget: injector[LocalManageTargetConnector],
            DockerManageTarget: injector[DockerManageTargetConnector],
            SshManageTarget: injector[SshManageTargetConnector],
        })
    lst.append(inj.bind(provide_manage_target_connector_map, singleton=True))

    #

    return inj.as_bindings(*lst)


########################################
# ../deploy/interp.py


##


@dc.dataclass(frozen=True)
class InterpCommand(Command['InterpCommand.Output']):
    spec: str
    install: bool = False

    @dc.dataclass(frozen=True)
    class Output(Command.Output):
        exe: str
        version: str
        opts: InterpOpts


class InterpCommandExecutor(CommandExecutor[InterpCommand, InterpCommand.Output]):
    async def execute(self, cmd: InterpCommand) -> InterpCommand.Output:
        i = InterpSpecifier.parse(check.not_none(cmd.spec))
        o = check.not_none(await DEFAULT_INTERP_RESOLVER.resolve(i, install=cmd.install))
        return InterpCommand.Output(
            exe=o.exe,
            version=str(o.version.version),
            opts=o.version.opts,
        )


########################################
# ../deploy/venvs.py
"""
TODO:
 - interp
 - share more code with pyproject?
"""


class DeployVenvManager:
    async def setup_venv(
            self,
            spec: DeployVenvSpec,
            home: DeployHome,
            git_dir: str,
            venv_dir: str,
    ) -> None:
        if spec.interp is not None:
            i = InterpSpecifier.parse(check.not_none(spec.interp))
            o = check.not_none(await DEFAULT_INTERP_RESOLVER.resolve(i))
            sys_exe = o.exe
        else:
            sys_exe = 'python3'

        #

        # !! NOTE: (most) venvs cannot be relocated, so an atomic swap can't be used. it's up to the path manager to
        # garbage collect orphaned dirs.
        await asyncio_subprocesses.check_call(sys_exe, '-m', 'venv', venv_dir)

        #

        venv_exe = os.path.join(venv_dir, 'bin', 'python3')

        #

        reqs_txt = os.path.join(git_dir, 'requirements.txt')

        if os.path.isfile(reqs_txt):
            if spec.use_uv:
                await asyncio_subprocesses.check_call(venv_exe, '-m', 'pip', 'install', 'uv')
                pip_cmd = ['-m', 'uv', 'pip']
            else:
                pip_cmd = ['-m', 'pip']

            await asyncio_subprocesses.check_call(venv_exe, *pip_cmd,'install', '-r', reqs_txt)


########################################
# ../deploy/apps.py


class DeployAppManager(DeployPathOwner):
    def __init__(
            self,
            *,
            conf: DeployConfManager,
            git: DeployGitManager,
            venvs: DeployVenvManager,
    ) -> None:
        super().__init__()

        self._conf = conf
        self._git = git
        self._venvs = venvs

    #

    _APP_DIR_STR = 'apps/@app/@time--@app-rev--@app-key/'
    _APP_DIR = DeployPath.parse(_APP_DIR_STR)

    _DEPLOY_DIR_STR = 'deploys/@time--@deploy-key/'
    _DEPLOY_DIR = DeployPath.parse(_DEPLOY_DIR_STR)

    _APP_DEPLOY_LINK = DeployPath.parse(f'{_DEPLOY_DIR_STR}apps/@app')
    _CONF_DEPLOY_DIR = DeployPath.parse(f'{_DEPLOY_DIR_STR}conf/@conf/')

    @cached_nullary
    def get_owned_deploy_paths(self) -> ta.AbstractSet[DeployPath]:
        return {
            self._APP_DIR,

            self._DEPLOY_DIR,

            self._APP_DEPLOY_LINK,
            self._CONF_DEPLOY_DIR,

            *[
                DeployPath.parse(f'{self._APP_DIR_STR}{sfx}/')
                for sfx in [
                    'conf',
                    'git',
                    'venv',
                ]
            ],
        }

    #

    async def prepare_app(
            self,
            spec: DeployAppSpec,
            home: DeployHome,
            tags: DeployTagMap,
    ) -> None:
        check.non_empty_str(home)

        def build_path(pth: DeployPath) -> str:
            return os.path.join(home, pth.render(tags))

        app_dir = build_path(self._APP_DIR)
        deploy_dir = build_path(self._DEPLOY_DIR)
        app_deploy_link = build_path(self._APP_DEPLOY_LINK)

        #

        os.makedirs(deploy_dir, exist_ok=True)

        deploying_link = os.path.join(home, 'deploys/deploying')
        if os.path.exists(deploying_link):
            os.unlink(deploying_link)
        relative_symlink(
            deploy_dir,
            deploying_link,
            target_is_directory=True,
            make_dirs=True,
        )

        #

        os.makedirs(app_dir)
        relative_symlink(
            app_dir,
            app_deploy_link,
            target_is_directory=True,
            make_dirs=True,
        )

        #

        deploy_conf_dir = os.path.join(deploy_dir, 'conf')
        os.makedirs(deploy_conf_dir, exist_ok=True)

        #

        # def mirror_symlinks(src: str, dst: str) -> None:
        #     def mirror_link(lp: str) -> None:
        #         check.state(os.path.islink(lp))
        #         shutil.copy2(
        #             lp,
        #             os.path.join(dst, os.path.relpath(lp, src)),
        #             follow_symlinks=False,
        #         )
        #
        #     for dp, dns, fns in os.walk(src, followlinks=False):
        #         for fn in fns:
        #             mirror_link(os.path.join(dp, fn))
        #
        #         for dn in dns:
        #             dp2 = os.path.join(dp, dn)
        #             if os.path.islink(dp2):
        #                 mirror_link(dp2)
        #             else:
        #                 os.makedirs(os.path.join(dst, os.path.relpath(dp2, src)))

        current_link = os.path.join(home, 'deploys/current')

        # if os.path.exists(current_link):
        #     mirror_symlinks(
        #         os.path.join(current_link, 'conf'),
        #         conf_tag_dir,
        #     )
        #     mirror_symlinks(
        #         os.path.join(current_link, 'apps'),
        #         os.path.join(deploy_dir, 'apps'),
        #     )

        #

        app_git_dir = os.path.join(app_dir, 'git')
        await self._git.checkout(
            spec.git,
            home,
            app_git_dir,
        )

        #

        if spec.venv is not None:
            app_venv_dir = os.path.join(app_dir, 'venv')
            await self._venvs.setup_venv(
                spec.venv,
                home,
                app_git_dir,
                app_venv_dir,
            )

        #

        if spec.conf is not None:
            app_conf_dir = os.path.join(app_dir, 'conf')
            await self._conf.write_app_conf(
                spec.conf,
                tags,
                app_conf_dir,
                deploy_conf_dir,
            )

        #

        os.replace(deploying_link, current_link)


########################################
# ../deploy/deploy.py


DEPLOY_TAG_DATETIME_FMT = '%Y%m%dT%H%M%SZ'


DeployManagerUtcClock = ta.NewType('DeployManagerUtcClock', Func0[datetime.datetime])


class DeployManager:
    def __init__(
            self,
            *,
            apps: DeployAppManager,
            paths: DeployPathsManager,

            utc_clock: ta.Optional[DeployManagerUtcClock] = None,
    ):
        super().__init__()

        self._apps = apps
        self._paths = paths

        self._utc_clock = utc_clock

    def _utc_now(self) -> datetime.datetime:
        if self._utc_clock is not None:
            return self._utc_clock()  # noqa
        else:
            return datetime.datetime.now(tz=datetime.timezone.utc)  # noqa

    def _make_deploy_time(self) -> DeployTime:
        return DeployTime(self._utc_now().strftime(DEPLOY_TAG_DATETIME_FMT))

    async def run_deploy(
            self,
            spec: DeploySpec,
    ) -> None:
        self._paths.validate_deploy_paths()

        #

        hs = check.non_empty_str(spec.home)
        hs = os.path.expanduser(hs)
        hs = os.path.realpath(hs)
        hs = os.path.abspath(hs)

        home = DeployHome(hs)

        #

        deploy_tags = DeployTagMap(
            self._make_deploy_time(),
            spec.key(),
        )

        #

        for app in spec.apps:
            app_tags = deploy_tags.add(
                app.app,
                app.key(),
                DeployAppRev(app.git.rev),
            )

            await self._apps.prepare_app(
                app,
                home,
                app_tags,
            )


########################################
# ../deploy/commands.py


##


@dc.dataclass(frozen=True)
class DeployCommand(Command['DeployCommand.Output']):
    spec: DeploySpec

    @dc.dataclass(frozen=True)
    class Output(Command.Output):
        pass


@dc.dataclass(frozen=True)
class DeployCommandExecutor(CommandExecutor[DeployCommand, DeployCommand.Output]):
    _deploy: DeployManager

    async def execute(self, cmd: DeployCommand) -> DeployCommand.Output:
        log.info('Deploying! %r', cmd.spec)

        await self._deploy.run_deploy(cmd.spec)

        return DeployCommand.Output()


########################################
# ../deploy/inject.py


def bind_deploy(
        *,
        deploy_config: DeployConfig,
) -> InjectorBindings:
    lst: ta.List[InjectorBindingOrBindings] = [
        inj.bind(deploy_config),

        bind_deploy_paths(),
    ]

    #

    def bind_manager(cls: type) -> InjectorBindings:
        return inj.as_bindings(
            inj.bind(cls, singleton=True),

            *([inj.bind(DeployPathOwner, to_key=cls, array=True)] if issubclass(cls, DeployPathOwner) else []),
        )

    #

    lst.extend([
        bind_manager(DeployAppManager),

        bind_manager(DeployConfManager),

        bind_manager(DeployGitManager),

        bind_manager(DeployManager),

        bind_manager(DeployTmpManager),

        bind_manager(DeployVenvManager),
    ])

    #

    def provide_deploy_home_atomics(tmp: DeployTmpManager) -> DeployHomeAtomics:
        return DeployHomeAtomics(tmp.get_swapping)
    lst.append(inj.bind(provide_deploy_home_atomics, singleton=True))

    #

    lst.extend([
        bind_command(DeployCommand, DeployCommandExecutor),
        bind_command(InterpCommand, InterpCommandExecutor),
    ])

    #

    return inj.as_bindings(*lst)


########################################
# ../inject.py


##


def bind_main(
        *,
        main_config: MainConfig = MainConfig(),

        deploy_config: DeployConfig = DeployConfig(),
        remote_config: RemoteConfig = RemoteConfig(),
        system_config: SystemConfig = SystemConfig(),

        main_bootstrap: ta.Optional[MainBootstrap] = None,
) -> InjectorBindings:
    lst: ta.List[InjectorBindingOrBindings] = [
        inj.bind(main_config),

        bind_commands(
            main_config=main_config,
        ),

        bind_deploy(
            deploy_config=deploy_config,
        ),

        bind_remote(
            remote_config=remote_config,
        ),

        bind_system(
            system_config=system_config,
        ),

        bind_targets(),
    ]

    #

    if main_bootstrap is not None:
        lst.append(inj.bind(main_bootstrap))

    #

    def build_obj_marshaler_manager(insts: ObjMarshalerInstallers) -> ObjMarshalerManager:
        msh = ObjMarshalerManager()
        inst: ObjMarshalerInstaller
        for inst in insts:
            inst.fn(msh)
        return msh

    lst.extend([
        inj.bind(build_obj_marshaler_manager, singleton=True),

        inj.bind_array(ObjMarshalerInstaller),
        inj.bind_array_type(ObjMarshalerInstaller, ObjMarshalerInstallers),
    ])

    #

    return inj.as_bindings(*lst)


########################################
# ../bootstrap_.py


def main_bootstrap(bs: MainBootstrap) -> Injector:
    if (log_level := bs.main_config.log_level) is not None:
        configure_standard_logging(log_level)

    injector = inj.create_injector(bind_main(  # noqa
        main_config=bs.main_config,

        deploy_config=bs.deploy_config,
        remote_config=bs.remote_config,
        system_config=bs.system_config,

        main_bootstrap=bs,
    ))

    return injector


########################################
# main.py


@dc.dataclass(frozen=True)
class ManageConfig:
    targets: ta.Optional[ta.Mapping[str, ManageTarget]] = None


class MainCli(ArgparseCli):
    config_file: ta.Optional[str] = argparse_arg('--config-file', help='Config file path')  # type: ignore

    @cached_nullary
    def config(self) -> ManageConfig:
        if (cf := self.config_file) is None:
            cf = os.path.expanduser('~/.omlish/manage.yml')
            if not os.path.isfile(cf):
                cf = None

        if cf is None:
            return ManageConfig()
        else:
            return read_config_file(cf, ManageConfig)

    #

    @argparse_command(
        argparse_arg('--_payload-file'),

        argparse_arg('--pycharm-debug-port', type=int),
        argparse_arg('--pycharm-debug-host'),
        argparse_arg('--pycharm-debug-version'),

        argparse_arg('--remote-timebomb-delay-s', type=float),

        argparse_arg('--debug', action='store_true'),

        argparse_arg('target'),
        argparse_arg('-f', '--command-file', action='append'),
        argparse_arg('command', nargs='*'),
    )
    async def run(self) -> None:
        bs = MainBootstrap(
            main_config=MainConfig(
                log_level='DEBUG' if self.args.debug else 'INFO',

                debug=bool(self.args.debug),
            ),

            deploy_config=DeployConfig(),

            remote_config=RemoteConfig(
                payload_file=self.args._payload_file,  # noqa

                pycharm_remote_debug=PycharmRemoteDebug(
                    port=self.args.pycharm_debug_port,
                    **(dict(host=self.args.pycharm_debug_host) if self.args.pycharm_debug_host is not None else {}),
                    install_version=self.args.pycharm_debug_version,
                ) if self.args.pycharm_debug_port is not None else None,

                timebomb_delay_s=self.args.remote_timebomb_delay_s,
            ),
        )

        #

        injector = main_bootstrap(
            bs,
        )

        #

        msh = injector[ObjMarshalerManager]

        tgt: ManageTarget
        if not (ts := self.args.target).startswith('{'):
            tgt = check.not_none(self.config().targets)[ts]
        else:
            tgt = msh.unmarshal_obj(json.loads(ts), ManageTarget)

        #

        cmds: ta.List[Command] = []

        cmd: Command

        for c in self.args.command or []:
            if not c.startswith('{'):
                c = json.dumps({c: {}})
            cmd = msh.unmarshal_obj(json.loads(c), Command)
            cmds.append(cmd)

        for cf in self.args.command_file or []:
            cmd = read_config_file(cf, Command, msh=msh)
            cmds.append(cmd)

        #

        async with injector[ManageTargetConnector].connect(tgt) as ce:
            async def run_command(cmd: Command) -> None:
                res = await ce.try_execute(
                    cmd,
                    log=log,
                    omit_exc_object=True,
                )

                print(msh.marshal_obj(res, opts=ObjMarshalOptions(raw_bytes=True)))

            await asyncio.gather(*[
                run_command(cmd)
                for cmd in cmds
            ])


def _main() -> None:
    sys.exit(asyncio.run(MainCli().async_cli_run()))


if __name__ == '__main__':
    _main()
