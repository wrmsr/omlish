import re
import typing as ta

from .... import check


##


IdentTokenKind: ta.TypeAlias = ta.Literal['IDENT']

ValueTokenKind: ta.TypeAlias = ta.Literal[
    'STRING',
    'NUMBER',
]

VALUE_TOKEN_KINDS = frozenset(check.isinstance(a, str) for a in ta.get_args(ValueTokenKind))

ControlTokenKind: ta.TypeAlias = ta.Literal[
    'LBRACE',
    'RBRACE',
    'LBRACKET',
    'RBRACKET',
    'COMMA',
    'COLON',
]

SpaceTokenKind: ta.TypeAlias = ta.Literal['SPACE']

CommentTokenKind: ta.TypeAlias = ta.Literal['COMMENT']

TokenKind: ta.TypeAlias = ta.Union[  # noqa
    IdentTokenKind,
    ValueTokenKind,
    ControlTokenKind,
    SpaceTokenKind,
    CommentTokenKind,
]


#

ScalarValue: ta.TypeAlias = str | float | int | None

SCALAR_VALUE_TYPES: tuple[type, ...] = tuple(
    check.isinstance(e, type) if e is not None else type(None)
    for e in ta.get_args(ScalarValue)
)


##


class Position(ta.NamedTuple):
    ofs: int
    line: int
    col: int


class Token(ta.NamedTuple):
    kind: TokenKind
    value: ScalarValue
    raw: str | None

    pos: Position

    def __iter__(self):
        raise TypeError


##


NUMBER_PAT = re.compile(r'-?(?:0|[1-9]\d*)(?:\.\d+)?(?:[eE][+-]?\d+)?')

CONTROL_TOKENS: ta.Mapping[str, TokenKind] = {
    '{': 'LBRACE',
    '}': 'RBRACE',
    '[': 'LBRACKET',
    ']': 'RBRACKET',
    ',': 'COMMA',
    ':': 'COLON',
}

CONST_IDENT_VALUES: ta.Mapping[str, str | float | None] = {
    'NaN': float('nan'),
    '-NaN': float('-nan'),  # distinguished in parsing even if indistinguishable in value
    'Infinity': float('inf'),
    '-Infinity': float('-inf'),

    'true': True,
    'false': False,
    'null': None,
}

MAX_CONST_IDENT_LEN = max(map(len, CONST_IDENT_VALUES))


##


EXPANDED_SPACE_CHARS = (
    '\u0009'
    '\u000A'
    '\u000B'
    '\u000C'
    '\u000D'
    '\u0020'
    '\u00A0'
    '\u2028'
    '\u2029'
    '\uFEFF'
    '\u1680'
    '\u2000'
    '\u2001'
    '\u2002'
    '\u2003'
    '\u2004'
    '\u2005'
    '\u2006'
    '\u2007'
    '\u2008'
    '\u2009'
    '\u200A'
    '\u202F'
    '\u205F'
    '\u3000'
)
