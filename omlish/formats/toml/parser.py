# ruff: noqa: UP006 UP007
# @omlish-lite
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
import datetime
import functools
import re
import string
import types
import typing as ta


TomlParseFloat = ta.Callable[[str], ta.Any]
TomlKey = ta.Tuple[str, ...]
TomlPos = int  # ta.TypeAlias


##


@functools.lru_cache()  # noqa
def toml_cached_tz(hour_str: str, minute_str: str, sign_str: str) -> datetime.timezone:
    sign = 1 if sign_str == '+' else -1
    return datetime.timezone(
        datetime.timedelta(
            hours=sign * int(hour_str),
            minutes=sign * int(minute_str),
        ),
    )


def toml_make_safe_parse_float(parse_float: TomlParseFloat) -> TomlParseFloat:
    """
    A decorator to make `parse_float` safe.

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

    parse_float = toml_make_safe_parse_float(parse_float)

    parser = TomlParser(
        src,
        parse_float=parse_float,
    )

    return parser.parse()


class TomlFlags:
    """Flags that map to parsed keys/namespaces."""

    # Marks an immutable namespace (inline array or inline table).
    FROZEN = 0
    # Marks a nest that has been explicitly created and can no longer be opened using the "[table]" syntax.
    EXPLICIT_NEST = 1

    def __init__(self) -> None:
        super().__init__()

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
        super().__init__()

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


class TomlParser:
    def __init__(
            self,
            src: str,
            *,
            parse_float: TomlParseFloat = float,
    ) -> None:
        super().__init__()

        self.src = src

        self.parse_float = parse_float

        self.data = TomlNestedDict()
        self.flags = TomlFlags()
        self.pos = 0

    ASCII_CTRL = frozenset(chr(i) for i in range(32)) | frozenset(chr(127))

    # Neither of these sets include quotation mark or backslash. They are currently handled as separate cases in the
    # parser functions.
    ILLEGAL_BASIC_STR_CHARS = ASCII_CTRL - frozenset('\t')
    ILLEGAL_MULTILINE_BASIC_STR_CHARS = ASCII_CTRL - frozenset('\t\n')

    ILLEGAL_LITERAL_STR_CHARS = ILLEGAL_BASIC_STR_CHARS
    ILLEGAL_MULTILINE_LITERAL_STR_CHARS = ILLEGAL_MULTILINE_BASIC_STR_CHARS

    ILLEGAL_COMMENT_CHARS = ILLEGAL_BASIC_STR_CHARS

    WS = frozenset(' \t')
    WS_AND_NEWLINE = WS | frozenset('\n')
    BARE_KEY_CHARS = frozenset(string.ascii_letters + string.digits + '-_')
    KEY_INITIAL_CHARS = BARE_KEY_CHARS | frozenset("\"'")
    HEXDIGIT_CHARS = frozenset(string.hexdigits)

    BASIC_STR_ESCAPE_REPLACEMENTS = types.MappingProxyType({
        '\\b': '\u0008',  # backspace
        '\\t': '\u0009',  # tab
        '\\n': '\u000A',  # linefeed
        '\\f': '\u000C',  # form feed
        '\\r': '\u000D',  # carriage return
        '\\"': '\u0022',  # quote
        '\\\\': '\u005C',  # backslash
    })

    def parse(self) -> ta.Dict[str, ta.Any]:  # noqa: C901
        header: TomlKey = ()

        # Parse one statement at a time (typically means one line in TOML source)
        while True:
            # 1. Skip line leading whitespace
            self.skip_chars(self.WS)

            # 2. Parse rules. Expect one of the following:
            #    - end of file
            #    - end of line
            #    - comment
            #    - key/value pair
            #    - append dict to list (and move to its namespace)
            #    - create dict (and move to its namespace)
            # Skip trailing whitespace when applicable.
            try:
                char = self.src[self.pos]
            except IndexError:
                break
            if char == '\n':
                self.pos += 1
                continue
            if char in self.KEY_INITIAL_CHARS:
                self.key_value_rule(header)
                self.skip_chars(self.WS)
            elif char == '[':
                try:
                    second_char: ta.Optional[str] = self.src[self.pos + 1]
                except IndexError:
                    second_char = None
                self.flags.finalize_pending()
                if second_char == '[':
                    header = self.create_list_rule()
                else:
                    header = self.create_dict_rule()
                self.skip_chars(self.WS)
            elif char != '#':
                raise self.suffixed_err('Invalid statement')

            # 3. Skip comment
            self.skip_comment()

            # 4. Expect end of line or end of file
            try:
                char = self.src[self.pos]
            except IndexError:
                break
            if char != '\n':
                raise self.suffixed_err('Expected newline or end of document after a statement')
            self.pos += 1

        return self.data.dict

    def skip_chars(self, chars: ta.Iterable[str]) -> None:
        try:
            while self.src[self.pos] in chars:
                self.pos += 1
        except IndexError:
            pass

    def skip_until(
            self,
            expect: str,
            *,
            error_on: ta.FrozenSet[str],
            error_on_eof: bool,
    ) -> None:
        try:
            new_pos = self.src.index(expect, self.pos)
        except ValueError:
            new_pos = len(self.src)
            if error_on_eof:
                raise self.suffixed_err(f'Expected {expect!r}', pos=new_pos) from None

        if not error_on.isdisjoint(self.src[self.pos:new_pos]):
            while self.src[self.pos] not in error_on:
                self.pos += 1
            raise self.suffixed_err(f'Found invalid character {self.src[self.pos]!r}')
        self.pos = new_pos

    def skip_comment(self) -> None:
        try:
            char: ta.Optional[str] = self.src[self.pos]
        except IndexError:
            char = None
        if char == '#':
            self.pos += 1
            self.skip_until(
                '\n',
                error_on=self.ILLEGAL_COMMENT_CHARS,
                error_on_eof=False,
            )

    def skip_comments_and_array_ws(self) -> None:
        while True:
            pos_before_skip = self.pos
            self.skip_chars(self.WS_AND_NEWLINE)
            self.skip_comment()
            if self.pos == pos_before_skip:
                return

    def create_dict_rule(self) -> TomlKey:
        self.pos += 1  # Skip "["
        self.skip_chars(self.WS)
        key = self.parse_key()

        if self.flags.is_(key, TomlFlags.EXPLICIT_NEST) or self.flags.is_(key, TomlFlags.FROZEN):
            raise self.suffixed_err(f'Cannot declare {key} twice')
        self.flags.set(key, TomlFlags.EXPLICIT_NEST, recursive=False)
        try:
            self.data.get_or_create_nest(key)
        except KeyError:
            raise self.suffixed_err('Cannot overwrite a value') from None

        if not self.src.startswith(']', self.pos):
            raise self.suffixed_err("Expected ']' at the end of a table declaration")
        self.pos += 1
        return key

    def create_list_rule(self) -> TomlKey:
        self.pos += 2  # Skip "[["
        self.skip_chars(self.WS)
        key = self.parse_key()

        if self.flags.is_(key, TomlFlags.FROZEN):
            raise self.suffixed_err(f'Cannot mutate immutable namespace {key}')
        # Free the namespace now that it points to another empty list item...
        self.flags.unset_all(key)
        # ...but this key precisely is still prohibited from table declaration
        self.flags.set(key, TomlFlags.EXPLICIT_NEST, recursive=False)
        try:
            self.data.append_nest_to_list(key)
        except KeyError:
            raise self.suffixed_err('Cannot overwrite a value') from None

        if not self.src.startswith(']]', self.pos):
            raise self.suffixed_err("Expected ']]' at the end of an array declaration")
        self.pos += 2
        return key

    def key_value_rule(self, header: TomlKey) -> None:
        key, value = self.parse_key_value_pair()
        key_parent, key_stem = key[:-1], key[-1]
        abs_key_parent = header + key_parent

        relative_path_cont_keys = (header + key[:i] for i in range(1, len(key)))
        for cont_key in relative_path_cont_keys:
            # Check that dotted key syntax does not redefine an existing table
            if self.flags.is_(cont_key, TomlFlags.EXPLICIT_NEST):
                raise self.suffixed_err(f'Cannot redefine namespace {cont_key}')
            # Containers in the relative path can't be opened with the table syntax or dotted key/value syntax in
            # following table sections.
            self.flags.add_pending(cont_key, TomlFlags.EXPLICIT_NEST)

        if self.flags.is_(abs_key_parent, TomlFlags.FROZEN):
            raise self.suffixed_err(f'Cannot mutate immutable namespace {abs_key_parent}')

        try:
            nest = self.data.get_or_create_nest(abs_key_parent)
        except KeyError:
            raise self.suffixed_err('Cannot overwrite a value') from None
        if key_stem in nest:
            raise self.suffixed_err('Cannot overwrite a value')
        # Mark inline table and array namespaces recursively immutable
        if isinstance(value, (dict, list)):
            self.flags.set(header + key, TomlFlags.FROZEN, recursive=True)
        nest[key_stem] = value

    def parse_key_value_pair(self) -> ta.Tuple[TomlKey, ta.Any]:
        key = self.parse_key()
        try:
            char: ta.Optional[str] = self.src[self.pos]
        except IndexError:
            char = None
        if char != '=':
            raise self.suffixed_err("Expected '=' after a key in a key/value pair")
        self.pos += 1
        self.skip_chars(self.WS)
        value = self.parse_value()
        return key, value

    def parse_key(self) -> TomlKey:
        key_part = self.parse_key_part()
        key: TomlKey = (key_part,)
        self.skip_chars(self.WS)
        while True:
            try:
                char: ta.Optional[str] = self.src[self.pos]
            except IndexError:
                char = None
            if char != '.':
                return key
            self.pos += 1
            self.skip_chars(self.WS)
            key_part = self.parse_key_part()
            key += (key_part,)
            self.skip_chars(self.WS)

    def parse_key_part(self) -> str:
        try:
            char: ta.Optional[str] = self.src[self.pos]
        except IndexError:
            char = None
        if char in self.BARE_KEY_CHARS:
            start_pos = self.pos
            self.skip_chars(self.BARE_KEY_CHARS)
            return self.src[start_pos:self.pos]
        if char == "'":
            return self.parse_literal_str()
        if char == '"':
            return self.parse_one_line_basic_str()
        raise self.suffixed_err('Invalid initial character for a key part')

    def parse_one_line_basic_str(self) -> str:
        self.pos += 1
        return self.parse_basic_str(multiline=False)

    def parse_array(self) -> list:
        self.pos += 1
        array: list = []

        self.skip_comments_and_array_ws()
        if self.src.startswith(']', self.pos):
            self.pos += 1
            return array
        while True:
            val = self.parse_value()
            array.append(val)
            self.skip_comments_and_array_ws()

            c = self.src[self.pos:self.pos + 1]
            if c == ']':
                self.pos += 1
                return array
            if c != ',':
                raise self.suffixed_err('Unclosed array')
            self.pos += 1

            self.skip_comments_and_array_ws()
            if self.src.startswith(']', self.pos):
                self.pos += 1
                return array

    def parse_inline_table(self) -> dict:
        self.pos += 1
        nested_dict = TomlNestedDict()
        flags = TomlFlags()

        self.skip_chars(self.WS)
        if self.src.startswith('}', self.pos):
            self.pos += 1
            return nested_dict.dict
        while True:
            key, value = self.parse_key_value_pair()
            key_parent, key_stem = key[:-1], key[-1]
            if flags.is_(key, TomlFlags.FROZEN):
                raise self.suffixed_err(f'Cannot mutate immutable namespace {key}')
            try:
                nest = nested_dict.get_or_create_nest(key_parent, access_lists=False)
            except KeyError:
                raise self.suffixed_err('Cannot overwrite a value') from None
            if key_stem in nest:
                raise self.suffixed_err(f'Duplicate inline table key {key_stem!r}')
            nest[key_stem] = value
            self.skip_chars(self.WS)
            c = self.src[self.pos:self.pos + 1]
            if c == '}':
                self.pos += 1
                return nested_dict.dict
            if c != ',':
                raise self.suffixed_err('Unclosed inline table')
            if isinstance(value, (dict, list)):
                flags.set(key, TomlFlags.FROZEN, recursive=True)
            self.pos += 1
            self.skip_chars(self.WS)

    def parse_basic_str_escape(self, multiline: bool = False) -> str:
        escape_id = self.src[self.pos:self.pos + 2]
        self.pos += 2
        if multiline and escape_id in {'\\ ', '\\\t', '\\\n'}:
            # Skip whitespace until next non-whitespace character or end of the doc. Error if non-whitespace is found
            # before newline.
            if escape_id != '\\\n':
                self.skip_chars(self.WS)
                try:
                    char = self.src[self.pos]
                except IndexError:
                    return ''
                if char != '\n':
                    raise self.suffixed_err("Unescaped '\\' in a string")
                self.pos += 1
            self.skip_chars(self.WS_AND_NEWLINE)
            return ''
        if escape_id == '\\u':
            return self.parse_hex_char(4)
        if escape_id == '\\U':
            return self.parse_hex_char(8)
        try:
            return self.BASIC_STR_ESCAPE_REPLACEMENTS[escape_id]
        except KeyError:
            raise self.suffixed_err("Unescaped '\\' in a string") from None

    def parse_basic_str_escape_multiline(self) -> str:
        return self.parse_basic_str_escape(multiline=True)

    @classmethod
    def is_unicode_scalar_value(cls, codepoint: int) -> bool:
        return (0 <= codepoint <= 55295) or (57344 <= codepoint <= 1114111)

    def parse_hex_char(self, hex_len: int) -> str:
        hex_str = self.src[self.pos:self.pos + hex_len]
        if len(hex_str) != hex_len or not self.HEXDIGIT_CHARS.issuperset(hex_str):
            raise self.suffixed_err('Invalid hex value')
        self.pos += hex_len
        hex_int = int(hex_str, 16)
        if not self.is_unicode_scalar_value(hex_int):
            raise self.suffixed_err('Escaped character is not a Unicode scalar value')
        return chr(hex_int)

    def parse_literal_str(self) -> str:
        self.pos += 1  # Skip starting apostrophe
        start_pos = self.pos
        self.skip_until("'", error_on=self.ILLEGAL_LITERAL_STR_CHARS, error_on_eof=True)
        end_pos = self.pos
        self.pos += 1
        return self.src[start_pos:end_pos]  # Skip ending apostrophe

    def parse_multiline_str(self, *, literal: bool) -> str:
        self.pos += 3
        if self.src.startswith('\n', self.pos):
            self.pos += 1

        if literal:
            delim = "'"
            start_pos = self.pos
            self.skip_until(
                "'''",
                error_on=self.ILLEGAL_MULTILINE_LITERAL_STR_CHARS,
                error_on_eof=True,
            )
            result = self.src[start_pos:self.pos]
            self.pos += 3
        else:
            delim = '"'
            result = self.parse_basic_str(multiline=True)

        # Add at maximum two extra apostrophes/quotes if the end sequence is 4 or 5 chars long instead of just 3.
        if not self.src.startswith(delim, self.pos):
            return result
        self.pos += 1
        if not self.src.startswith(delim, self.pos):
            return result + delim
        self.pos += 1
        return result + (delim * 2)

    def parse_basic_str(self, *, multiline: bool) -> str:
        if multiline:
            error_on = self.ILLEGAL_MULTILINE_BASIC_STR_CHARS
            parse_escapes = self.parse_basic_str_escape_multiline
        else:
            error_on = self.ILLEGAL_BASIC_STR_CHARS
            parse_escapes = self.parse_basic_str_escape
        result = ''
        start_pos = self.pos
        while True:
            try:
                char = self.src[self.pos]
            except IndexError:
                raise self.suffixed_err('Unterminated string') from None
            if char == '"':
                if not multiline:
                    end_pos = self.pos
                    self.pos += 1
                    return result + self.src[start_pos:end_pos]
                if self.src.startswith('"""', self.pos):
                    end_pos = self.pos
                    self.pos += 3
                    return result + self.src[start_pos:end_pos]
                self.pos += 1
                continue
            if char == '\\':
                result += self.src[start_pos:self.pos]
                parsed_escape = parse_escapes()
                result += parsed_escape
                start_pos = self.pos
                continue
            if char in error_on:
                raise self.suffixed_err(f'Illegal character {char!r}')
            self.pos += 1

    def parse_value(self) -> ta.Any:  # noqa: C901
        try:
            char: ta.Optional[str] = self.src[self.pos]
        except IndexError:
            char = None

        # IMPORTANT: order conditions based on speed of checking and likelihood

        # Basic strings
        if char == '"':
            if self.src.startswith('"""', self.pos):
                return self.parse_multiline_str(literal=False)
            return self.parse_one_line_basic_str()

        # Literal strings
        if char == "'":
            if self.src.startswith("'''", self.pos):
                return self.parse_multiline_str(literal=True)
            return self.parse_literal_str()

        # Booleans
        if char == 't':
            if self.src.startswith('true', self.pos):
                self.pos += 4
                return True
        if char == 'f':
            if self.src.startswith('false', self.pos):
                self.pos += 5
                return False

        # Arrays
        if char == '[':
            return self.parse_array()

        # Inline tables
        if char == '{':
            return self.parse_inline_table()

        # Dates and times
        datetime_match = self.RE_DATETIME.match(self.src, self.pos)
        if datetime_match:
            try:
                datetime_obj = self.match_to_datetime(datetime_match)
            except ValueError as e:
                raise self.suffixed_err('Invalid date or datetime') from e
            self.pos = datetime_match.end()
            return datetime_obj
        localtime_match = self.RE_LOCALTIME.match(self.src, self.pos)
        if localtime_match:
            self.pos = localtime_match.end()
            return self.match_to_localtime(localtime_match)

        # Integers and "normal" floats. The regex will greedily match any type starting with a decimal char, so needs to
        # be located after handling of dates and times.
        number_match = self.RE_NUMBER.match(self.src, self.pos)
        if number_match:
            self.pos = number_match.end()
            return self.match_to_number(number_match, self.parse_float)

        # Special floats
        first_three = self.src[self.pos:self.pos + 3]
        if first_three in {'inf', 'nan'}:
            self.pos += 3
            return self.parse_float(first_three)
        first_four = self.src[self.pos:self.pos + 4]
        if first_four in {'-inf', '+inf', '-nan', '+nan'}:
            self.pos += 4
            return self.parse_float(first_four)

        raise self.suffixed_err('Invalid value')

    def coord_repr(self, pos: TomlPos) -> str:
        if pos >= len(self.src):
            return 'end of document'
        line = self.src.count('\n', 0, pos) + 1
        if line == 1:
            column = pos + 1
        else:
            column = pos - self.src.rindex('\n', 0, pos)
        return f'line {line}, column {column}'

    def suffixed_err(self, msg: str, *, pos: ta.Optional[TomlPos] = None) -> TomlDecodeError:
        """Return a `TomlDecodeError` where error message is suffixed with coordinates in source."""

        if pos is None:
            pos = self.pos
        return TomlDecodeError(f'{msg} (at {self.coord_repr(pos)})')

    _TIME_RE_STR = r'([01][0-9]|2[0-3]):([0-5][0-9]):([0-5][0-9])(?:\.([0-9]{1,6})[0-9]*)?'

    RE_NUMBER = re.compile(
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

    RE_LOCALTIME = re.compile(_TIME_RE_STR)

    RE_DATETIME = re.compile(
        rf"""
        ([0-9]{{4}})-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])  # date, e.g. 1988-10-27
        (?:
            [Tt ]
            {_TIME_RE_STR}
            (?:([Zz])|([+-])([01][0-9]|2[0-3]):([0-5][0-9]))?  # optional time offset
        )?
        """,
        flags=re.VERBOSE,
    )

    @classmethod
    def match_to_datetime(cls, match: re.Match) -> ta.Union[datetime.datetime, datetime.date]:
        """
        Convert a `RE_DATETIME` match to `datetime.datetime` or `datetime.date`.

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

    @classmethod
    def match_to_localtime(cls, match: re.Match) -> datetime.time:
        hour_str, minute_str, sec_str, micros_str = match.groups()
        micros = int(micros_str.ljust(6, '0')) if micros_str else 0
        return datetime.time(int(hour_str), int(minute_str), int(sec_str), micros)

    @classmethod
    def match_to_number(cls, match: re.Match, parse_float: TomlParseFloat) -> ta.Any:
        if match.group('floatpart'):
            return parse_float(match.group())
        return int(match.group(), 0)
