#!/usr/bin/env python3
# noinspection DuplicatedCode
# @omlish-lite
# @omlish-script
# @omlish-amalg-output ../supervisor/main.py
# ruff: noqa: N802 U006 UP006 UP007 UP012 UP036
# Supervisor is licensed under the following license:
#
#  A copyright notice accompanies this license document that identifies the copyright holders.
#
#  Redistribution and use in source and binary forms, with or without modification, are permitted provided that the
#  following conditions are met:
#
#  1. Redistributions in source code must retain the accompanying copyright notice, this list of conditions, and the
#     following disclaimer.
#
#  2. Redistributions in binary form must reproduce the accompanying copyright notice, this list of conditions, and the
#     following disclaimer in the documentation and/or other materials provided with the distribution.
#
#  3. Names of the copyright holders must not be used to endorse or promote products derived from this software without
#     prior written permission from the copyright holders.
#
#  4. If any files are modified, you must cause the modified files to carry prominent notices stating that you changed
#     the files and the date of any change.
#
#  Disclaimer
#
#   THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS ``AS IS'' AND ANY EXPRESSED OR IMPLIED WARRANTIES, INCLUDING, BUT
#   NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO
#   EVENT SHALL THE COPYRIGHT HOLDERS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
#   CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
#   DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT,
#   STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE,
#   EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
import abc
import base64
import collections.abc
import contextlib
import ctypes as ct
import dataclasses as dc
import datetime
import decimal
import email.utils
import enum
import errno
import fcntl
import fractions
import functools
import grp
import html
import http.client
import http.server
import inspect
import io
import itertools
import json
import logging
import os
import os.path
import pwd
import re
import resource
import select
import shlex
import signal
import socket
import stat
import string
import sys
import syslog
import tempfile
import textwrap
import threading
import time
import traceback
import types
import typing as ta
import uuid
import warnings
import weakref  # noqa


########################################


if sys.version_info < (3, 8):
    raise OSError(f'Requires python (3, 8), got {sys.version_info} from {sys.executable}')  # noqa


########################################


# ../../omdev/toml/parser.py
TomlParseFloat = ta.Callable[[str], ta.Any]
TomlKey = ta.Tuple[str, ...]
TomlPos = int  # ta.TypeAlias

# utils/collections.py
K = ta.TypeVar('K')
V = ta.TypeVar('V')

# ../../omlish/lite/cached.py
T = ta.TypeVar('T')

# ../../omlish/lite/check.py
SizedT = ta.TypeVar('SizedT', bound=ta.Sized)

# ../../omlish/lite/socket.py
SocketAddress = ta.Any
SocketHandlerFactory = ta.Callable[[SocketAddress, ta.BinaryIO, ta.BinaryIO], 'SocketHandler']

# ../../omlish/lite/typing.py
A0 = ta.TypeVar('A0')
A1 = ta.TypeVar('A1')
A2 = ta.TypeVar('A2')

# events.py
EventCallback = ta.Callable[['Event'], None]

# ../../omlish/lite/http/parsing.py
HttpHeaders = http.client.HTTPMessage  # ta.TypeAlias

# ../../omlish/lite/inject.py
U = ta.TypeVar('U')
InjectorKeyCls = ta.Union[type, ta.NewType]
InjectorProviderFn = ta.Callable[['Injector'], ta.Any]
InjectorProviderFnMap = ta.Mapping['InjectorKey', 'InjectorProviderFn']
InjectorBindingOrBindings = ta.Union['InjectorBinding', 'InjectorBindings']

# ../configs.py
ConfigMapping = ta.Mapping[str, ta.Any]

# ../../omlish/lite/http/handlers.py
HttpHandler = ta.Callable[['HttpHandlerRequest'], 'HttpHandlerResponse']

# ../../omlish/lite/http/coroserver.py
CoroHttpServerFactory = ta.Callable[[SocketAddress], 'CoroHttpServer']


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
# ../exceptions.py


class ProcessError(Exception):
    """Specialized exceptions used when attempting to start a process."""


class BadCommandError(ProcessError):
    """Indicates the command could not be parsed properly."""


class NotExecutableError(ProcessError):
    """
    Indicates that the filespec cannot be executed because its path resolves to a file which is not executable, or which
    is a directory.
    """


class NotFoundError(ProcessError):
    """Indicates that the filespec cannot be executed because it could not be found."""


class NoPermissionError(ProcessError):
    """
    Indicates that the file cannot be executed because the supervisor process does not possess the appropriate UNIX
    filesystem permission to execute the file.
    """


########################################
# ../privileges.py


def drop_privileges(user: ta.Union[int, str, None]) -> ta.Optional[str]:
    """
    Drop privileges to become the specified user, which may be a username or uid. Called for supervisord startup and
    when spawning subprocesses. Returns None on success or a string error message if privileges could not be dropped.
    """

    if user is None:
        return 'No user specified to setuid to!'

    # get uid for user, which can be a number or username
    try:
        uid = int(user)
    except ValueError:
        try:
            pwrec = pwd.getpwnam(user)  # type: ignore
        except KeyError:
            return f"Can't find username {user!r}"
        uid = pwrec[2]
    else:
        try:
            pwrec = pwd.getpwuid(uid)
        except KeyError:
            return f"Can't find uid {uid!r}"

    current_uid = os.getuid()

    if current_uid == uid:
        # do nothing and return successfully if the uid is already the current one. this allows a supervisord running as
        # an unprivileged user "foo" to start a process where the config has "user=foo" (same user) in it.
        return None

    if current_uid != 0:
        return "Can't drop privilege as nonroot user"

    gid = pwrec[3]
    if hasattr(os, 'setgroups'):
        user = pwrec[0]
        groups = [grprec[2] for grprec in grp.getgrall() if user in grprec[3]]

        # always put our primary gid first in this list, otherwise we can lose group info since sometimes the first
        # group in the setgroups list gets overwritten on the subsequent setgid call (at least on freebsd 9 with
        # python 2.7 - this will be safe though for all unix /python version combos)
        groups.insert(0, gid)
        try:
            os.setgroups(groups)
        except OSError:
            return 'Could not set groups of effective user'

    try:
        os.setgid(gid)
    except OSError:
        return 'Could not set group id of effective user'

    os.setuid(uid)

    return None


########################################
# ../states.py


##


class ProcessState(enum.IntEnum):
    STOPPED = 0
    STARTING = 10
    RUNNING = 20
    BACKOFF = 30
    STOPPING = 40
    EXITED = 100
    FATAL = 200
    UNKNOWN = 1000

    @property
    def stopped(self) -> bool:
        return self in STOPPED_STATES

    @property
    def running(self) -> bool:
        return self in RUNNING_STATES

    @property
    def signalable(self) -> bool:
        return self in SIGNALABLE_STATES


STOPPED_STATES = (
    ProcessState.STOPPED,
    ProcessState.EXITED,
    ProcessState.FATAL,
    ProcessState.UNKNOWN,
)

RUNNING_STATES = (
    ProcessState.RUNNING,
    ProcessState.BACKOFF,
    ProcessState.STARTING,
)

SIGNALABLE_STATES = (
    ProcessState.RUNNING,
    ProcessState.STARTING,
    ProcessState.STOPPING,
)


##


class SupervisorState(enum.IntEnum):
    FATAL = 2
    RUNNING = 1
    RESTARTING = 0
    SHUTDOWN = -1


########################################
# ../utils/collections.py


class KeyedCollectionAccessors(abc.ABC, ta.Generic[K, V]):
    @property
    @abc.abstractmethod
    def _by_key(self) -> ta.Mapping[K, V]:
        raise NotImplementedError

    def __iter__(self) -> ta.Iterator[V]:
        return iter(self._by_key.values())

    def __len__(self) -> int:
        return len(self._by_key)

    def __contains__(self, key: K) -> bool:
        return key in self._by_key

    def __getitem__(self, key: K) -> V:
        return self._by_key[key]

    def get(self, key: K, default: ta.Optional[V] = None) -> ta.Optional[V]:
        return self._by_key.get(key, default)

    def items(self) -> ta.Iterator[ta.Tuple[K, V]]:
        return iter(self._by_key.items())


class KeyedCollection(KeyedCollectionAccessors[K, V]):
    def __init__(self, items: ta.Iterable[V]) -> None:
        super().__init__()

        by_key: ta.Dict[K, V] = {}
        for v in items:
            if (k := self._key(v)) in by_key:
                raise KeyError(f'key {k} of {v} already registered by {by_key[k]}')
            by_key[k] = v
        self.__by_key = by_key

    @property
    def _by_key(self) -> ta.Mapping[K, V]:
        return self.__by_key

    @abc.abstractmethod
    def _key(self, v: V) -> K:
        raise NotImplementedError


########################################
# ../utils/diag.py


def compact_traceback() -> ta.Tuple[
    ta.Tuple[str, str, int],
    ta.Type[BaseException],
    BaseException,
    types.TracebackType,
]:
    t, v, tb = sys.exc_info()
    if not tb:
        raise RuntimeError('No traceback')

    tbinfo = []
    while tb:
        tbinfo.append((
            tb.tb_frame.f_code.co_filename,
            tb.tb_frame.f_code.co_name,
            str(tb.tb_lineno),
        ))
        tb = tb.tb_next

    # just to be safe
    del tb

    file, function, line = tbinfo[-1]
    info = ' '.join(['[%s|%s|%s]' % x for x in tbinfo])  # noqa
    return (file, function, line), t, v, info  # type: ignore


########################################
# ../utils/fs.py


def try_unlink(path: str) -> bool:
    try:
        os.unlink(path)
    except OSError:
        return False
    return True


def mktempfile(suffix: str, prefix: str, dir: str) -> str:  # noqa
    fd, filename = tempfile.mkstemp(suffix, prefix, dir)
    os.close(fd)
    return filename


def get_path() -> ta.Sequence[str]:
    """Return a list corresponding to $PATH, or a default."""

    path = ['/bin', '/usr/bin', '/usr/local/bin']
    if 'PATH' in os.environ:
        p = os.environ['PATH']
        if p:
            path = p.split(os.pathsep)
    return path


def check_existing_dir(v: str) -> str:
    nv = os.path.expanduser(v)
    if os.path.isdir(nv):
        return nv
    raise ValueError(f'{v} is not an existing directory')


def check_path_with_existing_dir(v: str) -> str:
    nv = os.path.expanduser(v)
    dir = os.path.dirname(nv)  # noqa
    if not dir:
        # relative pathname with no directory component
        return nv
    if os.path.isdir(dir):
        return nv
    raise ValueError(f'The directory named as part of the path {v} does not exist')


########################################
# ../utils/ostypes.py


Fd = ta.NewType('Fd', int)
Pid = ta.NewType('Pid', int)
Rc = ta.NewType('Rc', int)

Uid = ta.NewType('Uid', int)
Gid = ta.NewType('Gid', int)


########################################
# ../utils/signals.py


##


_SIGS_BY_NUM: ta.Mapping[int, signal.Signals] = {s.value: s for s in signal.Signals}
_SIGS_BY_NAME: ta.Mapping[str, signal.Signals] = {s.name: s for s in signal.Signals}


def sig_num(value: ta.Union[int, str]) -> int:
    try:
        num = int(value)

    except (ValueError, TypeError):
        name = value.strip().upper()  # type: ignore
        if not name.startswith('SIG'):
            name = f'SIG{name}'

        if (sn := _SIGS_BY_NAME.get(name)) is None:
            raise ValueError(f'value {value!r} is not a valid signal name')  # noqa
        num = sn

    if num not in _SIGS_BY_NUM:
        raise ValueError(f'value {value!r} is not a valid signal number')

    return num


def sig_name(num: int) -> str:
    if (sig := _SIGS_BY_NUM.get(num)) is not None:
        return sig.name
    return f'signal {sig}'


##


class SignalReceiver:
    def __init__(self) -> None:
        super().__init__()

        self._signals_recvd: ta.List[int] = []

    def receive(self, sig: int, frame: ta.Any = None) -> None:
        if sig not in self._signals_recvd:
            self._signals_recvd.append(sig)

    def install(self, *sigs: int) -> None:
        for sig in sigs:
            signal.signal(sig, self.receive)

    def get_signal(self) -> ta.Optional[int]:
        if self._signals_recvd:
            sig = self._signals_recvd.pop(0)
        else:
            sig = None
        return sig


########################################
# ../utils/strings.py


##


def as_bytes(s: ta.Union[str, bytes], encoding: str = 'utf8') -> bytes:
    if isinstance(s, bytes):
        return s
    else:
        return s.encode(encoding)


@ta.overload
def find_prefix_at_end(haystack: str, needle: str) -> int:
    ...


@ta.overload
def find_prefix_at_end(haystack: bytes, needle: bytes) -> int:
    ...


def find_prefix_at_end(haystack, needle):
    l = len(needle) - 1
    while l and not haystack.endswith(needle[:l]):
        l -= 1
    return l


##


ANSI_ESCAPE_BEGIN = b'\x1b['
ANSI_TERMINATORS = (b'H', b'f', b'A', b'B', b'C', b'D', b'R', b's', b'u', b'J', b'K', b'h', b'l', b'p', b'm')


def strip_escapes(s: bytes) -> bytes:
    """Remove all ANSI color escapes from the given string."""

    result = b''
    show = 1
    i = 0
    l = len(s)
    while i < l:
        if show == 0 and s[i:i + 1] in ANSI_TERMINATORS:
            show = 1
        elif show:
            n = s.find(ANSI_ESCAPE_BEGIN, i)
            if n == -1:
                return result + s[i:]
            else:
                result = result + s[i:n]
                i = n
                show = 0
        i += 1
    return result


##


class SuffixMultiplier:
    # d is a dictionary of suffixes to integer multipliers. If no suffixes match, default is the multiplier. Matches are
    # case insensitive. Return values are in the fundamental unit.
    def __init__(self, d, default=1):
        super().__init__()
        self._d = d
        self._default = default
        # all keys must be the same size
        self._keysz = None
        for k in d:
            if self._keysz is None:
                self._keysz = len(k)
            elif self._keysz != len(k):  # type: ignore
                raise ValueError(k)

    def __call__(self, v: ta.Union[str, int]) -> int:
        if isinstance(v, int):
            return v
        v = v.lower()
        for s, m in self._d.items():
            if v[-self._keysz:] == s:  # type: ignore
                return int(v[:-self._keysz]) * m  # type: ignore
        return int(v) * self._default


parse_bytes_size = SuffixMultiplier({
    'kb': 1024,
    'mb': 1024 * 1024,
    'gb': 1024 * 1024 * 1024,
})


#


def parse_octal(arg: ta.Union[str, int]) -> int:
    if isinstance(arg, int):
        return arg
    try:
        return int(arg, 8)
    except (TypeError, ValueError):
        raise ValueError(f'{arg} can not be converted to an octal type')  # noqa


########################################
# ../../../omlish/lite/cached.py


class _cached_nullary:  # noqa
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


def cached_nullary(fn):  # ta.Callable[..., T]) -> ta.Callable[..., T]:
    return _cached_nullary(fn)


########################################
# ../../../omlish/lite/check.py


def check_isinstance(v: ta.Any, spec: ta.Union[ta.Type[T], tuple]) -> T:
    if not isinstance(v, spec):
        raise TypeError(v)
    return v


def check_not_isinstance(v: T, spec: ta.Union[type, tuple]) -> T:
    if isinstance(v, spec):
        raise TypeError(v)
    return v


def check_none(v: T) -> None:
    if v is not None:
        raise ValueError(v)


def check_not_none(v: ta.Optional[T]) -> T:
    if v is None:
        raise ValueError
    return v


def check_not(v: ta.Any) -> None:
    if v:
        raise ValueError(v)
    return v


def check_non_empty_str(v: ta.Optional[str]) -> str:
    if not v:
        raise ValueError
    return v


def check_state(v: bool, msg: str = 'Illegal state') -> None:
    if not v:
        raise ValueError(msg)


def check_equal(l: T, r: T) -> T:
    if l != r:
        raise ValueError(l, r)
    return l


def check_not_equal(l: T, r: T) -> T:
    if l == r:
        raise ValueError(l, r)
    return l


def check_is(l: T, r: T) -> T:
    if l is not r:
        raise ValueError(l, r)
    return l


def check_is_not(l: T, r: ta.Any) -> T:
    if l is r:
        raise ValueError(l, r)
    return l


def check_in(v: T, c: ta.Container[T]) -> T:
    if v not in c:
        raise ValueError(v, c)
    return v


def check_not_in(v: T, c: ta.Container[T]) -> T:
    if v in c:
        raise ValueError(v, c)
    return v


def check_single(vs: ta.Iterable[T]) -> T:
    [v] = vs
    return v


def check_empty(v: SizedT) -> SizedT:
    if len(v):
        raise ValueError(v)
    return v


def check_non_empty(v: SizedT) -> SizedT:
    if not len(v):
        raise ValueError(v)
    return v


########################################
# ../../../omlish/lite/fdio/pollers.py


##


