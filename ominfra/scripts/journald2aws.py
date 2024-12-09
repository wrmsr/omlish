#!/usr/bin/env python3
# noinspection DuplicatedCode
# @omlish-lite
# @omlish-script
# @omlish-amalg-output ../clouds/aws/journald2aws/main.py
# ruff: noqa: N802 UP006 UP007 UP036
import abc
import argparse
import base64
import collections.abc
import contextlib
import dataclasses as dc
import datetime
import decimal
import enum
import fcntl
import fractions
import functools
import hashlib
import hmac
import inspect
import io
import json
import logging
import os
import os.path
import queue
import re
import shlex
import signal
import string
import subprocess
import sys
import threading
import time
import types
import typing as ta
import urllib.parse
import urllib.request
import uuid
import weakref  # noqa


########################################


if sys.version_info < (3, 8):
    raise OSError(f'Requires python (3, 8), got {sys.version_info} from {sys.executable}')  # noqa


########################################


# ../../../../omdev/toml/parser.py
TomlParseFloat = ta.Callable[[str], ta.Any]
TomlKey = ta.Tuple[str, ...]
TomlPos = int  # ta.TypeAlias

# ../../../../omlish/lite/cached.py
T = ta.TypeVar('T')
CallableT = ta.TypeVar('CallableT', bound=ta.Callable)

# ../../../../omlish/lite/check.py
SizedT = ta.TypeVar('SizedT', bound=ta.Sized)

# ../../../../omlish/lite/contextmanagers.py
ExitStackedT = ta.TypeVar('ExitStackedT', bound='ExitStacked')

# ../../../configs.py
ConfigMapping = ta.Mapping[str, ta.Any]

# ../../../threadworkers.py
ThreadWorkerT = ta.TypeVar('ThreadWorkerT', bound='ThreadWorker')

# ../../../../omlish/lite/subprocesses.py
SubprocessChannelOption = ta.Literal['pipe', 'stdout', 'devnull']


########################################
# ../../../../../omdev/toml/parser.py
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
# ../../../../../omlish/lite/cached.py


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


def cached_nullary(fn):  # ta.Callable[..., T]) -> ta.Callable[..., T]:
    return _CachedNullary(fn)


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
# ../../../../../omlish/lite/check.py


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
# ../../../../../omlish/lite/json.py


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
# ../../../../../omlish/lite/pidfile.py


class Pidfile:
    def __init__(self, path: str) -> None:
        super().__init__()
        self._path = path

    _f: ta.TextIO

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({self._path!r})'

    def __enter__(self) -> 'Pidfile':
        fd = os.open(self._path, os.O_RDWR | os.O_CREAT, 0o600)
        try:
            os.set_inheritable(fd, True)
            f = os.fdopen(fd, 'r+')
        except Exception:
            try:
                os.close(fd)
            except Exception:  # noqa
                pass
            raise
        self._f = f
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if hasattr(self, '_f'):
            self._f.close()
            del self._f

    def try_lock(self) -> bool:
        try:
            fcntl.flock(self._f, fcntl.LOCK_EX | fcntl.LOCK_NB)
            return True
        except OSError:
            return False

    def ensure_locked(self) -> None:
        if not self.try_lock():
            raise RuntimeError('Could not get lock')

    def write(self, pid: ta.Optional[int] = None) -> None:
        self.ensure_locked()
        if pid is None:
            pid = os.getpid()
        self._f.write(f'{pid}\n')
        self._f.flush()

    def clear(self) -> None:
        self.ensure_locked()
        self._f.seek(0)
        self._f.truncate()

    def read(self) -> int:
        if self.try_lock():
            raise RuntimeError('Got lock')
        self._f.seek(0)
        return int(self._f.read())

    def kill(self, sig: int = signal.SIGTERM) -> None:
        pid = self.read()
        os.kill(pid, sig)  # FIXME: Still racy


########################################
# ../../../../../omlish/lite/reflect.py


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
# ../../../../../omlish/lite/strings.py


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
# ../../auth.py
"""
https://docs.aws.amazon.com/IAM/latest/UserGuide/create-signed-request.html

TODO:
 - https://docs.aws.amazon.com/AmazonS3/latest/API/sigv4-streaming.html
  - boto / s3transfer upload_fileobj doesn't stream either lol - eagerly calcs Content-MD5
 - sts tokens
 - !! fix canonical_qs - sort params
 - secrets
"""


##


class AwsSigner:
    def __init__(
            self,
            creds: 'AwsSigner.Credentials',
            region_name: str,
            service_name: str,
    ) -> None:
        super().__init__()
        self._creds = creds
        self._region_name = region_name
        self._service_name = service_name

    #

    @dc.dataclass(frozen=True)
    class Credentials:
        access_key_id: str
        secret_access_key: str = dc.field(repr=False)

    @dc.dataclass(frozen=True)
    class Request:
        method: str
        url: str
        headers: ta.Mapping[str, ta.Sequence[str]] = dc.field(default_factory=dict)
        payload: bytes = b''

    #

    ISO8601 = '%Y%m%dT%H%M%SZ'

    #

    @staticmethod
    def _host_from_url(url: str) -> str:
        url_parts = urllib.parse.urlsplit(url)
        host = check_non_empty_str(url_parts.hostname)
        default_ports = {
            'http': 80,
            'https': 443,
        }
        if url_parts.port is not None:
            if url_parts.port != default_ports.get(url_parts.scheme):
                host = f'{host}:{int(url_parts.port)}'
        return host

    @staticmethod
    def _lower_case_http_map(d: ta.Mapping[str, ta.Sequence[str]]) -> ta.Mapping[str, ta.Sequence[str]]:
        o: ta.Dict[str, ta.List[str]] = {}
        for k, vs in d.items():
            o.setdefault(k.lower(), []).extend(check_not_isinstance(vs, str))
        return o

    #

    @staticmethod
    def _as_bytes(data: ta.Union[str, bytes]) -> bytes:
        return data if isinstance(data, bytes) else data.encode('utf-8')

    @staticmethod
    def _sha256(data: ta.Union[str, bytes]) -> str:
        return hashlib.sha256(AwsSigner._as_bytes(data)).hexdigest()

    @staticmethod
    def _sha256_sign(key: bytes, msg: ta.Union[str, bytes]) -> bytes:
        return hmac.new(key, AwsSigner._as_bytes(msg), hashlib.sha256).digest()

    @staticmethod
    def _sha256_sign_hex(key: bytes, msg: ta.Union[str, bytes]) -> str:
        return hmac.new(key, AwsSigner._as_bytes(msg), hashlib.sha256).hexdigest()

    _EMPTY_SHA256: str

    #

    _SIGNED_HEADERS_BLACKLIST = frozenset([
        'authorization',
        'expect',
        'user-agent',
        'x-amzn-trace-id',
    ])

    def _validate_request(self, req: Request) -> None:
        check_non_empty_str(req.method)
        check_equal(req.method.upper(), req.method)
        for k, vs in req.headers.items():
            check_equal(k.strip(), k)
            for v in vs:
                check_equal(v.strip(), v)


AwsSigner._EMPTY_SHA256 = AwsSigner._sha256(b'')  # noqa


##


class V4AwsSigner(AwsSigner):
    def sign(
            self,
            req: AwsSigner.Request,
            *,
            sign_payload: bool = False,
            utcnow: ta.Optional[datetime.datetime] = None,
    ) -> ta.Mapping[str, ta.Sequence[str]]:
        self._validate_request(req)

        #

        if utcnow is None:
            utcnow = datetime.datetime.now(tz=datetime.timezone.utc)  # noqa
        req_dt = utcnow.strftime(self.ISO8601)

        #

        parsed_url = urllib.parse.urlsplit(req.url)
        canon_uri = parsed_url.path
        canon_qs = parsed_url.query

        #

        headers_to_sign: ta.Dict[str, ta.List[str]] = {
            k: list(v)
            for k, v in self._lower_case_http_map(req.headers).items()
            if k not in self._SIGNED_HEADERS_BLACKLIST
        }

        if 'host' not in headers_to_sign:
            headers_to_sign['host'] = [self._host_from_url(req.url)]

        headers_to_sign['x-amz-date'] = [req_dt]

        hashed_payload = self._sha256(req.payload) if req.payload else self._EMPTY_SHA256
        if sign_payload:
            headers_to_sign['x-amz-content-sha256'] = [hashed_payload]

        sorted_header_names = sorted(headers_to_sign)
        canon_headers = ''.join([
            ':'.join((k, ','.join(headers_to_sign[k]))) + '\n'
            for k in sorted_header_names
        ])
        signed_headers = ';'.join(sorted_header_names)

        #

        canon_req = '\n'.join([
            req.method,
            canon_uri,
            canon_qs,
            canon_headers,
            signed_headers,
            hashed_payload,
        ])

        #

        algorithm = 'AWS4-HMAC-SHA256'
        scope_parts = [
            req_dt[:8],
            self._region_name,
            self._service_name,
            'aws4_request',
        ]
        scope = '/'.join(scope_parts)
        hashed_canon_req = self._sha256(canon_req)
        string_to_sign = '\n'.join([
            algorithm,
            req_dt,
            scope,
            hashed_canon_req,
        ])

        #

        key = self._creds.secret_access_key
        key_date = self._sha256_sign(f'AWS4{key}'.encode('utf-8'), req_dt[:8])  # noqa
        key_region = self._sha256_sign(key_date, self._region_name)
        key_service = self._sha256_sign(key_region, self._service_name)
        key_signing = self._sha256_sign(key_service, 'aws4_request')
        sig = self._sha256_sign_hex(key_signing, string_to_sign)

        #

        cred_scope = '/'.join([
            self._creds.access_key_id,
            *scope_parts,
        ])
        auth = f'{algorithm} ' + ', '.join([
            f'Credential={cred_scope}',
            f'SignedHeaders={signed_headers}',
            f'Signature={sig}',
        ])

        #

        out = {
            'Authorization': [auth],
            'X-Amz-Date': [req_dt],
        }
        if sign_payload:
            out['X-Amz-Content-SHA256'] = [hashed_payload]
        return out


