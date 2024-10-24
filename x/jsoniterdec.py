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


##


allow_nan = False
strict = True


##


JSONDecodeError = json.JSONDecodeError

FLAGS = re.VERBOSE | re.MULTILINE | re.DOTALL


def _floatconstants():
    nan = float('nan')
    inf = float('inf')
    return nan, inf, -inf


NaN, PosInf, NegInf = _floatconstants()

_CONSTANTS = {
    '-Infinity': NegInf,
    'Infinity': PosInf,
    'NaN': NaN,
}

parse_constant = (allow_nan and _CONSTANTS.__getitem__ or None)


def scan_four_digit_hex(s, end, _m=re.compile(r'^[0-9a-fA-F]{4}$').match):
    """Scan a four digit hex number from s[end:end + 4]"""

    msg = 'Invalid \\uXXXX escape sequence'
    esc = s[end: end + 4]
    if not _m(esc):
        raise JSONDecodeError(msg, s, end - 2)

    try:
        return int(esc, 16), end + 4
    except ValueError:
        raise JSONDecodeError(msg, s, end - 2)


STRINGCHUNK = re.compile(r'(.*?)(["\\\x00-\x1f])', FLAGS)

BACKSLASH = {
    '"': '"',
    '\\': '\\',
    '/': '/',
    'b': '\b',
    'f': '\f',
    'n': '\n',
    'r': '\r',
    't': '\t',
}

memo = {}

def parse_string(
        s,
        end,
        strict=True,
        _b=BACKSLASH,  # noqa
        _m=STRINGCHUNK.match,
        _join=''.join,
        _maxunicode=sys.maxunicode,
        _scan_four_digit_hex=scan_four_digit_hex,
):
    """
    Scan the string s for a JSON string. End is the index of the character in s after the quote that started the JSON
    string. Unescapes all valid JSON string escape sequences and raises ValueError on attempt to decode an invalid
    string. If strict is False then literal control characters are allowed in the string.

    Returns a tuple of the decoded string and the index of the character in s after the end quote.
    """

    chunks = []
    _append = chunks.append
    begin = end - 1
    while True:
        chunk = _m(s, end)
        if chunk is None:
            raise JSONDecodeError('Unterminated string starting at', s, begin)

        prev_end = end
        end = chunk.end()
        content, terminator = chunk.groups()
        # Content is contains zero or more unescaped string characters
        if content:
            _append(content)

        # Terminator is the end of string, a literal control character, or a backslash denoting that an escape sequence
        # follows
        if terminator == '"':
            break
        elif terminator != '\\':
            if strict:
                msg = 'Invalid control character %r at'
                raise JSONDecodeError(msg, s, prev_end)
            else:
                _append(terminator)
                continue

        try:
            esc = s[end]
        except IndexError:
            raise JSONDecodeError('Unterminated string starting at', s, begin)

        # If not a unicode escape sequence, must be in the lookup table
        if esc != 'u':
            try:
                char = _b[esc]
            except KeyError:
                msg = 'Invalid \\X escape sequence %r'
                raise JSONDecodeError(msg, s, end)
            end += 1

        else:
            # Unicode escape sequence
            uni, end = _scan_four_digit_hex(s, end + 1)

            # Check for surrogate pair on UCS-4 systems Note that this will join high/low surrogate pairs but will also
            # pass unpaired surrogates through
            if (
                    _maxunicode > 65535 and
                    uni & 0xFC00 == 0xD800 and
                    s[end: end + 2] == '\\u'
            ):
                uni2, end2 = _scan_four_digit_hex(s, end + 2)
                if uni2 & 0xFC00 == 0xDC00:
                    uni = 0x10000 + (((uni - 0xD800) << 10) | (uni2 - 0xDC00))
                    end = end2

            char = chr(uni)

        # Append the unescaped character
        _append(char)

    return _join(chunks), end


NUMBER_RE = re.compile(
    r'(-?(?:0|[1-9]\d*))(\.\d+)?([eE][-+]?\d+)?',
    (re.VERBOSE | re.MULTILINE | re.DOTALL),
)

match_number = NUMBER_RE.match

parse_float = float
parse_int = int

WHITESPACE = re.compile(r'[ \t\n\r]*', FLAGS)
WHITESPACE_STR = ' \t\n\r'


