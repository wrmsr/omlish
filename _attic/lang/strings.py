"""
TODO:
 - unboxed Redacted (and various other AnyVals)
"""
import io
import typing as ta
import unicodedata


T = ta.TypeVar('T')


BOOL_STRS: ta.Mapping[bool, ta.AbstractSet[str]] = {
    b: {s for s in ss for s in [s, s.capitalize(), s.upper()]} for b, ss in [
        (True, ['1', 't', 'true', 'y', 'yes']),
        (False, ['0', 'f', 'false', 'n', 'no']),
    ]
}

BOOL_STR_VALS = {s: b for b, ss in BOOL_STRS.items() for s in ss}


def parse_bool(v: ta.Union[bool, str], *, strict: bool = False) -> bool:
    if isinstance(v, bool):
        return v
    if isinstance(v, str):
        if not strict:
            v = v.lower()
        try:
            return BOOL_STR_VALS[v]
        except KeyError:
            raise ValueError(v)
    raise TypeError(v)


def camelize(name: str) -> str:
    return ''.join(map(str.capitalize, name.split('_')))


def decamelize(name: str) -> str:
    uppers: ta.List[ta.Optional[int]] = [i for i, c in enumerate(name) if c.isupper()]
    return '_'.join([name[l:r].lower() for l, r in zip([None] + uppers, uppers + [None])]).strip('_')  # type: ignore


def prefix_lines(s: str, p: str) -> str:
    return '\n'.join([p + l for l in s.split('\n')])


def indent_lines(s: str, num: int) -> str:
    return prefix_lines(s, ' ' * num)


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


class _CharSpec(ta.NamedTuple):
    cats: ta.AbstractSet[str]
    chars: ta.AbstractSet[str]


_IDENT_START_CHAR_SPEC = _CharSpec(
    {
        'Ll',
        'Lm',
        'Lo',
        'Lt',
        'Lu',
        'Nl',
    },
    {
        '_',
        '\u2118',
        '\u212E',
        '\u309B',
        '\u309C',
    },
)


_IDENT_CONT_CHAR_SPEC = _CharSpec(
    {
        'Ll',
        'Lm',
        'Lo',
        'Lt',
        'Lu',
        'Mc',
        'Mn',
        'Nd',
        'Nl',
        'Pc',
    },
    {
        '_',
        '\u00B7',
        '\u0387',
        '\u1369',
        '\u136A',
        '\u136B',
        '\u136C',
        '\u136D',
        '\u136E',
        '\u136F',
        '\u1370',
        '\u1371',
        '\u19DA',
        '\u2118',
        '\u212E',
        '\u309B',
        '\u309C',
    },
)


def _is_char_in_spec(spec: _CharSpec, c: str) -> bool:
    if len(c) != 1:
        raise ValueError(c)
    return (
            unicodedata.category(c) in spec.cats or
            c in spec.chars or
            unicodedata.category(unicodedata.normalize('NFKC', c)) in spec.cats or
            unicodedata.normalize('NFKC', c) in spec.chars
    )


def is_ident_start(c: str) -> bool:
    return _is_char_in_spec(_IDENT_START_CHAR_SPEC, c)


def is_ident_cont(c: str) -> bool:
    return _is_char_in_spec(_IDENT_CONT_CHAR_SPEC, c)


def is_ident(name: str) -> bool:
    return is_ident_start(name[0]) and all(is_ident_cont(c) for c in name[1:])