########################################
# ../../dataclasses.py


class AwsDataclass:
    class Raw(dict):
        pass

    #

    _aws_meta: ta.ClassVar[ta.Optional['AwsDataclassMeta']] = None

    @classmethod
    def _get_aws_meta(cls) -> 'AwsDataclassMeta':
        try:
            return cls.__dict__['_aws_meta']
        except KeyError:
            pass
        ret = cls._aws_meta = AwsDataclassMeta(cls)
        return ret

    #

    def to_aws(self) -> ta.Mapping[str, ta.Any]:
        return self._get_aws_meta().converters().d2a(self)

    @classmethod
    def from_aws(cls, v: ta.Mapping[str, ta.Any]) -> 'AwsDataclass':
        return cls._get_aws_meta().converters().a2d(v)


@dc.dataclass(frozen=True)
class AwsDataclassMeta:
    cls: ta.Type['AwsDataclass']

    #

    class Field(ta.NamedTuple):
        d_name: str
        a_name: str
        is_opt: bool
        is_seq: bool
        dc_cls: ta.Optional[ta.Type['AwsDataclass']]

    @cached_nullary
    def fields(self) -> ta.Sequence[Field]:
        fs = []
        for f in dc.fields(self.cls):  # type: ignore  # noqa
            d_name = f.name
            a_name = camel_case(d_name, lower=True)

            is_opt = False
            is_seq = False
            dc_cls = None

            c = f.type
            if c is AwsDataclass.Raw:
                continue

            if is_optional_alias(c):
                is_opt = True
                c = get_optional_alias_arg(c)

            if is_generic_alias(c) and ta.get_origin(c) is collections.abc.Sequence:
                is_seq = True
                [c] = ta.get_args(c)

            if is_generic_alias(c):
                raise TypeError(c)

            if isinstance(c, type) and issubclass(c, AwsDataclass):
                dc_cls = c

            fs.append(AwsDataclassMeta.Field(
                d_name=d_name,
                a_name=a_name,
                is_opt=is_opt,
                is_seq=is_seq,
                dc_cls=dc_cls,
            ))

        return fs

    #

    class Converters(ta.NamedTuple):
        d2a: ta.Callable
        a2d: ta.Callable

    @cached_nullary
    def converters(self) -> Converters:
        for df in dc.fields(self.cls):  # type: ignore  # noqa
            c = df.type

            if is_optional_alias(c):
                c = get_optional_alias_arg(c)

            if c is AwsDataclass.Raw:
                rf = df.name
                break

        else:
            rf = None

        fs = [
            (f, f.dc_cls._get_aws_meta().converters() if f.dc_cls is not None else None)  # noqa
            for f in self.fields()
        ]

        def d2a(o):
            dct = {}
            for f, cs in fs:
                x = getattr(o, f.d_name)
                if x is None:
                    continue
                if cs is not None:
                    if f.is_seq:
                        x = list(map(cs.d2a, x))
                    else:
                        x = cs.d2a(x)
                dct[f.a_name] = x
            return dct

        def a2d(v):
            dct = {}
            for f, cs in fs:
                x = v.get(f.a_name)
                if x is None:
                    continue
                if cs is not None:
                    if f.is_seq:
                        x = list(map(cs.a2d, x))
                    else:
                        x = cs.a2d(x)
                dct[f.d_name] = x
            if rf is not None:
                dct[rf] = self.cls.Raw(v)
            return self.cls(**dct)

        return AwsDataclassMeta.Converters(d2a, a2d)


########################################
# ../../../../../omlish/lite/contextmanagers.py


##


class ExitStacked:
    _exit_stack: ta.Optional[contextlib.ExitStack] = None

    def __enter__(self: ExitStackedT) -> ExitStackedT:
        check_state(self._exit_stack is None)
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
        es = check_not_none(self._exit_stack)
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


########################################
# ../../../../../omlish/lite/io.py


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
# ../../../../../omlish/lite/logs.py
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
# ../../../../../omlish/lite/marshal.py
"""
TODO:
 - pickle stdlib objs? have to pin to 3.8 pickle protocol, will be cross-version
 - nonstrict toggle
"""


##


@dc.dataclass(frozen=True)
class ObjMarshalOptions:
    raw_bytes: bool = False
    nonstrict_dataclasses: bool = False


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
        return check_not_none(self.m).marshal(o, ctx)

    def unmarshal(self, o: ta.Any, ctx: 'ObjMarshalContext') -> ta.Any:
        return check_not_none(self.m).unmarshal(o, ctx)


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
class DataclassObjMarshaler(ObjMarshaler):
    ty: type
    fs: ta.Mapping[str, ObjMarshaler]
    nonstrict: bool = False

    def marshal(self, o: ta.Any, ctx: 'ObjMarshalContext') -> ta.Any:
        return {
            k: m.marshal(getattr(o, k), ctx)
            for k, m in self.fs.items()
        }

    def unmarshal(self, o: ta.Any, ctx: 'ObjMarshalContext') -> ta.Any:
        return self.ty(**{
            k: self.fs[k].unmarshal(v, ctx)
            for k, v in o.items()
            if not (self.nonstrict or ctx.options.nonstrict_dataclasses) or k in self.fs
        })


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
        return str(check_isinstance(o, decimal.Decimal))

    def unmarshal(self, v: ta.Any, ctx: 'ObjMarshalContext') -> ta.Any:
        return decimal.Decimal(check_isinstance(v, str))


class FractionObjMarshaler(ObjMarshaler):
    def marshal(self, o: ta.Any, ctx: 'ObjMarshalContext') -> ta.Any:
        fr = check_isinstance(o, fractions.Fraction)
        return [fr.numerator, fr.denominator]

    def unmarshal(self, v: ta.Any, ctx: 'ObjMarshalContext') -> ta.Any:
        num, denom = check_isinstance(v, list)
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


##


class ObjMarshalerManager:
    def __init__(
            self,
            *,
            default_options: ObjMarshalOptions = ObjMarshalOptions(),

            default_obj_marshalers: ta.Dict[ta.Any, ObjMarshaler] = _DEFAULT_OBJ_MARSHALERS,  # noqa
            generic_mapping_types: ta.Dict[ta.Any, type] = _OBJ_MARSHALER_GENERIC_MAPPING_TYPES,  # noqa
            generic_iterable_types: ta.Dict[ta.Any, type] = _OBJ_MARSHALER_GENERIC_ITERABLE_TYPES,  # noqa
    ) -> None:
        super().__init__()

        self._default_options = default_options

        self._obj_marshalers = dict(default_obj_marshalers)
        self._generic_mapping_types = generic_mapping_types
        self._generic_iterable_types = generic_iterable_types

        self._lock = threading.RLock()
        self._marshalers: ta.Dict[ta.Any, ObjMarshaler] = dict(_DEFAULT_OBJ_MARSHALERS)
        self._proxies: ta.Dict[ta.Any, ProxyObjMarshaler] = {}

    #

    def make_obj_marshaler(
            self,
            ty: ta.Any,
            rec: ta.Callable[[ta.Any], ObjMarshaler],
            *,
            nonstrict_dataclasses: bool = False,
    ) -> ObjMarshaler:
        if isinstance(ty, type):
            if abc.ABC in ty.__bases__:
                return PolymorphicObjMarshaler.of([  # type: ignore
                    PolymorphicObjMarshaler.Impl(
                        ity,
                        ity.__qualname__,
                        rec(ity),
                    )
                    for ity in deep_subclasses(ty)
                    if abc.ABC not in ity.__bases__
                ])

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

    def register_opj_marshaler(self, ty: ta.Any, m: ObjMarshaler) -> None:
        with self._lock:
            if ty in self._obj_marshalers:
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

register_opj_marshaler = OBJ_MARSHALER_MANAGER.register_opj_marshaler
get_obj_marshaler = OBJ_MARSHALER_MANAGER.get_obj_marshaler

marshal_obj = OBJ_MARSHALER_MANAGER.marshal_obj
unmarshal_obj = OBJ_MARSHALER_MANAGER.unmarshal_obj


########################################
# ../../../../../omlish/lite/runtime.py


