import dataclasses as dc
import io
import json
import re
import typing as ta

from ... import check
from ...genmachine import GenMachine


ValueTokenKind: ta.TypeAlias = ta.Literal[
    'STRING',
    'NUMBER',

    'SPECIAL_NUMBER',
    'BOOLEAN',
    'NULL',
]

ControlTokenKind: ta.TypeAlias = ta.Literal[
    'LBRACE',
    'RBRACE',
    'LBRACKET',
    'RBRACKET',
    'COMMA',
    'COLON',
]

TokenKind: ta.TypeAlias = ValueTokenKind | ControlTokenKind

TokenValue: ta.TypeAlias = str | float | int | None


class Token(ta.NamedTuple):
    kind: TokenKind
    value: TokenValue
    raw: str

    ofs: int
    line: int
    col: int

    def __iter__(self):
        raise TypeError


NUMBER_PAT = re.compile(r'-?(?:0|[1-9]\d*)(?:\.\d+)?(?:[eE][+-]?\d+)?')

VALUE_TOKEN_KINDS = frozenset(check.isinstance(a, str) for a in ta.get_args(ValueTokenKind))

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


@dc.dataclass(frozen=True)
class JsonLexError(Exception):
    message: str

    ofs: int
    line: int
    col: int


class JsonStreamLexer(GenMachine[str, Token]):
    def __init__(self) -> None:
        self._ofs = 0
        self._line = 0
        self._col = 0

        self._buf = io.StringIO()

        super().__init__(self._do_main())

    def _char_in(self, c: str) -> str:
        if len(c) != 1:
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
            value: TokenValue,
            raw: str,
    ) -> ta.Sequence[Token]:
        tok = Token(
            kind,
            value,
            raw,
            self._ofs,
            self._line,
            self._col,
        )
        return (tok,)

    def _flip_buf(self) -> str:
        raw = self._buf.getvalue()
        self._buf.seek(0)
        self._buf.truncate()
        return raw

    def _raise(self, msg: str) -> ta.NoReturn:
        raise JsonLexError(msg, self._ofs, self._line, self._col)

    def _do_main(self):
        while True:
            c = self._char_in((yield None))  # noqa

            if c.isspace():
                continue

            if c in CONTROL_TOKENS:
                yield self._make_tok(CONTROL_TOKENS[c], c, c)
                continue

            if c == '"':
                return self._do_string()

            if c.isdigit() or c == '-':
                return self._do_number(c)

            if c in 'tfnIN':
                return self._do_const(c)

            self._raise(f'Unexpected character: {c}')

    def _do_string(self):
        self._buf.write('"')

        last = None
        while True:
            try:
                c = self._char_in((yield None))  # noqa
            except GeneratorExit:
                self._raise('Unexpected end of input')

            self._buf.write(c)
            if c == '"' and last != '\\':
                break
            last = c

        raw = self._flip_buf()
        sv = json.loads(raw)
        yield self._make_tok('STRING', sv, raw)

        return self._do_main()

    def _do_number(self, c: str):
        self._buf.write(c)

        while True:
            try:
                c = self._char_in((yield None))  # noqa
            except GeneratorExit:
                self._raise('Unexpected end of input')

            if not (c.isdigit() or c in '.eE+-'):
                break
            self._buf.write(c)

        raw = self._flip_buf()
        if not NUMBER_PAT.fullmatch(raw):
            raw += c
            try:
                for _ in range(7):
                    raw += self._char_in((yield None))  # noqa
            except GeneratorExit:
                self._raise('Unexpected end of input')

            if raw != '-Infinity':
                self._raise(f'Invalid number format: {raw}')

            tk, tv = CONST_TOKENS[raw]
            yield self._make_tok(tk, tv, raw)

            return self._do_main()

        nv = float(raw) if '.' in raw or 'e' in raw or 'E' in raw else int(raw)
        yield self._make_tok('NUMBER', nv, raw)

        if c in CONTROL_TOKENS:
            yield self._make_tok(CONTROL_TOKENS[c], c, c)
        elif not c.isspace():
            self._raise(f'Unexpected character after number: {c}')

        return self._do_main()

    def _do_const(self, c: str):
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
        yield self._make_tok(tk, tv, raw)

        return self._do_main()


class JsonStreamObject(list):
    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({super().__repr__()})'


class JsonStreamValueBuilder(GenMachine[Token, ta.Any]):
    def __init__(self) -> None:
        super().__init__(self._do_value())

        self._stack = []

    def _emit_value(self, v: ta.Any):
        if not self._stack:
            return ((v,), None)

        tt, tv = self._stack[-1]
        if tt == 'pair':
            self._stack.pop()
            if not self._stack:
                raise self.StateError

            tt2, tv2 = self._stack[-1]
            if tt2 == 'object':
                tv2.append((tv, v))
                return ((), self._do_after_pair())

            else:
                raise NotImplementedError

        elif tt == 'array':
            tv.append(v)
            return ((), self._do_after_element())

        else:
            raise NotImplementedError

    def _do_value(self):
        tok = yield None

        if tok.kind in VALUE_TOKEN_KINDS:
            y, r = self._emit_value(tok.value)
            yield y
            return r

        elif tok.kind == 'LBRACE':
            return self._do_object()

        elif tok.kind == 'LBRACKET':
            return self._do_array()

        else:
            raise NotImplementedError

    def _do_object(self):
        self._stack.append(('object', JsonStreamObject()))
        return self._do_object_body()

    def _do_object_body(self):
        try:
            tok = yield None
        except GeneratorExit:
            raise self.StateError

        if tok.kind == 'STRING':
            k = tok.value

            try:
                tok = yield None
            except GeneratorExit:
                raise self.StateError
            if tok.kind != 'COLON':
                raise self.StateError

            self._stack.append(('pair', k))
            return self._do_value()

        raise NotImplementedError

    def _do_after_pair(self):
        try:
            tok = yield None
        except GeneratorExit:
            raise self.StateError

        if tok.kind == 'COMMA':
            return self._do_object_body()

        elif tok.kind == 'RBRACE':
            if not self._stack:
                raise self.StateError

            tt, tv = self._stack.pop()
            if tt != 'object':
                raise self.StateError

            y, r = self._emit_value(('object', tv))
            yield y
            return r

        else:
            raise NotImplementedError

    def _do_array(self):
        self._stack.append(('array', []))
        return self._do_value()

    def _do_after_element(self):
        try:
            tok = yield None
        except GeneratorExit:
            raise self.StateError

        if tok.kind == 'COMMA':
            return self._do_value()

        elif tok.kind == 'RBRACKET':
            if not self._stack:
                raise self.StateError

            tt, tv = self._stack.pop()
            if tt != 'array':
                raise self.StateError

            y, r = self._emit_value(('array', tv))
            yield y
            return r

        else:
            raise NotImplementedError
