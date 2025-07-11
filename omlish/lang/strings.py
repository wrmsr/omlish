import re
import typing as ta
import unicodedata


StrOrBytes: ta.TypeAlias = str | bytes
StrOrBytesT = ta.TypeVar('StrOrBytesT', bound=StrOrBytes)


##


def prefix_delimited(s: StrOrBytesT, p: StrOrBytesT, d: StrOrBytesT) -> StrOrBytesT:
    return d.join([p + l for l in s.split(d)])  # type: ignore


def prefix_lines(s: StrOrBytesT, p: StrOrBytesT) -> StrOrBytesT:
    return prefix_delimited(s, p, '\n' if isinstance(s, str) else b'\n')  # type: ignore


def indent_lines(s: StrOrBytesT, num: StrOrBytesT) -> StrOrBytesT:
    return prefix_lines(s, (' ' if isinstance(s, str) else b' ') * num)  # type: ignore


##


def strip_prefix(s: StrOrBytesT, pfx: StrOrBytesT) -> StrOrBytesT:
    if not s.startswith(pfx):  # type: ignore
        raise ValueError(f'{s!r} does not start with {pfx!r}')
    return s[len(pfx):]  # type: ignore


def strip_suffix(s: StrOrBytesT, sfx: StrOrBytesT) -> StrOrBytesT:
    if not s.endswith(sfx):  # type: ignore
        raise ValueError(f'{s!r} does not end with {sfx!r}')
    return s[:-len(sfx)]  # type: ignore


##


def replace_many(
        s: StrOrBytesT,
        old: ta.Iterable[StrOrBytesT],
        new: StrOrBytesT,
        count_each: int = -1,
) -> StrOrBytesT:
    for o in old:
        s = s.replace(o, new, count_each)  # type: ignore
    return s


##


def find_any(
        string: StrOrBytesT,
        subs: ta.Iterable[StrOrBytesT],
        start: int | None = None,
        end: int | None = None,
) -> int:
    r = -1
    for sub in subs:
        if (p := string.find(sub, start, end)) >= 0:  # type: ignore
            if r < 0 or p < r:
                r = p
    return r


def rfind_any(
        string: StrOrBytesT,
        subs: ta.Iterable[StrOrBytesT],
        start: int | None = None,
        end: int | None = None,
) -> int:
    r = -1
    for sub in subs:
        if (p := string.rfind(sub, start, end)) >= 0:  # type: ignore
            if r < 0 or p > r:
                r = p
    return r


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


##


BOOL_STRINGS: ta.Sequence[tuple[str, str]] = [
    ('n', 'y'),
    ('no', 'yes'),
    ('f', 't'),
    ('false', 'true'),
    ('off', 'on'),
    ('0', '1'),
]

BOOL_FALSE_STRINGS = frozenset(tup[0] for tup in BOOL_STRINGS)
BOOL_TRUE_STRINGS = frozenset(tup[1] for tup in BOOL_STRINGS)

STRING_BOOL_VALUES: ta.Mapping[str, bool] = {
    k: v
    for ks, v in [
        (BOOL_FALSE_STRINGS, False),
        (BOOL_TRUE_STRINGS, True),
    ]
    for k in ks
}


##


def iter_pat(pat: re.Pattern[str], s: str, **kwargs: ta.Any) -> ta.Generator[str | re.Match]:
    p = 0
    for m in re.finditer(pat, s, **kwargs):
        if p < (l := m.start()):
            yield s[p:l]
        yield m
        p = m.end()
    if p < len(s):
        yield s[p:]