@cached_nullary
def is_debugger_attached() -> bool:
    return any(frame[1].endswith('pydevd.py') for frame in inspect.stack())


REQUIRED_PYTHON_VERSION = (3, 8)


def check_runtime_version() -> None:
    if sys.version_info < REQUIRED_PYTHON_VERSION:
        raise OSError(f'Requires python {REQUIRED_PYTHON_VERSION}, got {sys.version_info} from {sys.executable}')  # noqa


########################################
# ../cursor.py


class JournalctlToAwsCursor:
    def __init__(
            self,
            cursor_file: ta.Optional[str] = None,
            *,
            ensure_locked: ta.Optional[ta.Callable[[], None]] = None,
    ) -> None:
        super().__init__()
        self._cursor_file = cursor_file
        self._ensure_locked = ensure_locked

    #

    def get(self) -> ta.Optional[str]:
        if self._ensure_locked is not None:
            self._ensure_locked()

        if not (cf := self._cursor_file):
            return None
        cf = os.path.expanduser(cf)

        try:
            with open(cf) as f:
                return f.read().strip()
        except FileNotFoundError:
            return None

    def set(self, cursor: str) -> None:
        if self._ensure_locked is not None:
            self._ensure_locked()

        if not (cf := self._cursor_file):
            return
        cf = os.path.expanduser(cf)

        log.info('Writing cursor file %s : %s', cf, cursor)
        with open(ncf := cf + '.next', 'w') as f:
            f.write(cursor)

        os.rename(ncf, cf)


########################################
# ../../logs.py
"""
https://docs.aws.amazon.com/AmazonCloudWatchLogs/latest/APIReference/API_PutLogEvents.html :
 - The maximum batch size is 1,048,576 bytes. This size is calculated as the sum of all event messages in UTF-8, plus 26
   bytes for each log event.
 - None of the log events in the batch can be more than 2 hours in the future.
 - None of the log events in the batch can be more than 14 days in the past. Also, none of the log events can be from
   earlier than the retention period of the log group.
 - The log events in the batch must be in chronological order by their timestamp. The timestamp is the time that the
   event occurred, expressed as the number of milliseconds after Jan 1, 1970 00:00:00 UTC. (In AWS Tools for PowerShell
   and the AWS SDK for .NET, the timestamp is specified in .NET format: yyyy-mm-ddThh:mm:ss. For example,
   2017-09-15T13:45:30.)
 - A batch of log events in a single request cannot span more than 24 hours. Otherwise, the operation fails.
 - Each log event can be no larger than 256 KB.
 - The maximum number of log events in a batch is 10,000.
"""


##


@dc.dataclass(frozen=True)
class AwsLogEvent(AwsDataclass):
    message: str
    timestamp: int  # milliseconds UTC


@dc.dataclass(frozen=True)
class AwsPutLogEventsRequest(AwsDataclass):
    log_group_name: str
    log_stream_name: str
    log_events: ta.Sequence[AwsLogEvent]
    sequence_token: ta.Optional[str] = None


@dc.dataclass(frozen=True)
class AwsRejectedLogEventsInfo(AwsDataclass):
    expired_log_event_end_index: ta.Optional[int] = None
    too_new_log_event_start_index: ta.Optional[int] = None
    too_old_log_event_end_index: ta.Optional[int] = None


@dc.dataclass(frozen=True)
class AwsPutLogEventsResponse(AwsDataclass):
    next_sequence_token: ta.Optional[str] = None
    rejected_log_events_info: ta.Optional[AwsRejectedLogEventsInfo] = None

    raw: ta.Optional[AwsDataclass.Raw] = None


##


class AwsLogMessageBuilder:
    """
    TODO:
     - max_items
     - max_bytes - manually build body
     - flush_interval
     - split sorted chunks if span over 24h
    """

    DEFAULT_URL = 'https://logs.{region_name}.amazonaws.com/'  # noqa

    DEFAULT_SERVICE_NAME = 'logs'

    DEFAULT_TARGET = 'Logs_20140328.PutLogEvents'
    DEFAULT_CONTENT_TYPE = 'application/x-amz-json-1.1'

    DEFAULT_HEADERS: ta.Mapping[str, str] = {
        'X-Amz-Target': DEFAULT_TARGET,
        'Content-Type': DEFAULT_CONTENT_TYPE,
    }

    def __init__(
            self,
            log_group_name: str,
            log_stream_name: str,
            region_name: str,
            credentials: ta.Optional[AwsSigner.Credentials],

            url: ta.Optional[str] = None,
            service_name: str = DEFAULT_SERVICE_NAME,
            headers: ta.Optional[ta.Mapping[str, str]] = None,
            extra_headers: ta.Optional[ta.Mapping[str, str]] = None,
    ) -> None:
        super().__init__()

        self._log_group_name = check_non_empty_str(log_group_name)
        self._log_stream_name = check_non_empty_str(log_stream_name)

        if url is None:
            url = self.DEFAULT_URL.format(region_name=region_name)
        self._url = url

        if headers is None:
            headers = self.DEFAULT_HEADERS
        if extra_headers is not None:
            headers = {**headers, **extra_headers}
        self._headers = {k: [v] for k, v in headers.items()}

        signer: ta.Optional[V4AwsSigner]
        if credentials is not None:
            signer = V4AwsSigner(
                credentials,
                region_name,
                service_name,
            )
        else:
            signer = None
        self._signer = signer

    #

    @dc.dataclass(frozen=True)
    class Message:
        message: str
        ts_ms: int  # milliseconds UTC

    @dc.dataclass(frozen=True)
    class Post:
        url: str
        headers: ta.Mapping[str, str]
        data: bytes

    def feed(self, messages: ta.Sequence[Message]) -> ta.Sequence[Post]:
        if not messages:
            return []

        payload = AwsPutLogEventsRequest(
            log_group_name=self._log_group_name,
            log_stream_name=self._log_stream_name,
            log_events=[
                AwsLogEvent(
                    message=m.message,
                    timestamp=m.ts_ms,
                )
                for m in sorted(messages, key=lambda m: m.ts_ms)
            ],
        )

        body = json.dumps(
            payload.to_aws(),
            indent=None,
            separators=(',', ':'),
        ).encode('utf-8')

        sig_req = V4AwsSigner.Request(
            method='POST',
            url=self._url,
            headers=self._headers,
            payload=body,
        )

        if (signer := self._signer) is not None:
            sig_headers = signer.sign(
                sig_req,
                sign_payload=False,
            )
            sig_req = dc.replace(sig_req, headers={**sig_req.headers, **sig_headers})

        post = AwsLogMessageBuilder.Post(
            url=self._url,
            headers={k: check_single(v) for k, v in sig_req.headers.items()},
            data=sig_req.payload,
        )

        return [post]


########################################
# ../../../../configs.py


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
) -> T:
    with open(path) as cf:
        config_dct = parse_config_file(os.path.basename(path), cf)

    if prepare is not None:
        config_dct = prepare(config_dct)

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
# ../../../../journald/messages.py


@dc.dataclass(frozen=True)
class JournalctlMessage:
    raw: bytes
    dct: ta.Optional[ta.Mapping[str, ta.Any]] = None
    cursor: ta.Optional[str] = None
    ts_us: ta.Optional[int] = None  # microseconds UTC


class JournalctlMessageBuilder:
    def __init__(self) -> None:
        super().__init__()

        self._buf = DelimitingBuffer(b'\n')

    _cursor_field = '__CURSOR'

    _timestamp_fields: ta.Sequence[str] = [
        '_SOURCE_REALTIME_TIMESTAMP',
        '__REALTIME_TIMESTAMP',
    ]

    def _get_message_timestamp(self, dct: ta.Mapping[str, ta.Any]) -> ta.Optional[int]:
        for fld in self._timestamp_fields:
            if (tsv := dct.get(fld)) is None:
                continue

            if isinstance(tsv, str):
                try:
                    return int(tsv)
                except ValueError:
                    try:
                        return int(float(tsv))
                    except ValueError:
                        log.exception('Failed to parse timestamp: %r', tsv)

            elif isinstance(tsv, (int, float)):
                return int(tsv)

        log.error('Invalid timestamp: %r', dct)
        return None

    def _make_message(self, raw: bytes) -> JournalctlMessage:
        dct = None
        cursor = None
        ts = None

        try:
            dct = json.loads(raw.decode('utf-8', 'replace'))
        except Exception:  # noqa
            log.exception('Failed to parse raw message: %r', raw)

        else:
            cursor = dct.get(self._cursor_field)
            ts = self._get_message_timestamp(dct)

        return JournalctlMessage(
            raw=raw,
            dct=dct,
            cursor=cursor,
            ts_us=ts,
        )

    def feed(self, data: bytes) -> ta.Sequence[JournalctlMessage]:
        ret: ta.List[JournalctlMessage] = []
        for line in self._buf.feed(data):
            ret.append(self._make_message(check_isinstance(line, bytes)))
        return ret


########################################
# ../../../../threadworkers.py
"""
FIXME:
 - group is racy af - meditate on has_started, etc

TODO:
 - overhaul stop lol
 - group -> 'context'? :|
  - shared stop_event?
"""