class FdIoPoller(abc.ABC):
    def __init__(self) -> None:
        super().__init__()

        self._readable: ta.Set[int] = set()
        self._writable: ta.Set[int] = set()

    #

    def close(self) -> None:  # noqa
        pass

    def reopen(self) -> None:  # noqa
        pass

    #

    @property
    @ta.final
    def readable(self) -> ta.AbstractSet[int]:
        return self._readable

    @property
    @ta.final
    def writable(self) -> ta.AbstractSet[int]:
        return self._writable

    #

    @ta.final
    def register_readable(self, fd: int) -> bool:
        if fd in self._readable:
            return False
        self._readable.add(fd)
        self._register_readable(fd)
        return True

    @ta.final
    def register_writable(self, fd: int) -> bool:
        if fd in self._writable:
            return False
        self._writable.add(fd)
        self._register_writable(fd)
        return True

    @ta.final
    def unregister_readable(self, fd: int) -> bool:
        if fd not in self._readable:
            return False
        self._readable.discard(fd)
        self._unregister_readable(fd)
        return True

    @ta.final
    def unregister_writable(self, fd: int) -> bool:
        if fd not in self._writable:
            return False
        self._writable.discard(fd)
        self._unregister_writable(fd)
        return True

    #

    def _register_readable(self, fd: int) -> None:  # noqa
        pass

    def _register_writable(self, fd: int) -> None:  # noqa
        pass

    def _unregister_readable(self, fd: int) -> None:  # noqa
        pass

    def _unregister_writable(self, fd: int) -> None:  # noqa
        pass

    #

    def update(
            self,
            r: ta.AbstractSet[int],
            w: ta.AbstractSet[int],
    ) -> None:
        for f in r - self._readable:
            self.register_readable(f)
        for f in w - self._writable:
            self.register_writable(f)
        for f in self._readable - r:
            self.unregister_readable(f)
        for f in self._writable - w:
            self.unregister_writable(f)

    #

    @dc.dataclass(frozen=True)
    class PollResult:
        r: ta.Sequence[int] = ()
        w: ta.Sequence[int] = ()

        inv: ta.Sequence[int] = ()

        msg: ta.Optional[str] = None
        exc: ta.Optional[BaseException] = None

    @abc.abstractmethod
    def poll(self, timeout: ta.Optional[float]) -> PollResult:
        raise NotImplementedError


##


class SelectFdIoPoller(FdIoPoller):
    def poll(self, timeout: ta.Optional[float]) -> FdIoPoller.PollResult:
        try:
            r, w, x = select.select(
                self._readable,
                self._writable,
                [],
                timeout,
            )

        except OSError as exc:
            if exc.errno == errno.EINTR:
                return FdIoPoller.PollResult(msg='EINTR encountered in poll', exc=exc)
            elif exc.errno == errno.EBADF:
                return FdIoPoller.PollResult(msg='EBADF encountered in poll', exc=exc)
            else:
                raise

        return FdIoPoller.PollResult(r, w)


##


PollFdIoPoller: ta.Optional[ta.Type[FdIoPoller]]
if hasattr(select, 'poll'):

    class _PollFdIoPoller(FdIoPoller):
        def __init__(self) -> None:
            super().__init__()

            self._poller = select.poll()

        #

        _READ = select.POLLIN | select.POLLPRI | select.POLLHUP
        _WRITE = select.POLLOUT

        def _register_readable(self, fd: int) -> None:
            self._update_registration(fd)

        def _register_writable(self, fd: int) -> None:
            self._update_registration(fd)

        def _unregister_readable(self, fd: int) -> None:
            self._update_registration(fd)

        def _unregister_writable(self, fd: int) -> None:
            self._update_registration(fd)

        def _update_registration(self, fd: int) -> None:
            r = fd in self._readable
            w = fd in self._writable
            if r or w:
                self._poller.register(fd, (self._READ if r else 0) | (self._WRITE if w else 0))
            else:
                self._poller.unregister(fd)

        #

        def poll(self, timeout: ta.Optional[float]) -> FdIoPoller.PollResult:
            polled: ta.List[ta.Tuple[int, int]]
            try:
                polled = self._poller.poll(timeout * 1000 if timeout is not None else None)

            except OSError as exc:
                if exc.errno == errno.EINTR:
                    return FdIoPoller.PollResult(msg='EINTR encountered in poll', exc=exc)
                else:
                    raise

            r: ta.List[int] = []
            w: ta.List[int] = []
            inv: ta.List[int] = []
            for fd, mask in polled:
                if mask & select.POLLNVAL:
                    self._poller.unregister(fd)
                    self._readable.discard(fd)
                    self._writable.discard(fd)
                    inv.append(fd)
                    continue
                if mask & self._READ:
                    r.append(fd)
                if mask & self._WRITE:
                    w.append(fd)
            return FdIoPoller.PollResult(r, w, inv=inv)

    PollFdIoPoller = _PollFdIoPoller
else:
    PollFdIoPoller = None


########################################
# ../../../omlish/lite/http/versions.py


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


def is_new_type(spec: ta.Any) -> bool:
    if isinstance(ta.NewType, type):
        return isinstance(spec, ta.NewType)
    else:
        # Before https://github.com/python/cpython/commit/c2f33dfc83ab270412bf243fb21f724037effa1a
        return isinstance(spec, types.FunctionType) and spec.__code__ is ta.NewType.__code__.co_consts[1]  # type: ignore  # noqa


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
# ../../../omlish/lite/socket.py
"""
TODO:
 - SocketClientAddress family / tuple pairs
  + codification of https://docs.python.org/3/library/socket.html#socket-families
"""


##


@dc.dataclass(frozen=True)
class SocketAddressInfoArgs:
    host: ta.Optional[str]
    port: ta.Union[str, int, None]
    family: socket.AddressFamily = socket.AddressFamily.AF_UNSPEC
    type: int = 0
    proto: int = 0
    flags: socket.AddressInfo = socket.AddressInfo(0)


@dc.dataclass(frozen=True)
class SocketAddressInfo:
    family: socket.AddressFamily
    type: int
    proto: int
    canonname: ta.Optional[str]
    sockaddr: SocketAddress


def get_best_socket_family(
        host: ta.Optional[str],
        port: ta.Union[str, int, None],
        family: ta.Union[int, socket.AddressFamily] = socket.AddressFamily.AF_UNSPEC,
) -> ta.Tuple[socket.AddressFamily, SocketAddress]:
    """https://github.com/python/cpython/commit/f289084c83190cc72db4a70c58f007ec62e75247"""

    infos = socket.getaddrinfo(
        host,
        port,
        family,
        type=socket.SOCK_STREAM,
        flags=socket.AI_PASSIVE,
    )
    ai = SocketAddressInfo(*next(iter(infos)))
    return ai.family, ai.sockaddr


##


class SocketHandler(abc.ABC):
    def __init__(
            self,
            client_address: SocketAddress,
            rfile: ta.BinaryIO,
            wfile: ta.BinaryIO,
    ) -> None:
        super().__init__()

        self._client_address = client_address
        self._rfile = rfile
        self._wfile = wfile

    @abc.abstractmethod
    def handle(self) -> None:
        raise NotImplementedError


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
# ../events.py


##


class Event(abc.ABC):  # noqa
    """Abstract event type."""


##


class EventCallbacks:
    def __init__(self) -> None:
        super().__init__()

        self._callbacks: ta.List[ta.Tuple[ta.Type[Event], EventCallback]] = []

    def subscribe(self, type: ta.Type[Event], callback: EventCallback) -> None:  # noqa
        self._callbacks.append((type, callback))

    def unsubscribe(self, type: ta.Type[Event], callback: EventCallback) -> None:  # noqa
        self._callbacks.remove((type, callback))

    def notify(self, event: Event) -> None:
        for type, callback in self._callbacks:  # noqa
            if isinstance(event, type):
                callback(event)

    def clear(self) -> None:
        self._callbacks[:] = []


##


class ProcessLogEvent(Event, abc.ABC):
    channel: ta.Optional[str] = None

    def __init__(self, process, pid, data):
        super().__init__()
        self.process = process
        self.pid = pid
        self.data = data


class ProcessLogStdoutEvent(ProcessLogEvent):
    channel = 'stdout'


class ProcessLogStderrEvent(ProcessLogEvent):
    channel = 'stderr'


#


class ProcessCommunicationEvent(Event, abc.ABC):
    # event mode tokens
    BEGIN_TOKEN = b'<!--XSUPERVISOR:BEGIN-->'
    END_TOKEN = b'<!--XSUPERVISOR:END-->'

    channel: ta.ClassVar[str]

    def __init__(self, process, pid, data):
        super().__init__()
        self.process = process
        self.pid = pid
        self.data = data


class ProcessCommunicationStdoutEvent(ProcessCommunicationEvent):
    channel = 'stdout'


class ProcessCommunicationStderrEvent(ProcessCommunicationEvent):
    channel = 'stderr'


#


class RemoteCommunicationEvent(Event):
    def __init__(self, type, data):  # noqa
        super().__init__()
        self.type = type
        self.data = data


#


class SupervisorStateChangeEvent(Event):
    """Abstract class."""


class SupervisorRunningEvent(SupervisorStateChangeEvent):
    pass


class SupervisorStoppingEvent(SupervisorStateChangeEvent):
    pass


#


class EventRejectedEvent:  # purposely does not subclass Event
    def __init__(self, process, event):
        super().__init__()
        self.process = process
        self.event = event


#


class ProcessStateEvent(Event):
    """Abstract class, never raised directly."""
    frm = None
    to = None

    def __init__(self, process, from_state, expected=True):
        super().__init__()
        self.process = process
        self.from_state = from_state
        self.expected = expected
        # we eagerly render these so if the process pid, etc changes beneath
        # us, we stash the values at the time the event was sent
        self.extra_values = self.get_extra_values()

    def get_extra_values(self):
        return []


class ProcessStateFatalEvent(ProcessStateEvent):
    pass


class ProcessStateUnknownEvent(ProcessStateEvent):
    pass


class ProcessStateStartingOrBackoffEvent(ProcessStateEvent):
    def get_extra_values(self):
        return [('tries', int(self.process.backoff))]


class ProcessStateBackoffEvent(ProcessStateStartingOrBackoffEvent):
    pass


class ProcessStateStartingEvent(ProcessStateStartingOrBackoffEvent):
    pass


class ProcessStateExitedEvent(ProcessStateEvent):
    def get_extra_values(self):
        return [('expected', int(self.expected)), ('pid', self.process.pid)]


class ProcessStateRunningEvent(ProcessStateEvent):
    def get_extra_values(self):
        return [('pid', self.process.pid)]


class ProcessStateStoppingEvent(ProcessStateEvent):
    def get_extra_values(self):
        return [('pid', self.process.pid)]


class ProcessStateStoppedEvent(ProcessStateEvent):
    def get_extra_values(self):
        return [('pid', self.process.pid)]


PROCESS_STATE_EVENT_MAP: ta.Mapping[ProcessState, ta.Type[ProcessStateEvent]] = {
    ProcessState.BACKOFF: ProcessStateBackoffEvent,
    ProcessState.FATAL: ProcessStateFatalEvent,
    ProcessState.UNKNOWN: ProcessStateUnknownEvent,
    ProcessState.STOPPED: ProcessStateStoppedEvent,
    ProcessState.EXITED: ProcessStateExitedEvent,
    ProcessState.RUNNING: ProcessStateRunningEvent,
    ProcessState.STARTING: ProcessStateStartingEvent,
    ProcessState.STOPPING: ProcessStateStoppingEvent,
}


#


class ProcessGroupEvent(Event):
    def __init__(self, group):
        super().__init__()
        self.group = group


class ProcessGroupAddedEvent(ProcessGroupEvent):
    pass


class ProcessGroupRemovedEvent(ProcessGroupEvent):
    pass


#


class TickEvent(Event):
    """Abstract."""

    def __init__(self, when, supervisord):
        super().__init__()
        self.when = when
        self.supervisord = supervisord


class Tick5Event(TickEvent):
    period = 5


class Tick60Event(TickEvent):
    period = 60


class Tick3600Event(TickEvent):
    period = 3600


TICK_EVENTS = (  # imported elsewhere
    Tick5Event,
    Tick60Event,
    Tick3600Event,
)


##


class EventTypes:
    EVENT = Event  # abstract

    PROCESS_STATE = ProcessStateEvent  # abstract
    PROCESS_STATE_STOPPED = ProcessStateStoppedEvent
    PROCESS_STATE_EXITED = ProcessStateExitedEvent
    PROCESS_STATE_STARTING = ProcessStateStartingEvent
    PROCESS_STATE_STOPPING = ProcessStateStoppingEvent
    PROCESS_STATE_BACKOFF = ProcessStateBackoffEvent
    PROCESS_STATE_FATAL = ProcessStateFatalEvent
    PROCESS_STATE_RUNNING = ProcessStateRunningEvent
    PROCESS_STATE_UNKNOWN = ProcessStateUnknownEvent

    PROCESS_COMMUNICATION = ProcessCommunicationEvent  # abstract
    PROCESS_COMMUNICATION_STDOUT = ProcessCommunicationStdoutEvent
    PROCESS_COMMUNICATION_STDERR = ProcessCommunicationStderrEvent

    PROCESS_LOG = ProcessLogEvent
    PROCESS_LOG_STDOUT = ProcessLogStdoutEvent
    PROCESS_LOG_STDERR = ProcessLogStderrEvent

    REMOTE_COMMUNICATION = RemoteCommunicationEvent

    SUPERVISOR_STATE_CHANGE = SupervisorStateChangeEvent  # abstract
    SUPERVISOR_STATE_CHANGE_RUNNING = SupervisorRunningEvent
    SUPERVISOR_STATE_CHANGE_STOPPING = SupervisorStoppingEvent

    TICK = TickEvent  # abstract
    TICK_5 = Tick5Event
    TICK_60 = Tick60Event
    TICK_3600 = Tick3600Event

    PROCESS_GROUP = ProcessGroupEvent  # abstract
    PROCESS_GROUP_ADDED = ProcessGroupAddedEvent
    PROCESS_GROUP_REMOVED = ProcessGroupRemovedEvent


def get_event_name_by_type(requested):
    for name, typ in EventTypes.__dict__.items():
        if typ is requested:
            return name
    return None


########################################
# ../utils/fds.py


class PipeFds(ta.NamedTuple):
    r: Fd
    w: Fd


def make_pipe() -> PipeFds:
    return PipeFds(*os.pipe())  # type: ignore


def read_fd(fd: Fd) -> bytes:
    try:
        data = os.read(fd, 2 << 16)  # 128K
    except OSError as why:
        if why.args[0] not in (errno.EWOULDBLOCK, errno.EBADF, errno.EINTR):
            raise
        data = b''
    return data


def close_fd(fd: Fd) -> bool:
    try:
        os.close(fd)
    except OSError:
        return False
    return True


def is_fd_open(fd: Fd) -> bool:
    try:
        n = os.dup(fd)
    except OSError:
        return False
    os.close(n)
    return True


def get_open_fds(limit: int) -> ta.FrozenSet[Fd]:
    return frozenset(fd for i in range(limit) if is_fd_open(fd := Fd(i)))


########################################
# ../utils/os.py


##


def real_exit(code: Rc) -> None:
    os._exit(code)  # noqa


##


def decode_wait_status(sts: int) -> ta.Tuple[Rc, str]:
    """
    Decode the status returned by wait() or waitpid().

    Return a tuple (exitstatus, message) where exitstatus is the exit status, or -1 if the process was killed by a
    signal; and message is a message telling what happened. It is the caller's responsibility to display the message.
    """

    if os.WIFEXITED(sts):
        es = os.WEXITSTATUS(sts) & 0xffff
        msg = f'exit status {es}'
        return Rc(es), msg

    elif os.WIFSIGNALED(sts):
        sig = os.WTERMSIG(sts)
        msg = f'terminated by {sig_name(sig)}'
        if hasattr(os, 'WCOREDUMP'):
            iscore = os.WCOREDUMP(sts)
        else:
            iscore = bool(sts & 0x80)
        if iscore:
            msg += ' (core dumped)'
        return Rc(-1), msg

    else:
        msg = 'unknown termination cause 0x%04x' % sts  # noqa
        return Rc(-1), msg


########################################
# ../utils/users.py


##


def name_to_uid(name: str) -> Uid:
    try:
        uid = int(name)
    except ValueError:
        try:
            pwdrec = pwd.getpwnam(name)
        except KeyError:
            raise ValueError(f'Invalid user name {name}')  # noqa
        uid = pwdrec[2]
    else:
        try:
            pwd.getpwuid(uid)  # check if uid is valid
        except KeyError:
            raise ValueError(f'Invalid user id {name}')  # noqa
    return Uid(uid)


def name_to_gid(name: str) -> Gid:
    try:
        gid = int(name)
    except ValueError:
        try:
            grprec = grp.getgrnam(name)
        except KeyError:
            raise ValueError(f'Invalid group name {name}')  # noqa
        gid = grprec[2]
    else:
        try:
            grp.getgrgid(gid)  # check if gid is valid
        except KeyError:
            raise ValueError(f'Invalid group id {name}')  # noqa
    return Gid(gid)


def gid_for_uid(uid: Uid) -> Gid:
    pwrec = pwd.getpwuid(uid)
    return Gid(pwrec[3])


##


@dc.dataclass(frozen=True)
class User:
    name: str
    uid: Uid
    gid: Gid


def get_user(name: str) -> User:
    return User(
        name=name,
        uid=(uid := name_to_uid(name)),
        gid=gid_for_uid(uid),
    )


########################################
# ../../../omlish/lite/fdio/handlers.py


class FdIoHandler(abc.ABC):
    @abc.abstractmethod
    def fd(self) -> int:
        raise NotImplementedError

    #

    @property
    @abc.abstractmethod
    def closed(self) -> bool:
        raise NotImplementedError

    @abc.abstractmethod
    def close(self) -> None:
        raise NotImplementedError

    #

    def readable(self) -> bool:
        return False

    def writable(self) -> bool:
        return False

    #

    def on_readable(self) -> None:
        raise TypeError

    def on_writable(self) -> None:
        raise TypeError

    def on_error(self, exc: ta.Optional[BaseException] = None) -> None:  # noqa
        pass


class SocketFdIoHandler(FdIoHandler, abc.ABC):
    def __init__(
            self,
            addr: SocketAddress,
            sock: socket.socket,
    ) -> None:
        super().__init__()

        self._addr = addr
        self._sock: ta.Optional[socket.socket] = sock

    def fd(self) -> int:
        return check_not_none(self._sock).fileno()

    @property
    def closed(self) -> bool:
        return self._sock is None

    def close(self) -> None:
        if self._sock is not None:
            self._sock.close()
        self._sock = None


########################################
# ../../../omlish/lite/fdio/kqueue.py


