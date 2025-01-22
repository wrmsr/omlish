"""
TODO:
 - max buf size
 - max recursion depth
 - mark start pos of tokens, currently returning end
 - _do_string inner loop optimization somehow
 - json5 mode
"""
import dataclasses as dc
import io
import json
import re
import typing as ta

from .... import check
from ....funcs.genmachine import GenMachine
from .errors import JsonStreamError


##


ValueTokenKind: ta.TypeAlias = ta.Literal[
    'STRING',
    'NUMBER',

    'SPECIAL_NUMBER',
    'BOOLEAN',
    'NULL',
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

TokenKind: ta.TypeAlias = ValueTokenKind | ControlTokenKind

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


NUMBER_PAT = re.compile(r'-?(?:0|[1-9]\d*)(?:\.\d+)?(?:[eE][+-]?\d+)?')

CONTROL_TOKENS: ta.Mapping[str, TokenKind] = {
    '{': 'LBRACE',
    '}': 'RBRACE',
    '[': 'LBRACKET',
    ']': 'RBRACKET',
    ',': 'COMMA',
    ':': 'COLON',
}

CONST_TOKENS: ta.Mapping[str, tuple[TokenKind, str | float | None]] = {
    'NaN': ('SPECIAL_NUMBER', float('nan')),
    'Infinity': ('SPECIAL_NUMBER', float('inf')),
    '-Infinity': ('SPECIAL_NUMBER', float('-inf')),

    'true': ('BOOLEAN', True),
    'false': ('BOOLEAN', False),
    'null': ('NULL', None),
}


##


@dc.dataclass()
class JsonStreamLexError(JsonStreamError):
    message: str

    pos: Position


class JsonStreamLexer(GenMachine[str, Token]):
    def __init__(
            self,
            *,
            include_raw: bool = False,
    ) -> None:
        self._include_raw = include_raw

        self._ofs = 0
        self._line = 1
        self._col = 0

        self._buf = io.StringIO()

        super().__init__(self._do_main())

    @property
    def pos(self) -> Position:
        return Position(
            self._ofs,
            self._line,
            self._col,
        )

    def _char_in(self, c: str) -> str:
        if c and len(c) != 1:
            raise ValueError(c)

        self._ofs += 1

        if c == '\n':
            self._line += 1
            self._col = 0
        else:
            self._col += 1

        return c

    def _make_tok(
            self,
            kind: TokenKind,
            value: ScalarValue,
            raw: str,
            pos: Position,
    ) -> ta.Sequence[Token]:
        tok = Token(
            kind,
            value,
            raw if self._include_raw else None,
            pos,
        )
        return (tok,)

    def _flip_buf(self) -> str:
        raw = self._buf.getvalue()
        self._buf.seek(0)
        self._buf.truncate()
        return raw

    def _raise(self, msg: str, src: Exception | None = None) -> ta.NoReturn:
        raise JsonStreamLexError(msg, self.pos) from src

    def _do_main(self):
        while True:
            c = self._char_in((yield None))  # noqa

            if not c:
                return None

            if c.isspace():
                continue

            if c in CONTROL_TOKENS:
                yield self._make_tok(CONTROL_TOKENS[c], c, c, self.pos)
                continue

            if c == '"':
                return self._do_string()

            if c.isdigit() or c == '-':
                return self._do_number(c)

            if c in 'tfnIN':
                return self._do_const(c)

            self._raise(f'Unexpected character: {c}')

    def _do_string(self):
        check.state(self._buf.tell() == 0)
        self._buf.write('"')

        pos = self.pos

        last = None
        while True:
            try:
                c = self._char_in((yield None))  # noqa
            except GeneratorExit:
                self._raise('Unexpected end of input')

            if not c:
                self._raise(f'Unterminated string literal: {self._buf.getvalue()}')

            self._buf.write(c)
            if c == '"' and last != '\\':
                break
            last = c

        raw = self._flip_buf()
        try:
            sv = json.loads(raw)
        except json.JSONDecodeError as e:
            self._raise(f'Invalid string literal: {raw!r}', e)

        yield self._make_tok('STRING', sv, raw, pos)

        return self._do_main()

    def _do_number(self, c: str):
        check.state(self._buf.tell() == 0)
        self._buf.write(c)

        pos = self.pos

        while True:
            try:
                c = self._char_in((yield None))  # noqa
            except GeneratorExit:
                self._raise('Unexpected end of input')

            if not c:
                break

            if not (c.isdigit() or c in '.eE+-'):
                break
            self._buf.write(c)

        raw = self._flip_buf()

        #

        if not NUMBER_PAT.fullmatch(raw):
            # Can only be -Infinity

            if not c:
                self._raise('Unexpected end of input')

            raw += c
            try:
                for _ in range(7):
                    raw += self._char_in((yield None))  # noqa
            except GeneratorExit:
                self._raise('Unexpected end of input')

            if raw != '-Infinity':
                self._raise(f'Invalid number format: {raw}')

            tk, tv = CONST_TOKENS[raw]
            yield self._make_tok(tk, tv, raw, pos)

            return self._do_main()

        #

        if '.' in raw or 'e' in raw or 'E' in raw:
            nv = float(raw)
        else:
            nv = int(raw)
        yield self._make_tok('NUMBER', nv, raw, pos)

        #

        if not c:
            return None

        if c in CONTROL_TOKENS:
            yield self._make_tok(CONTROL_TOKENS[c], c, c, pos)

        elif not c.isspace():
            self._raise(f'Unexpected character after number: {c}')

        return self._do_main()

    def _do_const(self, c: str):
        pos = self.pos
        raw = c
        while True:
            try:
                raw += self._char_in((yield None))  # noqa
            except GeneratorExit:
                self._raise('Unexpected end of input')

            if raw in CONST_TOKENS:
                break

            if len(raw) > 8:  # None of the keywords are longer than 8 characters
                self._raise(f'Invalid literal: {raw}')

        tk, tv = CONST_TOKENS[raw]
        yield self._make_tok(tk, tv, raw, pos)

        return self._do_main()
