r"""
https://github.com/edn-format/edn
https://github.com/antlr/grammars-v4/blob/master/edn/edn.g4
https://github.com/jorinvo/edn-data/blob/1e5824f63803eb58f35e98839352000053d47115/src/parse.ts
https://clojure.org/reference/reader#_extensible_data_notation_edn
"""
import dataclasses as dc
import io
import typing as ta

from ... import check
from ...funcs.genmachine import GenMachine


##


TokenKind: ta.TypeAlias = ta.Literal[
    'STRING',
    'CHAR',
    'WORD',
    'COMMENT',

    'LPAREN',
    'RPAREN',
    'LBRACKET',
    'RBRACKET',
    'HASH_LBRACE',
    'LBRACE',
    'RBRACE',

    'HASH_UNDERSCORE',
    'META',
    'QUOTE',

    'SPACE',
]


class Position(ta.NamedTuple):
    ofs: int
    line: int
    col: int


class Token(ta.NamedTuple):
    kind: TokenKind
    src: str

    pos: Position

    def __iter__(self):
        raise TypeError


##


SINGLE_TOKENS: ta.Mapping[str, TokenKind] = {
    '(': 'LPAREN',
    ')': 'RPAREN',
    '[': 'LBRACKET',
    ']': 'RBRACKET',
    '{': 'LBRACE',
    '}': 'RBRACE',

    '^': 'META',
    "'": 'QUOTE',
}


HASH_TOKENS: ta.Mapping[str, TokenKind] = {
    '{': 'HASH_LBRACE',
    '_': 'HASH_UNDERSCORE',
}


WORD_FIRST_SPECIAL_CHARS = ':.*+!-_?$%&=<>.'
WORD_BODY_SPECIAL_CHARS = '/'


##


@dc.dataclass()
class StreamLexError(Exception):
    message: str

    pos: Position


class StreamLexer(GenMachine[str, Token]):
    def __init__(
            self,
            *,
            include_space: bool = False,
    ) -> None:
        self._include_space = include_space

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
        if not isinstance(c, str):
            raise TypeError(c)
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
            src: str,
            pos: Position,
    ) -> ta.Sequence[Token]:
        tok = Token(
            kind,
            src,
            pos,
        )
        return (tok,)

    def _flip_buf(self) -> str:
        src = self._buf.getvalue()
        self._buf.seek(0)
        self._buf.truncate()
        return src

    def _raise(self, msg: str, src: Exception | None = None) -> ta.NoReturn:
        raise StreamLexError(msg, self.pos) from src

    def _do_main(self, p: str | None = None):
        while True:
            if p is not None:
                c = p
                p = None
            else:
                c = self._char_in((yield None))  # noqa

            if not c:
                return None

            if c.isspace() or c == ',':
                if self._include_space:
                    yield self._make_tok('SPACE', c, self.pos)
                continue

            if c in SINGLE_TOKENS:
                yield self._make_tok(SINGLE_TOKENS[c], c, self.pos)
                continue

            if c == ';':
                return self._do_comment()

            if c == '"':
                return self._do_string()

            if c == '\\':
                return self._do_char()

            if c == '#':
                return self._do_hash()

            if (
                    c.isalnum() or
                    c in WORD_FIRST_SPECIAL_CHARS
            ):
                return self._do_word(c)

            self._raise(f'Unexpected input: {c}')

    def _do_comment(self):
        check.state(self._buf.tell() == 0)
        self._buf.write(';')

        pos = self.pos

        while True:
            try:
                c = self._char_in((yield None))  # noqa
            except GeneratorExit:
                self._raise('Unexpected end of input')

            if not c or c == '\n':
                break

            self._buf.write(c)

        src = self._flip_buf()
        yield self._make_tok('COMMENT', src, pos)
        return self._do_main()

    def _do_string(self):
        check.state(self._buf.tell() == 0)
        self._buf.write('"')

        pos = self.pos

        esc = False
        while True:
            try:
                c = self._char_in((yield None))  # noqa
            except GeneratorExit:
                self._raise('Unexpected end of input')

            if not c:
                self._raise(f'Unterminated string literal: {self._buf.getvalue()}')

            self._buf.write(c)
            if esc:
                esc = False
            elif c == '\\':
                esc = True
            elif c == '"':
                break

        src = self._flip_buf()
        yield self._make_tok('STRING', src, pos)
        return self._do_main()

    def _do_char(self):
        check.state(self._buf.tell() == 0)
        self._buf.write('\\')

        pos = self.pos

        while True:
            try:
                c = self._char_in((yield None))  # noqa
            except GeneratorExit:
                self._raise('Unexpected end of input')

            if not c or not (
                    c.isalnum() or
                    c == '\\'
            ):
                break

            self._buf.write(c)

        src = self._flip_buf()
        yield self._make_tok('CHAR', src, pos)
        return self._do_main(c)

    def _do_hash(self):
        check.state(self._buf.tell() == 0)

        pos = self.pos

        try:
            c = self._char_in((yield None))  # noqa
        except GeneratorExit:
            self._raise('Unexpected end of input')

        if (ht := HASH_TOKENS.get(c)) is not None:
            yield self._make_tok(ht, '#' + c, pos)
            return self._do_main()

        elif (
                c.isalnum() or
                c == '#' or
                c in WORD_FIRST_SPECIAL_CHARS
        ):
            return self._do_word('#' + c, pos=pos)

        else:
            self._raise(f'Unexpected input: {c}')

    def _do_word(self, pfx: str, *, pos: Position | None = None):
        check.state(self._buf.tell() == 0)
        self._buf.write(pfx)

        if pos is None:
            pos = self.pos

        while True:
            try:
                c = self._char_in((yield None))  # noqa
            except GeneratorExit:
                self._raise('Unexpected end of input')

            if not c or not (
                    c.isalnum() or
                    c in WORD_FIRST_SPECIAL_CHARS or
                    c in WORD_BODY_SPECIAL_CHARS
            ):
                break

            self._buf.write(c)

        src = self._flip_buf()
        yield self._make_tok('WORD', src, pos)
        return self._do_main(c)