KqueueFdIoPoller: ta.Optional[ta.Type[FdIoPoller]]
if sys.platform == 'darwin' or sys.platform.startswith('freebsd'):

    class _KqueueFdIoPoller(FdIoPoller):
        DEFAULT_MAX_EVENTS = 1000

        def __init__(
                self,
                *,
                max_events: int = DEFAULT_MAX_EVENTS,
        ) -> None:
            super().__init__()

            self._max_events = max_events

            self._kqueue: ta.Optional[ta.Any] = None

        #

        def _get_kqueue(self) -> 'select.kqueue':
            if (kq := self._kqueue) is not None:
                return kq
            kq = select.kqueue()
            self._kqueue = kq
            return kq

        def close(self) -> None:
            if self._kqueue is not None:
                self._kqueue.close()
                self._kqueue = None

        def reopen(self) -> None:
            for fd in self._readable:
                self._register_readable(fd)
            for fd in self._writable:
                self._register_writable(fd)

        #

        def _register_readable(self, fd: int) -> None:
            self._control(fd, select.KQ_FILTER_READ, select.KQ_EV_ADD)

        def _register_writable(self, fd: int) -> None:
            self._control(fd, select.KQ_FILTER_WRITE, select.KQ_EV_ADD)

        def _unregister_readable(self, fd: int) -> None:
            self._control(fd, select.KQ_FILTER_READ, select.KQ_EV_DELETE)

        def _unregister_writable(self, fd: int) -> None:
            self._control(fd, select.KQ_FILTER_WRITE, select.KQ_EV_DELETE)

        def _control(self, fd: int, filter: int, flags: int) -> None:  # noqa
            ke = select.kevent(fd, filter=filter, flags=flags)
            kq = self._get_kqueue()
            try:
                kq.control([ke], 0)

            except OSError as exc:
                if exc.errno == errno.EBADF:
                    # log.debug('EBADF encountered in kqueue. Invalid file descriptor %s', ke.ident)
                    pass
                elif exc.errno == errno.ENOENT:
                    # Can happen when trying to remove an already closed socket
                    pass
                else:
                    raise

        #

        def poll(self, timeout: ta.Optional[float]) -> FdIoPoller.PollResult:
            kq = self._get_kqueue()
            try:
                kes = kq.control(None, self._max_events, timeout)

            except OSError as exc:
                if exc.errno == errno.EINTR:
                    return FdIoPoller.PollResult(msg='EINTR encountered in poll', exc=exc)
                else:
                    raise

            r: ta.List[int] = []
            w: ta.List[int] = []
            for ke in kes:
                if ke.filter == select.KQ_FILTER_READ:
                    r.append(ke.ident)
                if ke.filter == select.KQ_FILTER_WRITE:
                    w.append(ke.ident)

            return FdIoPoller.PollResult(r, w)

    KqueueFdIoPoller = _KqueueFdIoPoller
else:
    KqueueFdIoPoller = None


########################################
# ../../../omlish/lite/http/parsing.py
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


class ParseHttpRequestResult(abc.ABC):  # noqa
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
        check_not_isinstance(self.fn, type)

    def provider_fn(self) -> InjectorProviderFn:
        def pfn(i: Injector) -> ta.Any:
            return i.inject(self.fn)

        return pfn