##


class ThreadWorker(ExitStacked, abc.ABC):
    def __init__(
            self,
            *,
            stop_event: ta.Optional[threading.Event] = None,
            worker_groups: ta.Optional[ta.Iterable['ThreadWorkerGroup']] = None,
    ) -> None:
        super().__init__()

        if stop_event is None:
            stop_event = threading.Event()
        self._stop_event = stop_event

        self._lock = threading.RLock()
        self._thread: ta.Optional[threading.Thread] = None
        self._last_heartbeat: ta.Optional[float] = None

        for g in worker_groups or []:
            g.add(self)

    #

    def __enter__(self: ThreadWorkerT) -> ThreadWorkerT:
        with self._lock:
            return super().__enter__()  # noqa

    #

    def should_stop(self) -> bool:
        return self._stop_event.is_set()

    class Stopping(Exception):  # noqa
        pass

    #

    @property
    def last_heartbeat(self) -> ta.Optional[float]:
        return self._last_heartbeat

    def _heartbeat(
            self,
            *,
            no_stop_check: bool = False,
    ) -> None:
        self._last_heartbeat = time.time()

        if not no_stop_check and self.should_stop():
            log.info('Stopping: %s', self)
            raise ThreadWorker.Stopping

    #

    def has_started(self) -> bool:
        return self._thread is not None

    def is_alive(self) -> bool:
        return (thr := self._thread) is not None and thr.is_alive()

    def start(self) -> None:
        with self._lock:
            if self._thread is not None:
                raise RuntimeError('Thread already started: %r', self)

            thr = threading.Thread(target=self.__thread_main)
            self._thread = thr
            thr.start()

    #

    def __thread_main(self) -> None:
        try:
            self._run()
        except ThreadWorker.Stopping:
            log.exception('Thread worker stopped: %r', self)
        except Exception:  # noqa
            log.exception('Error in worker thread: %r', self)
            raise

    @abc.abstractmethod
    def _run(self) -> None:
        raise NotImplementedError

    #

    def stop(self) -> None:
        self._stop_event.set()

    def join(
            self,
            timeout: ta.Optional[float] = None,
            *,
            unless_not_started: bool = False,
    ) -> None:
        with self._lock:
            if self._thread is None:
                if not unless_not_started:
                    raise RuntimeError('Thread not started: %r', self)
                return
            self._thread.join(timeout)


##


class ThreadWorkerGroup:
    @dc.dataclass()
    class _State:
        worker: ThreadWorker

        last_heartbeat: ta.Optional[float] = None

    def __init__(self) -> None:
        super().__init__()

        self._lock = threading.RLock()
        self._states: ta.Dict[ThreadWorker, ThreadWorkerGroup._State] = {}
        self._last_heartbeat_check: ta.Optional[float] = None

    #

    def add(self, *workers: ThreadWorker) -> 'ThreadWorkerGroup':
        with self._lock:
            for w in workers:
                if w in self._states:
                    raise KeyError(w)
                self._states[w] = ThreadWorkerGroup._State(w)

        return self

    #

    def start_all(self) -> None:
        thrs = list(self._states)
        with self._lock:
            for thr in thrs:
                if not thr.has_started():
                    thr.start()

    def stop_all(self) -> None:
        for w in reversed(list(self._states)):
            if w.has_started():
                w.stop()

    def join_all(self, timeout: ta.Optional[float] = None) -> None:
        for w in reversed(list(self._states)):
            if w.has_started():
                w.join(timeout, unless_not_started=True)

    #

    def get_dead(self) -> ta.List[ThreadWorker]:
        with self._lock:
            return [thr for thr in self._states if not thr.is_alive()]

    def check_heartbeats(self) -> ta.Dict[ThreadWorker, float]:
        with self._lock:
            dct: ta.Dict[ThreadWorker, float] = {}
            for thr, st in self._states.items():
                if not thr.has_started():
                    continue
                hb = thr.last_heartbeat
                if hb is None:
                    hb = time.time()
                st.last_heartbeat = hb
                dct[st.worker] = time.time() - hb
            self._last_heartbeat_check = time.time()
        return dct


########################################
# ../../../../../omlish/lite/subprocesses.py


##


SUBPROCESS_CHANNEL_OPTION_VALUES: ta.Mapping[SubprocessChannelOption, int] = {
    'pipe': subprocess.PIPE,
    'stdout': subprocess.STDOUT,
    'devnull': subprocess.DEVNULL,
}


##


_SUBPROCESS_SHELL_WRAP_EXECS = False


def subprocess_shell_wrap_exec(*args: str) -> ta.Tuple[str, ...]:
    return ('sh', '-c', ' '.join(map(shlex.quote, args)))


def subprocess_maybe_shell_wrap_exec(*args: str) -> ta.Tuple[str, ...]:
    if _SUBPROCESS_SHELL_WRAP_EXECS or is_debugger_attached():
        return subprocess_shell_wrap_exec(*args)
    else:
        return args


def prepare_subprocess_invocation(
        *args: str,
        env: ta.Optional[ta.Mapping[str, ta.Any]] = None,
        extra_env: ta.Optional[ta.Mapping[str, ta.Any]] = None,
        quiet: bool = False,
        shell: bool = False,
        **kwargs: ta.Any,
) -> ta.Tuple[ta.Tuple[ta.Any, ...], ta.Dict[str, ta.Any]]:
    log.debug('prepare_subprocess_invocation: args=%r', args)
    if extra_env:
        log.debug('prepare_subprocess_invocation: extra_env=%r', extra_env)

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


##


@contextlib.contextmanager
def subprocess_common_context(*args: ta.Any, **kwargs: ta.Any) -> ta.Iterator[None]:
    start_time = time.time()
    try:
        log.debug('subprocess_common_context.try: args=%r', args)
        yield

    except Exception as exc:  # noqa
        log.debug('subprocess_common_context.except: exc=%r', exc)
        raise

    finally:
        end_time = time.time()
        elapsed_s = end_time - start_time
        log.debug('subprocess_common_context.finally: elapsed_s=%f args=%r', elapsed_s, args)


##


def subprocess_check_call(
        *args: str,
        stdout: ta.Any = sys.stderr,
        **kwargs: ta.Any,
) -> None:
    args, kwargs = prepare_subprocess_invocation(*args, stdout=stdout, **kwargs)
    with subprocess_common_context(*args, **kwargs):
        return subprocess.check_call(args, **kwargs)  # type: ignore


def subprocess_check_output(
        *args: str,
        **kwargs: ta.Any,
) -> bytes:
    args, kwargs = prepare_subprocess_invocation(*args, **kwargs)
    with subprocess_common_context(*args, **kwargs):
        return subprocess.check_output(args, **kwargs)


def subprocess_check_output_str(*args: str, **kwargs: ta.Any) -> str:
    return subprocess_check_output(*args, **kwargs).decode().strip()


##


DEFAULT_SUBPROCESS_TRY_EXCEPTIONS: ta.Tuple[ta.Type[Exception], ...] = (
    FileNotFoundError,
    subprocess.CalledProcessError,
)


def _subprocess_try_run(
        fn: ta.Callable[..., T],
        *args: ta.Any,
        try_exceptions: ta.Tuple[ta.Type[Exception], ...] = DEFAULT_SUBPROCESS_TRY_EXCEPTIONS,
        **kwargs: ta.Any,
) -> ta.Union[T, Exception]:
    try:
        return fn(*args, **kwargs)
    except try_exceptions as e:  # noqa
        if log.isEnabledFor(logging.DEBUG):
            log.exception('command failed')
        return e


def subprocess_try_call(
        *args: str,
        try_exceptions: ta.Tuple[ta.Type[Exception], ...] = DEFAULT_SUBPROCESS_TRY_EXCEPTIONS,
        **kwargs: ta.Any,
) -> bool:
    if isinstance(_subprocess_try_run(
            subprocess_check_call,
            *args,
            try_exceptions=try_exceptions,
            **kwargs,
    ), Exception):
        return False
    else:
        return True


def subprocess_try_output(
        *args: str,
        try_exceptions: ta.Tuple[ta.Type[Exception], ...] = DEFAULT_SUBPROCESS_TRY_EXCEPTIONS,
        **kwargs: ta.Any,
) -> ta.Optional[bytes]:
    if isinstance(ret := _subprocess_try_run(
            subprocess_check_output,
            *args,
            try_exceptions=try_exceptions,
            **kwargs,
    ), Exception):
        return None
    else:
        return ret


def subprocess_try_output_str(*args: str, **kwargs: ta.Any) -> ta.Optional[str]:
    out = subprocess_try_output(*args, **kwargs)
    return out.decode().strip() if out is not None else None


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


########################################
# ../poster.py
"""
TODO:
 - retries
"""


