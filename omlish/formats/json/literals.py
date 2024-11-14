# MIT License
# ===========
#
# Copyright (c) 2006 Bob Ippolito
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
# https://github.com/simplejson/simplejson/blob/6932004966ab70ef47250a2b3152acd8c904e6b5/simplejson/scanner.py
import json
import re
import sys
import typing as ta


##


_FOUR_DIGIT_HEX_PAT = re.compile(r'^[0-9a-fA-F]{4}$')


def _scan_four_digit_hex(
        s: str,
        end: int,
):
    """Scan a four digit hex number from s[end:end + 4]"""

    msg = 'Invalid \\uXXXX escape sequence'
    esc = s[end: end + 4]
    if not _FOUR_DIGIT_HEX_PAT.match(esc):
        raise json.JSONDecodeError(msg, s, end - 2)

    try:
        return int(esc, 16), end + 4
    except ValueError:
        raise json.JSONDecodeError(msg, s, end - 2) from None


_STRING_CHUNK_PAT = re.compile(r'(.*?)(["\\\x00-\x1f])', re.VERBOSE | re.MULTILINE | re.DOTALL)

_BACKSLASH_MAP = {
    '"': '"',
    '\\': '\\',
    '/': '/',
    'b': '\b',
    'f': '\f',
    'n': '\n',
    'r': '\r',
    't': '\t',
}


def parse_string(
        s: str,
        idx: int = 0,
        *,
        strict: bool = True,
) -> tuple[str, int]:
    """
    Scan the string s for a JSON string. Idx is the index of the quote that starts the JSON string. Unescapes all valid
    JSON string escape sequences and raises ValueError on attempt to decode an invalid string. If strict is False then
    literal control characters are allowed in the string.

    Returns a tuple of the decoded string and the index of the character in s after the end quote.
    """

    if s[idx] != '"':
        raise json.JSONDecodeError('No opening string quotes at', s, idx)

    chunks: list[str] = []
    end = idx + 1
    while True:
        chunk = _STRING_CHUNK_PAT.match(s, end)
        if chunk is None:
            raise json.JSONDecodeError('Unterminated string starting at', s, idx)

        prev_end = end
        end = chunk.end()
        content, terminator = chunk.groups()
        # Content is contains zero or more unescaped string characters
        if content:
            chunks.append(content)

        # Terminator is the end of string, a literal control character, or a backslash denoting that an escape sequence
        # follows
        if terminator == '"':
            break
        elif terminator != '\\':
            if strict:
                msg = 'Invalid control character %r at'
                raise json.JSONDecodeError(msg, s, prev_end)
            else:
                chunks.append(terminator)
                continue

        try:
            esc = s[end]
        except IndexError:
            raise json.JSONDecodeError('Unterminated string starting at', s, idx) from None

        # If not a unicode escape sequence, must be in the lookup table
        if esc != 'u':
            try:
                char = _BACKSLASH_MAP[esc]
            except KeyError:
                msg = 'Invalid \\X escape sequence %r'
                raise json.JSONDecodeError(msg, s, end) from None
            end += 1

        else:
            # Unicode escape sequence
            uni, end = _scan_four_digit_hex(s, end + 1)

            # Check for surrogate pair on UCS-4 systems Note that this will join high/low surrogate pairs but will also
            # pass unpaired surrogates through
            if (
                    sys.maxunicode > 65535 and
                    uni & 0xFC00 == 0xD800 and
                    s[end: end + 2] == '\\u'
            ):
                uni2, end2 = _scan_four_digit_hex(s, end + 2)
                if uni2 & 0xFC00 == 0xDC00:
                    uni = 0x10000 + (((uni - 0xD800) << 10) | (uni2 - 0xDC00))
                    end = end2

            char = chr(uni)

        # Append the unescaped character
        chunks.append(char)

    return ''.join(chunks), end


def try_parse_string(
        s: str,
        idx: int = 0,
        *,
        strict: bool = True,
) -> tuple[str, int] | None:
    if not s or s[idx] != '"':
        return None

    return parse_string(s, idx, strict=strict)


##


_NUMBER_PAT = re.compile(
    r'(-?(?:0|[1-9]\d*))(\.\d+)?([eE][-+]?\d+)?',
    (re.VERBOSE | re.MULTILINE | re.DOTALL),
)


def try_parse_number(
        s: str,
        idx: int = 0,
        *,
        parse_float: ta.Callable[[str], float] = float,
        parse_int: ta.Callable[[str], int] = int,
) -> tuple[int | float, int] | None:
    if (m := _NUMBER_PAT.match(s, idx)) is None:
        return None

    integer, frac, exp = m.groups()
    if frac or exp:
        res = parse_float(integer + (frac or '') + (exp or ''))
    else:
        res = parse_int(integer)
    return res, m.end()