@dc.dataclass(frozen=True)
class CtorInjectorProvider(InjectorProvider):
    cls_: type

    def __post_init__(self) -> None:
        check_isinstance(self.cls_, type)

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
        check_isinstance(self.p, InjectorProvider)

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
        check_isinstance(self.k, InjectorKey)

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
        skip_names.update(check_not_isinstance(skip_kwargs, str))

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

        self._bs = check_isinstance(bs, InjectorBindings)
        self._p: ta.Optional[Injector] = check_isinstance(p, (Injector, type(None)))

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
            check_in(key, self._seen_keys)
            check_not_in(key, self._provisions)
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

    _FN_TYPES: ta.Tuple[type, ...] = (
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
        check_isinstance(icls, type)
        if icls not in cls._FN_TYPES:
            cls._FN_TYPES = (*cls._FN_TYPES, icls)
        return icls

    _BANNED_BIND_TYPES: ta.Tuple[type, ...] = (
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
                key_cls: ta.Any = check_valid_injector_key_cls(check_not_none(insp.type_hints.get('return')))
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


class Injection:
    def __new__(cls, *args, **kwargs):  # noqa
        raise TypeError

    # keys

    @classmethod
    def as_key(cls, o: ta.Any) -> InjectorKey:
        return as_injector_key(o)

    @classmethod
    def array(cls, o: ta.Any) -> InjectorKey:
        return dc.replace(as_injector_key(o), array=True)

    @classmethod
    def tag(cls, o: ta.Any, t: ta.Any) -> InjectorKey:
        return dc.replace(as_injector_key(o), tag=t)

    # bindings

    @classmethod
    def as_bindings(cls, *args: InjectorBindingOrBindings) -> InjectorBindings:
        return as_injector_bindings(*args)

    @classmethod
    def override(cls, p: InjectorBindings, *args: InjectorBindingOrBindings) -> InjectorBindings:
        return injector_override(p, *args)

    # injector

    @classmethod
    def create_injector(cls, *args: InjectorBindingOrBindings, parent: ta.Optional[Injector] = None) -> Injector:
        return _Injector(as_injector_bindings(*args), parent)

    # binder

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

    @classmethod
    def bind_factory(
            cls,
            fn: ta.Callable[..., T],
            cls_: U,
            ann: ta.Any = None,
    ) -> InjectorBindingOrBindings:
        return cls.bind(make_injector_factory(fn, cls_, ann))

    @classmethod
    def bind_array(
            cls,
            obj: ta.Any = None,
            *,
            tag: ta.Any = None,
    ) -> InjectorBindingOrBindings:
        return bind_injector_array(obj, tag=tag)

    @classmethod
    def bind_array_type(
            cls,
            ele: ta.Union[InjectorKey, InjectorKeyCls],
            cls_: U,
            ann: ta.Any = None,
    ) -> InjectorBindingOrBindings:
        return cls.bind(make_injector_array_type(ele, cls_, ann))


inj = Injection


########################################
# ../../../omlish/lite/io.py


class DelimitingBuffer:
    """
    https://github.com/python-trio/trio/issues/796 :|
    """

    #

    class Error(Exception):
        def __init__(self, buffer: 'DelimitingBuffer') -> None:
            super().__init__(buffer)
            self.buffer = buffer

        def __repr__(self) -> str:
            return attr_repr(self, 'buffer')

    class ClosedError(Error):
        pass

    #

    DEFAULT_DELIMITERS: bytes = b'\n'

    def __init__(
            self,
            delimiters: ta.Iterable[int] = DEFAULT_DELIMITERS,
            *,
            keep_ends: bool = False,
            max_size: ta.Optional[int] = None,
    ) -> None:
        super().__init__()

        self._delimiters = frozenset(check_isinstance(d, int) for d in delimiters)
        self._keep_ends = keep_ends
        self._max_size = max_size

        self._buf: ta.Optional[io.BytesIO] = io.BytesIO()

    #

    @property
    def is_closed(self) -> bool:
        return self._buf is None

    def tell(self) -> int:
        if (buf := self._buf) is None:
            raise self.ClosedError(self)
        return buf.tell()

    def peek(self) -> bytes:
        if (buf := self._buf) is None:
            raise self.ClosedError(self)
        return buf.getvalue()

    def _find_delim(self, data: ta.Union[bytes, bytearray], i: int) -> ta.Optional[int]:
        r = None  # type: int | None
        for d in self._delimiters:
            if (p := data.find(d, i)) >= 0:
                if r is None or p < r:
                    r = p
        return r

    def _append_and_reset(self, chunk: bytes) -> bytes:
        buf = check_not_none(self._buf)
        if not buf.tell():
            return chunk

        buf.write(chunk)
        ret = buf.getvalue()
        buf.seek(0)
        buf.truncate()
        return ret

    class Incomplete(ta.NamedTuple):
        b: bytes

    def feed(self, data: ta.Union[bytes, bytearray]) -> ta.Generator[ta.Union[bytes, Incomplete], None, None]:
        if (buf := self._buf) is None:
            raise self.ClosedError(self)

        if not data:
            self._buf = None

            if buf.tell():
                yield self.Incomplete(buf.getvalue())

            return

        l = len(data)
        i = 0
        while i < l:
            if (p := self._find_delim(data, i)) is None:
                break

            n = p + 1
            if self._keep_ends:
                p = n

            yield self._append_and_reset(data[i:p])

            i = n

        if i >= l:
            return

        if self._max_size is None:
            buf.write(data[i:])
            return

        while i < l:
            remaining_data_len = l - i
            remaining_buf_capacity = self._max_size - buf.tell()

            if remaining_data_len < remaining_buf_capacity:
                buf.write(data[i:])
                return

            p = i + remaining_buf_capacity
            yield self.Incomplete(self._append_and_reset(data[i:p]))
            i = p


class ReadableListBuffer:
    def __init__(self) -> None:
        super().__init__()
        self._lst: list[bytes] = []

    def feed(self, d: bytes) -> None:
        if d:
            self._lst.append(d)

    def _chop(self, i: int, e: int) -> bytes:
        lst = self._lst
        d = lst[i]

        o = b''.join([
            *lst[:i],
            d[:e],
        ])

        self._lst = [
            *([d[e:]] if e < len(d) else []),
            *lst[i + 1:],
        ]

        return o

    def read(self, n: ta.Optional[int] = None) -> ta.Optional[bytes]:
        if n is None:
            o = b''.join(self._lst)
            self._lst = []
            return o

        if not (lst := self._lst):
            return None

        c = 0
        for i, d in enumerate(lst):
            r = n - c
            if (l := len(d)) >= r:
                return self._chop(i, r)
            c += l

        return None

    def read_until(self, delim: bytes = b'\n') -> ta.Optional[bytes]:
        if not (lst := self._lst):
            return None

        for i, d in enumerate(lst):
            if (p := d.find(delim)) >= 0:
                return self._chop(i, p + len(delim))

        return None


class IncrementalWriteBuffer:
    def __init__(
            self,
            data: bytes,
            *,
            write_size: int = 0x10000,
    ) -> None:
        super().__init__()

        check_non_empty(data)
        self._len = len(data)
        self._write_size = write_size

        self._lst = [
            data[i:i + write_size]
            for i in range(0, len(data), write_size)
        ]
        self._pos = 0

    @property
    def rem(self) -> int:
        return self._len - self._pos

    def write(self, fn: ta.Callable[[bytes], int]) -> int:
        lst = check_non_empty(self._lst)

        t = 0
        for i, d in enumerate(lst):  # noqa
            n = fn(check_non_empty(d))
            if not n:
                break
            t += n

        if t:
            self._lst = [
                *([d[n:]] if n < len(d) else []),
                *lst[i + 1:],
            ]
            self._pos += t

        return t


########################################
# ../../../omlish/lite/journald.py


##


class sd_iovec(ct.Structure):  # noqa
    pass


sd_iovec._fields_ = [
    ('iov_base', ct.c_void_p),  # Pointer to data.
    ('iov_len', ct.c_size_t),  # Length of data.
]


##


@cached_nullary
def sd_libsystemd() -> ta.Any:
    lib = ct.CDLL('libsystemd.so.0')

    lib.sd_journal_sendv.restype = ct.c_int
    lib.sd_journal_sendv.argtypes = [ct.POINTER(sd_iovec), ct.c_int]

    return lib


@cached_nullary
def sd_try_libsystemd() -> ta.Optional[ta.Any]:
    try:
        return sd_libsystemd()
    except OSError:  # noqa
        return None


##


def sd_journald_send(**fields: str) -> int:
    lib = sd_libsystemd()

    msgs = [
        f'{k.upper()}={v}\0'.encode('utf-8')
        for k, v in fields.items()
    ]

    vec = (sd_iovec * len(msgs))()
    cl = (ct.c_char_p * len(msgs))()  # noqa
    for i in range(len(msgs)):
        vec[i].iov_base = ct.cast(ct.c_char_p(msgs[i]), ct.c_void_p)
        vec[i].iov_len = len(msgs[i]) - 1

    return lib.sd_journal_sendv(vec, len(msgs))


##


SD_LOG_LEVEL_MAP: ta.Mapping[int, int] = {
    logging.FATAL: syslog.LOG_EMERG,  # system is unusable
    # LOG_ALERT ?  # action must be taken immediately
    logging.CRITICAL: syslog.LOG_CRIT,
    logging.ERROR: syslog.LOG_ERR,
    logging.WARNING: syslog.LOG_WARNING,
    # LOG_NOTICE ?  # normal but significant condition
    logging.INFO: syslog.LOG_INFO,
    logging.DEBUG: syslog.LOG_DEBUG,
}


class JournaldLogHandler(logging.Handler):
    """
    TODO:
     - fallback handler for when this barfs
    """

    def __init__(
            self,
            *,
            use_formatter_output: bool = False,
    ) -> None:
        super().__init__()

        sd_libsystemd()

        self._use_formatter_output = use_formatter_output

    #

    EXTRA_RECORD_ATTRS_BY_JOURNALD_FIELD: ta.ClassVar[ta.Mapping[str, str]] = {
        'name': 'name',
        'module': 'module',
        'exception': 'exc_text',
        'thread_name': 'threadName',
        'task_name': 'taskName',
    }

    def make_fields(self, record: logging.LogRecord) -> ta.Mapping[str, str]:
        formatter_message = self.format(record)
        if self._use_formatter_output:
            message = formatter_message
        else:
            message = record.message

        fields: dict[str, str] = {
            'message': message,
            'priority': str(SD_LOG_LEVEL_MAP[record.levelno]),
            'tid': str(threading.get_ident()),
        }

        if (pathname := record.pathname) is not None:
            fields['code_file'] = pathname
        if (lineno := record.lineno) is not None:
            fields['code_lineno'] = str(lineno)
        if (func_name := record.funcName) is not None:
            fields['code_func'] = func_name

        for f, a in self.EXTRA_RECORD_ATTRS_BY_JOURNALD_FIELD.items():
            if (v := getattr(record, a, None)) is not None:
                fields[f] = str(v)

        return fields

    #

    def emit(self, record: logging.LogRecord) -> None:
        try:
            fields = self.make_fields(record)

            if rc := sd_journald_send(**fields):
                raise RuntimeError(f'{self.__class__.__name__}.emit failed: {rc=}')  # noqa

        except RecursionError:  # See issue 36272
            raise

        except Exception:  # noqa
            self.handleError(record)


def journald_log_handler_factory(
        *,
        no_tty_check: bool = False,
        no_fallback: bool = False,
) -> logging.Handler:
    if (
            sys.platform == 'linux' and
            (no_tty_check or not sys.stderr.isatty()) and
            (no_fallback or sd_try_libsystemd() is not None)
    ):
        return JournaldLogHandler()

    return logging.StreamHandler()


########################################
# ../../../omlish/lite/logs.py
"""
TODO:
 - translate json keys
 - debug
"""


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


##


class StandardLogHandler(ProxyLogHandler):
    pass


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
) -> ta.Optional[StandardLogHandler]:
    with _locking_logging_module_lock():
        if target is None:
            target = logging.root

        #

        if not force:
            if any(isinstance(h, StandardLogHandler) for h in list(target.handlers)):
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

        return StandardLogHandler(handler)


########################################
# ../../../omlish/lite/marshal.py
"""
TODO:
 - pickle stdlib objs? have to pin to 3.8 pickle protocol, will be cross-version
 - nonstrict toggle
"""


##


class ObjMarshaler(abc.ABC):
    @abc.abstractmethod
    def marshal(self, o: ta.Any) -> ta.Any:
        raise NotImplementedError

    @abc.abstractmethod
    def unmarshal(self, o: ta.Any) -> ta.Any:
        raise NotImplementedError


class NopObjMarshaler(ObjMarshaler):
    def marshal(self, o: ta.Any) -> ta.Any:
        return o

    def unmarshal(self, o: ta.Any) -> ta.Any:
        return o


@dc.dataclass()
class ProxyObjMarshaler(ObjMarshaler):
    m: ta.Optional[ObjMarshaler] = None

    def marshal(self, o: ta.Any) -> ta.Any:
        return check_not_none(self.m).marshal(o)

    def unmarshal(self, o: ta.Any) -> ta.Any:
        return check_not_none(self.m).unmarshal(o)


@dc.dataclass(frozen=True)
class CastObjMarshaler(ObjMarshaler):
    ty: type

    def marshal(self, o: ta.Any) -> ta.Any:
        return o

    def unmarshal(self, o: ta.Any) -> ta.Any:
        return self.ty(o)


class DynamicObjMarshaler(ObjMarshaler):
    def marshal(self, o: ta.Any) -> ta.Any:
        return marshal_obj(o)

    def unmarshal(self, o: ta.Any) -> ta.Any:
        return o


@dc.dataclass(frozen=True)
class Base64ObjMarshaler(ObjMarshaler):
    ty: type

    def marshal(self, o: ta.Any) -> ta.Any:
        return base64.b64encode(o).decode('ascii')

    def unmarshal(self, o: ta.Any) -> ta.Any:
        return self.ty(base64.b64decode(o))


@dc.dataclass(frozen=True)
class EnumObjMarshaler(ObjMarshaler):
    ty: type

    def marshal(self, o: ta.Any) -> ta.Any:
        return o.name

    def unmarshal(self, o: ta.Any) -> ta.Any:
        return self.ty.__members__[o]  # type: ignore


@dc.dataclass(frozen=True)
class OptionalObjMarshaler(ObjMarshaler):
    item: ObjMarshaler

    def marshal(self, o: ta.Any) -> ta.Any:
        if o is None:
            return None
        return self.item.marshal(o)

    def unmarshal(self, o: ta.Any) -> ta.Any:
        if o is None:
            return None
        return self.item.unmarshal(o)


@dc.dataclass(frozen=True)
class MappingObjMarshaler(ObjMarshaler):
    ty: type
    km: ObjMarshaler
    vm: ObjMarshaler

    def marshal(self, o: ta.Any) -> ta.Any:
        return {self.km.marshal(k): self.vm.marshal(v) for k, v in o.items()}

    def unmarshal(self, o: ta.Any) -> ta.Any:
        return self.ty((self.km.unmarshal(k), self.vm.unmarshal(v)) for k, v in o.items())


@dc.dataclass(frozen=True)
class IterableObjMarshaler(ObjMarshaler):
    ty: type
    item: ObjMarshaler

    def marshal(self, o: ta.Any) -> ta.Any:
        return [self.item.marshal(e) for e in o]

    def unmarshal(self, o: ta.Any) -> ta.Any:
        return self.ty(self.item.unmarshal(e) for e in o)


@dc.dataclass(frozen=True)
class DataclassObjMarshaler(ObjMarshaler):
    ty: type
    fs: ta.Mapping[str, ObjMarshaler]
    nonstrict: bool = False

    def marshal(self, o: ta.Any) -> ta.Any:
        return {k: m.marshal(getattr(o, k)) for k, m in self.fs.items()}

    def unmarshal(self, o: ta.Any) -> ta.Any:
        return self.ty(**{k: self.fs[k].unmarshal(v) for k, v in o.items() if not self.nonstrict or k in self.fs})


@dc.dataclass(frozen=True)
class PolymorphicObjMarshaler(ObjMarshaler):
    class Impl(ta.NamedTuple):
        ty: type
        tag: str
        m: ObjMarshaler

    impls_by_ty: ta.Mapping[type, Impl]
    impls_by_tag: ta.Mapping[str, Impl]

    def marshal(self, o: ta.Any) -> ta.Any:
        impl = self.impls_by_ty[type(o)]
        return {impl.tag: impl.m.marshal(o)}

    def unmarshal(self, o: ta.Any) -> ta.Any:
        [(t, v)] = o.items()
        impl = self.impls_by_tag[t]
        return impl.m.unmarshal(v)


@dc.dataclass(frozen=True)
class DatetimeObjMarshaler(ObjMarshaler):
    ty: type

    def marshal(self, o: ta.Any) -> ta.Any:
        return o.isoformat()

    def unmarshal(self, o: ta.Any) -> ta.Any:
        return self.ty.fromisoformat(o)  # type: ignore


class DecimalObjMarshaler(ObjMarshaler):
    def marshal(self, o: ta.Any) -> ta.Any:
        return str(check_isinstance(o, decimal.Decimal))

    def unmarshal(self, v: ta.Any) -> ta.Any:
        return decimal.Decimal(check_isinstance(v, str))


class FractionObjMarshaler(ObjMarshaler):
    def marshal(self, o: ta.Any) -> ta.Any:
        fr = check_isinstance(o, fractions.Fraction)
        return [fr.numerator, fr.denominator]

    def unmarshal(self, v: ta.Any) -> ta.Any:
        num, denom = check_isinstance(v, list)
        return fractions.Fraction(num, denom)


class UuidObjMarshaler(ObjMarshaler):
    def marshal(self, o: ta.Any) -> ta.Any:
        return str(o)

    def unmarshal(self, o: ta.Any) -> ta.Any:
        return uuid.UUID(o)


##


_DEFAULT_OBJ_MARSHALERS: ta.Dict[ta.Any, ObjMarshaler] = {
    **{t: NopObjMarshaler() for t in (type(None),)},
    **{t: CastObjMarshaler(t) for t in (int, float, str, bool)},
    **{t: Base64ObjMarshaler(t) for t in (bytes, bytearray)},
    **{t: IterableObjMarshaler(t, DynamicObjMarshaler()) for t in (list, tuple, set, frozenset)},
    **{t: MappingObjMarshaler(t, DynamicObjMarshaler(), DynamicObjMarshaler()) for t in (dict,)},

    ta.Any: DynamicObjMarshaler(),

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


def _make_obj_marshaler(
        ty: ta.Any,
        rec: ta.Callable[[ta.Any], ObjMarshaler],
        *,
        nonstrict_dataclasses: bool = False,
) -> ObjMarshaler:
    if isinstance(ty, type):
        if abc.ABC in ty.__bases__:
            impls = [  # type: ignore
                PolymorphicObjMarshaler.Impl(
                    ity,
                    ity.__qualname__,
                    rec(ity),
                )
                for ity in deep_subclasses(ty)
                if abc.ABC not in ity.__bases__
            ]
            return PolymorphicObjMarshaler(
                {i.ty: i for i in impls},
                {i.tag: i for i in impls},
            )

        if issubclass(ty, enum.Enum):
            return EnumObjMarshaler(ty)

        if dc.is_dataclass(ty):
            return DataclassObjMarshaler(
                ty,
                {f.name: rec(f.type) for f in dc.fields(ty)},
                nonstrict=nonstrict_dataclasses,
            )

    if is_generic_alias(ty):
        try:
            mt = _OBJ_MARSHALER_GENERIC_MAPPING_TYPES[ta.get_origin(ty)]
        except KeyError:
            pass
        else:
            k, v = ta.get_args(ty)
            return MappingObjMarshaler(mt, rec(k), rec(v))

        try:
            st = _OBJ_MARSHALER_GENERIC_ITERABLE_TYPES[ta.get_origin(ty)]
        except KeyError:
            pass
        else:
            [e] = ta.get_args(ty)
            return IterableObjMarshaler(st, rec(e))

        if is_union_alias(ty):
            return OptionalObjMarshaler(rec(get_optional_alias_arg(ty)))

    raise TypeError(ty)


##


_OBJ_MARSHALERS_LOCK = threading.RLock()

_OBJ_MARSHALERS: ta.Dict[ta.Any, ObjMarshaler] = dict(_DEFAULT_OBJ_MARSHALERS)

_OBJ_MARSHALER_PROXIES: ta.Dict[ta.Any, ProxyObjMarshaler] = {}


def register_opj_marshaler(ty: ta.Any, m: ObjMarshaler) -> None:
    with _OBJ_MARSHALERS_LOCK:
        if ty in _OBJ_MARSHALERS:
            raise KeyError(ty)
        _OBJ_MARSHALERS[ty] = m


def get_obj_marshaler(
        ty: ta.Any,
        *,
        no_cache: bool = False,
        **kwargs: ta.Any,
) -> ObjMarshaler:
    with _OBJ_MARSHALERS_LOCK:
        if not no_cache:
            try:
                return _OBJ_MARSHALERS[ty]
            except KeyError:
                pass

        try:
            return _OBJ_MARSHALER_PROXIES[ty]
        except KeyError:
            pass

        rec = functools.partial(
            get_obj_marshaler,
            no_cache=no_cache,
            **kwargs,
        )

        p = ProxyObjMarshaler()
        _OBJ_MARSHALER_PROXIES[ty] = p
        try:
            m = _make_obj_marshaler(ty, rec, **kwargs)
        finally:
            del _OBJ_MARSHALER_PROXIES[ty]
        p.m = m

        if not no_cache:
            _OBJ_MARSHALERS[ty] = m
        return m


##


def marshal_obj(o: ta.Any, ty: ta.Any = None) -> ta.Any:
    return get_obj_marshaler(ty if ty is not None else type(o)).marshal(o)


def unmarshal_obj(o: ta.Any, ty: ta.Union[ta.Type[T], ta.Any]) -> T:
    return get_obj_marshaler(ty).unmarshal(o)


########################################
# ../../../omlish/lite/runtime.py


@cached_nullary
def is_debugger_attached() -> bool:
    return any(frame[1].endswith('pydevd.py') for frame in inspect.stack())


REQUIRED_PYTHON_VERSION = (3, 8)


def check_runtime_version() -> None:
    if sys.version_info < REQUIRED_PYTHON_VERSION:
        raise OSError(f'Requires python {REQUIRED_PYTHON_VERSION}, got {sys.version_info} from {sys.executable}')  # noqa


########################################
# ../../configs.py


def read_config_file(
        path: str,
        cls: ta.Type[T],
        *,
        prepare: ta.Optional[ta.Callable[[ConfigMapping], ConfigMapping]] = None,
) -> T:
    with open(path) as cf:
        if path.endswith('.toml'):
            config_dct = toml_loads(cf.read())
        else:
            config_dct = json.loads(cf.read())

    if prepare is not None:
        config_dct = prepare(config_dct)  # type: ignore

    return unmarshal_obj(config_dct, cls)


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
            check_isinstance(v, ta.Mapping)
            if name_key in v:
                n = v[name_key]
                if k != n:
                    raise KeyError(f'Given names do not match: {n} != {k}')
                lst.append(v)
            else:
                lst.append({name_key: k, **v})

    else:
        check_not_isinstance(o, str)
        lst.extend(o)

    seen = set()
    for d in lst:
        n = d['name']
        if n in d:
            raise KeyError(f'Duplicate name: {n}')
        seen.add(n)

    return lst


########################################
# ../pipes.py


@dc.dataclass(frozen=True)
class ProcessPipes:
    child_stdin: ta.Optional[Fd] = None
    stdin: ta.Optional[Fd] = None

    stdout: ta.Optional[Fd] = None
    child_stdout: ta.Optional[Fd] = None

    stderr: ta.Optional[Fd] = None
    child_stderr: ta.Optional[Fd] = None

    def child_fds(self) -> ta.List[Fd]:
        return [fd for fd in [self.child_stdin, self.child_stdout, self.child_stderr] if fd is not None]

    def parent_fds(self) -> ta.List[Fd]:
        return [fd for fd in [self.stdin, self.stdout, self.stderr] if fd is not None]


def make_process_pipes(stderr=True) -> ProcessPipes:
    """
    Create pipes for parent to child stdin/stdout/stderr communications. Open fd in non-blocking mode so we can read
    them in the mainloop without blocking. If stderr is False, don't create a pipe for stderr.
    """

    pipes: ta.Dict[str, ta.Optional[Fd]] = {
        'child_stdin': None,
        'stdin': None,

        'stdout': None,
        'child_stdout': None,

        'stderr': None,
        'child_stderr': None,
    }

    try:
        pipes['child_stdin'], pipes['stdin'] = make_pipe()
        pipes['stdout'], pipes['child_stdout'] = make_pipe()

        if stderr:
            pipes['stderr'], pipes['child_stderr'] = make_pipe()

        for fd in (
                pipes['stdout'],
                pipes['stderr'],
                pipes['stdin'],
        ):
            if fd is not None:
                flags = fcntl.fcntl(fd, fcntl.F_GETFL) | os.O_NDELAY
                fcntl.fcntl(fd, fcntl.F_SETFL, flags)

        return ProcessPipes(**pipes)

    except OSError:
        for fd in pipes.values():
            if fd is not None:
                close_fd(fd)

        raise


def close_pipes(pipes: ProcessPipes) -> None:
    close_parent_pipes(pipes)
    close_child_pipes(pipes)


def close_parent_pipes(pipes: ProcessPipes) -> None:
    for fd in pipes.parent_fds():
        close_fd(fd)


def close_child_pipes(pipes: ProcessPipes) -> None:
    for fd in pipes.child_fds():
        close_fd(fd)


########################################
# ../setup.py


##


SupervisorUser = ta.NewType('SupervisorUser', User)


##


class DaemonizeListener(abc.ABC):  # noqa
    def before_daemonize(self) -> None:  # noqa
        pass

    def after_daemonize(self) -> None:  # noqa
        pass


DaemonizeListeners = ta.NewType('DaemonizeListeners', ta.Sequence[DaemonizeListener])


##


class SupervisorSetup(abc.ABC):
    @abc.abstractmethod
    def setup(self) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def cleanup(self) -> None:
        raise NotImplementedError


########################################
# ../../../omlish/lite/http/handlers.py


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
    data: ta.Optional[bytes] = None
    close_connection: ta.Optional[bool] = None


class HttpHandlerError(Exception):
    pass


class UnsupportedMethodHttpHandlerError(Exception):
    pass


########################################
# ../configs.py


##


class RestartWhenExitUnexpected:
    pass


class RestartUnconditionally:
    pass


##


@dc.dataclass(frozen=True)
class ProcessConfig:
    name: str
    command: str

    uid: ta.Optional[int] = None
    directory: ta.Optional[str] = None
    umask: ta.Optional[int] = None
    priority: int = 999

    auto_start: bool = True
    auto_restart: str = 'unexpected'

    start_secs: int = 1
    start_retries: int = 3

    num_procs: int = 1
    num_procs_start: int = 0

    @dc.dataclass(frozen=True)
    class Log:
        file: ta.Optional[str] = None
        capture_max_bytes: ta.Optional[int] = None
        events_enabled: bool = False
        syslog: bool = False
        backups: ta.Optional[int] = None
        max_bytes: ta.Optional[int] = None

    stdout: Log = Log()
    stderr: Log = Log()

    stop_signal: int = signal.SIGTERM
    stop_wait_secs: int = 10
    stop_as_group: bool = False

    kill_as_group: bool = False

    exitcodes: ta.Sequence[int] = (0,)

    redirect_stderr: bool = False

    environment: ta.Optional[ta.Mapping[str, str]] = None


@dc.dataclass(frozen=True)
class ProcessGroupConfig:
    name: str

    priority: int = 999

    processes: ta.Optional[ta.Sequence[ProcessConfig]] = None


@dc.dataclass(frozen=True)
class ServerConfig:
    user: ta.Optional[str] = None
    nodaemon: bool = False
    umask: int = 0o22
    directory: ta.Optional[str] = None
    logfile: str = 'supervisord.log'
    logfile_max_bytes: int = 50 * 1024 * 1024
    logfile_backups: int = 10
    loglevel: int = logging.INFO
    pidfile: str = 'supervisord.pid'
    identifier: str = 'supervisor'
    child_logdir: str = '/dev/null'
    min_fds: int = 1024
    min_procs: int = 200
    nocleanup: bool = False
    strip_ansi: bool = False
    silent: bool = False

    groups: ta.Optional[ta.Sequence[ProcessGroupConfig]] = None

    @classmethod
    def new(
            cls,
            umask: ta.Union[int, str] = 0o22,
            directory: ta.Optional[str] = None,
            logfile: str = 'supervisord.log',
            logfile_max_bytes: ta.Union[int, str] = 50 * 1024 * 1024,
            loglevel: ta.Union[int, str] = logging.INFO,
            pidfile: str = 'supervisord.pid',
            child_logdir: ta.Optional[str] = None,
            **kwargs: ta.Any,
    ) -> 'ServerConfig':
        return cls(
            umask=parse_octal(umask),
            directory=check_existing_dir(directory) if directory is not None else None,
            logfile=check_path_with_existing_dir(logfile),
            logfile_max_bytes=parse_bytes_size(logfile_max_bytes),
            loglevel=parse_logging_level(loglevel),
            pidfile=check_path_with_existing_dir(pidfile),
            child_logdir=child_logdir if child_logdir else tempfile.gettempdir(),
            **kwargs,
        )


##


def prepare_process_group_config(dct: ConfigMapping) -> ConfigMapping:
    out = dict(dct)
    out['processes'] = build_config_named_children(out.get('processes'))
    return out


def prepare_server_config(dct: ta.Mapping[str, ta.Any]) -> ta.Mapping[str, ta.Any]:
    out = dict(dct)
    group_dcts = build_config_named_children(out.get('groups'))
    out['groups'] = [prepare_process_group_config(group_dct) for group_dct in group_dcts or []]
    return out


##


def parse_logging_level(value: ta.Union[str, int]) -> int:
    if isinstance(value, int):
        return value
    s = str(value).lower()
    level = logging.getLevelNamesMapping().get(s.upper())
    if level is None:
        raise ValueError(f'bad logging level name {value!r}')
    return level


########################################
# ../../../omlish/lite/http/coroserver.py
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
        data: ta.Optional[bytes] = None
        close_connection: ta.Optional[bool] = False

        def get_header(self, key: str) -> ta.Optional['CoroHttpServer._Header']:
            for h in self.headers or []:
                if h.key.lower() == key.lower():
                    return h
            return None

    #

    def _build_response_bytes(self, a: _Response) -> bytes:
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

        if a.data is not None:
            out.write(a.data)

        return out.getvalue()

    #

    DEFAULT_CONTENT_TYPE = 'text/plain'

    def _preprocess_response(self, resp: _Response) -> _Response:
        nh: ta.List[CoroHttpServer._Header] = []
        kw: ta.Dict[str, ta.Any] = {}

        if resp.get_header('Content-Type') is None:
            nh.append(self._Header('Content-Type', self._default_content_type))
        if resp.data is not None and resp.get_header('Content-Length') is None:
            nh.append(self._Header('Content-Length', str(len(resp.data))))

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

    class Io(abc.ABC):  # noqa
        pass

    #

    class AnyLogIo(Io):
        pass

    @dc.dataclass(frozen=True)
    class ParsedRequestLogIo(AnyLogIo):
        request: ParsedHttpRequest

    @dc.dataclass(frozen=True)
    class ErrorLogIo(AnyLogIo):
        error: 'CoroHttpServer.Error'

    #

    class AnyReadIo(Io):  # noqa
        pass

    @dc.dataclass(frozen=True)
    class ReadIo(AnyReadIo):
        sz: int

    @dc.dataclass(frozen=True)
    class ReadLineIo(AnyReadIo):
        sz: int

    #

    @dc.dataclass(frozen=True)
    class WriteIo(Io):
        data: bytes

    #

    def coro_handle(self) -> ta.Generator[Io, ta.Optional[bytes], None]:
        while True:
            gen = self.coro_handle_one()

            o = next(gen)
            i: ta.Optional[bytes]
            while True:
                if isinstance(o, self.AnyLogIo):
                    i = None
                    yield o

                elif isinstance(o, self.AnyReadIo):
                    i = check_isinstance((yield o), bytes)

                elif isinstance(o, self._Response):
                    i = None
                    r = self._preprocess_response(o)
                    b = self._build_response_bytes(r)
                    check_none((yield self.WriteIo(b)))

                else:
                    raise TypeError(o)

                try:
                    o = gen.send(i)
                except EOFError:
                    return
                except StopIteration:
                    break

    def coro_handle_one(self) -> ta.Generator[
        ta.Union[AnyLogIo, AnyReadIo, _Response],
        ta.Optional[bytes],
        None,
    ]:
        # Parse request

        gen = self._parser.coro_parse()
        sz = next(gen)
        while True:
            try:
                line = check_isinstance((yield self.ReadLineIo(sz)), bytes)
                sz = gen.send(line)
            except StopIteration as e:
                parsed = e.value
                break

        if isinstance(parsed, EmptyParsedHttpResult):
            raise EOFError  # noqa

        if isinstance(parsed, ParseHttpRequestError):
            err = self._build_error(
                parsed.code,
                *parsed.message,
                version=parsed.version,
            )
            yield self.ErrorLogIo(err)
            yield self._build_error_response(err)
            return

        parsed = check_isinstance(parsed, ParsedHttpRequest)

        # Log

        check_none((yield self.ParsedRequestLogIo(parsed)))

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
            request_data = check_isinstance((yield self.ReadIo(int(cl))), bytes)
        else:
            request_data = None

        # Build request

        handler_request = HttpHandlerRequest(
            client_address=self._client_address,
            method=check_not_none(parsed.method),
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


##


class CoroHttpServerSocketHandler(SocketHandler):
    def __init__(
            self,
            client_address: SocketAddress,
            rfile: ta.BinaryIO,
            wfile: ta.BinaryIO,
            *,
            server_factory: CoroHttpServerFactory,
            log_handler: ta.Optional[ta.Callable[[CoroHttpServer, CoroHttpServer.AnyLogIo], None]] = None,
    ) -> None:
        super().__init__(
            client_address,
            rfile,
            wfile,
        )

        self._server_factory = server_factory
        self._log_handler = log_handler

    def handle(self) -> None:
        server = self._server_factory(self._client_address)

        gen = server.coro_handle()

        o = next(gen)
        while True:
            if isinstance(o, CoroHttpServer.AnyLogIo):
                i = None
                if self._log_handler is not None:
                    self._log_handler(server, o)

            elif isinstance(o, CoroHttpServer.ReadIo):
                i = self._rfile.read(o.sz)

            elif isinstance(o, CoroHttpServer.ReadLineIo):
                i = self._rfile.readline(o.sz)

            elif isinstance(o, CoroHttpServer.WriteIo):
                i = None
                self._wfile.write(o.data)
                self._wfile.flush()

            else:
                raise TypeError(o)

            try:
                if i is not None:
                    o = gen.send(i)
                else:
                    o = next(gen)
            except StopIteration:
                break


########################################
# ../types.py


##


class ExitNow(Exception):  # noqa
    pass


ServerEpoch = ta.NewType('ServerEpoch', int)


##


@functools.total_ordering
class ConfigPriorityOrdered(abc.ABC):
    @property
    @abc.abstractmethod
    def config(self) -> ta.Any:
        raise NotImplementedError

    def __lt__(self, other):
        return self.config.priority < other.config.priority

    def __eq__(self, other):
        return self.config.priority == other.config.priority


##


class SupervisorStateManager(abc.ABC):
    @property
    @abc.abstractmethod
    def state(self) -> SupervisorState:
        raise NotImplementedError

    @abc.abstractmethod
    def set_state(self, state: SupervisorState) -> None:
        raise NotImplementedError


##


class HasDispatchers(abc.ABC):
    @abc.abstractmethod
    def get_dispatchers(self) -> 'Dispatchers':
        raise NotImplementedError


class ProcessDispatcher(FdIoHandler, abc.ABC):
    @property
    @abc.abstractmethod
    def channel(self) -> str:
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def process(self) -> 'Process':
        raise NotImplementedError


class ProcessOutputDispatcher(ProcessDispatcher, abc.ABC):
    @abc.abstractmethod
    def remove_logs(self) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def reopen_logs(self) -> None:
        raise NotImplementedError


class ProcessInputDispatcher(ProcessDispatcher, abc.ABC):
    @abc.abstractmethod
    def write(self, chars: ta.Union[bytes, str]) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def flush(self) -> None:
        raise NotImplementedError


##


class Process(
    ConfigPriorityOrdered,
    HasDispatchers,
    abc.ABC,
):
    @property
    @abc.abstractmethod
    def name(self) -> str:
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def config(self) -> ProcessConfig:
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def group(self) -> 'ProcessGroup':
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def pid(self) -> Pid:
        raise NotImplementedError

    #

    @abc.abstractmethod
    def finish(self, sts: Rc) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def stop(self) -> ta.Optional[str]:
        raise NotImplementedError

    @abc.abstractmethod
    def give_up(self) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def transition(self) -> None:
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def state(self) -> ProcessState:
        raise NotImplementedError

    @abc.abstractmethod
    def after_setuid(self) -> None:
        raise NotImplementedError


##


class ProcessGroup(
    ConfigPriorityOrdered,
    KeyedCollectionAccessors[str, Process],
    abc.ABC,
):
    @property
    @abc.abstractmethod
    def name(self) -> str:
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def config(self) -> ProcessGroupConfig:
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def by_name(self) -> ta.Mapping[str, Process]:
        raise NotImplementedError

    #

    @abc.abstractmethod
    def stop_all(self) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def get_unstopped_processes(self) -> ta.List[Process]:
        raise NotImplementedError

    @abc.abstractmethod
    def before_remove(self) -> None:
        raise NotImplementedError


########################################
# ../../../omlish/lite/fdio/corohttp.py


class CoroHttpServerConnectionFdIoHandler(SocketFdIoHandler):
    def __init__(
            self,
            addr: SocketAddress,
            sock: socket.socket,
            handler: HttpHandler,
            *,
            read_size: int = 0x10000,
            write_size: int = 0x10000,
    ) -> None:
        check_state(not sock.getblocking())

        super().__init__(addr, sock)

        self._handler = handler
        self._read_size = read_size
        self._write_size = write_size

        self._read_buf = ReadableListBuffer()
        self._write_buf: IncrementalWriteBuffer | None = None

        self._coro_srv = CoroHttpServer(
            addr,
            handler=self._handler,
        )
        self._srv_coro: ta.Optional[ta.Generator[CoroHttpServer.Io, ta.Optional[bytes], None]] = self._coro_srv.coro_handle()  # noqa

        self._cur_io: CoroHttpServer.Io | None = None
        self._next_io()

    #

    def _next_io(self) -> None:  # noqa
        coro = check_not_none(self._srv_coro)

        d: bytes | None = None
        o = self._cur_io
        while True:
            if o is None:
                try:
                    if d is not None:
                        o = coro.send(d)
                        d = None
                    else:
                        o = next(coro)
                except StopIteration:
                    self.close()
                    o = None
                    break

            if isinstance(o, CoroHttpServer.AnyLogIo):
                print(o)
                o = None

            elif isinstance(o, CoroHttpServer.ReadIo):
                if (d := self._read_buf.read(o.sz)) is None:
                    break
                o = None

            elif isinstance(o, CoroHttpServer.ReadLineIo):
                if (d := self._read_buf.read_until(b'\n')) is None:
                    break
                o = None

            elif isinstance(o, CoroHttpServer.WriteIo):
                check_none(self._write_buf)
                self._write_buf = IncrementalWriteBuffer(o.data, write_size=self._write_size)
                break

            else:
                raise TypeError(o)

        self._cur_io = o

    #

    def readable(self) -> bool:
        return True

    def writable(self) -> bool:
        return self._write_buf is not None

    #

    def on_readable(self) -> None:
        try:
            buf = check_not_none(self._sock).recv(self._read_size)
        except BlockingIOError:
            return
        except ConnectionResetError:
            self.close()
            return
        if not buf:
            self.close()
            return

        self._read_buf.feed(buf)

        if isinstance(self._cur_io, CoroHttpServer.AnyReadIo):
            self._next_io()

    def on_writable(self) -> None:
        check_isinstance(self._cur_io, CoroHttpServer.WriteIo)
        wb = check_not_none(self._write_buf)
        while wb.rem > 0:
            def send(d: bytes) -> int:
                try:
                    return check_not_none(self._sock).send(d)
                except ConnectionResetError:
                    self.close()
                    return 0
                except BlockingIOError:
                    return 0
            if not wb.write(send):
                break

        if wb.rem < 1:
            self._write_buf = None
            self._cur_io = None
            self._next_io()


########################################
# ../dispatchers.py


class Dispatchers(KeyedCollection[Fd, FdIoHandler]):
    def _key(self, v: FdIoHandler) -> Fd:
        return Fd(v.fd())

    #

    def drain(self) -> None:
        for d in self:
            # note that we *must* call readable() for every dispatcher, as it may have side effects for a given
            # dispatcher (eg. call handle_listener_state_change for event listener processes)
            if d.readable():
                d.on_readable()
            if d.writable():
                d.on_writable()

    #

    def remove_logs(self) -> None:
        for d in self:
            if isinstance(d, ProcessOutputDispatcher):
                d.remove_logs()

    def reopen_logs(self) -> None:
        for d in self:
            if isinstance(d, ProcessOutputDispatcher):
                d.reopen_logs()


########################################
# ../dispatchersimpl.py


class BaseProcessDispatcherImpl(ProcessDispatcher, abc.ABC):
    def __init__(
            self,
            process: Process,
            channel: str,
            fd: Fd,
            *,
            event_callbacks: EventCallbacks,
            server_config: ServerConfig,
    ) -> None:
        super().__init__()

        self._process = process  # process which "owns" this dispatcher
        self._channel = channel  # 'stderr' or 'stdout'
        self._fd = fd
        self._event_callbacks = event_callbacks
        self._server_config = server_config

        self._closed = False  # True if close() has been called

    #

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__} at {id(self)} for {self._process} ({self._channel})>'

    #

    @property
    def process(self) -> Process:
        return self._process

    @property
    def channel(self) -> str:
        return self._channel

    def fd(self) -> Fd:
        return self._fd

    @property
    def closed(self) -> bool:
        return self._closed

    #

    def close(self) -> None:
        if not self._closed:
            log.debug('fd %s closed, stopped monitoring %s', self._fd, self)
            self._closed = True

    def on_error(self, exc: ta.Optional[BaseException] = None) -> None:
        nil, t, v, tbinfo = compact_traceback()

        log.critical('uncaptured python exception, closing channel %s (%s:%s %s)', repr(self), t, v, tbinfo)
        self.close()


class ProcessOutputDispatcherImpl(BaseProcessDispatcherImpl, ProcessOutputDispatcher):
    """
    Dispatcher for one channel (stdout or stderr) of one process. Serves several purposes:

    - capture output sent within <!--XSUPERVISOR:BEGIN--> and <!--XSUPERVISOR:END--> tags and signal a
      ProcessCommunicationEvent by calling notify_event(event).
    - route the output to the appropriate log handlers as specified in the config.
    """

    def __init__(
            self,
            process: Process,
            event_type: ta.Type[ProcessCommunicationEvent],
            fd: Fd,
            *,
            event_callbacks: EventCallbacks,
            server_config: ServerConfig,
    ) -> None:
        super().__init__(
            process,
            event_type.channel,
            fd,
            event_callbacks=event_callbacks,
            server_config=server_config,
        )

        self._event_type = event_type

        self._lc: ProcessConfig.Log = getattr(process.config, self._channel)

        self._init_normal_log()
        self._init_capture_log()

        self._child_log = self._normal_log

        self._capture_mode = False  # are we capturing process event data
        self._output_buffer = b''  # data waiting to be logged

        # all code below is purely for minor speedups

        begin_token = self._event_type.BEGIN_TOKEN
        end_token = self._event_type.END_TOKEN
        self._begin_token_data = (begin_token, len(begin_token))
        self._end_token_data = (end_token, len(end_token))

        self._main_log_level = logging.DEBUG

        self._log_to_main_log = self._server_config.loglevel <= self._main_log_level

        self._stdout_events_enabled = self._process.config.stdout.events_enabled
        self._stderr_events_enabled = self._process.config.stderr.events_enabled

    _child_log: ta.Optional[logging.Logger] = None  # the current logger (normal_log or capture_log)
    _normal_log: ta.Optional[logging.Logger] = None  # the "normal" (non-capture) logger
    _capture_log: ta.Optional[logging.Logger] = None  # the logger used while we're in capture_mode

    def _init_normal_log(self) -> None:
        """
        Configure the "normal" (non-capture) log for this channel of this process. Sets self.normal_log if logging is
        enabled.
        """

        config = self._process.config  # noqa
        channel = self._channel  # noqa

        logfile = self._lc.file
        max_bytes = self._lc.max_bytes  # noqa
        backups = self._lc.backups  # noqa
        to_syslog = self._lc.syslog

        if logfile or to_syslog:
            self._normal_log = logging.getLogger(__name__)

        # if logfile:
        #     loggers.handle_file(
        #         self.normal_log,
        #         filename=logfile,
        #         fmt='%(message)s',
        #         rotating=bool(max_bytes),  # optimization
        #         max_bytes=max_bytes,
        #         backups=backups,
        #     )

        # if to_syslog:
        #     loggers.handle_syslog(
        #         self.normal_log,
        #         fmt=config.name + ' %(message)s',
        #     )

    def _init_capture_log(self) -> None:
        """
        Configure the capture log for this process. This log is used to temporarily capture output when special output
        is detected. Sets self.capture_log if capturing is enabled.
        """

        capture_max_bytes = self._lc.capture_max_bytes
        if capture_max_bytes:
            self._capture_log = logging.getLogger(__name__)
            # loggers.handle_boundIO(
            #     self._capture_log,
            #     fmt='%(message)s',
            #     max_bytes=capture_max_bytes,
            # )

    def remove_logs(self) -> None:
        for l in (self._normal_log, self._capture_log):
            if l is not None:
                for handler in l.handlers:
                    handler.remove()  # type: ignore
                    handler.reopen()  # type: ignore

    def reopen_logs(self) -> None:
        for l in (self._normal_log, self._capture_log):
            if l is not None:
                for handler in l.handlers:
                    handler.reopen()  # type: ignore

    def _log(self, data: ta.Union[str, bytes, None]) -> None:
        if not data:
            return

        if self._server_config.strip_ansi:
            data = strip_escapes(as_bytes(data))

        if self._child_log:
            self._child_log.info(data)

        if self._log_to_main_log:
            if not isinstance(data, bytes):
                text = data
            else:
                try:
                    text = data.decode('utf-8')
                except UnicodeDecodeError:
                    text = f'Undecodable: {data!r}'
            log.log(self._main_log_level, '%r %s output:\n%s', self._process.config.name, self._channel, text)  # noqa

        if self._channel == 'stdout':
            if self._stdout_events_enabled:
                self._event_callbacks.notify(ProcessLogStdoutEvent(self._process, self._process.pid, data))

        elif self._stderr_events_enabled:
            self._event_callbacks.notify(ProcessLogStderrEvent(self._process, self._process.pid, data))

    def record_output(self) -> None:
        if self._capture_log is None:
            # shortcut trying to find capture data
            data = self._output_buffer
            self._output_buffer = b''
            self._log(data)
            return

        if self._capture_mode:
            token, token_len = self._end_token_data
        else:
            token, token_len = self._begin_token_data

        if len(self._output_buffer) <= token_len:
            return  # not enough data

        data = self._output_buffer
        self._output_buffer = b''

        try:
            before, after = data.split(token, 1)
        except ValueError:
            after = None
            index = find_prefix_at_end(data, token)
            if index:
                self._output_buffer = self._output_buffer + data[-index:]
                data = data[:-index]
            self._log(data)
        else:
            self._log(before)
            self.toggle_capture_mode()
            self._output_buffer = after  # type: ignore

        if after:
            self.record_output()

    def toggle_capture_mode(self) -> None:
        self._capture_mode = not self._capture_mode

        if self._capture_log is not None:
            if self._capture_mode:
                self._child_log = self._capture_log
            else:
                for handler in self._capture_log.handlers:
                    handler.flush()
                data = self._capture_log.getvalue()  # type: ignore
                channel = self._channel
                procname = self._process.config.name
                event = self._event_type(self._process, self._process.pid, data)
                self._event_callbacks.notify(event)

                log.debug('%r %s emitted a comm event', procname, channel)
                for handler in self._capture_log.handlers:
                    handler.remove()  # type: ignore
                    handler.reopen()  # type: ignore
                self._child_log = self._normal_log

    def writable(self) -> bool:
        return False

    def readable(self) -> bool:
        if self._closed:
            return False
        return True

    def on_readable(self) -> None:
        data = read_fd(self._fd)
        self._output_buffer += data
        self.record_output()
        if not data:
            # if we get no data back from the pipe, it means that the child process has ended. See
            # mail.python.org/pipermail/python-dev/2004-August/046850.html
            self.close()


class ProcessInputDispatcherImpl(BaseProcessDispatcherImpl, ProcessInputDispatcher):
    def __init__(
            self,
            process: Process,
            channel: str,
            fd: Fd,
            *,
            event_callbacks: EventCallbacks,
            server_config: ServerConfig,
    ) -> None:
        super().__init__(
            process,
            channel,
            fd,
            event_callbacks=event_callbacks,
            server_config=server_config,
        )

        self._input_buffer = b''

    def write(self, chars: ta.Union[bytes, str]) -> None:
        self._input_buffer += as_bytes(chars)

    def writable(self) -> bool:
        if self._input_buffer and not self._closed:
            return True
        return False

    def flush(self) -> None:
        # other code depends on this raising EPIPE if the pipe is closed
        sent = os.write(self._fd, as_bytes(self._input_buffer))
        self._input_buffer = self._input_buffer[sent:]

    def on_writable(self) -> None:
        if self._input_buffer:
            try:
                self.flush()
            except OSError as why:
                if why.args[0] == errno.EPIPE:
                    self._input_buffer = b''
                    self.close()
                else:
                    raise


########################################
# ../groupsimpl.py


class ProcessFactory(Func2[ProcessConfig, ProcessGroup, Process]):
    pass


class ProcessGroupImpl(ProcessGroup):
    def __init__(
            self,
            config: ProcessGroupConfig,
            *,
            process_factory: ProcessFactory,
    ):
        super().__init__()

        self._config = config
        self._process_factory = process_factory

        by_name: ta.Dict[str, Process] = {}
        for pconfig in self._config.processes or []:
            p = check_isinstance(self._process_factory(pconfig, self), Process)
            if p.name in by_name:
                raise KeyError(f'name {p.name} of process {p} already registered by {by_name[p.name]}')
            by_name[pconfig.name] = p
        self._by_name = by_name

    @property
    def _by_key(self) -> ta.Mapping[str, Process]:
        return self._by_name

    #

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__} instance at {id(self)} named {self._config.name}>'

    #

    @property
    def name(self) -> str:
        return self._config.name

    @property
    def config(self) -> ProcessGroupConfig:
        return self._config

    @property
    def by_name(self) -> ta.Mapping[str, Process]:
        return self._by_name

    #

    def get_unstopped_processes(self) -> ta.List[Process]:
        return [x for x in self if not x.state.stopped]

    def stop_all(self) -> None:
        processes = list(self._by_name.values())
        processes.sort()
        processes.reverse()  # stop in desc priority order

        for proc in processes:
            state = proc.state
            if state == ProcessState.RUNNING:
                # RUNNING -> STOPPING
                proc.stop()

            elif state == ProcessState.STARTING:
                # STARTING -> STOPPING
                proc.stop()

            elif state == ProcessState.BACKOFF:
                # BACKOFF -> FATAL
                proc.give_up()

    def before_remove(self) -> None:
        pass


########################################
# ../process.py


##


class ProcessStateError(RuntimeError):
    pass


##


class PidHistory(ta.Dict[Pid, Process]):
    pass


########################################
# ../setupimpl.py


##


class SupervisorSetupImpl(SupervisorSetup):
    def __init__(
            self,
            *,
            config: ServerConfig,
            user: ta.Optional[SupervisorUser] = None,
            epoch: ServerEpoch = ServerEpoch(0),
            daemonize_listeners: DaemonizeListeners = DaemonizeListeners([]),
    ) -> None:
        super().__init__()

        self._config = config
        self._user = user
        self._epoch = epoch
        self._daemonize_listeners = daemonize_listeners

    #

    @property
    def first(self) -> bool:
        return not self._epoch

    #

    @cached_nullary
    def setup(self) -> None:
        if not self.first:
            # prevent crash on libdispatch-based systems, at least for the first request
            self._cleanup_fds()

        self._set_uid_or_exit()

        if self.first:
            self._set_rlimits_or_exit()

        # this sets the options.logger object delay logger instantiation until after setuid
        if not self._config.nocleanup:
            # clean up old automatic logs
            self._clear_auto_child_logdir()

        if not self._config.nodaemon and self.first:
            self._daemonize()

        # writing pid file needs to come *after* daemonizing or pid will be wrong
        self._write_pidfile()

    @cached_nullary
    def cleanup(self) -> None:
        self._cleanup_pidfile()

    #

    def _cleanup_fds(self) -> None:
        # try to close any leaked file descriptors (for reload)
        start = 5
        os.closerange(start, self._config.min_fds)

    #

    def _set_uid_or_exit(self) -> None:
        """
        Set the uid of the supervisord process. Called during supervisord startup only. No return value. Exits the
        process via usage() if privileges could not be dropped.
        """

        if self._user is None:
            if os.getuid() == 0:
                warnings.warn(
                    'Supervisor is running as root. Privileges were not dropped because no user is specified in the '
                    'config file. If you intend to run as root, you can set user=root in the config file to avoid '
                    'this message.',
                )
        else:
            msg = drop_privileges(self._user.uid)
            if msg is None:
                log.info('Set uid to user %s succeeded', self._user.uid)
            else:  # failed to drop privileges
                raise RuntimeError(msg)

    #

    def _set_rlimits_or_exit(self) -> None:
        """
        Set the rlimits of the supervisord process. Called during supervisord startup only. No return value. Exits the
        process via usage() if any rlimits could not be set.
        """

        limits = []

        if hasattr(resource, 'RLIMIT_NOFILE'):
            limits.append({
                'msg': (
                    'The minimum number of file descriptors required to run this process is %(min_limit)s as per the '
                    '"min_fds" command-line argument or config file setting. The current environment will only allow '
                    'you to open %(hard)s file descriptors. Either raise the number of usable file descriptors in '
                    'your environment (see README.rst) or lower the min_fds setting in the config file to allow the '
                    'process to start.'
                ),
                'min': self._config.min_fds,
                'resource': resource.RLIMIT_NOFILE,
                'name': 'RLIMIT_NOFILE',
            })

        if hasattr(resource, 'RLIMIT_NPROC'):
            limits.append({
                'msg': (
                    'The minimum number of available processes required to run this program is %(min_limit)s as per '
                    'the "minprocs" command-line argument or config file setting. The current environment will only '
                    'allow you to open %(hard)s processes. Either raise the number of usable processes in your '
                    'environment (see README.rst) or lower the minprocs setting in the config file to allow the '
                    'program to start.'
                ),
                'min': self._config.min_procs,
                'resource': resource.RLIMIT_NPROC,
                'name': 'RLIMIT_NPROC',
            })

        for limit in limits:
            min_limit = limit['min']
            res = limit['resource']
            msg = limit['msg']
            name = limit['name']

            soft, hard = resource.getrlimit(res)  # type: ignore

            # -1 means unlimited
            if soft < min_limit and soft != -1:  # type: ignore
                if hard < min_limit and hard != -1:  # type: ignore
                    # setrlimit should increase the hard limit if we are root, if not then setrlimit raises and we print
                    # usage
                    hard = min_limit  # type: ignore

                try:
                    resource.setrlimit(res, (min_limit, hard))  # type: ignore
                    log.info('Increased %s limit to %s', name, min_limit)
                except (resource.error, ValueError):
                    raise RuntimeError(msg % dict(  # type: ignore  # noqa
                        min_limit=min_limit,
                        res=res,
                        name=name,
                        soft=soft,
                        hard=hard,
                    ))

    #

    _unlink_pidfile = False

    def _write_pidfile(self) -> None:
        pid = os.getpid()
        try:
            with open(self._config.pidfile, 'w') as f:
                f.write(f'{pid}\n')
        except OSError:
            log.critical('could not write pidfile %s', self._config.pidfile)
        else:
            self._unlink_pidfile = True
            log.info('supervisord started with pid %s', pid)

    def _cleanup_pidfile(self) -> None:
        if self._unlink_pidfile:
            try_unlink(self._config.pidfile)

    #

    def _clear_auto_child_logdir(self) -> None:
        # must be called after realize()
        child_logdir = self._config.child_logdir
        if child_logdir == '/dev/null':
            return

        fnre = re.compile(rf'.+?---{self._config.identifier}-\S+\.log\.?\d{{0,4}}')
        try:
            filenames = os.listdir(child_logdir)
        except OSError:
            log.warning('Could not clear child_log dir')
            return

        for filename in filenames:
            if fnre.match(filename):
                pathname = os.path.join(child_logdir, filename)
                try:
                    os.remove(pathname)
                except OSError:
                    log.warning('Failed to clean up %r', pathname)

    #

    def _daemonize(self) -> None:
        for dl in self._daemonize_listeners:
            dl.before_daemonize()

        self._do_daemonize()

        for dl in self._daemonize_listeners:
            dl.after_daemonize()

    def _do_daemonize(self) -> None:
        # To daemonize, we need to become the leader of our own session (process) group. If we do not, signals sent to
        # our parent process will also be sent to us. This might be bad because signals such as SIGINT can be sent to
        # our parent process during normal (uninteresting) operations such as when we press Ctrl-C in the parent
        # terminal window to escape from a logtail command. To disassociate ourselves from our parent's session group we
        # use os.setsid. It means "set session id", which has the effect of disassociating a process from is current
        # session and process group and setting itself up as a new session leader.
        #
        # Unfortunately we cannot call setsid if we're already a session group leader, so we use "fork" to make a copy
        # of ourselves that is guaranteed to not be a session group leader.
        #
        # We also change directories, set stderr and stdout to null, and change our umask.
        #
        # This explanation was (gratefully) garnered from
        # http://www.cems.uwe.ac.uk/~irjohnso/coursenotes/lrc/system/daemons/d3.htm

        pid = os.fork()
        if pid != 0:
            # Parent
            log.debug('supervisord forked; parent exiting')
            real_exit(Rc(0))

        # Child
        log.info('daemonizing the supervisord process')
        if self._config.directory:
            try:
                os.chdir(self._config.directory)
            except OSError as err:
                log.critical("can't chdir into %r: %s", self._config.directory, err)
            else:
                log.info('set current directory: %r', self._config.directory)

        os.dup2(0, os.open('/dev/null', os.O_RDONLY))
        os.dup2(1, os.open('/dev/null', os.O_WRONLY))
        os.dup2(2, os.open('/dev/null', os.O_WRONLY))

        # XXX Stevens, in his Advanced Unix book, section 13.3 (page 417) recommends calling umask(0) and closing unused
        # file descriptors. In his Network Programming book, he additionally recommends ignoring SIGHUP and forking
        # again after the setsid() call, for obscure SVR4 reasons.
        os.setsid()
        os.umask(self._config.umask)


########################################
# ../groups.py


class ProcessGroupManager(
    KeyedCollectionAccessors[str, ProcessGroup],
    HasDispatchers,
):
    def __init__(
            self,
            *,
            event_callbacks: EventCallbacks,
    ) -> None:
        super().__init__()

        self._event_callbacks = event_callbacks

        self._by_name: ta.Dict[str, ProcessGroup] = {}

    @property
    def _by_key(self) -> ta.Mapping[str, ProcessGroup]:
        return self._by_name

    #

    def all_processes(self) -> ta.Iterator[Process]:
        for g in self:
            yield from g

    #

    def get_dispatchers(self) -> Dispatchers:
        return Dispatchers(
            d
            for g in self
            for p in g
            for d in p.get_dispatchers()
        )

    #

    def add(self, group: ProcessGroup) -> None:
        if (name := group.name) in self._by_name:
            raise KeyError(f'Process group already exists: {name}')

        self._by_name[name] = group

        self._event_callbacks.notify(ProcessGroupAddedEvent(name))

    def remove(self, name: str) -> None:
        group = self._by_name[name]

        group.before_remove()

        del self._by_name[name]

        self._event_callbacks.notify(ProcessGroupRemovedEvent(name))

    def clear(self) -> None:
        # FIXME: events?
        self._by_name.clear()

    #

    class Diff(ta.NamedTuple):
        added: ta.List[ProcessGroupConfig]
        changed: ta.List[ProcessGroupConfig]
        removed: ta.List[ProcessGroupConfig]

    def diff(self, new: ta.Sequence[ProcessGroupConfig]) -> Diff:
        cur = [group.config for group in self]

        cur_by_name = {cfg.name: cfg for cfg in cur}
        new_by_name = {cfg.name: cfg for cfg in new}

        added = [cand for cand in new if cand.name not in cur_by_name]
        removed = [cand for cand in cur if cand.name not in new_by_name]
        changed = [cand for cand in new if cand != cur_by_name.get(cand.name, cand)]

        return ProcessGroupManager.Diff(
            added,
            changed,
            removed,
        )


########################################
# ../io.py


##


HasDispatchersList = ta.NewType('HasDispatchersList', ta.Sequence[HasDispatchers])


class IoManager(HasDispatchers):
    def __init__(
            self,
            *,
            poller: FdIoPoller,
            has_dispatchers_list: HasDispatchersList,
    ) -> None:
        super().__init__()

        self._poller = poller
        self._has_dispatchers_list = has_dispatchers_list

    def get_dispatchers(self) -> Dispatchers:
        return Dispatchers(
            d
            for hd in self._has_dispatchers_list
            for d in hd.get_dispatchers()
        )

    def poll(self) -> None:
        dispatchers = self.get_dispatchers()

        self._poller.update(
            {fd for fd, d in dispatchers.items() if d.readable()},
            {fd for fd, d in dispatchers.items() if d.writable()},
        )

        timeout = 1  # this cannot be fewer than the smallest TickEvent (5)
        log.info(f'Polling: {timeout=}')  # noqa
        polled = self._poller.poll(timeout)
        log.info(f'Polled: {polled=}')  # noqa
        if polled.msg is not None:
            log.error(polled.msg)
        if polled.exc is not None:
            log.error('Poll exception: %r', polled.exc)

        for r in polled.r:
            fd = Fd(r)
            if fd in dispatchers:
                dispatcher = dispatchers[fd]
                try:
                    log.debug('read event caused by %r', dispatcher)
                    dispatcher.on_readable()
                    if not dispatcher.readable():
                        self._poller.unregister_readable(fd)
                except ExitNow:
                    raise
                except Exception as exc:  # noqa
                    log.exception('Error in dispatcher: %r', dispatcher)
                    dispatcher.on_error(exc)
            else:
                # if the fd is not in combined map, we should unregister it. otherwise, it will be polled every
                # time, which may cause 100% cpu usage
                log.debug('unexpected read event from fd %r', fd)
                try:
                    self._poller.unregister_readable(fd)
                except Exception:  # noqa
                    pass

        for w in polled.w:
            fd = Fd(w)
            if fd in dispatchers:
                dispatcher = dispatchers[fd]
                try:
                    log.debug('write event caused by %r', dispatcher)
                    dispatcher.on_writable()
                    if not dispatcher.writable():
                        self._poller.unregister_writable(fd)
                except ExitNow:
                    raise
                except Exception as exc:  # noqa
                    log.exception('Error in dispatcher: %r', dispatcher)
                    dispatcher.on_error(exc)
            else:
                log.debug('unexpected write event from fd %r', fd)
                try:
                    self._poller.unregister_writable(fd)
                except Exception:  # noqa
                    pass


########################################
# ../spawning.py


@dc.dataclass(frozen=True)
class SpawnedProcess:
    pid: Pid
    pipes: ProcessPipes
    dispatchers: Dispatchers


class ProcessSpawnError(RuntimeError):
    pass


class ProcessSpawning:
    @property
    @abc.abstractmethod
    def process(self) -> Process:
        raise NotImplementedError

    #

    @abc.abstractmethod
    def spawn(self) -> SpawnedProcess:  # Raises[ProcessSpawnError]
        raise NotImplementedError


########################################
# ../http.py


##


class SocketServerFdIoHandler(SocketFdIoHandler):
    def __init__(
            self,
            addr: SocketAddress,
            on_connect: ta.Callable[[socket.socket, SocketAddress], None],
    ) -> None:
        sock = socket.create_server(addr)
        sock.setblocking(False)

        super().__init__(addr, sock)

        self._on_connect = on_connect

        sock.listen(1)

    def readable(self) -> bool:
        return True

    def on_readable(self) -> None:
        cli_sock, cli_addr = check_not_none(self._sock).accept()
        cli_sock.setblocking(False)

        self._on_connect(cli_sock, cli_addr)


##


class HttpServer(HasDispatchers):
    class Address(ta.NamedTuple):
        a: SocketAddress

    class Handler(ta.NamedTuple):
        h: HttpHandler

    def __init__(
            self,
            handler: Handler,
            addr: Address = Address(('localhost', 8000)),
    ) -> None:
        super().__init__()

        self._handler = handler.h
        self._addr = addr.a

        self._server = SocketServerFdIoHandler(self._addr, self._on_connect)

        self._conns: ta.List[CoroHttpServerConnectionFdIoHandler] = []

    def get_dispatchers(self) -> Dispatchers:
        l = []
        for c in self._conns:
            if not c.closed:
                l.append(c)
        self._conns = l
        return Dispatchers([
            self._server,
            *l,
        ])

    def _on_connect(self, sock: socket.socket, addr: SocketAddress) -> None:
        conn = CoroHttpServerConnectionFdIoHandler(
            addr,
            sock,
            self._handler,
        )

        self._conns.append(conn)


##


class SupervisorHttpHandler:
    def __init__(
            self,
            *,
            groups: ProcessGroupManager,
    ) -> None:
        super().__init__()

        self._groups = groups

    def handle(self, req: HttpHandlerRequest) -> HttpHandlerResponse:
        dct = {
            'method': req.method,
            'path': req.path,
            'data': len(req.data or b''),
            'groups': {
                g.name: {
                    'processes': {
                        p.name: {
                            'pid': p.pid,
                        }
                        for p in g
                    },
                }
                for g in self._groups
            },
        }

        return HttpHandlerResponse(
            200,
            data=json.dumps(dct, **JSON_PRETTY_KWARGS).encode('utf-8') + b'\n',
            headers={
                'Content-Type': 'application/json',
            },
        )


########################################
# ../processimpl.py


class ProcessSpawningFactory(Func1[Process, ProcessSpawning]):
    pass


##


class ProcessImpl(Process):
    """A class to manage a subprocess."""

    def __init__(
            self,
            config: ProcessConfig,
            group: ProcessGroup,
            *,
            supervisor_states: SupervisorStateManager,
            event_callbacks: EventCallbacks,
            process_spawning_factory: ProcessSpawningFactory,
    ) -> None:
        super().__init__()

        self._config = config
        self._group = group

        self._supervisor_states = supervisor_states
        self._event_callbacks = event_callbacks

        self._spawning = process_spawning_factory(self)

        #

        self._dispatchers = Dispatchers([])
        self._pipes = ProcessPipes()

        self._state = ProcessState.STOPPED
        self._pid = Pid(0)  # 0 when not running

        self._last_start = 0.  # Last time the subprocess was started; 0 if never
        self._last_stop = 0.  # Last time the subprocess was stopped; 0 if never
        self._last_stop_report = 0.  # Last time "waiting for x to stop" logged, to throttle
        self._delay = 0.  # If nonzero, delay starting or killing until this time

        self._administrative_stop = False  # true if process has been stopped by an admin
        self._system_stop = False  # true if process has been stopped by the system

        self._killing = False  # true if we are trying to kill this process

        self._backoff = 0  # backoff counter (to start_retries)

        self._exitstatus: ta.Optional[Rc] = None  # status attached to dead process by finish()
        self._spawn_err: ta.Optional[str] = None  # error message attached by spawn() if any

    #

    def __repr__(self) -> str:
        return f'<Subprocess at {id(self)} with name {self._config.name} in state {self._state.name}>'

    #

    @property
    def name(self) -> str:
        return self._config.name

    @property
    def config(self) -> ProcessConfig:
        return self._config

    @property
    def group(self) -> ProcessGroup:
        return self._group

    @property
    def pid(self) -> Pid:
        return self._pid

    #

    @property
    def state(self) -> ProcessState:
        return self._state

    @property
    def backoff(self) -> int:
        return self._backoff

    #

    def spawn(self) -> ta.Optional[Pid]:
        if self.pid:
            log.warning('process \'%s\' already running', self.name)
            return None

        self.check_in_state(
            ProcessState.EXITED,
            ProcessState.FATAL,
            ProcessState.BACKOFF,
            ProcessState.STOPPED,
        )

        self._killing = False
        self._spawn_err = None
        self._exitstatus = None
        self._system_stop = False
        self._administrative_stop = False

        self._last_start = time.time()

        self.change_state(ProcessState.STARTING)

        try:
            sp = self._spawning.spawn()
        except ProcessSpawnError as err:
            log.exception('Spawn error')
            self._spawn_err = err.args[0]
            self.check_in_state(ProcessState.STARTING)
            self.change_state(ProcessState.BACKOFF)
            return None

        log.info("Spawned: '%s' with pid %s", self.name, sp.pid)

        self._pid = sp.pid
        self._pipes = sp.pipes
        self._dispatchers = sp.dispatchers

        self._delay = time.time() + self.config.start_secs

        return sp.pid

    def get_dispatchers(self) -> Dispatchers:
        return self._dispatchers

    def write(self, chars: ta.Union[bytes, str]) -> None:
        if not self.pid or self._killing:
            raise OSError(errno.EPIPE, 'Process already closed')

        stdin_fd = self._pipes.stdin
        if stdin_fd is None:
            raise OSError(errno.EPIPE, 'Process has no stdin channel')

        dispatcher = check_isinstance(self._dispatchers[stdin_fd], ProcessInputDispatcher)
        if dispatcher.closed:
            raise OSError(errno.EPIPE, "Process' stdin channel is closed")

        dispatcher.write(chars)
        dispatcher.flush()  # this must raise EPIPE if the pipe is closed

    #

    def change_state(self, new_state: ProcessState, expected: bool = True) -> bool:
        old_state = self._state
        if new_state is old_state:
            return False

        self._state = new_state
        if new_state == ProcessState.BACKOFF:
            now = time.time()
            self._backoff += 1
            self._delay = now + self._backoff

        event_class = PROCESS_STATE_EVENT_MAP.get(new_state)
        if event_class is not None:
            event = event_class(self, old_state, expected)
            self._event_callbacks.notify(event)

        return True

    def check_in_state(self, *states: ProcessState) -> None:
        if self._state not in states:
            raise ProcessStateError(
                f'Check failed for {self._config.name}: '
                f'{self._state.name} not in {" ".join(s.name for s in states)}',
            )

    #

    def _check_and_adjust_for_system_clock_rollback(self, test_time):
        """
        Check if system clock has rolled backward beyond test_time. If so, set affected timestamps to test_time.
        """

        if self._state == ProcessState.STARTING:
            self._last_start = min(test_time, self._last_start)
            if self._delay > 0 and test_time < (self._delay - self._config.start_secs):
                self._delay = test_time + self._config.start_secs

        elif self._state == ProcessState.RUNNING:
            if test_time > self._last_start and test_time < (self._last_start + self._config.start_secs):
                self._last_start = test_time - self._config.start_secs

        elif self._state == ProcessState.STOPPING:
            self._last_stop_report = min(test_time, self._last_stop_report)
            if self._delay > 0 and test_time < (self._delay - self._config.stop_wait_secs):
                self._delay = test_time + self._config.stop_wait_secs

        elif self._state == ProcessState.BACKOFF:
            if self._delay > 0 and test_time < (self._delay - self._backoff):
                self._delay = test_time + self._backoff

    def stop(self) -> ta.Optional[str]:
        self._administrative_stop = True
        self._last_stop_report = 0
        return self.kill(self._config.stop_signal)

    def stop_report(self) -> None:
        """Log a 'waiting for x to stop' message with throttling."""

        if self._state == ProcessState.STOPPING:
            now = time.time()

            self._check_and_adjust_for_system_clock_rollback(now)

            if now > (self._last_stop_report + 2):  # every 2 seconds
                log.info('waiting for %s to stop', self.name)
                self._last_stop_report = now

    def give_up(self) -> None:
        self._delay = 0
        self._backoff = 0
        self._system_stop = True
        self.check_in_state(ProcessState.BACKOFF)
        self.change_state(ProcessState.FATAL)

    def kill(self, sig: int) -> ta.Optional[str]:
        """
        Send a signal to the subprocess with the intention to kill it (to make it exit). This may or may not actually
        kill it.

        Return None if the signal was sent, or an error message string if an error occurred or if the subprocess is not
        running.
        """
        now = time.time()

        # If the process is in BACKOFF and we want to stop or kill it, then BACKOFF -> STOPPED. This is needed because
        # if start_retries is a large number and the process isn't starting successfully, the stop request would be
        # blocked for a long time waiting for the retries.
        if self._state == ProcessState.BACKOFF:
            log.debug('Attempted to kill %s, which is in BACKOFF state.', self.name)
            self.change_state(ProcessState.STOPPED)
            return None

        args: tuple
        if not self.pid:
            fmt, args = "attempted to kill %s with sig %s but it wasn't running", (self.name, sig_name(sig))
            log.debug(fmt, *args)
            return fmt % args

        # If we're in the stopping state, then we've already sent the stop signal and this is the kill signal
        if self._state == ProcessState.STOPPING:
            kill_as_group = self._config.kill_as_group
        else:
            kill_as_group = self._config.stop_as_group

        as_group = ''
        if kill_as_group:
            as_group = 'process group '

        log.debug('killing %s (pid %s) %s with signal %s', self.name, self.pid, as_group, sig_name(sig))

        # RUNNING/STARTING/STOPPING -> STOPPING
        self._killing = True
        self._delay = now + self._config.stop_wait_secs
        # we will already be in the STOPPING state if we're doing a SIGKILL as a result of overrunning stop_wait_secs
        self.check_in_state(ProcessState.RUNNING, ProcessState.STARTING, ProcessState.STOPPING)
        self.change_state(ProcessState.STOPPING)

        kpid = int(self.pid)
        if kill_as_group:
            # send to the whole process group instead
            kpid = -kpid

        try:
            try:
                os.kill(kpid, sig)
            except OSError as exc:
                if exc.errno == errno.ESRCH:
                    log.debug('unable to signal %s (pid %s), it probably just exited on its own: %s', self.name, self.pid, str(exc))  # noqa
                    # we could change the state here but we intentionally do not. we will do it during normal SIGCHLD
                    # processing.
                    return None
                raise
        except Exception:  # noqa
            tb = traceback.format_exc()
            fmt, args = 'unknown problem killing %s (%s):%s', (self.name, self.pid, tb)
            log.critical(fmt, *args)
            self.change_state(ProcessState.UNKNOWN)
            self._killing = False
            self._delay = 0
            return fmt % args

        return None

    def signal(self, sig: int) -> ta.Optional[str]:
        """
        Send a signal to the subprocess, without intending to kill it.

        Return None if the signal was sent, or an error message string if an error occurred or if the subprocess is not
        running.
        """
        args: tuple
        if not self.pid:
            fmt, args = "Attempted to send %s sig %s but it wasn't running", (self.name, sig_name(sig))
            log.debug(fmt, *args)
            return fmt % args

        log.debug('sending %s (pid %s) sig %s', self.name, self.pid, sig_name(sig))

        self.check_in_state(ProcessState.RUNNING, ProcessState.STARTING, ProcessState.STOPPING)

        try:
            try:
                os.kill(self.pid, sig)
            except OSError as exc:
                if exc.errno == errno.ESRCH:
                    log.debug(
                        'unable to signal %s (pid %s), it probably just now exited on its own: %s',
                        self.name,
                        self.pid,
                        str(exc),
                    )
                    # we could change the state here but we intentionally do not. we will do it during normal SIGCHLD
                    # processing.
                    return None
                raise
        except Exception:  # noqa
            tb = traceback.format_exc()
            fmt, args = 'unknown problem sending sig %s (%s):%s', (self.name, self.pid, tb)
            log.critical(fmt, *args)
            self.change_state(ProcessState.UNKNOWN)
            return fmt % args

        return None

    def finish(self, sts: Rc) -> None:
        """The process was reaped and we need to report and manage its state."""

        self._dispatchers.drain()

        es, msg = decode_wait_status(sts)

        now = time.time()

        self._check_and_adjust_for_system_clock_rollback(now)

        self._last_stop = now

        if now > self._last_start:
            log.info(f'{now - self._last_start=}')  # noqa
            too_quickly = now - self._last_start < self._config.start_secs
        else:
            too_quickly = False
            log.warning(
                "process '%s' (%s) last_start time is in the future, don't know how long process was running so "
                "assuming it did not exit too quickly",
                self.name,
                self.pid,
            )

        exit_expected = es in self._config.exitcodes

        if self._killing:
            # likely the result of a stop request implies STOPPING -> STOPPED
            self._killing = False
            self._delay = 0
            self._exitstatus = Rc(es)

            fmt, args = 'stopped: %s (%s)', (self.name, msg)
            self.check_in_state(ProcessState.STOPPING)
            self.change_state(ProcessState.STOPPED)
            if exit_expected:
                log.info(fmt, *args)
            else:
                log.warning(fmt, *args)

        elif too_quickly:
            # the program did not stay up long enough to make it to RUNNING implies STARTING -> BACKOFF
            self._exitstatus = None
            self._spawn_err = 'Exited too quickly (process log may have details)'
            self.check_in_state(ProcessState.STARTING)
            self.change_state(ProcessState.BACKOFF)
            log.warning('exited: %s (%s)', self.name, msg + '; not expected')

        else:
            # this finish was not the result of a stop request, the program was in the RUNNING state but exited implies
            # RUNNING -> EXITED normally but see next comment
            self._delay = 0
            self._backoff = 0
            self._exitstatus = es

            # if the process was STARTING but a system time change causes self.last_start to be in the future, the
            # normal STARTING->RUNNING transition can be subverted so we perform the transition here.
            if self._state == ProcessState.STARTING:
                self.change_state(ProcessState.RUNNING)

            self.check_in_state(ProcessState.RUNNING)

            if exit_expected:
                # expected exit code
                self.change_state(ProcessState.EXITED, expected=True)
                log.info('exited: %s (%s)', self.name, msg + '; expected')
            else:
                # unexpected exit code
                self._spawn_err = f'Bad exit code {es}'
                self.change_state(ProcessState.EXITED, expected=False)
                log.warning('exited: %s (%s)', self.name, msg + '; not expected')

        self._pid = Pid(0)
        close_parent_pipes(self._pipes)
        self._pipes = ProcessPipes()
        self._dispatchers = Dispatchers([])

    def transition(self) -> None:
        now = time.time()
        state = self._state

        self._check_and_adjust_for_system_clock_rollback(now)

        if self._supervisor_states.state > SupervisorState.RESTARTING:
            # dont start any processes if supervisor is shutting down
            if state == ProcessState.EXITED:
                if self._config.auto_restart:
                    if self._config.auto_restart is RestartUnconditionally:
                        # EXITED -> STARTING
                        self.spawn()
                    elif self._exitstatus not in self._config.exitcodes:
                        # EXITED -> STARTING
                        self.spawn()

            elif state == ProcessState.STOPPED and not self._last_start:
                if self._config.auto_start:
                    # STOPPED -> STARTING
                    self.spawn()

            elif state == ProcessState.BACKOFF:
                if self._backoff <= self._config.start_retries:
                    if now > self._delay:
                        # BACKOFF -> STARTING
                        self.spawn()

        if state == ProcessState.STARTING:
            if now - self._last_start > self._config.start_secs:
                # STARTING -> RUNNING if the proc has started successfully and it has stayed up for at least
                # proc.config.start_secs,
                self._delay = 0
                self._backoff = 0
                self.check_in_state(ProcessState.STARTING)
                self.change_state(ProcessState.RUNNING)
                msg = ('entered RUNNING state, process has stayed up for > than %s seconds (start_secs)' % self._config.start_secs)  # noqa
                log.info('success: %s %s', self.name, msg)

        if state == ProcessState.BACKOFF:
            if self._backoff > self._config.start_retries:
                # BACKOFF -> FATAL if the proc has exceeded its number of retries
                self.give_up()
                msg = ('entered FATAL state, too many start retries too quickly')
                log.info('gave up: %s %s', self.name, msg)

        elif state == ProcessState.STOPPING:
            time_left = self._delay - now
            if time_left <= 0:
                # kill processes which are taking too long to stop with a final sigkill. if this doesn't kill it, the
                # process will be stuck in the STOPPING state forever.
                log.warning('killing \'%s\' (%s) with SIGKILL', self.name, self.pid)
                self.kill(signal.SIGKILL)

    def after_setuid(self) -> None:
        # temporary logfiles which are erased at start time
        # get_autoname = self.context.get_auto_child_log_name  # noqa
        # sid = self.context.config.identifier  # noqa
        # name = self._config.name  # noqa
        # if self.stdout_logfile is Automatic:
        #     self.stdout_logfile = get_autoname(name, sid, 'stdout')
        # if self.stderr_logfile is Automatic:
        #     self.stderr_logfile = get_autoname(name, sid, 'stderr')
        pass


########################################
# ../signals.py


class SignalHandler:
    def __init__(
            self,
            *,
            states: SupervisorStateManager,
            signal_receiver: SignalReceiver,
            process_groups: ProcessGroupManager,
    ) -> None:
        super().__init__()

        self._states = states
        self._signal_receiver = signal_receiver
        self._process_groups = process_groups

    def set_signals(self) -> None:
        self._signal_receiver.install(
            signal.SIGTERM,
            signal.SIGINT,
            signal.SIGQUIT,
            signal.SIGHUP,
            signal.SIGCHLD,
            signal.SIGUSR2,
        )

    def handle_signals(self) -> None:
        sig = self._signal_receiver.get_signal()
        if not sig:
            return

        if sig in (signal.SIGTERM, signal.SIGINT, signal.SIGQUIT):
            log.warning('received %s indicating exit request', sig_name(sig))
            self._states.set_state(SupervisorState.SHUTDOWN)

        elif sig == signal.SIGHUP:
            if self._states.state == SupervisorState.SHUTDOWN:
                log.warning('ignored %s indicating restart request (shutdown in progress)', sig_name(sig))  # noqa
            else:
                log.warning('received %s indicating restart request', sig_name(sig))  # noqa
                self._states.set_state(SupervisorState.RESTARTING)

        elif sig == signal.SIGCHLD:
            log.debug('received %s indicating a child quit', sig_name(sig))

        elif sig == signal.SIGUSR2:
            log.info('received %s indicating log reopen request', sig_name(sig))

            for p in self._process_groups.all_processes():
                for d in p.get_dispatchers():
                    if isinstance(d, ProcessOutputDispatcher):
                        d.reopen_logs()

        else:
            log.debug('received %s indicating nothing', sig_name(sig))


########################################
# ../spawningimpl.py


class ProcessOutputDispatcherFactory(Func3[Process, ta.Type[ProcessCommunicationEvent], Fd, ProcessOutputDispatcher]):
    pass


class ProcessInputDispatcherFactory(Func3[Process, str, Fd, ProcessInputDispatcher]):
    pass


InheritedFds = ta.NewType('InheritedFds', ta.FrozenSet[Fd])


##


class ProcessSpawningImpl(ProcessSpawning):
    def __init__(
            self,
            process: Process,
            *,
            server_config: ServerConfig,
            pid_history: PidHistory,

            output_dispatcher_factory: ProcessOutputDispatcherFactory,
            input_dispatcher_factory: ProcessInputDispatcherFactory,

            inherited_fds: ta.Optional[InheritedFds] = None,
    ) -> None:
        super().__init__()

        self._process = process

        self._server_config = server_config
        self._pid_history = pid_history

        self._output_dispatcher_factory = output_dispatcher_factory
        self._input_dispatcher_factory = input_dispatcher_factory

        self._inherited_fds = InheritedFds(frozenset(inherited_fds or []))

    #

    @property
    def process(self) -> Process:
        return self._process

    @property
    def config(self) -> ProcessConfig:
        return self._process.config

    @property
    def group(self) -> ProcessGroup:
        return self._process.group

    #

    def spawn(self) -> SpawnedProcess:  # Raises[ProcessSpawnError]
        try:
            exe, argv = self._get_execv_args()
        except ProcessError as exc:
            raise ProcessSpawnError(exc.args[0]) from exc

        try:
            pipes = make_process_pipes(not self.config.redirect_stderr)
        except OSError as exc:
            code = exc.args[0]
            if code == errno.EMFILE:
                # too many file descriptors open
                msg = f"Too many open files to spawn '{self.process.name}'"
            else:
                msg = f"Unknown error making pipes for '{self.process.name}': {errno.errorcode.get(code, code)}"
            raise ProcessSpawnError(msg) from exc

        try:
            dispatchers = self._make_dispatchers(pipes)
        except Exception as exc:  # noqa
            close_pipes(pipes)
            raise ProcessSpawnError(f"Unknown error making dispatchers for '{self.process.name}': {exc}") from exc

        try:
            pid = Pid(os.fork())
        except OSError as exc:
            code = exc.args[0]
            if code == errno.EAGAIN:
                # process table full
                msg = f"Too many processes in process table to spawn '{self.process.name}'"
            else:
                msg = f"Unknown error during fork for '{self.process.name}': {errno.errorcode.get(code, code)}"
            err = ProcessSpawnError(msg)
            close_pipes(pipes)
            raise err from exc

        if pid != 0:
            sp = SpawnedProcess(
                pid,
                pipes,
                dispatchers,
            )
            self._spawn_as_parent(sp)
            return sp

        else:
            self._spawn_as_child(
                exe,
                argv,
                pipes,
            )
            raise RuntimeError('Unreachable')  # noqa

    def _get_execv_args(self) -> ta.Tuple[str, ta.Sequence[str]]:
        """
        Internal: turn a program name into a file name, using $PATH, make sure it exists / is executable, raising a
        ProcessError if not
        """

        try:
            args = shlex.split(self.config.command)
        except ValueError as e:
            raise BadCommandError(f"Can't parse command {self.config.command!r}: {e}")  # noqa

        if args:
            program = args[0]
        else:
            raise BadCommandError('Command is empty')

        if '/' in program:
            exe = program
            try:
                st = os.stat(exe)
            except OSError:
                st = None

        else:
            path = get_path()
            found = None
            st = None
            for dir in path:  # noqa
                found = os.path.join(dir, program)
                try:
                    st = os.stat(found)
                except OSError:
                    pass
                else:
                    break

            if st is None:
                exe = program
            else:
                exe = found  # type: ignore

        # check_execv_args will raise a ProcessError if the execv args are bogus, we break it out into a separate
        # options method call here only to service unit tests
        check_execv_args(exe, args, st)

        return exe, args

    def _make_dispatchers(self, pipes: ProcessPipes) -> Dispatchers:
        dispatchers: ta.List[FdIoHandler] = []

        if pipes.stdout is not None:
            dispatchers.append(check_isinstance(self._output_dispatcher_factory(
                self.process,
                ProcessCommunicationStdoutEvent,
                pipes.stdout,
            ), ProcessOutputDispatcher))

        if pipes.stderr is not None:
            dispatchers.append(check_isinstance(self._output_dispatcher_factory(
                self.process,
                ProcessCommunicationStderrEvent,
                pipes.stderr,
            ), ProcessOutputDispatcher))

        if pipes.stdin is not None:
            dispatchers.append(check_isinstance(self._input_dispatcher_factory(
                self.process,
                'stdin',
                pipes.stdin,
            ), ProcessInputDispatcher))

        return Dispatchers(dispatchers)

    #

    def _spawn_as_parent(self, sp: SpawnedProcess) -> None:
        close_child_pipes(sp.pipes)

        self._pid_history[sp.pid] = self.process

    #

    def _spawn_as_child(
            self,
            exe: str,
            argv: ta.Sequence[str],
            pipes: ProcessPipes,
    ) -> ta.NoReturn:
        try:
            # Prevent child from receiving signals sent to the parent by calling os.setpgrp to create a new process
            # group for the child. This prevents, for instance, the case of child processes being sent a SIGINT when
            # running supervisor in foreground mode and Ctrl-C in the terminal window running supervisord is pressed.
            # Presumably it also prevents HUP, etc. received by supervisord from being sent to children.
            os.setpgrp()

            #

            # After preparation sending to fd 2 will put this output in the stderr log.
            self._prepare_child_fds(pipes)

            #

            setuid_msg = self._set_uid()
            if setuid_msg:
                uid = self.config.uid
                msg = f"Couldn't setuid to {uid}: {setuid_msg}\n"
                os.write(2, as_bytes('supervisor: ' + msg))
                raise RuntimeError(msg)

            #

            env = os.environ.copy()
            env['SUPERVISOR_ENABLED'] = '1'
            env['SUPERVISOR_PROCESS_NAME'] = self.process.name
            if self.group:
                env['SUPERVISOR_GROUP_NAME'] = self.group.name
            if self.config.environment is not None:
                env.update(self.config.environment)

            #

            cwd = self.config.directory
            try:
                if cwd is not None:
                    os.chdir(os.path.expanduser(cwd))
            except OSError as exc:
                code = errno.errorcode.get(exc.args[0], exc.args[0])
                msg = f"Couldn't chdir to {cwd}: {code}\n"
                os.write(2, as_bytes('supervisor: ' + msg))
                raise RuntimeError(msg) from exc

            #

            try:
                if self.config.umask is not None:
                    os.umask(self.config.umask)
                os.execve(exe, list(argv), env)

            except OSError as exc:
                code = errno.errorcode.get(exc.args[0], exc.args[0])
                msg = f"Couldn't exec {argv[0]}: {code}\n"
                os.write(2, as_bytes('supervisor: ' + msg))

            except Exception:  # noqa
                (file, fun, line), t, v, tb = compact_traceback()
                msg = f"Couldn't exec {exe}: {t}, {v}: file: {file} line: {line}\n"
                os.write(2, as_bytes('supervisor: ' + msg))

        finally:
            os.write(2, as_bytes('supervisor: child process was not spawned\n'))
            real_exit(Rc(127))  # exit process with code for spawn failure

        raise RuntimeError('Unreachable')

    def _prepare_child_fds(self, pipes: ProcessPipes) -> None:
        os.dup2(check_not_none(pipes.child_stdin), 0)

        os.dup2(check_not_none(pipes.child_stdout), 1)

        if self.config.redirect_stderr:
            os.dup2(check_not_none(pipes.child_stdout), 2)
        else:
            os.dup2(check_not_none(pipes.child_stderr), 2)

        for i in range(3, self._server_config.min_fds):
            if i in self._inherited_fds:
                continue
            close_fd(Fd(i))

    def _set_uid(self) -> ta.Optional[str]:
        if self.config.uid is None:
            return None

        msg = drop_privileges(self.config.uid)
        return msg


##


def check_execv_args(
        exe: str,
        argv: ta.Sequence[str],
        st: ta.Optional[os.stat_result],
) -> None:
    if st is None:
        raise NotFoundError(f"Can't find command {exe!r}")

    elif stat.S_ISDIR(st[stat.ST_MODE]):
        raise NotExecutableError(f'Command at {exe!r} is a directory')

    elif not (stat.S_IMODE(st[stat.ST_MODE]) & 0o111):
        raise NotExecutableError(f'Command at {exe!r} is not executable')

    elif not os.access(exe, os.X_OK):
        raise NoPermissionError(f'No permission to run command {exe!r}')


########################################
# ../supervisor.py


##


def timeslice(period: int, when: float) -> int:
    return int(when - (when % period))


##


class SupervisorStateManagerImpl(SupervisorStateManager):
    def __init__(self) -> None:
        super().__init__()

        self._state: SupervisorState = SupervisorState.RUNNING

    @property
    def state(self) -> SupervisorState:
        return self._state

    def set_state(self, state: SupervisorState) -> None:
        self._state = state


##


class ProcessGroupFactory(Func1[ProcessGroupConfig, ProcessGroup]):
    pass


class Supervisor:
    def __init__(
            self,
            *,
            config: ServerConfig,
            poller: FdIoPoller,
            process_groups: ProcessGroupManager,
            signal_handler: SignalHandler,
            event_callbacks: EventCallbacks,
            process_group_factory: ProcessGroupFactory,
            pid_history: PidHistory,
            setup: SupervisorSetup,
            states: SupervisorStateManager,
            io: IoManager,
    ) -> None:
        super().__init__()

        self._config = config
        self._poller = poller
        self._process_groups = process_groups
        self._signal_handler = signal_handler
        self._event_callbacks = event_callbacks
        self._process_group_factory = process_group_factory
        self._pid_history = pid_history
        self._setup = setup
        self._states = states
        self._io = io

        self._ticks: ta.Dict[int, float] = {}
        self._stop_groups: ta.Optional[ta.List[ProcessGroup]] = None  # list used for priority ordered shutdown
        self._stopping = False  # set after we detect that we are handling a stop request
        self._last_shutdown_report = 0.  # throttle for delayed process error reports at stop

    #

    @property
    def state(self) -> SupervisorState:
        return self._states.state

    #

    def add_process_group(self, config: ProcessGroupConfig) -> bool:
        if self._process_groups.get(config.name) is not None:
            return False

        group = check_isinstance(self._process_group_factory(config), ProcessGroup)
        for process in group:
            process.after_setuid()

        self._process_groups.add(group)

        return True

    def remove_process_group(self, name: str) -> bool:
        if self._process_groups[name].get_unstopped_processes():
            return False

        self._process_groups.remove(name)

        return True

    #

    def shutdown_report(self) -> ta.List[Process]:
        unstopped: ta.List[Process] = []

        for group in self._process_groups:
            unstopped.extend(group.get_unstopped_processes())

        if unstopped:
            # throttle 'waiting for x to die' reports
            now = time.time()
            if now > (self._last_shutdown_report + 3):  # every 3 secs
                names = [p.config.name for p in unstopped]
                namestr = ', '.join(names)
                log.info('waiting for %s to die', namestr)
                self._last_shutdown_report = now
                for proc in unstopped:
                    log.debug('%s state: %s', proc.config.name, proc.state.name)

        return unstopped

    #

    def main(self, **kwargs: ta.Any) -> None:
        self._setup.setup()
        try:
            self.run(**kwargs)
        finally:
            self._setup.cleanup()

    def run(
            self,
            *,
            callback: ta.Optional[ta.Callable[['Supervisor'], bool]] = None,
    ) -> None:
        self._process_groups.clear()
        self._stop_groups = None  # clear

        self._event_callbacks.clear()

        try:
            for config in self._config.groups or []:
                self.add_process_group(config)

            self._signal_handler.set_signals()

            self._event_callbacks.notify(SupervisorRunningEvent())

            while True:
                if callback is not None and not callback(self):
                    break

                self._run_once()

        finally:
            self._poller.close()

    #

    def _run_once(self) -> None:
        now = time.time()
        self._poll()
        log.info(f'Poll took {time.time() - now}')  # noqa
        self._reap()
        self._signal_handler.handle_signals()
        self._tick()

        if self._states.state < SupervisorState.RUNNING:
            self._ordered_stop_groups_phase_2()

    def _ordered_stop_groups_phase_1(self) -> None:
        if self._stop_groups:
            # stop the last group (the one with the "highest" priority)
            self._stop_groups[-1].stop_all()

    def _ordered_stop_groups_phase_2(self) -> None:
        # after phase 1 we've transitioned and reaped, let's see if we can remove the group we stopped from the
        # stop_groups queue.
        if self._stop_groups:
            # pop the last group (the one with the "highest" priority)
            group = self._stop_groups.pop()
            if group.get_unstopped_processes():
                # if any processes in the group aren't yet in a stopped state, we're not yet done shutting this group
                # down, so push it back on to the end of the stop group queue
                self._stop_groups.append(group)

    def _poll(self) -> None:
        sorted_groups = list(self._process_groups)
        sorted_groups.sort()

        if self._states.state < SupervisorState.RUNNING:
            if not self._stopping:
                # first time, set the stopping flag, do a notification and set stop_groups
                self._stopping = True
                self._stop_groups = sorted_groups[:]
                self._event_callbacks.notify(SupervisorStoppingEvent())

            self._ordered_stop_groups_phase_1()

            if not self.shutdown_report():
                # if there are no unstopped processes (we're done killing everything), it's OK to shutdown or reload
                raise ExitNow

        self._io.poll()

        for group in sorted_groups:
            for process in group:
                process.transition()

    def _reap(self, *, once: bool = False, depth: int = 0) -> None:
        if depth >= 100:
            return

        wp = waitpid()
        log.info(f'Waited pid: {wp}')  # noqa
        if wp is None or not wp.pid:
            return

        process = self._pid_history.get(wp.pid, None)
        if process is None:
            _, msg = decode_wait_status(wp.sts)
            log.info('reaped unknown pid %s (%s)', wp.pid, msg)
        else:
            process.finish(wp.sts)
            del self._pid_history[wp.pid]

        if not once:
            # keep reaping until no more kids to reap, but don't recurse infinitely
            self._reap(once=False, depth=depth + 1)

    def _tick(self, now: ta.Optional[float] = None) -> None:
        """Send one or more 'tick' events when the timeslice related to the period for the event type rolls over"""

        if now is None:
            # now won't be None in unit tests
            now = time.time()

        for event in TICK_EVENTS:
            period = event.period

            last_tick = self._ticks.get(period)
            if last_tick is None:
                # we just started up
                last_tick = self._ticks[period] = timeslice(period, now)

            this_tick = timeslice(period, now)
            if this_tick != last_tick:
                self._ticks[period] = this_tick
                self._event_callbacks.notify(event(this_tick, self))


##


class WaitedPid(ta.NamedTuple):
    pid: Pid
    sts: Rc


def waitpid() -> ta.Optional[WaitedPid]:
    # Need pthread_sigmask here to avoid concurrent sigchld, but Python doesn't offer in Python < 3.4. There is
    # still a race condition here; we can get a sigchld while we're sitting in the waitpid call. However, AFAICT, if
    # waitpid is interrupted by SIGCHLD, as long as we call waitpid again (which happens every so often during the
    # normal course in the mainloop), we'll eventually reap the child that we tried to reap during the interrupted
    # call. At least on Linux, this appears to be true, or at least stopping 50 processes at once never left zombies
    # lying around.
    try:
        pid, sts = os.waitpid(-1, os.WNOHANG)
    except OSError as exc:
        code = exc.args[0]
        if code not in (errno.ECHILD, errno.EINTR):
            log.critical('waitpid error %r; a process may not be cleaned up properly', code)
        if code == errno.EINTR:
            log.debug('EINTR during reap')
        return None
    else:
        return WaitedPid(pid, sts)  # type: ignore


########################################
# ../inject.py


@dc.dataclass(frozen=True)
class _FdIoPollerDaemonizeListener(DaemonizeListener):
    _poller: FdIoPoller

    def before_daemonize(self) -> None:
        self._poller.close()

    def after_daemonize(self) -> None:
        self._poller.reopen()


def bind_server(
        config: ServerConfig,
        *,
        server_epoch: ta.Optional[ServerEpoch] = None,
        inherited_fds: ta.Optional[InheritedFds] = None,
) -> InjectorBindings:
    lst: ta.List[InjectorBindingOrBindings] = [
        inj.bind(config),

        inj.bind_array(DaemonizeListener),
        inj.bind_array_type(DaemonizeListener, DaemonizeListeners),

        inj.bind(SupervisorSetupImpl, singleton=True),
        inj.bind(SupervisorSetup, to_key=SupervisorSetupImpl),

        inj.bind(EventCallbacks, singleton=True),

        inj.bind(SignalReceiver, singleton=True),

        inj.bind(IoManager, singleton=True),
        inj.bind_array(HasDispatchers),
        inj.bind_array_type(HasDispatchers, HasDispatchersList),

        inj.bind(SignalHandler, singleton=True),

        inj.bind(ProcessGroupManager, singleton=True),
        inj.bind(HasDispatchers, array=True, to_key=ProcessGroupManager),

        inj.bind(Supervisor, singleton=True),

        inj.bind(SupervisorStateManagerImpl, singleton=True),
        inj.bind(SupervisorStateManager, to_key=SupervisorStateManagerImpl),

        inj.bind(PidHistory()),

        inj.bind_factory(ProcessGroupImpl, ProcessGroupFactory),
        inj.bind_factory(ProcessImpl, ProcessFactory),

        inj.bind_factory(ProcessSpawningImpl, ProcessSpawningFactory),

        inj.bind_factory(ProcessOutputDispatcherImpl, ProcessOutputDispatcherFactory),
        inj.bind_factory(ProcessInputDispatcherImpl, ProcessInputDispatcherFactory),
    ]

    #

    if server_epoch is not None:
        lst.append(inj.bind(server_epoch, key=ServerEpoch))
    if inherited_fds is not None:
        lst.append(inj.bind(inherited_fds, key=InheritedFds))

    #

    if config.user is not None:
        user = get_user(config.user)
        lst.append(inj.bind(user, key=SupervisorUser))

    #

    poller_impl = next(filter(None, [
        KqueueFdIoPoller,
        PollFdIoPoller,
        SelectFdIoPoller,
    ]))
    lst.append(inj.bind(poller_impl, key=FdIoPoller, singleton=True))
    inj.bind(_FdIoPollerDaemonizeListener, array=True, singleton=True)

    #

    def _provide_http_handler(s: SupervisorHttpHandler) -> HttpServer.Handler:
        return HttpServer.Handler(s.handle)

    lst.extend([
        inj.bind(HttpServer, singleton=True, eager=True),
        inj.bind(HasDispatchers, array=True, to_key=HttpServer),

        inj.bind(SupervisorHttpHandler, singleton=True),
        inj.bind(_provide_http_handler),
    ])

    #

    return inj.as_bindings(*lst)


########################################
# main.py


##


def main(
        argv: ta.Optional[ta.Sequence[str]] = None,
        *,
        no_logging: bool = False,
) -> None:
    server_cls = CoroHttpServer  # noqa

    #

    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('config_file', metavar='config-file')
    parser.add_argument('--no-journald', action='store_true')
    parser.add_argument('--inherit-initial-fds', action='store_true')
    args = parser.parse_args(argv)

    #

    if not (cf := args.config_file):
        raise RuntimeError('No config file specified')

    if not no_logging:
        configure_standard_logging(
            'INFO',
            handler_factory=journald_log_handler_factory if not (args.no_journald or is_debugger_attached()) else None,
        )

    #

    inherited_fds: ta.Optional[InheritedFds] = None
    if args.inherit_initial_fds:
        inherited_fds = InheritedFds(get_open_fds(0x10000))

    # if we hup, restart by making a new Supervisor()
    for epoch in itertools.count():
        config = read_config_file(
            os.path.expanduser(cf),
            ServerConfig,
            prepare=prepare_server_config,
        )

        injector = inj.create_injector(bind_server(
            config,
            server_epoch=ServerEpoch(epoch),
            inherited_fds=inherited_fds,
        ))

        supervisor = injector[Supervisor]

        try:
            supervisor.main()
        except ExitNow:
            pass

        if supervisor.state < SupervisorState.RESTARTING:
            break


if __name__ == '__main__':
    main()
