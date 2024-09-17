#!/usr/bin/env python3
# noinspection DuplicatedCode
# @omlish-lite
# @omlish-script
# @omdev-amalg-output ../pyproject/cli.py
# ruff: noqa: N802 TCH003 UP006 UP007 UP036
"""
TODO:
 - check / tests, src dir sets
 - ci
 - build / package / publish / version roll
  - {pkg_name: [src_dirs]}, default excludes, generate MANIFST.in, ...
 - env vars - PYTHONPATH
 - optional uv backend

lookit:
 - https://pdm-project.org/en/latest/
 - https://rye.astral.sh/philosophy/
 - https://github.com/indygreg/python-build-standalone/blob/main/pythonbuild/cpython.py
 - https://astral.sh/blog/uv
 - https://github.com/jazzband/pip-tools
 - https://github.com/Osiris-Team/1JPM
 - https://github.com/brettcannon/microvenv
 - https://github.com/pypa/pipx
 - https://github.com/tox-dev/tox/
"""
import abc
import argparse
import base64
import collections
import collections.abc
import concurrent.futures as cf
import csv
import dataclasses as dc
import datetime
import decimal
import enum
import fractions
import functools
import glob
import hashlib
import importlib
import inspect
import io
import itertools
import json
import logging
import multiprocessing as mp
import os
import os.path
import re
import shlex
import shutil
import stat
import string
import subprocess
import sys
import tarfile
import tempfile
import threading
import time
import types
import typing as ta
import uuid
import weakref  # noqa
import zipfile


########################################


if sys.version_info < (3, 8):
    raise OSError(
        f'Requires python (3, 8), got {sys.version_info} from {sys.executable}')  # noqa


########################################


# ../../toml/parser.py
TomlParseFloat = ta.Callable[[str], ta.Any]
TomlKey = ta.Tuple[str, ...]
TomlPos = int  # ta.TypeAlias

# ../../versioning/versions.py
VersionLocalType = ta.Tuple[ta.Union[int, str], ...]
VersionCmpPrePostDevType = ta.Union['InfinityVersionType', 'NegativeInfinityVersionType', ta.Tuple[str, int]]
_VersionCmpLocalType0 = ta.Tuple[ta.Union[ta.Tuple[int, str], ta.Tuple['NegativeInfinityVersionType', ta.Union[int, str]]], ...]  # noqa
VersionCmpLocalType = ta.Union['NegativeInfinityVersionType', _VersionCmpLocalType0]
VersionCmpKey = ta.Tuple[int, ta.Tuple[int, ...], VersionCmpPrePostDevType, VersionCmpPrePostDevType, VersionCmpPrePostDevType, VersionCmpLocalType]  # noqa
VersionComparisonMethod = ta.Callable[[VersionCmpKey, VersionCmpKey], bool]

# ../../../omlish/lite/check.py
T = ta.TypeVar('T')

# ../../versioning/specifiers.py
UnparsedVersion = ta.Union['Version', str]
UnparsedVersionVar = ta.TypeVar('UnparsedVersionVar', bound=UnparsedVersion)
CallableVersionOperator = ta.Callable[['Version', str], bool]


########################################
# ../../cexts/magic.py


class CextMagic:
    MAGIC = '@omdev-cext'
    MAGIC_COMMENT = f'// {MAGIC}'

    FILE_EXTENSIONS = ('c', 'cc', 'cpp')


########################################
# ../../findmagic.py


def compile_magic_pat(m: str) -> re.Pattern:
    return re.compile('^' + re.escape(m) + r'($|(\s.*))')


def find_magic(
        roots: ta.Sequence[str],
        magics: ta.Sequence[str],
        exts: ta.Sequence[str],
        *,
        py: bool = False,
) -> ta.Iterator[str]:
    if isinstance(roots, str):
        raise TypeError(roots)
    if isinstance(magics, str):
        raise TypeError(magics)
    if isinstance(exts, str):
        raise TypeError(exts)

    if not magics:
        raise Exception('Must specify magics')
    if not exts:
        raise Exception('Must specify extensions')

    pats = [compile_magic_pat(m) for m in magics]

    for root in roots:
        for dp, dns, fns in os.walk(root):  # noqa
            for fn in fns:
                if not any(fn.endswith(f'.{x}') for x in exts):
                    continue

                fp = os.path.join(dp, fn)
                try:
                    with open(fp) as f:
                        src = f.read()
                except UnicodeDecodeError:
                    continue

                if not any(
                        any(pat.fullmatch(l) for pat in pats)
                        for l in src.splitlines()
                ):
                    continue

                if py:
                    if fn == '__init__.py':
                        out = dp.replace(os.sep, '.')
                    elif fn.endswith('.py'):
                        out = fp[:-3].replace(os.sep, '.')
                    else:
                        out = fp
                else:
                    out = fp
                yield out


########################################
# ../../git.py


def git_clone_subtree(
        *,
        base_dir: str,
        repo_url: str,
        repo_dir: str,
        branch: ta.Optional[str] = None,
        rev: ta.Optional[str] = None,
        repo_subtrees: ta.Sequence[str],
) -> None:
    if not bool(branch) ^ bool(rev):
        raise ValueError('must set branch or rev')

    if isinstance(repo_subtrees, str):
        raise TypeError(repo_subtrees)

    git_opts = [
        '-c', 'advice.detachedHead=false',
    ]

    subprocess.check_call(
        [
            'git',
            *git_opts,
            'clone',
            '-n',
            '--depth=1',
            '--filter=tree:0',
            *(['-b', branch] if branch else []),
            '--single-branch',
            repo_url,
            repo_dir,
        ],
        cwd=base_dir,
    )

    rd = os.path.join(base_dir, repo_dir)
    subprocess.check_call(
        [
            'git',
            *git_opts,
            'sparse-checkout',
            'set',
            '--no-cone',
            *repo_subtrees,
        ],
        cwd=rd,
    )

    subprocess.check_call(
        [
            'git',
            *git_opts,
            'checkout',
            *([rev] if rev else []),
        ],
        cwd=rd,
    )


def get_git_revision(
        *,
        cwd: ta.Optional[str] = None,
) -> ta.Optional[str]:
    subprocess.check_output(['git', '--version'])

    if cwd is None:
        cwd = os.getcwd()

    if subprocess.run([  # noqa
        'git',
        'rev-parse',
        '--is-inside-work-tree',
    ], stderr=subprocess.PIPE).returncode:
        return None

    has_untracked = bool(subprocess.check_output([
        'git',
        'ls-files',
        '.',
        '--exclude-standard',
        '--others',
    ], cwd=cwd).decode().strip())

    dirty_rev = subprocess.check_output([
        'git',
        'describe',
        '--match=NeVeRmAtCh',
        '--always',
        '--abbrev=40',
        '--dirty',
    ], cwd=cwd).decode().strip()

    return dirty_rev + ('-untracked' if has_untracked else '')


########################################
# ../../toml/parser.py
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
# https://github.com/python/cpython/blob/f5009b69e0cd94b990270e04e65b9d4d2b365844/Lib/tomllib/_parser.py


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
    src = s.replace('\r\n', '\n')
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
# ../../toml/writer.py


