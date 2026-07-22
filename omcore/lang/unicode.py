import typing as ta
import unicodedata


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
        '\u1885',
        '\u1886',
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
    if (
            unicodedata.category(c) in spec.cats or
            c in spec.chars
    ):
        return True
    n = unicodedata.normalize('NFKC', c)
    return (
        len(n) == 1 and
        (unicodedata.category(n) in spec.cats or n in spec.chars)
    )


def is_ident_start(c: str) -> bool:
    return _is_char_in_spec(_IDENT_START_CHAR_SPEC, c)


def is_ident_cont(c: str) -> bool:
    return _is_char_in_spec(_IDENT_CONT_CHAR_SPEC, c)


def is_ident(name: str) -> bool:
    return (
        bool(name) and
        is_ident_start(name[0]) and
        all(is_ident_cont(c) for c in name[1:])
    )