class JournalctlToAwsPosterWorker(ThreadWorker):
    def __init__(
            self,
            queue,  # type: queue.Queue[ta.Sequence[JournalctlMessage]]  # noqa
            builder: AwsLogMessageBuilder,
            cursor: JournalctlToAwsCursor,
            *,
            ensure_locked: ta.Optional[ta.Callable[[], None]] = None,
            dry_run: bool = False,
            queue_timeout_s: float = 1.,
            **kwargs: ta.Any,
    ) -> None:
        super().__init__(**kwargs)
        self._queue = queue
        self._builder = builder
        self._cursor = cursor
        self._ensure_locked = ensure_locked
        self._dry_run = dry_run
        self._queue_timeout_s = queue_timeout_s
    #

    def _run(self) -> None:
        if self._ensure_locked is not None:
            self._ensure_locked()

        last_cursor: ta.Optional[str] = None  # noqa
        while True:
            self._heartbeat()

            try:
                msgs: ta.Sequence[JournalctlMessage] = self._queue.get(timeout=self._queue_timeout_s)
            except queue.Empty:
                msgs = []

            if not msgs:
                log.debug('Empty queue chunk')
                continue

            log.debug('%r', msgs)

            cur_cursor: ta.Optional[str] = None
            for m in reversed(msgs):
                if m.cursor is not None:
                    cur_cursor = m.cursor
                    break

            feed_msgs = []
            for m in msgs:
                feed_msgs.append(AwsLogMessageBuilder.Message(
                    message=json.dumps(m.dct, sort_keys=True),
                    ts_ms=int((m.ts_us / 1000.) if m.ts_us is not None else (time.time() * 1000.)),
                ))

            for post in self._builder.feed(feed_msgs):
                log.debug('%r', post)

                if not self._dry_run:
                    with urllib.request.urlopen(urllib.request.Request(  # noqa
                            post.url,
                            method='POST',
                            headers=dict(post.headers),
                            data=post.data,
                    )) as resp:
                        response = AwsPutLogEventsResponse.from_aws(json.loads(resp.read().decode('utf-8')))
                    log.debug('%r', response)

            if cur_cursor is not None:
                self._cursor.set(cur_cursor)
                last_cursor = cur_cursor  # noqa