class DelimitedEscaping:

    def __init__(
            self,
            delimit_char: str,
            quote_char: str,
            escape_char: str,
            escaped_chars: ta.Iterable[str] = (),
    ) -> None:
        super().__init__()

        self._delimit_char = delimit_char
        self._quote_char = quote_char
        self._escape_char = escape_char
        self._escaped_chars = frozenset(escaped_chars)

        for c in [delimit_char, quote_char, escape_char]:
            if not isinstance(c, str) or len(c) != 1:
                raise TypeError(c)
        for c in self._escaped_chars:
            if not isinstance(c, str):
                raise TypeError(c)

        self._all_escaped_chars = frozenset({delimit_char, quote_char, escape_char} | self._escaped_chars)

    @property
    def delimit_char(self) -> str:
        return self._delimit_char

    def quote_char(self) -> str:
        return self._quote_char

    def escape_char(self) -> str:
        return self._escape_char

    def escaped_chars(self) -> ta.FrozenSet[str]:
        return self._escaped_chars

    def all_escaped_chars(self) -> ta.FrozenSet[str]:
        return self._all_escaped_chars

    def is_control_char(self, c: str) -> bool:
        if not len(c) == 1:
            raise TypeError(c)
        return c == self._delimit_char or c == self._quote_char or c == self._escape_char

    def contains_escaped_char(self, s: str) -> bool:
        return any(c in self._all_escaped_chars for c in s)

    def escape(self, s: str) -> str:
        buf = io.StringIO()
        for c in s:
            if c in self._all_escaped_chars:
                buf.write(self._escape_char)
            buf.write(c)
        return buf.getvalue()

    def unescape(self, s: str) -> str:
        buf = io.StringIO()
        i = 0
        while i < len(s):
            c = s[i]
            if c == self._escape_char:
                if i > (len(s) - 2):
                    raise ValueError(s)
                i += 1
                buf.write(s[i])
            else:
                if c in self._all_escaped_chars:
                    raise ValueError(s)
                buf.write(c)
            i += 1
        return buf.getvalue()

    def quote(self, s: str) -> str:
        if self.contains_escaped_char(s):
            return self._quote_char + self.escape(s) + self._quote_char
        else:
            return s

    def unquote(self, s: str) -> str:
        if s and s[0] == self._quote_char:
            if len(s) < 2 or s[-1] != self._quote_char:
                raise ValueError(s)
            return self.unescape(s[1:-1])
        else:
            return s

    def delimit_many(self, strs: ta.Iterable[str]) -> str:
        if isinstance(strs, str):
            raise TypeError(strs)
        buf = io.StringIO()
        count = 0
        for s in strs:
            if count:
                buf.write(self._delimit_char)
            count += 1
            if self.contains_escaped_char(s):
                buf.write(self.quote(s))
            else:
                buf.write(s)
        return buf.getvalue()

    def delimit(self, s: str) -> str:
        if not isinstance(s, str):
            raise TypeError(s)
        return self.delimit_many([s])

    def undelimit(self, s: str) -> ta.List[str]:
        ret = []
        buf = io.StringIO()
        count = 0
        i = 0

        while i < len(s):
            c = s[i]

            if count:
                if c != self._delimit_char or i >= (len(s) - 1):
                    raise ValueError(s)
                i += 1
                c = s[i]

            quoted = c == self._quote_char
            if quoted:
                if i >= (len(s) - 1):
                    raise ValueError(s)
                i += 1
                c = s[i]
            unquoted = False

            while True:
                if c == self._delimit_char:
                    if not quoted:
                        break
                    else:
                        buf.write(c)
                elif c == self._quote_char:
                    if not quoted:
                        raise ValueError(s)
                    unquoted = True
                    i += 1
                    break
                elif c == self._escape_char:
                    if not quoted or i > (len(s) - 2):
                        raise ValueError(s)
                    i += 1
                    buf.write(s[i])
                else:
                    if c in self._escaped_chars:
                        raise ValueError(s)
                    buf.write(c)

                i += 1
                if i == len(s):
                    break
                c = s[i]

            if quoted and not unquoted:
                raise ValueError(s)

            ret.append(buf.getvalue())
            buf.seek(0)
            buf.truncate()
            count += 1

        return ret


class Redacted(ta.Generic[T]):

    def __new__(cls, value, *args, **kwargs):
        if isinstance(value, Redacted):
            return value
        return super().__new__(cls, *args, **kwargs)

    def __init__(self, value: T) -> None:
        if value is self:
            return
        super().__init__()
        if isinstance(value, Redacted):
            raise TypeError(value)
        self._value = value

    def __init_subclass__(cls, **kwargs):
        raise TypeError

    @property
    def value(self) -> T:
        return self._value

    def __repr__(self) -> str:
        return f'{type(self).__name__}@{hex(id(self))[2:]}'

    def __str__(self) -> str:
        return repr(self)

    def __hash__(self) -> int:
        return hash(self._value)

    def __eq__(self, o: object) -> bool:
        return self._value == (o._value if isinstance(o, Redacted) else o)  # type: ignore

    def __ne__(self, o: object) -> bool:
        return self._value != (o._value if isinstance(o, Redacted) else o)  # type: ignore

    def __lt__(self, o: object) -> bool:
        return self._value < (o._value if isinstance(o, Redacted) else o)  # type: ignore

    def __le__(self, o: object) -> bool:
        return self._value <= (o._value if isinstance(o, Redacted) else o)  # type: ignore

    def __gt__(self, o: object) -> bool:
        return self._value > (o._value if isinstance(o, Redacted) else o)  # type: ignore

    def __ge__(self, o: object) -> bool:
        return self._value >= (o._value if isinstance(o, Redacted) else o)  # type: ignore


def redact(value: T) -> Redacted[T]:
    return Redacted(value)
