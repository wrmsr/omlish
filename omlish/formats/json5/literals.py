"""
https://spec.json5.org/
"""
import io
import json
import typing as ta

from ... import lang
from .errors import Json5Error


##


LITERAL_VALUES: ta.Mapping[str, ta.Any] = {
    'true': True,
    'false': False,
    'null': None,
}


##


STRING_LITERAL_ESCAPES: ta.Mapping[str, str] = {
    'b': '\\u0008',
    'f': '\\u000C',
    'n': '\\u000A',
    'r': '\\u000D',
    't': '\\u0009',
    'v': '\\u000B',
    '0': '\\u0000',
    'u': '\\u',
    '"': '\\"',
    "'": "'",
    '\\': '\\\\',
}


def _check_state(b: bool, fmt: str = 'Json5 error', *args: ta.Any) -> None:
    if not b:
        raise Json5Error(fmt % args)


def translate_string_literal(s: str) -> str:
    _check_state(len(s) > 1)
    q = s[0]
    _check_state(q in '\'"')
    _check_state(s[-1] == q)

    c = 1
    e = len(s) - 1

    b = io.StringIO()
    b.write('"')

    ds = '\\\'"'
    while True:
        n = lang.find_any(s, ds, c, e)
        if n < 0:
            b.write(s[c:e])
            break

        _check_state(n < e)
        b.write(s[c:n])

        x = s[n]
        if x == '\\':
            _check_state(n < (e - 1))

            y = s[n + 1]
            if y in '\n\u2028\u2029':
                c = n + 2

            elif y == '\r':
                c = n + 2
                if c < e and s[c] == '\n':
                    c += 1

            elif y in 'x':
                _check_state(n < (e - 3))
                u = int(s[n + 2:n + 4], 16)
                b.write(f'\\u00{u:02x}')
                c = n + 4

            elif (g := STRING_LITERAL_ESCAPES.get(y)) is not None:
                b.write(g)
                c = n + 2

            elif not ('0' <= y <= '9'):
                b.write(y)
                c = n + 2

            else:
                raise Json5Error(f'Invalid string literal escape: {x}{y}')

        elif x in '\\\'"':
            _check_state(x != q)
            if x == '"':
                b.write('\\"')
            else:
                b.write(x)
            c = n + 1

        else:
            raise RuntimeError

    b.write('"')
    return b.getvalue()


def parse_string_literal(s: str) -> str:
    j = translate_string_literal(s)

    try:
        return json.loads(j)
    except json.JSONDecodeError as e:
        raise Json5Error from e


##


def parse_number_literal(s: str) -> int | float:
    s = s.lower()

    if 'x' in s:
        return int(s, 16)
    else:
        return float(s)