class TomlWriter:
    def __init__(self, out: ta.TextIO) -> None:
        super().__init__()
        self._out = out

        self._indent = 0
        self._wrote_indent = False

    #

    def _w(self, s: str) -> None:
        if not self._wrote_indent:
            self._out.write('    ' * self._indent)
            self._wrote_indent = True
        self._out.write(s)

    def _nl(self) -> None:
        self._out.write('\n')
        self._wrote_indent = False

    def _needs_quote(self, s: str) -> bool:
        return (
            not s or
            any(c in s for c in '\'"\n') or
            s[0] not in string.ascii_letters
        )

    def _maybe_quote(self, s: str) -> str:
        if self._needs_quote(s):
            return repr(s)
        else:
            return s

    #

    def write_root(self, obj: ta.Mapping) -> None:
        for i, (k, v) in enumerate(obj.items()):
            if i:
                self._nl()
            self._w('[')
            self._w(self._maybe_quote(k))
            self._w(']')
            self._nl()
            self.write_table_contents(v)

    def write_table_contents(self, obj: ta.Mapping) -> None:
        for k, v in obj.items():
            self.write_key(k)
            self._w(' = ')
            self.write_value(v)
            self._nl()

    def write_array(self, obj: ta.Sequence) -> None:
        self._w('[')
        self._nl()
        self._indent += 1
        for e in obj:
            self.write_value(e)
            self._w(',')
            self._nl()
        self._indent -= 1
        self._w(']')

    def write_inline_table(self, obj: ta.Mapping) -> None:
        self._w('{')
        for i, (k, v) in enumerate(obj.items()):
            if i:
                self._w(', ')
            self.write_key(k)
            self._w(' = ')
            self.write_value(v)
        self._w('}')

    def write_inline_array(self, obj: ta.Sequence) -> None:
        self._w('[')
        for i, e in enumerate(obj):
            if i:
                self._w(', ')
            self.write_value(e)
        self._w(']')

    def write_key(self, obj: ta.Any) -> None:
        if isinstance(obj, str):
            self._w(self._maybe_quote(obj.replace('_', '-')))
        elif isinstance(obj, int):
            self._w(repr(str(obj)))
        else:
            raise TypeError(obj)

    def write_value(self, obj: ta.Any) -> None:
        if isinstance(obj, bool):
            self._w(str(obj).lower())
        elif isinstance(obj, (str, int, float)):
            self._w(repr(obj))
        elif isinstance(obj, ta.Mapping):
            self.write_inline_table(obj)
        elif isinstance(obj, ta.Sequence):
            if not obj:
                self.write_inline_array(obj)
            else:
                self.write_array(obj)
        else:
            raise TypeError(obj)


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
# ../../wheelfile.py
# https://github.com/pypa/wheel/blob/7bb46d7727e6e89fe56b3c78297b3af2672bbbe2/src/wheel/wheelfile.py
# MIT License
#
# Copyright (c) 2012 Daniel Holth <dholth@fastmail.fm> and contributors
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
# documentation files (the "Software"), to deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit
# persons to whom the Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the
# Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
# WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
# COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
# OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.


class WheelError(Exception):
    pass


# Non-greedy matching of an optional build number may be too clever (more invalid wheel filenames will match). Separate
# regex for .dist-info?
WHEEL_INFO_RE = re.compile(
    r'^'
    r'(?P<namever>(?P<name>[^\s-]+?)-(?P<ver>[^\s-]+?))'
    r'(-(?P<build>\d[^\s-]*))?-'
    r'(?P<pyver>[^\s-]+?)-'
    r'(?P<abi>[^\s-]+?)-'
    r'(?P<plat>\S+)'
    r'\.whl$',
    re.VERBOSE,
)