########################################
# ../../../../journald/tailer.py
"""
TODO:
 - https://www.rootusers.com/how-to-change-log-rate-limiting-in-linux/

==

https://www.freedesktop.org/software/systemd/man/latest/journalctl.html

Source Options
--system, --user
    Show messages from system services and the kernel (with --system). Show messages from service of current user (with
    --user). If neither is specified, show all messages that the user can see. The --user option affects how --unit=
    arguments are treated. See --unit=. Note that --user only works if persistent logging is enabled, via the Storage=
    setting in journald.conf(5).
-M, --machine=
    Show messages from a running, local container. Specify a container name to connect to.
-m, --merge
    Show entries interleaved from all available journals, including remote ones.
-D DIR, --directory=DIR
    Takes a directory path as argument. If specified, journalctl will operate on the specified journal directory DIR
    instead of the default runtime and system journal paths.
-i GLOB, --file=GLOB
    Takes a file glob as an argument. If specified, journalctl will operate on the specified journal files matching GLOB
    instead of the default runtime and system journal paths. May be specified multiple times, in which case files will
    be suitably interleaved.
--root=ROOT
    Takes a directory path as an argument. If specified, journalctl will operate on journal directories and catalog file
    hierarchy underneath the specified directory instead of the root directory (e.g. --update-catalog will create
    ROOT/var/lib/systemd/catalog/database, and journal files under ROOT/run/journal/ or ROOT/var/log/journal/ will be
    displayed).
--image=IMAGE
    Takes a path to a disk image file or block device node. If specified, journalctl will operate on the file system in
    the indicated disk image. This option is similar to --root=, but operates on file systems stored in disk images or
    block devices, thus providing an easy way to extract log data from disk images. The disk image should either contain
    just a file system or a set of file systems within a GPT partition table, following the Discoverable Partitions
    Specification. For further information on supported disk images, see systemd-nspawn(1)'s switch of the same name.
--image-policy=policy
    Takes an image policy string as argument, as per systemd.image-policy(7). The policy is enforced when operating on
    the disk image specified via --image=, see above. If not specified defaults to the "*" policy, i.e. all recognized
    file systems in the image are used.
--namespace=NAMESPACE
    Takes a journal namespace identifier string as argument. If not specified the data collected by the default
    namespace is shown. If specified shows the log data of the specified namespace instead. If the namespace is
    specified as "*" data from all namespaces is shown, interleaved. If the namespace identifier is prefixed with "+"
    data from the specified namespace and the default namespace is shown, interleaved, but no other. For details about
    journal namespaces see systemd-journald.service(8).

Filtering Options
-S, --since=, -U, --until=
    Start showing entries on or newer than the specified date, or on or older than the specified date, respectively.
    Date specifications should be of the format "2012-10-30 18:17:16". If the time part is omitted, "00:00:00" is
    assumed. If only the seconds component is omitted, ":00" is assumed. If the date component is omitted, the current
    day is assumed. Alternatively the strings "yesterday", "today", "tomorrow" are understood, which refer to 00:00:00
    of the day before the current day, the current day, or the day after the current day, respectively. "now" refers to
    the current time. Finally, relative times may be specified, prefixed with "-" or "+", referring to times before or
    after the current time, respectively. For complete time and date specification, see systemd.time(7). Note that
    --output=short-full prints timestamps that follow precisely this format.
-c, --cursor=
    Start showing entries from the location in the journal specified by the passed cursor.
--after-cursor=
    Start showing entries from the location in the journal after the location specified by the passed cursor. The cursor
    is shown when the --show-cursor option is used.
--cursor-file=FILE
    If FILE exists and contains a cursor, start showing entries after this location. Otherwise show entries according to
    the other given options. At the end, write the cursor of the last entry to FILE. Use this option to continually read
    the journal by sequentially calling journalctl.
-b [[ID][±offset]|all], --boot[=[ID][±offset]|all]
    Show messages from a specific boot. This will add a match for "_BOOT_ID=". The argument may be empty, in which case
    logs for the current boot will be shown. If the boot ID is omitted, a positive offset will look up the boots
    starting from the beginning of the journal, and an equal-or-less-than zero offset will look up boots starting from
    the end of the journal. Thus, 1 means the first boot found in the journal in chronological order, 2 the second and
    so on; while -0 is the last boot, -1 the boot before last, and so on. An empty offset is equivalent to specifying
    -0, except when the current boot is not the last boot (e.g. because --directory= was specified to look at logs from
    a different machine). If the 32-character ID is specified, it may optionally be followed by offset which identifies
    the boot relative to the one given by boot ID. Negative values mean earlier boots and positive values mean later
    boots. If offset is not specified, a value of zero is assumed, and the logs for the boot given by ID are shown. The
    special argument all can be used to negate the effect of an earlier use of -b.
-u, --unit=UNIT|PATTERN
    Show messages for the specified systemd unit UNIT (such as a service unit), or for any of the units matched by
    PATTERN. If a pattern is specified, a list of unit names found in the journal is compared with the specified pattern
    and all that match are used. For each unit name, a match is added for messages from the unit ("_SYSTEMD_UNIT=UNIT"),
    along with additional matches for messages from systemd and messages about coredumps for the specified unit. A match
    is also added for "_SYSTEMD_SLICE=UNIT", such that if the provided UNIT is a systemd.slice(5) unit, all logs of
    children of the slice will be shown. With --user, all --unit= arguments will be converted to match user messages as
    if specified with --user-unit=. This parameter can be specified multiple times.
--user-unit=
    Show messages for the specified user session unit. This will add a match for messages from the unit
    ("_SYSTEMD_USER_UNIT=" and "_UID=") and additional matches for messages from session systemd and messages about
    coredumps for the specified unit. A match is also added for "_SYSTEMD_USER_SLICE=UNIT", such that if the provided
    UNIT is a systemd.slice(5) unit, all logs of children of the unit will be shown. This parameter can be specified
    multiple times.
-t, --identifier=SYSLOG_IDENTIFIER
    Show messages for the specified syslog identifier SYSLOG_IDENTIFIER. This parameter can be specified multiple times.
-T, --exclude-identifier=SYSLOG_IDENTIFIER
    Exclude messages for the specified syslog identifier SYSLOG_IDENTIFIER. This parameter can be specified multiple
    times.
-p, --priority=
    Filter output by message priorities or priority ranges. Takes either a single numeric or textual log level (i.e.
    between 0/"emerg" and 7/"debug"), or a range of numeric/text log levels in the form FROM..TO. The log levels are the
    usual syslog log levels as documented in syslog(3), i.e. "emerg" (0), "alert" (1), "crit" (2), "err" (3), "warning"
    (4), "notice" (5), "info" (6), "debug" (7). If a single log level is specified, all messages with this log level or
    a lower (hence more important) log level are shown. If a range is specified, all messages within the range are
    shown, including both the start and the end value of the range. This will add "PRIORITY=" matches for the specified
    priorities.
--facility=
    Filter output by syslog facility. Takes a comma-separated list of numbers or facility names. The names are the usual
    syslog facilities as documented in syslog(3). --facility=help may be used to display a list of known facility names
    and exit.
-g, --grep=
    Filter output to entries where the MESSAGE= field matches the specified regular expression. PERL-compatible regular
    expressions are used, see pcre2pattern(3) for a detailed description of the syntax. If the pattern is all lowercase,
    matching is case insensitive. Otherwise, matching is case sensitive. This can be overridden with the
    --case-sensitive option, see below. When used with --lines= (not prefixed with "+"), --reverse is implied.
--case-sensitive[=BOOLEAN]
    Make pattern matching case sensitive or case insensitive.
-k, --dmesg
    Show only kernel messages. This implies -b and adds the match "_TRANSPORT=kernel".

Output Options
-o, --output=
    Controls the formatting of the journal entries that are shown. Takes one of the following options:
        short
            is the default and generates an output that is mostly identical to the formatting of classic syslog files,
            showing one line per journal entry.
        short-full
            is very similar, but shows timestamps in the format the --since= and --until= options accept. Unlike the
            timestamp information shown in short output mode this mode includes weekday, year and timezone information
            in the output, and is locale-independent.
        short-iso
            is very similar, but shows timestamps in the RFC 3339 profile of ISO 8601.
        short-iso-precise
            as for short-iso but includes full microsecond precision.
        short-precise
            is very similar, but shows classic syslog timestamps with full microsecond precision.
        short-monotonic
            is very similar, but shows monotonic timestamps instead of wallclock timestamps.
        short-delta
            as for short-monotonic but includes the time difference to the previous entry. Maybe unreliable time
            differences are marked by a "*".
        short-unix
            is very similar, but shows seconds passed since January 1st 1970 UTC instead of wallclock timestamps ("UNIX
            time"). The time is shown with microsecond accuracy.
        verbose
            shows the full-structured entry items with all fields.
        export
            serializes the journal into a binary (but mostly text-based) stream suitable for backups and network
            transfer (see Journal Export Format for more information). To import the binary stream back into native
            journald format use systemd-journal-remote(8).
        json
            formats entries as JSON objects, separated by newline characters (see Journal JSON Format for more
            information). Field values are generally encoded as JSON strings, with three exceptions: Fields larger than
            4096 bytes are encoded as null values. (This may be turned off by passing --all, but be aware that this may
            allocate overly long JSON objects.) Journal entries permit non-unique fields within the same log entry. JSON
            does not allow non-unique fields within objects. Due to this, if a non-unique field is encountered a JSON
            array is used as field value, listing all field values as elements. Fields containing non-printable or
            non-UTF8 bytes are encoded as arrays containing the raw bytes individually formatted as unsigned numbers.
            Note that this encoding is reversible (with the exception of the size limit).
        json-pretty
            formats entries as JSON data structures, but formats them in multiple lines in order to make them more
            readable by humans.
        json-sse
            formats entries as JSON data structures, but wraps them in a format suitable for Server-Sent Events.
        json-seq
            formats entries as JSON data structures, but prefixes them with an ASCII Record Separator character (0x1E)
            and suffixes them with an ASCII Line Feed character (0x0A), in accordance with JavaScript Object Notation
            (JSON) Text Sequences ("application/json-seq").
        cat
            generates a very terse output, only showing the actual message of each journal entry with no metadata, not
            even a timestamp. If combined with the --output-fields= option will output the listed fields for each log
            record, instead of the message.
        with-unit
            similar to short-full, but prefixes the unit and user unit names instead of the traditional syslog
            identifier. Useful when using templated instances, as it will include the arguments in the unit names.
--truncate-newline
    Truncate each log message at the first newline character on output, so that only the first line of each message is
    displayed.
--output-fields=
    A comma separated list of the fields which should be included in the output. This has an effect only for the output
    modes which would normally show all fields (verbose, export, json, json-pretty, json-sse and json-seq), as well as
    on cat. For the former, the "__CURSOR", "__REALTIME_TIMESTAMP", "__MONOTONIC_TIMESTAMP", and "_BOOT_ID" fields are
    always printed.
-n, --lines=
    Show the most recent journal events and limit the number of events shown. The argument is a positive integer or
    "all" to disable the limit. Additionally, if the number is prefixed with "+", the oldest journal events are used
    instead. The default value is 10 if no argument is given. If --follow is used, this option is implied. When not
    prefixed with "+" and used with --grep=, --reverse is implied.
-r, --reverse
    Reverse output so that the newest entries are displayed first.
--show-cursor
    The cursor is shown after the last entry after two dashes:
-- cursor: s=0639…
    The format of the cursor is private and subject to change.
--utc
    Express time in Coordinated Universal Time (UTC).
-x, --catalog
    Augment log lines with explanation texts from the message catalog. This will add explanatory help texts to log
    messages in the output where this is available. These short help texts will explain the context of an error or log
    event, possible solutions, as well as pointers to support forums, developer documentation, and any other relevant
    manuals. Note that help texts are not available for all messages, but only for selected ones. For more information
    on the message catalog, see Journal Message Catalogs. Note: when attaching journalctl output to bug reports, please
    do not use -x.
--no-hostname
    Don't show the hostname field of log messages originating from the local host. This switch has an effect only on the
    short family of output modes (see above). Note: this option does not remove occurrences of the hostname from log
    entries themselves, so it does not prevent the hostname from being visible in the logs.
--no-full, --full, -l
    Ellipsize fields when they do not fit in available columns. The default is to show full fields, allowing them to
    wrap or be truncated by the pager, if one is used. The old options -l/--full are not useful anymore, except to undo
    --no-full.
-a, --all
    Show all fields in full, even if they include unprintable characters or are very long. By default, fields with
    unprintable characters are abbreviated as "blob data". (Note that the pager may escape unprintable characters
    again.)
-f, --follow
    Show only the most recent journal entries, and continuously print new entries as they are appended to the journal.
--no-tail
    Show all stored output lines, even in follow mode. Undoes the effect of --lines=.
-q, --quiet
    Suppresses all informational messages (i.e. "-- Journal begins at …", "-- Reboot --"), any warning messages
    regarding inaccessible system journals when run as a normal user.

Pager Control Options
--no-pager
    Do not pipe output into a pager.
-e, --pager-end
    Immediately jump to the end of the journal inside the implied pager tool. This implies -n1000 to guarantee that the
    pager will not buffer logs of unbounded size. This may be overridden with an explicit -n with some other numeric
    value, while -nall will disable this cap. Note that this option is only supported for the less(1) pager.

Forward Secure Sealing (FSS) Options
--interval=
    Specifies the change interval for the sealing key when generating an FSS key pair with --setup-keys. Shorter
    intervals increase CPU consumption but shorten the time range of undetectable journal alterations. Defaults to
    15min.
--verify-key=
    Specifies the FSS verification key to use for the --verify operation.
--force
    When --setup-keys is passed and Forward Secure Sealing (FSS) has already been configured, recreate FSS keys.

Commands
-N, --fields
    Print all field names currently used in all entries of the journal.
-F, --field=
    Print all possible data values the specified field can take in all entries of the journal.
--list-boots
    Show a tabular list of boot numbers (relative to the current boot), their IDs, and the timestamps of the first and
    last message pertaining to the boot. When specified with -n/--lines=[+]N option, only the first (when the number
    prefixed with "+") or the last (without prefix) N entries will be shown. When specified with -r/--reverse, the list
    will be shown in the reverse order.
--disk-usage
    Shows the current disk usage of all journal files. This shows the sum of the disk usage of all archived and active
    journal files.
--vacuum-size=, --vacuum-time=, --vacuum-files=
    --vacuum-size=
        removes the oldest archived journal files until the disk space they use falls below the specified size. Accepts
        the usual "K", "M", "G" and "T" suffixes (to the base of 1024).
    --vacuum-time=
        removes archived journal files older than the specified timespan. Accepts the usual "s" (default), "m", "h",
        "days", "weeks", "months", and "years" suffixes, see systemd.time(7) for details.
    --vacuum-files=
        leaves only the specified number of separate journal files. Note that running --vacuum-size= has only an
        indirect effect on the output shown by --disk-usage, as the latter includes active journal files, while the
        vacuuming operation only operates on archived journal files. Similarly,
    --vacuum-files= might not actually reduce the number of journal files to below the specified number, as it will not
    remove active journal files.
    --vacuum-size=, --vacuum-time= and --vacuum-files= may be combined in a single invocation to enforce any combination
    of a size, a time and a number of files limit on the archived journal files. Specifying any of these three
    parameters as zero is equivalent to not enforcing the specific limit, and is thus redundant.
    These three switches may also be combined with --rotate into one command. If so, all active files are rotated first,
    and the requested vacuuming operation is executed right after. The rotation has the effect that all currently active
    files are archived (and potentially new, empty journal files opened as replacement), and hence the vacuuming
    operation has the greatest effect as it can take all log data written so far into account.
--verify
    Check the journal file for internal consistency. If the file has been generated with FSS enabled and the FSS
    verification key has been specified with --verify-key=, authenticity of the journal file is verified.
--sync
    Asks the journal daemon to write all yet unwritten journal data to the backing file system and synchronize all
    journals. This call does not return until the synchronization operation is complete. This command guarantees that
    any log messages written before its invocation are safely stored on disk at the time it returns.
--relinquish-var
    Asks the journal daemon for the reverse operation to --flush: if requested the daemon will write further log data to
    /run/log/journal/ and stops writing to /var/log/journal/. A subsequent call to --flush causes the log output to
    switch back to /var/log/journal/, see above.
--smart-relinquish-var
    Similar to --relinquish-var, but executes no operation if the root file system and /var/log/journal/ reside on the
    same mount point. This operation is used during system shutdown in order to make the journal daemon stop writing
    data to /var/log/journal/ in case that directory is located on a mount point that needs to be unmounted.
--flush
    Asks the journal daemon to flush any log data stored in /run/log/journal/ into /var/log/journal/, if persistent
    storage is enabled. This call does not return until the operation is complete. Note that this call is idempotent:
    the data is only flushed from /run/log/journal/ into /var/log/journal/ once during system runtime (but see
    --relinquish-var below), and this command exits cleanly without executing any operation if this has already
    happened. This command effectively guarantees that all data is flushed to /var/log/journal/ at the time it returns.
--rotate
    Asks the journal daemon to rotate journal files. This call does not return until the rotation operation is complete.
    Journal file rotation has the effect that all currently active journal files are marked as archived and renamed, so
    that they are never written to in future. New (empty) journal files are then created in their place. This operation
    may be combined with --vacuum-size=, --vacuum-time= and --vacuum-file= into a single command, see above.
--header
    Instead of showing journal contents, show internal header information of the journal fields accessed. This option is
    particularly useful when trying to identify out-of-order journal entries, as happens for example when the machine is
    booted with the wrong system time.
--list-catalog [128-bit-ID…]
    List the contents of the message catalog as a table of message IDs, plus their short description strings. If any
    128-bit-IDs are specified, only those entries are shown.
--dump-catalog [128-bit-ID…]
    Show the contents of the message catalog, with entries separated by a line consisting of two dashes and the ID (the
    format is the same as .catalog files). If any 128-bit-IDs are specified, only those entries are shown.
--update-catalog
    Update the message catalog index. This command needs to be executed each time new catalog files are installed,
    removed, or updated to rebuild the binary catalog index.
--setup-keys
    Instead of showing journal contents, generate a new key pair for Forward Secure Sealing (FSS). This will generate a
    sealing key and a verification key. The sealing key is stored in the journal data directory and shall remain on the
    host. The verification key should be stored externally. Refer to the Seal= option in journald.conf(5) for
    information on Forward Secure Sealing and for a link to a refereed scholarly paper detailing the cryptographic
    theory it is based on.
-h, --help
    Print a short help text and exit.
--version
    Print a short version string and exit.

Environment
$SYSTEMD_LOG_LEVEL
    The maximum log level of emitted messages (messages with a higher log level, i.e. less important ones, will be
    suppressed). Takes a comma-separated list of values. A value may be either one of (in order of decreasing
    importance) emerg, alert, crit, err, warning, notice, info, debug, or an integer in the range 0…7. See syslog(3) for
    more information. Each value may optionally be prefixed with one of console, syslog, kmsg or journal followed by a
    colon to set the maximum log level for that specific log target (e.g. SYSTEMD_LOG_LEVEL=debug,console:info specifies
    to log at debug level except when logging to the console which should be at info level). Note that the global
    maximum log level takes priority over any per target maximum log levels.
$SYSTEMD_LOG_COLOR
    A boolean. If true, messages written to the tty will be colored according to priority. This setting is only useful
    when messages are written directly to the terminal, because journalctl(1) and other tools that display logs will
    color messages based on the log level on their own.
$SYSTEMD_LOG_TIME
    A boolean. If true, console log messages will be prefixed with a timestamp. This setting is only useful when
    messages are written directly to the terminal or a file, because journalctl(1) and other tools that display logs
    will attach timestamps based on the entry metadata on their own.
$SYSTEMD_LOG_LOCATION
    A boolean. If true, messages will be prefixed with a filename and line number in the source code where the message
    originates. Note that the log location is often attached as metadata to journal entries anyway. Including it
    directly in the message text can nevertheless be convenient when debugging programs.
$SYSTEMD_LOG_TID
    A boolean. If true, messages will be prefixed with the current numerical thread ID (TID). Note that the this
    information is attached as metadata to journal entries anyway. Including it directly in the message text can
    nevertheless be convenient when debugging programs.
$SYSTEMD_LOG_TARGET
    The destination for log messages. One of console (log to the attached tty), console-prefixed (log to the attached
    tty but with prefixes encoding the log level and "facility", see syslog(3), kmsg (log to the kernel circular log
    buffer), journal (log to the journal), journal-or-kmsg (log to the journal if available, and to kmsg otherwise),
    auto (determine the appropriate log target automatically, the default), null (disable log output).
$SYSTEMD_LOG_RATELIMIT_KMSG
    Whether to ratelimit kmsg or not. Takes a boolean. Defaults to "true". If disabled, systemd will not ratelimit
    messages written to kmsg.
$SYSTEMD_PAGER
    Pager to use when --no-pager is not given; overrides $PAGER. If neither $SYSTEMD_PAGER nor $PAGER are set, a set of
    well-known pager implementations are tried in turn, including less(1) and more(1), until one is found. If no pager
    implementation is discovered no pager is invoked. Setting this environment variable to an empty string or the value
    "cat" is equivalent to passing --no-pager. Note: if $SYSTEMD_PAGERSECURE is not set, $SYSTEMD_PAGER (as well as
    $PAGER) will be silently ignored.
$SYSTEMD_LESS
    Override the options passed to less (by default "FRSXMK"). Users might want to change two options in particular:
        K
            This option instructs the pager to exit immediately when Ctrl+C is pressed. To allow less to handle Ctrl+C
            itself to switch back to the pager command prompt, unset this option. If the value of $SYSTEMD_LESS does not
            include "K", and the pager that is invoked is less, Ctrl+C will be ignored by the executable, and needs to
            be handled by the pager.
        X
            This option instructs the pager to not send termcap initialization and deinitialization strings to the
            terminal. It is set by default to allow command output to remain visible in the terminal even after the
            pager exits. Nevertheless, this prevents some pager functionality from working, in particular paged output
            cannot be scrolled with the mouse. Note that setting the regular $LESS environment variable has no effect
            for less invocations by systemd tools.
$SYSTEMD_LESSCHARSET
    Override the charset passed to less (by default "utf-8", if the invoking terminal is determined to be UTF-8
    compatible). Note that setting the regular $LESSCHARSET environment variable has no effect for less invocations by
    systemd tools.
$SYSTEMD_PAGERSECURE
    Takes a boolean argument. When true, the "secure" mode of the pager is enabled; if false, disabled. If
    $SYSTEMD_PAGERSECURE is not set at all, secure mode is enabled if the effective UID is not the same as the owner of
    the login session, see geteuid(2) and sd_pid_get_owner_uid(3). In secure mode, LESSSECURE=1 will be set when
    invoking the pager, and the pager shall disable commands that open or create new files or start new subprocesses.
    When $SYSTEMD_PAGERSECURE is not set at all, pagers which are not known to implement secure mode will not be used.
    (Currently only less(1) implements secure mode.) Note: when commands are invoked with elevated privileges, for
    example under sudo(8) or pkexec(1), care must be taken to ensure that unintended interactive features are not
    enabled. "Secure" mode for the pager may be enabled automatically as describe above. Setting SYSTEMD_PAGERSECURE=0
    or not removing it from the inherited environment allows the user to invoke arbitrary commands. Note that if the
    $SYSTEMD_PAGER or $PAGER variables are to be honoured, $SYSTEMD_PAGERSECURE must be set too. It might be reasonable
    to completely disable the pager using --no-pager instead.
$SYSTEMD_COLORS
    Takes a boolean argument. When true, systemd and related utilities will use colors in their output, otherwise the
    output will be monochrome. Additionally, the variable can take one of the following special values: "16", "256" to
    restrict the use of colors to the base 16 or 256 ANSI colors, respectively. This can be specified to override the
    automatic decision based on $TERM and what the console is connected to.
$SYSTEMD_URLIFY
    The value must be a boolean. Controls whether clickable links should be generated in the output for terminal
    emulators supporting this. This can be specified to override the decision that systemd makes based on $TERM and
    other conditions.
"""


