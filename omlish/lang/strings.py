import typing as ta
import unicodedata


##


def prefix_lines(s: str, p: str) -> str:
    return '\n'.join([p + l for l in s.split('\n')])


def indent_lines(s: str, num: int) -> str:
    return prefix_lines(s, ' ' * num)


##


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