class WheelFile(zipfile.ZipFile):
    """
    A ZipFile derivative class that also reads SHA-256 hashes from .dist-info/RECORD and checks any read files against
    those.
    """

    _default_algorithm = hashlib.sha256

    def __init__(
            self,
            file: str,
            mode: str = 'r',  # ta.Literal["r", "w", "x", "a"]
            compression: int = zipfile.ZIP_DEFLATED,
    ) -> None:
        basename = os.path.basename(file)
        self.parsed_filename = WHEEL_INFO_RE.match(basename)
        if not basename.endswith('.whl') or self.parsed_filename is None:
            raise WheelError(f'Bad wheel filename {basename!r}')

        super().__init__(  # type: ignore
            file,
            mode,
            compression=compression,
            allowZip64=True,
        )

        self.dist_info_path = '{}.dist-info'.format(self.parsed_filename.group('namever'))
        self.record_path = self.dist_info_path + '/RECORD'
        self._file_hashes: ta.Dict[str, ta.Union[ta.Tuple[None, None], ta.Tuple[int, bytes]]] = {}
        self._file_sizes: ta.Dict[str, int] = {}

        if mode == 'r':
            # Ignore RECORD and any embedded wheel signatures
            self._file_hashes[self.record_path] = None, None
            self._file_hashes[self.record_path + '.jws'] = None, None
            self._file_hashes[self.record_path + '.p7s'] = None, None

            # Fill in the expected hashes by reading them from RECORD
            try:
                record = self.open(self.record_path)
            except KeyError:
                raise WheelError(f'Missing {self.record_path} file') from None

            with record:
                for line in csv.reader(io.TextIOWrapper(record, newline='', encoding='utf-8')):
                    path, hash_sum, size = line
                    if not hash_sum:
                        continue

                    algorithm, hash_sum = hash_sum.split('=')
                    try:
                        hashlib.new(algorithm)
                    except ValueError:
                        raise WheelError(f'Unsupported hash algorithm: {algorithm}') from None

                    if algorithm.lower() in {'md5', 'sha1'}:
                        raise WheelError(f'Weak hash algorithm ({algorithm}) is not permitted by PEP 427')

                    self._file_hashes[path] = (  # type: ignore
                        algorithm,
                        self._urlsafe_b64decode(hash_sum.encode('ascii')),
                    )

    @staticmethod
    def _urlsafe_b64encode(data: bytes) -> bytes:
        """urlsafe_b64encode without padding"""
        return base64.urlsafe_b64encode(data).rstrip(b'=')

    @staticmethod
    def _urlsafe_b64decode(data: bytes) -> bytes:
        """urlsafe_b64decode without padding"""
        pad = b'=' * (4 - (len(data) & 3))
        return base64.urlsafe_b64decode(data + pad)

    def open(  # type: ignore  # noqa
            self,
            name_or_info: ta.Union[str, zipfile.ZipInfo],
            mode: str = 'r',  # ta.Literal["r", "w"]
            pwd: ta.Optional[bytes] = None,
    ) -> ta.IO[bytes]:
        def _update_crc(newdata: bytes) -> None:
            eof = ef._eof  # type: ignore  # noqa
            update_crc_orig(newdata)
            running_hash.update(newdata)
            if eof and running_hash.digest() != expected_hash:
                raise WheelError(f"Hash mismatch for file '{ef_name}'")

        ef_name = name_or_info.filename if isinstance(name_or_info, zipfile.ZipInfo) else name_or_info
        if (
                mode == 'r'
                and not ef_name.endswith('/')
                and ef_name not in self._file_hashes
        ):
            raise WheelError(f"No hash found for file '{ef_name}'")

        ef = super().open(name_or_info, mode, pwd)  # noqa
        if mode == 'r' and not ef_name.endswith('/'):
            algorithm, expected_hash = self._file_hashes[ef_name]
            if expected_hash is not None:
                # Monkey patch the _update_crc method to also check for the hash from RECORD
                running_hash = hashlib.new(algorithm)  # type: ignore
                update_crc_orig, ef._update_crc = ef._update_crc, _update_crc  # type: ignore  # noqa

        return ef

    def write_files(self, base_dir: str) -> None:
        deferred: list[tuple[str, str]] = []
        for root, dirnames, filenames in os.walk(base_dir):
            # Sort the directory names so that `os.walk` will walk them in a defined order on the next iteration.
            dirnames.sort()
            for name in sorted(filenames):
                path = os.path.normpath(os.path.join(root, name))
                if os.path.isfile(path):
                    arcname = os.path.relpath(path, base_dir).replace(os.path.sep, '/')
                    if arcname == self.record_path:
                        pass
                    elif root.endswith('.dist-info'):
                        deferred.append((path, arcname))
                    else:
                        self.write(path, arcname)

        deferred.sort()
        for path, arcname in deferred:
            self.write(path, arcname)

    def write(  # type: ignore  # noqa
            self,
            filename: str,
            arcname: ta.Optional[str] = None,
            compress_type: ta.Optional[int] = None,
    ) -> None:
        with open(filename, 'rb') as f:
            st = os.fstat(f.fileno())
            data = f.read()

        zinfo = zipfile.ZipInfo(
            arcname or filename,
            date_time=self._get_zipinfo_datetime(st.st_mtime),
        )
        zinfo.external_attr = (stat.S_IMODE(st.st_mode) | stat.S_IFMT(st.st_mode)) << 16
        zinfo.compress_type = compress_type or self.compression
        self.writestr(zinfo, data, compress_type)

    _MINIMUM_TIMESTAMP = 315532800  # 1980-01-01 00:00:00 UTC

    @classmethod
    def _get_zipinfo_datetime(cls, timestamp: ta.Optional[float] = None) -> ta.Any:
        # Some applications need reproducible .whl files, but they can't do this without forcing the timestamp of the
        # individual ZipInfo objects. See issue #143.
        timestamp = int(os.environ.get('SOURCE_DATE_EPOCH', timestamp or time.time()))
        timestamp = max(timestamp, cls._MINIMUM_TIMESTAMP)
        return time.gmtime(timestamp)[0:6]

    def writestr(  # type: ignore  # noqa
            self,
            zinfo_or_arcname: ta.Union[str, zipfile.ZipInfo],
            data: ta.Any,  # SizedBuffer | str,
            compress_type: ta.Optional[int] = None,
    ) -> None:
        if isinstance(zinfo_or_arcname, str):
            zinfo_or_arcname = zipfile.ZipInfo(
                zinfo_or_arcname,
                date_time=self._get_zipinfo_datetime(),
            )
            zinfo_or_arcname.compress_type = self.compression
            zinfo_or_arcname.external_attr = (0o664 | stat.S_IFREG) << 16

        if isinstance(data, str):
            data = data.encode('utf-8')

        super().writestr(zinfo_or_arcname, data, compress_type)
        fname = (
            zinfo_or_arcname.filename
            if isinstance(zinfo_or_arcname, zipfile.ZipInfo)
            else zinfo_or_arcname
        )
        if fname != self.record_path:
            hash_ = self._default_algorithm(data)  # type: ignore
            self._file_hashes[fname] = (  # type: ignore
                hash_.name,
                self._urlsafe_b64encode(hash_.digest()).decode('ascii'),
            )
            self._file_sizes[fname] = len(data)

    def close(self) -> None:
        # Write RECORD
        if self.fp is not None and self.mode == 'w' and self._file_hashes:
            data = io.StringIO()
            writer = csv.writer(data, delimiter=',', quotechar='"', lineterminator='\n')
            writer.writerows((
                (fname, algorithm + '=' + hash_, self._file_sizes[fname])  # type: ignore
                for fname, (algorithm, hash_) in self._file_hashes.items()
            ))
            writer.writerow((format(self.record_path), '', ''))
            self.writestr(self.record_path, data.getvalue())

        super().close()


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


def check_non_empty_str(v: ta.Optional[str]) -> str:
    if not v:
        raise ValueError
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
# ../reqs.py
"""
TODO:
 - embed pip._internal.req.parse_requirements, add additional env stuff? breaks compat with raw pip
"""


class RequirementsRewriter:
    def __init__(
            self,
            venv: ta.Optional[str] = None,
    ) -> None:
        super().__init__()
        self._venv = venv

    @cached_nullary
    def _tmp_dir(self) -> str:
        return tempfile.mkdtemp('-omlish-reqs')

    VENV_MAGIC = '# @omdev-venv'

    def rewrite_file(self, in_file: str) -> str:
        with open(in_file) as f:
            src = f.read()

        in_lines = src.splitlines(keepends=True)
        out_lines = []

        for l in in_lines:
            if self.VENV_MAGIC in l:
                lp, _, rp = l.partition(self.VENV_MAGIC)
                rp = rp.partition('#')[0]
                omit = False
                for v in rp.split():
                    if v[0] == '!':
                        if self._venv is not None and self._venv == v[1:]:
                            omit = True
                            break
                    else:
                        raise NotImplementedError

                if omit:
                    out_lines.append('# OMITTED:  ' + l)
                    continue

            out_req = self.rewrite(l.rstrip('\n'), for_file=True)
            out_lines.append(out_req + '\n')

        out_file = os.path.join(self._tmp_dir(), os.path.basename(in_file))
        if os.path.exists(out_file):
            raise Exception(f'file exists: {out_file}')

        with open(out_file, 'w') as f:
            f.write(''.join(out_lines))
        return out_file

    def rewrite(self, in_req: str, *, for_file: bool = False) -> str:
        if in_req.strip().startswith('-r'):
            l = in_req.strip()
            lp, _, rp = l.partition(' ')
            if lp == '-r':
                inc_in_file, _, rest = rp.partition(' ')
            else:
                inc_in_file, rest = lp[2:], rp

            inc_out_file = self.rewrite_file(inc_in_file)
            if for_file:
                return ' '.join(['-r ', inc_out_file, rest])
            else:
                return '-r' + inc_out_file

        else:
            return in_req


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
            t = ct.strftime("%Y-%m-%d %H:%M:%S")  # noqa
            return '%s.%03d' % (t, record.msecs)


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


def configure_standard_logging(
        level: ta.Union[int, str] = logging.INFO,
        *,
        json: bool = False,
        target: ta.Optional[logging.Logger] = None,
        force: bool = False,
) -> ta.Optional[StandardLogHandler]:
    logging._acquireLock()  # type: ignore  # noqa
    try:
        if target is None:
            target = logging.root

        #

        if not force:
            if any(isinstance(h, StandardLogHandler) for h in list(target.handlers)):
                return None

        #

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

    finally:
        logging._releaseLock()  # type: ignore  # noqa


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
        return self.ty(**{k: self.fs[k].unmarshal(v) for k, v in o.items() if self.nonstrict or k in self.fs})


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