class JournalctlTailerWorker(ThreadWorker):
    DEFAULT_CMD: ta.ClassVar[ta.Sequence[str]] = ['journalctl']

    def __init__(
            self,
            output,  # type: queue.Queue[ta.Sequence[JournalctlMessage]]
            *,
            since: ta.Optional[str] = None,
            after_cursor: ta.Optional[str] = None,

            cmd: ta.Optional[ta.Sequence[str]] = None,
            shell_wrap: bool = False,

            read_size: int = 0x4000,
            sleep_s: float = 1.,

            **kwargs: ta.Any,
    ) -> None:
        super().__init__(**kwargs)

        self._output = output

        self._since = since
        self._after_cursor = after_cursor

        self._cmd = cmd or self.DEFAULT_CMD
        self._shell_wrap = shell_wrap

        self._read_size = read_size
        self._sleep_s = sleep_s

        self._builder = JournalctlMessageBuilder()

        self._proc: ta.Optional[subprocess.Popen] = None

    @cached_nullary
    def _full_cmd(self) -> ta.Sequence[str]:
        cmd = [
            *self._cmd,
            '--output', 'json',
            '--show-cursor',
            '--follow',
        ]

        if self._since is not None:
            cmd.extend(['--since', self._since])

        if self._after_cursor is not None:
            cmd.extend(['--after-cursor', self._after_cursor])

        if self._shell_wrap:
            cmd = list(subprocess_shell_wrap_exec(*cmd))

        return cmd

    def _read_loop(self, stdout: ta.IO) -> None:
        while stdout.readable():
            self._heartbeat()

            buf = stdout.read(self._read_size)
            if not buf:
                log.debug('Journalctl empty read')
                break

            log.debug('Journalctl read buffer: %r', buf)
            msgs = self._builder.feed(buf)
            if msgs:
                while True:
                    try:
                        self._output.put(msgs, timeout=1.)
                    except queue.Full:
                        self._heartbeat()
                    else:
                        break

    def _run(self) -> None:
        with subprocess.Popen(
            self._full_cmd(),
            stdout=subprocess.PIPE,
        ) as self._proc:
            try:
                stdout = check_not_none(self._proc.stdout)

                fd = stdout.fileno()
                fl = fcntl.fcntl(fd, fcntl.F_GETFL)
                fcntl.fcntl(fd, fcntl.F_SETFL, fl | os.O_NONBLOCK)

                while True:
                    self._heartbeat()

                    self._read_loop(stdout)

                    log.debug('Journalctl not readable')

                    if self._proc.poll() is not None:
                        log.critical('Journalctl process terminated')
                        return

                    time.sleep(self._sleep_s)

            finally:
                subprocess_close(self._proc)