def parse_object(
        state,
        strict,
        scan_once,
        _w=WHITESPACE.match,
        _ws=WHITESPACE_STR,
):
    (s, end) = state

    # Backwards compatibility
    memo_get = memo.setdefault

    pairs = []
    # Use a slice to prevent IndexError from being raised, the following check will raise a more specific ValueError if
    # the string is empty
    nextchar = s[end: end + 1]
    # Normally we expect nextchar == '"'
    if nextchar != '"':
        if nextchar in _ws:
            end = _w(s, end).end()
            nextchar = s[end: end + 1]

        # Trivial empty object
        if nextchar == '}':
            pairs = {}
            return pairs, end + 1
        elif nextchar != '"':
            raise JSONDecodeError("Expecting property name enclosed in double quotes or '}'", s, end )

    end += 1
    while True:
        key, end = parse_string(s, end, strict)
        key = memo_get(key, key)

        # To skip some function call overhead we optimize the fast paths where the JSON key separator is ": " or just
        # ":".
        if s[end: end + 1] != ':':
            end = _w(s, end).end()
            if s[end: end + 1] != ':':
                raise JSONDecodeError("Expecting ':' delimiter", s, end)

        end += 1

        try:
            if s[end] in _ws:
                end += 1
                if s[end] in _ws:
                    end = _w(s, end + 1).end()
        except IndexError:
            pass

        value, end = scan_once(s, end)
        pairs.append((key, value))

        try:
            nextchar = s[end]
            if nextchar in _ws:
                end = _w(s, end + 1).end()
                nextchar = s[end]
        except IndexError:
            nextchar = ''
        end += 1

        if nextchar == '}':
            break
        elif nextchar != ',':
            raise JSONDecodeError("Expecting ',' delimiter or '}'", s, end - 1)

        try:
            nextchar = s[end]
            if nextchar in _ws:
                end += 1
                nextchar = s[end]
                if nextchar in _ws:
                    end = _w(s, end + 1).end()
                    nextchar = s[end]
        except IndexError:
            nextchar = ''

        end += 1
        if nextchar != '"':
            raise JSONDecodeError('Expecting property name enclosed in double quotes', s, end - 1)

    pairs = dict(pairs)
    return pairs, end


def parse_array(
        state,
        scan_once,
        _w=WHITESPACE.match,
        _ws=WHITESPACE_STR,
):
    (s, end) = state

    values = []

    nextchar = s[end: end + 1]
    if nextchar in _ws:
        end = _w(s, end + 1).end()
        nextchar = s[end: end + 1]

    # Look-ahead for trivial empty array
    if nextchar == ']':
        return values, end + 1
    elif nextchar == '':
        raise JSONDecodeError("Expecting value or ']'", s, end)

    _append = values.append
    while True:
        value, end = scan_once(s, end)
        _append(value)

        nextchar = s[end: end + 1]
        if nextchar in _ws:
            end = _w(s, end + 1).end()
            nextchar = s[end: end + 1]

        end += 1

        if nextchar == ']':
            break
        elif nextchar != ',':
            raise JSONDecodeError("Expecting ',' delimiter or ']'", s, end - 1)

        try:
            if s[end] in _ws:
                end += 1
                if s[end] in _ws:
                    end = _w(s, end + 1).end()
        except IndexError:
            pass

    return values, end


def _scan_once(string: str, idx: int):
    errmsg = 'Expecting value'
    try:
        nextchar = string[idx]
    except IndexError:
        raise JSONDecodeError(errmsg, string, idx)

    if nextchar == '"':
        return parse_string(string, idx + 1, strict)

    elif nextchar == '{':
        return parse_object(
            (string, idx + 1),
            strict,
            _scan_once,
        )

    elif nextchar == '[':
        return parse_array((string, idx + 1), _scan_once)

    elif nextchar == 'n' and string[idx: idx + 4] == 'null':
        return None, idx + 4

    elif nextchar == 't' and string[idx: idx + 4] == 'true':
        return True, idx + 4

    elif nextchar == 'f' and string[idx: idx + 5] == 'false':
        return False, idx + 5

    if (m := match_number(string, idx)) is not None:
        integer, frac, exp = m.groups()
        if frac or exp:
            res = parse_float(integer + (frac or '') + (exp or ''))
        else:
            res = parse_int(integer)
        return res, m.end()

    elif parse_constant and nextchar == 'N' and string[idx: idx + 3] == 'NaN':
        return parse_constant('NaN'), idx + 3

    elif parse_constant and nextchar == 'I' and string[idx: idx + 8] == 'Infinity':
        return parse_constant('Infinity'), idx + 8

    elif parse_constant and nextchar == '-' and string[idx: idx + 9] == '-Infinity':
        return parse_constant('-Infinity'), idx + 9

    else:
        raise JSONDecodeError(errmsg, string, idx)


def scan_once(string, idx):
    if idx < 0:
        # Ensure the same behavior as the C speedup, otherwise this would work for *some* negative string indices due to
        # the behavior of __getitem__ for strings. #98
        raise JSONDecodeError('Expecting value', string, idx)

    memo = {}
    try:
        return _scan_once(string, idx)
    finally:
        memo.clear()


##


def _main() -> None:
    import json
    import yaml
    with open('x/llm/openai/api.yaml') as f:
        json_input = json.dumps(yaml.safe_load(f))

    print(scan_once(json_input, 0))


if __name__ == '__main__':
    _main()