_OBJ_MARSHALERS: ta.Dict[ta.Any, ObjMarshaler] = {
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


def register_opj_marshaler(ty: ta.Any, m: ObjMarshaler) -> None:
    if ty in _OBJ_MARSHALERS:
        raise KeyError(ty)
    _OBJ_MARSHALERS[ty] = m


def _make_obj_marshaler(ty: ta.Any) -> ObjMarshaler:
    if isinstance(ty, type) and abc.ABC in ty.__bases__:
        impls = [  # type: ignore
            PolymorphicObjMarshaler.Impl(
                ity,
                ity.__qualname__,
                get_obj_marshaler(ity),
            )
            for ity in deep_subclasses(ty)
            if abc.ABC not in ity.__bases__
        ]
        return PolymorphicObjMarshaler(
            {i.ty: i for i in impls},
            {i.tag: i for i in impls},
        )

    if isinstance(ty, type) and issubclass(ty, enum.Enum):
        return EnumObjMarshaler(ty)

    if dc.is_dataclass(ty):
        return DataclassObjMarshaler(
            ty,
            {f.name: get_obj_marshaler(f.type) for f in dc.fields(ty)},
        )

    if is_generic_alias(ty):
        try:
            mt = _OBJ_MARSHALER_GENERIC_MAPPING_TYPES[ta.get_origin(ty)]
        except KeyError:
            pass
        else:
            k, v = ta.get_args(ty)
            return MappingObjMarshaler(mt, get_obj_marshaler(k), get_obj_marshaler(v))

        try:
            st = _OBJ_MARSHALER_GENERIC_ITERABLE_TYPES[ta.get_origin(ty)]
        except KeyError:
            pass
        else:
            [e] = ta.get_args(ty)
            return IterableObjMarshaler(st, get_obj_marshaler(e))

        if is_union_alias(ty):
            return OptionalObjMarshaler(get_obj_marshaler(get_optional_alias_arg(ty)))

    raise TypeError(ty)


def get_obj_marshaler(ty: ta.Any) -> ObjMarshaler:
    try:
        return _OBJ_MARSHALERS[ty]
    except KeyError:
        pass

    p = ProxyObjMarshaler()
    _OBJ_MARSHALERS[ty] = p
    try:
        m = _make_obj_marshaler(ty)
    except Exception:
        del _OBJ_MARSHALERS[ty]
        raise
    else:
        p.m = m
        _OBJ_MARSHALERS[ty] = m
        return m


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
        raise OSError(
            f'Requires python {REQUIRED_PYTHON_VERSION}, got {sys.version_info} from {sys.executable}')  # noqa


########################################
# ../../interp/types.py


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

    def __contains__(self, iv: InterpVersion) -> bool:
        return self.contains(iv)


@dc.dataclass(frozen=True)
class Interp:
    exe: str
    version: InterpVersion


########################################
# ../configs.py


@dc.dataclass(frozen=True)
class VenvConfig:
    inherits: ta.Optional[ta.Sequence[str]] = None
    interp: ta.Optional[str] = None
    requires: ta.Optional[ta.List[str]] = None
    docker: ta.Optional[str] = None
    srcs: ta.Optional[ta.List[str]] = None
    use_uv: ta.Optional[bool] = None


@dc.dataclass(frozen=True)
class PyprojectConfig:
    pkgs: ta.Sequence[str] = dc.field(default_factory=list)
    srcs: ta.Mapping[str, ta.Sequence[str]] = dc.field(default_factory=dict)
    venvs: ta.Mapping[str, VenvConfig] = dc.field(default_factory=dict)

    venvs_dir: str = '.venvs'
    versions_file: ta.Optional[str] = '.versions'


class PyprojectConfigPreparer:
    def __init__(
            self,
            *,
            python_versions: ta.Optional[ta.Mapping[str, str]] = None,
    ) -> None:
        super().__init__()

        self._python_versions = python_versions or {}

    def _inherit_venvs(self, m: ta.Mapping[str, VenvConfig]) -> ta.Mapping[str, VenvConfig]:
        done: ta.Dict[str, VenvConfig] = {}

        def rec(k):
            try:
                return done[k]
            except KeyError:
                pass

            c = m[k]
            kw = dc.asdict(c)
            for i in c.inherits or ():
                ic = rec(i)
                kw.update({k: v for k, v in dc.asdict(ic).items() if v is not None and kw.get(k) is None})
            del kw['inherits']

            d = done[k] = VenvConfig(**kw)
            return d

        for k in m:
            rec(k)
        return done

    def _resolve_srcs(
            self,
            lst: ta.Sequence[str],
            aliases: ta.Mapping[str, ta.Sequence[str]],
    ) -> ta.List[str]:
        todo = list(reversed(lst))
        raw: ta.List[str] = []
        seen: ta.Set[str] = set()

        while todo:
            cur = todo.pop()
            if cur in seen:
                continue

            seen.add(cur)
            if not cur.startswith('@'):
                raw.append(cur)
                continue

            todo.extend(aliases[cur[1:]][::-1])

        return raw

    def _fixup_interp(self, s: ta.Optional[str]) -> ta.Optional[str]:
        if not s or not s.startswith('@'):
            return s
        return self._python_versions[s[1:]]

    def prepare_config(self, dct: ta.Mapping[str, ta.Any]) -> PyprojectConfig:
        pcfg: PyprojectConfig = unmarshal_obj(dct, PyprojectConfig)

        ivs = dict(self._inherit_venvs(pcfg.venvs or {}))
        for k, v in ivs.items():
            v = dc.replace(v, srcs=self._resolve_srcs(v.srcs or [], pcfg.srcs or {}))
            v = dc.replace(v, interp=self._fixup_interp(v.interp))
            ivs[k] = v

        pcfg = dc.replace(pcfg, venvs=ivs)
        return pcfg


########################################
# ../../revisions.py
"""
TODO:
 - omlish-lite, move to pyproject/
  - vendor-lite wheel.wheelfile
"""


##


class GitRevisionAdder:
    def __init__(
            self,
            revision: ta.Optional[str] = None,
            output_suffix: ta.Optional[str] = None,
    ) -> None:
        super().__init__()
        self._given_revision = revision
        self._output_suffix = output_suffix

    @cached_nullary
    def revision(self) -> str:
        if self._given_revision is not None:
            return self._given_revision
        return check_non_empty_str(get_git_revision())

    REVISION_ATTR = '__revision__'

    def add_to_contents(self, dct: ta.Dict[str, bytes]) -> bool:
        changed = False
        for n in dct:
            if not n.endswith('__about__.py'):
                continue
            src = dct[n].decode('utf-8')
            lines = src.splitlines(keepends=True)
            for i, l in enumerate(lines):
                if l != f'{self.REVISION_ATTR} = None\n':
                    continue
                lines[i] = f"{self.REVISION_ATTR} = '{self.revision()}'\n"
                changed = True
            dct[n] = ''.join(lines).encode('utf-8')
        return changed

    def add_to_wheel(self, f: str) -> None:
        if not f.endswith('.whl'):
            raise Exception(f)
        log.info('Scanning wheel %s', f)

        zis: ta.Dict[str, zipfile.ZipInfo] = {}
        dct: ta.Dict[str, bytes] = {}
        with WheelFile(f) as wf:
            for zi in wf.filelist:
                if zi.filename == wf.record_path:
                    continue
                zis[zi.filename] = zi
                dct[zi.filename] = wf.read(zi.filename)

        if self.add_to_contents(dct):
            of = f[:-4] + (self._output_suffix or '') + '.whl'
            log.info('Repacking wheel %s', of)
            with WheelFile(of, 'w') as wf:
                for n, d in dct.items():
                    log.info('Adding zipinfo %s', n)
                    wf.writestr(zis[n], d)

    def add_to_tgz(self, f: str) -> None:
        if not f.endswith('.tar.gz'):
            raise Exception(f)
        log.info('Scanning tgz %s', f)

        tis: ta.Dict[str, tarfile.TarInfo] = {}
        dct: ta.Dict[str, bytes] = {}
        with tarfile.open(f, 'r:gz') as tf:
            for ti in tf:
                tis[ti.name] = ti
                if ti.type == tarfile.REGTYPE:
                    with tf.extractfile(ti.name) as tif:  # type: ignore
                        dct[ti.name] = tif.read()

        if self.add_to_contents(dct):
            of = f[:-7] + (self._output_suffix or '') + '.tar.gz'
            log.info('Repacking tgz %s', of)
            with tarfile.open(of, 'w:gz') as tf:
                for n, ti in tis.items():
                    log.info('Adding tarinfo %s', n)
                    if n in dct:
                        data = dct[n]
                        ti.size = len(data)
                        fo = io.BytesIO(data)
                    else:
                        fo = None
                    tf.addfile(ti, fileobj=fo)

    EXTS = ('.tar.gz', '.whl')

    def add_to_file(self, f: str) -> None:
        if f.endswith('.whl'):
            self.add_to_wheel(f)

        elif f.endswith('.tar.gz'):
            self.add_to_tgz(f)

    def add_to(self, tgt: str) -> None:
        log.info('Using revision %s', self.revision())

        if os.path.isfile(tgt):
            self.add_to_file(tgt)

        elif os.path.isdir(tgt):
            for dp, dns, fns in os.walk(tgt):  # noqa
                for f in fns:
                    if any(f.endswith(ext) for ext in self.EXTS):
                        self.add_to_file(os.path.join(dp, f))


#


########################################
# ../../../omlish/lite/subprocesses.py


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
# ../../interp/inspect.py


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
# ../pkg.py
"""
TODO:
 - ext scanning
 - __revision__
 - entry_points

** NOTE **
setuptools now (2024/09/02) has experimental support for extensions in pure pyproject.toml - but we still want a
separate '-cext' package
  https://setuptools.pypa.io/en/latest/userguide/ext_modules.html
  https://github.com/pypa/setuptools/commit/1a9d87308dc0d8aabeaae0dce989b35dfb7699f0#diff-61d113525e9cc93565799a4bb8b34a68e2945b8a3f7d90c81380614a4ea39542R7-R8

--

https://setuptools.pypa.io/en/latest/references/keywords.html
https://packaging.python.org/en/latest/specifications/pyproject-toml

How to build a C extension in keeping with PEP 517, i.e. with pyproject.toml instead of setup.py?
https://stackoverflow.com/a/66479252

https://github.com/pypa/sampleproject/blob/db5806e0a3204034c51b1c00dde7d5eb3fa2532e/setup.py

https://pip.pypa.io/en/stable/cli/pip_install/#vcs-support
vcs+protocol://repo_url/#egg=pkg&subdirectory=pkg_dir
'git+https://github.com/wrmsr/omlish@master#subdirectory=.pip/omlish'
"""  # noqa


#


class BasePyprojectPackageGenerator(abc.ABC):
    def __init__(
            self,
            dir_name: str,
            pkgs_root: str,
            *,
            pkg_suffix: str = '',
    ) -> None:
        super().__init__()
        self._dir_name = dir_name
        self._pkgs_root = pkgs_root
        self._pkg_suffix = pkg_suffix

    #

    @cached_nullary
    def about(self) -> types.ModuleType:
        return importlib.import_module(f'{self._dir_name}.__about__')

    #

    @cached_nullary
    def _pkg_dir(self) -> str:
        pkg_dir: str = os.path.join(self._pkgs_root, self._dir_name + self._pkg_suffix)
        if os.path.isdir(pkg_dir):
            shutil.rmtree(pkg_dir)
        os.makedirs(pkg_dir)
        return pkg_dir

    #

    _GIT_IGNORE: ta.Sequence[str] = [
        '/*.egg-info/',
        '/dist',
    ]

    def _write_git_ignore(self) -> None:
        with open(os.path.join(self._pkg_dir(), '.gitignore'), 'w') as f:
            f.write('\n'.join(self._GIT_IGNORE))

    #

    def _symlink_source_dir(self) -> None:
        os.symlink(
            os.path.relpath(self._dir_name, self._pkg_dir()),
            os.path.join(self._pkg_dir(), self._dir_name),
        )

    #

    @cached_nullary
    def project_cls(self) -> type:
        return self.about().Project

    @cached_nullary
    def setuptools_cls(self) -> type:
        return self.about().Setuptools

    @staticmethod
    def _build_cls_dct(cls: type) -> ta.Dict[str, ta.Any]:  # noqa
        dct = {}
        for b in reversed(cls.__mro__):
            for k, v in b.__dict__.items():
                if k.startswith('_'):
                    continue
                dct[k] = v
        return dct

    @staticmethod
    def _move_dict_key(
            sd: ta.Dict[str, ta.Any],
            sk: str,
            dd: ta.Dict[str, ta.Any],
            dk: str,
    ) -> None:
        if sk in sd:
            dd[dk] = sd.pop(sk)

    @dc.dataclass(frozen=True)
    class Specs:
        pyproject: ta.Dict[str, ta.Any]
        setuptools: ta.Dict[str, ta.Any]

    def build_specs(self) -> Specs:
        return self.Specs(
            self._build_cls_dct(self.project_cls()),
            self._build_cls_dct(self.setuptools_cls()),
        )

    #

    class _PkgData(ta.NamedTuple):
        inc: ta.List[str]
        exc: ta.List[str]

    @cached_nullary
    def _collect_pkg_data(self) -> _PkgData:
        inc: ta.List[str] = []
        exc: ta.List[str] = []

        for p, ds, fs in os.walk(self._dir_name):  # noqa
            for f in fs:
                if f != '.pkgdata':
                    continue
                rp = os.path.relpath(p, self._dir_name)
                log.info('Found pkgdata %s for pkg %s', rp, self._dir_name)
                with open(os.path.join(p, f)) as fo:
                    src = fo.read()
                for l in src.splitlines():
                    if not (l := l.strip()):
                        continue
                    if l.startswith('!'):
                        exc.append(os.path.join(rp, l[1:]))
                    else:
                        inc.append(os.path.join(rp, l))

        return self._PkgData(inc, exc)

    #

    @abc.abstractmethod
    def _write_file_contents(self) -> None:
        raise NotImplementedError

    #

    _STANDARD_FILES: ta.Sequence[str] = [
        'LICENSE',
        'README.rst',
    ]

    def _symlink_standard_files(self) -> None:
        for fn in self._STANDARD_FILES:
            if os.path.exists(fn):
                os.symlink(os.path.relpath(fn, self._pkg_dir()), os.path.join(self._pkg_dir(), fn))

    #

    def _run_build(
            self,
            build_output_dir: ta.Optional[str] = None,
            *,
            add_revision: bool = False,
            test: bool = False,
    ) -> None:
        subprocess_check_call(
            sys.executable,
            '-m',
            'build',
            cwd=self._pkg_dir(),
        )

        dist_dir = os.path.join(self._pkg_dir(), 'dist')

        if add_revision:
            GitRevisionAdder().add_to(dist_dir)

        if test:
            for fn in os.listdir(dist_dir):
                tmp_dir = tempfile.mkdtemp()

                subprocess_check_call(
                    sys.executable,
                    '-m', 'venv',
                    'test-install',
                    cwd=tmp_dir,
                )

                subprocess_check_call(
                    os.path.join(tmp_dir, 'test-install', 'bin', 'python3'),
                    '-m', 'pip',
                    'install',
                    os.path.abspath(os.path.join(dist_dir, fn)),
                    cwd=tmp_dir,
                )

        if build_output_dir is not None:
            for fn in os.listdir(dist_dir):
                shutil.copyfile(os.path.join(dist_dir, fn), os.path.join(build_output_dir, fn))

    #

    @dc.dataclass(frozen=True)
    class GenOpts:
        run_build: bool = False
        build_output_dir: ta.Optional[str] = None
        add_revision: bool = False

    def gen(self, opts: GenOpts = GenOpts()) -> str:
        log.info('Generating pyproject package: %s -> %s (%s)', self._dir_name, self._pkgs_root, self._pkg_suffix)

        self._pkg_dir()
        self._write_git_ignore()
        self._symlink_source_dir()
        self._write_file_contents()
        self._symlink_standard_files()

        if opts.run_build:
            self._run_build(
                opts.build_output_dir,
                add_revision=opts.add_revision,
            )

        return self._pkg_dir()


#


class PyprojectPackageGenerator(BasePyprojectPackageGenerator):

    #

    @dc.dataclass(frozen=True)
    class FileContents:
        pyproject_dct: ta.Mapping[str, ta.Any]
        manifest_in: ta.Optional[ta.Sequence[str]]

    @cached_nullary
    def file_contents(self) -> FileContents:
        specs = self.build_specs()

        #

        pyp_dct = {}

        pyp_dct['build-system'] = {
            'requires': ['setuptools'],
            'build-backend': 'setuptools.build_meta',
        }

        prj = specs.pyproject
        prj['name'] += self._pkg_suffix

        pyp_dct['project'] = prj

        self._move_dict_key(prj, 'optional_dependencies', pyp_dct, extrask := 'project.optional-dependencies')
        if (extras := pyp_dct.get(extrask)):
            pyp_dct[extrask] = {
                'all': [
                    e
                    for lst in extras.values()
                    for e in lst
                ],
                **extras,
            }

        #

        st = dict(specs.setuptools)
        pyp_dct['tool.setuptools'] = st

        st.pop('cexts', None)

        #

        # TODO: default
        # find_packages = {
        #     'include': [Project.name, f'{Project.name}.*'],
        #     'exclude': [*SetuptoolsBase.find_packages['exclude']],
        # }

        fp = dict(st.pop('find_packages', {}))

        pyp_dct['tool.setuptools.packages.find'] = fp

        #

        # TODO: default
        # package_data = {
        #     '*': [
        #         '*.c',
        #         '*.cc',
        #         '*.h',
        #         '.manifests.json',
        #         'LICENSE',
        #     ],
        # }

        pd = dict(st.pop('package_data', {}))
        epd = dict(st.pop('exclude_package_data', {}))

        cpd = self._collect_pkg_data()
        if cpd.inc:
            pd['*'] = [*pd.get('*', []), *sorted(set(cpd.inc))]
        if cpd.exc:
            epd['*'] = [*epd.get('*', []), *sorted(set(cpd.exc))]

        if pd:
            pyp_dct['tool.setuptools.package-data'] = pd
        if epd:
            pyp_dct['tool.setuptools.exclude-package-data'] = epd

        #

        # TODO: default
        # manifest_in = [
        #     'global-exclude **/conftest.py',
        # ]

        mani_in = st.pop('manifest_in', None)

        #

        return self.FileContents(
            pyp_dct,
            mani_in,
        )

    def _write_file_contents(self) -> None:
        fc = self.file_contents()

        with open(os.path.join(self._pkg_dir(), 'pyproject.toml'), 'w') as f:
            TomlWriter(f).write_root(fc.pyproject_dct)

        if fc.manifest_in:
            with open(os.path.join(self._pkg_dir(), 'MANIFEST.in'), 'w') as f:
                f.write('\n'.join(fc.manifest_in))  # noqa

    #

    def gen(self, opts: BasePyprojectPackageGenerator.GenOpts = BasePyprojectPackageGenerator.GenOpts()) -> str:
        ret = super().gen(opts)

        if self.build_specs().setuptools.get('cexts'):
            _PyprojectCextPackageGenerator(
                self._dir_name,
                self._pkgs_root,
                pkg_suffix='-cext',
            ).gen(opts)

        return ret


#


class _PyprojectCextPackageGenerator(BasePyprojectPackageGenerator):

    #

    @cached_nullary
    def find_cext_srcs(self) -> ta.Sequence[str]:
        return sorted(find_magic(
            [self._dir_name],
            [CextMagic.MAGIC_COMMENT],
            CextMagic.FILE_EXTENSIONS,
        ))

    #

    @dc.dataclass(frozen=True)
    class FileContents:
        pyproject_dct: ta.Mapping[str, ta.Any]
        setup_py: str

    @cached_nullary
    def file_contents(self) -> FileContents:
        specs = self.build_specs()

        #

        pyp_dct = {}

        pyp_dct['build-system'] = {
            'requires': ['setuptools'],
            'build-backend': 'setuptools.build_meta',
        }

        prj = specs.pyproject
        prj['dependencies'] = [f'{prj["name"]} == {prj["version"]}']
        prj['name'] += self._pkg_suffix
        prj.pop('optional_dependencies', None)

        pyp_dct['project'] = prj

        #

        st = dict(specs.setuptools)
        pyp_dct['tool.setuptools'] = st

        for k in [
            'cexts',

            'find_packages',
            'package_data',
            'manifest_in',
        ]:
            st.pop(k, None)

        pyp_dct['tool.setuptools.packages.find'] = {
            'include': [],
        }

        #

        ext_lines = []

        for ext_src in self.find_cext_srcs():
            ext_name = ext_src.rpartition('.')[0].replace(os.sep, '.')
            ext_lines.extend([
                'st.Extension(',
                f"    name='{ext_name}',",
                f"    sources=['{ext_src}'],",
                "    extra_compile_args=['-std=c++20'],",
                '),',
            ])

        src = '\n'.join([
            'import setuptools as st',
            '',
            '',
            'st.setup(',
            '    ext_modules=[',
            *['        ' + l for l in ext_lines],
            '    ]',
            ')',
            '',
        ])

        #

        return self.FileContents(
            pyp_dct,
            src,
        )

    def _write_file_contents(self) -> None:
        fc = self.file_contents()

        with open(os.path.join(self._pkg_dir(), 'pyproject.toml'), 'w') as f:
            TomlWriter(f).write_root(fc.pyproject_dct)

        with open(os.path.join(self._pkg_dir(), 'setup.py'), 'w') as f:
            f.write(fc.setup_py)


########################################
# ../../interp/providers.py
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
# ../../interp/pyenv.py
"""
TODO:
 - custom tags
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

    def update(self) -> bool:
        if (root := self.root()) is None:
            return False
        if not os.path.isdir(os.path.join(root, '.git')):
            return False
        subprocess_check_call('git', 'pull', cwd=root)
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


DEFAULT_PYENV_INSTALL_OPTS = PyenvInstallOpts(opts=['-s', '-v'])
DEBUG_PYENV_INSTALL_OPTS = PyenvInstallOpts(opts=['-g'])
THREADED_PYENV_INSTALL_OPTS = PyenvInstallOpts(conf_opts=['--disable-gil'])


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

    # @cached_nullary
    # def brew_ssl_opts(self) -> PyenvInstallOpts:
    #     pkg_config_path = subprocess_check_output_str('brew', '--prefix', 'openssl')
    #     if 'PKG_CONFIG_PATH' in os.environ:
    #         pkg_config_path += ':' + os.environ['PKG_CONFIG_PATH']
    #     return PyenvInstallOpts(env={'PKG_CONFIG_PATH': pkg_config_path})

    def opts(self) -> PyenvInstallOpts:
        return PyenvInstallOpts().merge(
            self.framework_opts(),
            self.brew_deps_opts(),
            self.brew_tcl_opts(),
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
            no_default_opts: bool = False,
            pyenv: Pyenv = Pyenv(),
    ) -> None:
        super().__init__()

        if no_default_opts:
            if opts is None:
                opts = PyenvInstallOpts()
        else:
            lst = [opts if opts is not None else DEFAULT_PYENV_INSTALL_OPTS]
            if interp_opts.debug:
                lst.append(DEBUG_PYENV_INSTALL_OPTS)
            if interp_opts.threaded:
                lst.append(THREADED_PYENV_INSTALL_OPTS)
            lst.append(PLATFORM_PYENV_INSTALL_OPTS[sys.platform].opts())
            opts = PyenvInstallOpts().merge(*lst)

        self._version = version
        self._opts = opts
        self._interp_opts = interp_opts

        self._no_default_opts = no_default_opts
        self._pyenv = pyenv

    @property
    def version(self) -> str:
        return self._version

    @property
    def opts(self) -> PyenvInstallOpts:
        return self._opts

    @cached_nullary
    def install_name(self) -> str:
        return self._version + ('-debug' if self._interp_opts.debug else '')

    @cached_nullary
    def install_dir(self) -> str:
        return str(os.path.join(check_not_none(self._pyenv.root()), 'versions', self.install_name()))

    @cached_nullary
    def install(self) -> str:
        env = {**os.environ, **self._opts.env}
        for k, l in [
            ('CFLAGS', self._opts.cflags),
            ('LDFLAGS', self._opts.ldflags),
            ('PYTHON_CONFIGURE_OPTS', self._opts.conf_opts),
        ]:
            v = ' '.join(l)
            if k in os.environ:
                v += ' ' + os.environ[k]
            env[k] = v

        subprocess_check_call(
            self._pyenv.exe(),
            'install',
            *self._opts.opts,
            self._version,
            env=env,
        )

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

    def _get_installable_versions(self, spec: InterpSpecifier) -> ta.Sequence[InterpVersion]:
        lst = []

        for vs in self._pyenv.installable_versions():
            if (iv := self.guess_version(vs)) is None:
                continue
            if iv.opts.debug:
                raise Exception('Pyenv installable versions not expected to have debug suffix')
            for d in [False, True]:
                lst.append(dc.replace(iv, opts=dc.replace(iv.opts, debug=d)))

        return lst

    def get_installable_versions(self, spec: InterpSpecifier) -> ta.Sequence[InterpVersion]:
        lst = self._get_installable_versions(spec)

        if self._try_update and not any(v in spec for v in lst):
            if self._pyenv.update():
                lst = self._get_installable_versions(spec)

        return lst

    def install_version(self, version: InterpVersion) -> Interp:
        inst_version = str(version.version)
        inst_opts = version.opts
        if inst_opts.threaded:
            inst_version += 't'
            inst_opts = dc.replace(inst_opts, threaded=False)

        installer = PyenvVersionInstaller(
            inst_version,
            interp_opts=inst_opts,
        )

        exe = installer.install()
        return Interp(exe, version)


########################################
# ../../interp/system.py
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
# ../../interp/resolvers.py


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

    def _resolve_installed(self, spec: InterpSpecifier) -> ta.Optional[ta.Tuple[InterpProvider, InterpVersion]]:
        lst = [
            (i, si)
            for i, p in enumerate(self._providers.values())
            for si in p.get_installed_versions(spec)
            if spec.contains(si)
        ]

        slst = sorted(lst, key=lambda t: (-t[0], t[1]))
        if not slst:
            return None

        bi, bv = slst[-1]
        bp = list(self._providers.values())[bi]
        return (bp, bv)

    def resolve(
            self,
            spec: InterpSpecifier,
            *,
            install: bool = False,
    ) -> ta.Optional[Interp]:
        tup = self._resolve_installed(spec)
        if tup is not None:
            bp, bv = tup
            return bp.get_installed_version(bv)

        if not install:
            return None

        tp = list(self._providers.values())[0]  # noqa

        sv = sorted(
            [s for s in tp.get_installable_versions(spec) if s in spec],
            key=lambda s: s.version,
        )
        if not sv:
            return None

        bv = sv[-1]
        return tp.install_version(bv)

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
    PyenvInterpProvider(try_update=True),

    RunningInterpProvider(),

    SystemInterpProvider(),
]])


########################################
# cli.py


##


@dc.dataclass(frozen=True)
class VersionsFile:
    name: ta.Optional[str] = '.versions'

    @staticmethod
    def parse(s: str) -> ta.Mapping[str, str]:
        return {
            k: v
            for l in s.splitlines()
            if (sl := l.split('#')[0].strip())
            for k, _, v in (sl.partition('='),)
        }

    @cached_nullary
    def contents(self) -> ta.Mapping[str, str]:
        if not self.name or not os.path.exists(self.name):
            return {}
        with open(self.name) as f:
            s = f.read()
        return self.parse(s)

    @staticmethod
    def get_pythons(d: ta.Mapping[str, str]) -> ta.Mapping[str, str]:
        pfx = 'PYTHON_'
        return {k[len(pfx):].lower(): v for k, v in d.items() if k.startswith(pfx)}

    @cached_nullary
    def pythons(self) -> ta.Mapping[str, str]:
        return self.get_pythons(self.contents())


##


@cached_nullary
def _script_rel_path() -> str:
    cwd = os.getcwd()
    if not (f := __file__).startswith(cwd):
        raise OSError(f'file {f} not in {cwd}')
    return f[len(cwd):].lstrip(os.sep)


##


class Venv:
    def __init__(
            self,
            name: str,
            cfg: VenvConfig,
    ) -> None:
        super().__init__()
        self._name = name
        self._cfg = cfg

    @property
    def cfg(self) -> VenvConfig:
        return self._cfg

    DIR_NAME = '.venvs'

    @property
    def dir_name(self) -> str:
        return os.path.join(self.DIR_NAME, self._name)

    @cached_nullary
    def interp_exe(self) -> str:
        i = InterpSpecifier.parse(check_not_none(self._cfg.interp))
        return check_not_none(DEFAULT_INTERP_RESOLVER.resolve(i, install=True)).exe

    @cached_nullary
    def exe(self) -> str:
        ve = os.path.join(self.dir_name, 'bin/python')
        if not os.path.isfile(ve):
            raise Exception(f'venv exe {ve} does not exist or is not a file!')
        return ve

    @cached_nullary
    def create(self) -> bool:
        if os.path.exists(dn := self.dir_name):
            if not os.path.isdir(dn):
                raise Exception(f'{dn} exists but is not a directory!')
            return False

        log.info('Using interpreter %s', (ie := self.interp_exe()))
        subprocess_check_call(ie, '-m', 'venv', dn)

        ve = self.exe()
        uv = self._cfg.use_uv

        subprocess_check_call(
            ve,
            '-m', 'pip',
            'install', '-v', '--upgrade',
            'pip',
            'setuptools',
            'wheel',
            *(['uv'] if uv else []),
        )

        if (sr := self._cfg.requires):
            rr = RequirementsRewriter(self._name)
            reqs = [rr.rewrite(req) for req in sr]
            subprocess_check_call(
                ve,
                '-m',
                *(['uv'] if uv else []),
                'pip',
                'install',
                *([] if uv else ['-v']),
                *reqs,
            )

        return True

    @staticmethod
    def _resolve_srcs(raw: ta.List[str]) -> ta.List[str]:
        out: list[str] = []
        seen: ta.Set[str] = set()
        for r in raw:
            es: list[str]
            if any(c in r for c in '*?'):
                es = list(glob.glob(r, recursive=True))
            else:
                es = [r]
            for e in es:
                if e not in seen:
                    seen.add(e)
                    out.append(e)
        return out

    @cached_nullary
    def srcs(self) -> ta.Sequence[str]:
        return self._resolve_srcs(self._cfg.srcs or [])


##


class Run:
    def __init__(
            self,
            *,
            raw_cfg: ta.Union[ta.Mapping[str, ta.Any], str, None] = None,
    ) -> None:
        super().__init__()

        self._raw_cfg = raw_cfg

    @cached_nullary
    def raw_cfg(self) -> ta.Mapping[str, ta.Any]:
        if self._raw_cfg is None:
            with open('pyproject.toml') as f:
                buf = f.read()
        elif isinstance(self._raw_cfg, str):
            buf = self._raw_cfg
        else:
            return self._raw_cfg
        return toml_loads(buf)

    @cached_nullary
    def cfg(self) -> PyprojectConfig:
        dct = self.raw_cfg()['tool']['omlish']['pyproject']
        return PyprojectConfigPreparer(
            python_versions=VersionsFile().pythons(),
        ).prepare_config(dct)

    @cached_nullary
    def venvs(self) -> ta.Mapping[str, Venv]:
        return {
            n: Venv(n, c)
            for n, c in self.cfg().venvs.items()
            if not n.startswith('_')
        }


##


def _venv_cmd(args) -> None:
    venv = Run().venvs()[args.name]
    if (sd := venv.cfg.docker) is not None and sd != (cd := args._docker_container):  # noqa
        script = ' '.join([
            'python3',
            shlex.quote(_script_rel_path()),
            f'--_docker_container={shlex.quote(sd)}',
            *map(shlex.quote, sys.argv[1:]),
        ])

        docker_env = {
            'DOCKER_HOST_PLATFORM': os.environ.get('DOCKER_HOST_PLATFORM', sys.platform),
        }
        for e in args.docker_env or []:
            if '=' in e:
                k, _, v = e.split('=')
                docker_env[k] = v
            else:
                docker_env[e] = os.environ.get(e, '')

        subprocess_check_call(
            'docker',
            'compose',
            '-f', 'docker/compose.yml',
            'exec',
            *itertools.chain.from_iterable(
                ('-e', f'{k}={v}')
                for k, v in docker_env.items()
            ),
            '-it', sd,
            'bash', '--login', '-c', script,
        )

        return

    cmd = args.cmd
    if not cmd:
        venv.create()

    elif cmd == 'python':
        venv.create()
        os.execl(
            (exe := venv.exe()),
            exe,
            *args.args,
        )

    elif cmd == 'exe':
        venv.create()
        check_not(args.args)
        print(venv.exe())

    elif cmd == 'run':
        venv.create()
        sh = check_not_none(shutil.which('bash'))
        script = ' '.join(args.args)
        if not script:
            script = sh
        os.execl(
            (bash := check_not_none(sh)),
            bash,
            '-c',
            f'. {venv.dir_name}/bin/activate && ' + script,
        )

    elif cmd == 'srcs':
        check_not(args.args)
        print('\n'.join(venv.srcs()))

    elif cmd == 'test':
        venv.create()
        subprocess_check_call(venv.exe(), '-m', 'pytest', *(args.args or []), *venv.srcs())

    else:
        raise Exception(f'unknown subcommand: {cmd}')


##


def _pkg_cmd(args) -> None:
    run = Run()

    cmd = args.cmd
    if not cmd:
        raise Exception('must specify command')

    elif cmd == 'gen':
        pkgs_root = os.path.join('.pkg')

        if os.path.exists(pkgs_root):
            shutil.rmtree(pkgs_root)

        build_output_dir = 'dist'
        run_build = bool(args.build)
        add_revision = bool(args.revision)

        if run_build:
            os.makedirs(build_output_dir, exist_ok=True)

        num_threads = max(mp.cpu_count() // 2, 1)
        with cf.ThreadPoolExecutor(num_threads) as ex:
            futs = [
                ex.submit(functools.partial(
                    PyprojectPackageGenerator(
                        dir_name,
                        pkgs_root,
                    ).gen,
                    PyprojectPackageGenerator.GenOpts(
                        run_build=run_build,
                        build_output_dir=build_output_dir,
                        add_revision=add_revision,
                    ),
                ))
                for dir_name in run.cfg().pkgs
            ]
            for fut in futs:
                fut.result()

    else:
        raise Exception(f'unknown subcommand: {cmd}')


##


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument('--_docker_container', help=argparse.SUPPRESS)

    subparsers = parser.add_subparsers()

    parser_resolve = subparsers.add_parser('venv')
    parser_resolve.add_argument('name')
    parser_resolve.add_argument('-e', '--docker-env', action='append')
    parser_resolve.add_argument('cmd', nargs='?')
    parser_resolve.add_argument('args', nargs=argparse.REMAINDER)
    parser_resolve.set_defaults(func=_venv_cmd)

    parser_resolve = subparsers.add_parser('pkg')
    parser_resolve.add_argument('-b', '--build', action='store_true')
    parser_resolve.add_argument('-r', '--revision', action='store_true')
    parser_resolve.add_argument('cmd', nargs='?')
    parser_resolve.add_argument('args', nargs=argparse.REMAINDER)
    parser_resolve.set_defaults(func=_pkg_cmd)

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
