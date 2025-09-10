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
from .... import lang
from ....funcs.genmachine import GenMachine
from .errors import JsonStreamError


with lang.auto_proxy_import(globals()):
    import unicodedata


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


@dc.dataclass()
class JsonStreamLexError(JsonStreamError):
    message: str

    pos: Position


class JsonStreamLexer(GenMachine[str, Token]):
    def __init__(
            self,
            *,
            include_raw: bool = False,

            allow_extended_space: bool = False,
            include_space: bool = False,

            allow_comments: bool = False,
            include_comments: bool = False,

            allow_single_quotes: bool = False,
            string_literal_parser: ta.Callable[[str], str] | None = None,

            allow_extended_number_literals: bool = False,
            number_literal_parser: ta.Callable[[str], ta.Any] | None = None,

            allow_extended_idents: bool = False,
    ) -> None:
        self._include_raw = include_raw

        self._allow_extended_space = allow_extended_space
        self._include_space = include_space

        self._allow_comments = allow_comments
        self._include_comments = include_comments

        self._allow_single_quotes = allow_single_quotes
        if string_literal_parser is None:
            string_literal_parser = json.loads  # noqa
        self._string_literal_parser = string_literal_parser

        self._allow_extended_number_literals = allow_extended_number_literals
        self._number_literal_parser = number_literal_parser

        self._allow_extended_idents = allow_extended_idents

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
            raw: str | None,
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

    def _do_main(self, peek: str | None = None):
        while True:
            if peek is not None:
                c = peek
                peek = None
            else:
                c = self._char_in((yield None))  # noqa

            if not c:
                return None

            if c.isspace() or (self._allow_extended_space and c in (
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
            )):
                if self._include_space:
                    yield self._make_tok('SPACE', c, c, self.pos)
                continue

            if c in CONTROL_TOKENS:
                yield self._make_tok(CONTROL_TOKENS[c], c, c, self.pos)
                continue

            if c == '"' or (self._allow_single_quotes and c == "'"):
                return self._do_string(c)

            if c.isdigit() or c == '-' or (self._allow_extended_number_literals and c in '.+'):
                return self._do_number(c)

            if self._allow_comments and c == '/':
                return self._do_comment()

            if self._allow_extended_idents:
                return self._do_extended_ident(c)

            if c in 'tfnIN':
                return self._do_const(c)

            self._raise(f'Unexpected character: {c}')

    def _do_string(self, q: str):
        check.state(self._buf.tell() == 0)
        self._buf.write(q)

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
            if c == q and last != '\\':
                break
            last = c

        raw = self._flip_buf()
        try:
            sv = self._string_literal_parser(raw)
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

            if not (c.isdigit() or c in '.eE+-' or (self._allow_extended_number_literals and c in 'xXabcdefABCDEF')):
                break
            self._buf.write(c)

        raw = self._flip_buf()

        #

        if self._allow_extended_number_literals:
            p = 1 if raw[0] in '+-' else 0
            if (len(raw) - p) > 1 and raw[p] == '0' and raw[p + 1].isdigit():
                self._raise('Invalid number literal')

        if raw == '-' or (self._allow_extended_number_literals and raw == '+'):
            for svs in [
                'Infinity',
                *(['NaN'] if self._allow_extended_number_literals else []),
            ]:
                if c != svs[0]:
                    continue

                if not c:
                    self._raise('Unexpected end of input')

                raw += c
                try:
                    for _ in range(len(svs) - 1):
                        c = self._char_in((yield None))  # noqa
                        if not c:
                            break
                        raw += c
                except GeneratorExit:
                    self._raise('Unexpected end of input')

                if raw[1:] != svs:
                    self._raise(f'Invalid number format: {raw}')

                if raw[0] == '+':
                    raw = raw[1:]

                yield self._make_tok('IDENT', raw, raw, pos)

                return self._do_main()

        #

        nv: ta.Any

        if (np := self._number_literal_parser) is not None:
            nv = np(raw)

        else:
            if not NUMBER_PAT.fullmatch(raw):
                self._raise(f'Invalid number format: {raw}')

            if '.' in raw or 'e' in raw or 'E' in raw:
                nv = float(raw)
            else:
                nv = int(raw)

        yield self._make_tok('NUMBER', nv, raw, pos)

        #

        if not c:
            return None

        return self._do_main(c)

    def _do_const(self, c: str):
        pos = self.pos
        raw = c
        while True:
            try:
                raw += self._char_in((yield None))  # noqa
            except GeneratorExit:
                self._raise('Unexpected end of input')

            if raw in CONST_IDENT_VALUES:
                break

            if len(raw) > MAX_CONST_IDENT_LEN:
                self._raise(f'Invalid literal: {raw}')

        yield self._make_tok('IDENT', raw, raw, pos)

        return self._do_main()

    def _do_unicode_escape(self):
        try:
            c = self._char_in((yield None))  # noqa
        except GeneratorExit:
            self._raise('Unexpected end of input')

        if c != 'u':
            self._raise('Illegal identifier escape')

        ux = []
        for _ in range(4):
            try:
                c = self._char_in((yield None))  # noqa
            except GeneratorExit:
                self._raise('Unexpected end of input')

            if c not in '0123456789abcdefABCDEF':
                self._raise('Illegal identifier escape')

            ux.append(c)

        return chr(int(''.join(ux), 16))

    def _do_extended_ident(self, c: str):
        check.state(self._buf.tell() == 0)

        if c == '\\':
            c = yield from self._do_unicode_escape()

        elif not (c in '$_' or unicodedata.category(c).startswith('L')):
            self._raise('Illegal identifier start')

        self._buf.write(c)

        pos = self.pos

        while True:
            try:
                c = self._char_in((yield None))  # noqa
            except GeneratorExit:
                self._raise('Unexpected end of input')

            if c == '\\':
                c = yield from self._do_unicode_escape()
                self._buf.write(c)
                continue

            if not c:
                break

            if c not in '$_\u200C\u200D':
                uc = unicodedata.category(c)
                if not (uc.startswith(('L', 'M', 'N')) or uc == 'Pc'):
                    break

            self._buf.write(c)

        raw = self._flip_buf()

        yield self._make_tok('IDENT', raw, raw, pos)

        return self._do_main(c)

    def _do_comment(self):
        check.state(self._buf.tell() == 0)

        pos = self.pos
        try:
            oc = self._char_in((yield None))  # noqa
        except GeneratorExit:
            self._raise('Unexpected end of input')

        if oc == '/':
            while True:
                try:
                    ic = self._char_in((yield None))  # noqa
                except GeneratorExit:
                    self._raise('Unexpected end of input')

                if not ic or ic == '\n':
                    break

                if self._include_comments:
                    self._buf.write(ic)

            if self._include_comments:
                cmt = self._flip_buf()
                raw = f'//{cmt}\n' if self._include_raw else None
                yield self._make_tok('COMMENT', cmt, raw, pos)

            if not ic:
                return

        elif oc == '*':
            lc: str | None = None
            while True:
                try:
                    ic = self._char_in((yield None))  # noqa
                except GeneratorExit:
                    self._raise('Unexpected end of input')

                if lc == '*' and ic == '/':
                    break

                if lc is not None and self._include_comments:
                    self._buf.write(lc)
                lc = ic

            if self._include_comments:
                cmt = self._flip_buf()
                raw = f'/*{cmt}*/' if self._include_raw else None
                yield self._make_tok('COMMENT', cmt, raw, pos)

        else:
            self._raise(f'Unexpected character after comment start: {oc}')

        return self._do_main()