########################################
# ../driver.py
"""
TODO:
 - create log group
 - log stats - chunk sizes, byte count, num calls, etc

==

https://www.freedesktop.org/software/systemd/man/latest/journalctl.html

journalctl:
  -o json
  --show-cursor

  --since "2012-10-30 18:17:16"
  --until "2012-10-30 18:17:16"

  --after-cursor <cursor>

==

https://www.freedesktop.org/software/systemd/man/latest/systemd.journal-fields.html

==

@dc.dataclass(frozen=True)
class Journald2AwsConfig:
    log_group_name: str
    log_stream_name: str

    aws_batch_size: int = 1_000
    aws_flush_interval_s: float = 1.
"""


##


class JournalctlToAwsDriver(ExitStacked):
    @dc.dataclass(frozen=True)
    class Config:
        pid_file: ta.Optional[str] = None

        cursor_file: ta.Optional[str] = None

        runtime_limit: ta.Optional[float] = None
        heartbeat_age_limit: ta.Optional[float] = 60.

        #

        aws_log_group_name: str = 'omlish'
        aws_log_stream_name: ta.Optional[str] = None

        aws_access_key_id: ta.Optional[str] = None
        aws_secret_access_key: ta.Optional[str] = dc.field(default=None, repr=False)

        aws_region_name: str = 'us-west-1'

        aws_dry_run: bool = False

        #

        journalctl_cmd: ta.Optional[ta.Sequence[str]] = None

        journalctl_after_cursor: ta.Optional[str] = None
        journalctl_since: ta.Optional[str] = None

    def __init__(self, config: Config) -> None:
        super().__init__()

        self._config = config

    #

    @cached_nullary
    def _pidfile(self) -> ta.Optional[Pidfile]:
        if self._config.pid_file is None:
            return None

        pfp = os.path.expanduser(self._config.pid_file)

        log.info('Opening pidfile %s', pfp)

        pf = self._enter_context(Pidfile(pfp))
        pf.write()
        return pf

    def _ensure_locked(self) -> None:
        if (pf := self._pidfile()) is not None:
            pf.ensure_locked()

    #

    @cached_nullary
    def _cursor(self) -> JournalctlToAwsCursor:
        return JournalctlToAwsCursor(
            self._config.cursor_file,
            ensure_locked=self._ensure_locked,
        )

    #

    @cached_nullary
    def _aws_credentials(self) -> ta.Optional[AwsSigner.Credentials]:
        if self._config.aws_access_key_id is None and self._config.aws_secret_access_key is None:
            return None

        return AwsSigner.Credentials(
            access_key_id=check_non_empty_str(self._config.aws_access_key_id),
            secret_access_key=check_non_empty_str(self._config.aws_secret_access_key),
        )

    @cached_nullary
    def _aws_log_message_builder(self) -> AwsLogMessageBuilder:
        return AwsLogMessageBuilder(
            log_group_name=self._config.aws_log_group_name,
            log_stream_name=check_non_empty_str(self._config.aws_log_stream_name),
            region_name=self._config.aws_region_name,
            credentials=self._aws_credentials(),
        )

    #

    @cached_nullary
    def _worker_group(self) -> ThreadWorkerGroup:
        return ThreadWorkerGroup()

    #

    @cached_nullary
    def _journalctl_message_queue(self):  # type: () -> queue.Queue[ta.Sequence[JournalctlMessage]]
        return queue.Queue()

    @cached_nullary
    def _journalctl_tailer_worker(self) -> JournalctlTailerWorker:
        ac: ta.Optional[str] = None

        if (since := self._config.journalctl_since):
            log.info('Starting since %s', since)

        else:
            ac = self._config.journalctl_after_cursor
            if ac is None:
                ac = self._cursor().get()
            if ac is not None:
                log.info('Starting from cursor %s', ac)

        return JournalctlTailerWorker(
            self._journalctl_message_queue(),

            since=since,
            after_cursor=ac,

            cmd=self._config.journalctl_cmd,
            shell_wrap=is_debugger_attached(),

            worker_groups=[self._worker_group()],
        )

    #

    @cached_nullary
    def _aws_poster_worker(self) -> JournalctlToAwsPosterWorker:
        return JournalctlToAwsPosterWorker(
            self._journalctl_message_queue(),
            self._aws_log_message_builder(),
            self._cursor(),

            ensure_locked=self._ensure_locked,
            dry_run=self._config.aws_dry_run,

            worker_groups=[self._worker_group()],
        )

    #

    def _exit_contexts(self) -> None:
        wg = self._worker_group()
        wg.stop_all()
        wg.join_all()

    def run(self) -> None:
        self._aws_poster_worker()
        self._journalctl_tailer_worker()

        wg = self._worker_group()
        wg.start_all()

        start = time.time()

        while True:
            for w in wg.get_dead():
                log.critical('Worker died: %r', w)
                break

            if (al := self._config.heartbeat_age_limit) is not None:
                hbs = wg.check_heartbeats()
                log.debug('Worker heartbeats: %r', hbs)
                for w, age in hbs.items():
                    if age > al:
                        log.critical('Worker heartbeat age limit exceeded: %r %f > %f', w, age, al)
                        break

            if (rl := self._config.runtime_limit) is not None and time.time() - start >= rl:
                log.warning('Runtime limit reached')
                break

            time.sleep(1.)

        wg.stop_all()
        wg.join_all()


########################################
# main.py


def _main() -> None:
    parser = argparse.ArgumentParser()

    parser.add_argument('--config-file')
    parser.add_argument('-v', '--verbose', action='store_true')

    parser.add_argument('--after-cursor', nargs='?')
    parser.add_argument('--since', nargs='?')
    parser.add_argument('--dry-run', action='store_true')

    parser.add_argument('--message', nargs='?')
    parser.add_argument('--real', action='store_true')
    parser.add_argument('--num-messages', type=int)
    parser.add_argument('--runtime-limit', type=float)

    args = parser.parse_args()

    #

    configure_standard_logging('DEBUG' if args.verbose else 'INFO')

    #

    config: JournalctlToAwsDriver.Config
    if args.config_file:
        config = read_config_file(os.path.expanduser(args.config_file), JournalctlToAwsDriver.Config)
    else:
        config = JournalctlToAwsDriver.Config()

    #

    for k in ['aws_access_key_id', 'aws_secret_access_key']:
        if not getattr(config, k) and k.upper() in os.environ:
            config = dc.replace(config, **{k: os.environ.get(k.upper())})  # type: ignore

    #

    if not args.real:
        config = dc.replace(config, journalctl_cmd=[
            sys.executable,
            os.path.join(os.path.dirname(__file__), '..', '..', '..', 'journald', 'genmessages.py'),
            '--sleep-n', '2',
            '--sleep-s', '.5',
            *(['--message', args.message] if args.message else []),
            str(args.num_messages or 100_000),
        ])

    #

    for ca, pa in [
        ('journalctl_after_cursor', 'after_cursor'),
        ('journalctl_since', 'since'),
        ('aws_dry_run', 'dry_run'),
    ]:
        if (av := getattr(args, pa)):
            config = dc.replace(config, **{ca: av})

    #

    with JournalctlToAwsDriver(config) as jta:
        jta.run()


if __name__ == '__main__':
    _main()
