"""
TODO:
 - max buf size
 - max recursion depth
"""
import dataclasses as dc
import io
import json
import re
import typing as ta

from ... import check
from ... import lang
from ...genmachine import GenMachine


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


class Token(ta.NamedTuple):
    kind: TokenKind
    value: ScalarValue
    raw: str | None

    ofs: int
    line: int
    col: int

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


@dc.dataclass(frozen=True)
class JsonLexError(Exception):
    message: str

    ofs: int
    line: int
    col: int


class JsonStreamLexer(GenMachine[str, Token]):
    def __init__(
            self,
            *,
            include_raw: bool = False,
    ) -> None:
        self._include_raw = include_raw

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
            value: ScalarValue,
            raw: str,
    ) -> ta.Sequence[Token]:
        tok = Token(
            kind,
            value,
            raw if self._include_raw else None,
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

        if '.' in raw or 'e' in raw or 'E' in raw:
            nv = float(raw)
        else:
            nv = int(raw)
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


##


class BeginObject(lang.Marker):
    pass


class Key(ta.NamedTuple):
    key: str


class EndObject(lang.Marker):
    pass


class BeginArray(lang.Marker):
    pass


class EndArray(lang.Marker):
    pass


JsonStreamParserEvent: ta.TypeAlias = ta.Union[  # noqa
    type[BeginObject],
    Key,
    type[EndObject],

    type[BeginArray],
    type[EndArray],

    ScalarValue,
]


def yield_parser_events(obj: ta.Any) -> ta.Generator[JsonStreamParserEvent, None, None]:
    if isinstance(obj, SCALAR_VALUE_TYPES):
        yield obj  # type: ignore

    elif isinstance(obj, ta.Mapping):
        yield BeginObject
        for k, v in obj.items():
            yield Key(k)
            yield from yield_parser_events(v)
        yield EndObject

    elif isinstance(obj, ta.Sequence):
        yield BeginArray
        for v in obj:
            yield from yield_parser_events(v)
        yield EndArray

    else:
        raise TypeError(obj)


class JsonStreamParser(GenMachine[Token, JsonStreamParserEvent]):
    def __init__(self) -> None:
        super().__init__(self._do_value())

        self._stack: list[ta.Literal['OBJECT', 'KEY', 'ARRAY']] = []

    #

    def _emit_event(self, v):
        if not self._stack:
            return ((v,), self._do_value())

        tt = self._stack[-1]
        if tt == 'KEY':
            self._stack.pop()
            if not self._stack:
                raise self.StateError

            tt2 = self._stack[-1]
            if tt2 == 'OBJECT':
                return ((v,), self._do_after_pair())

            else:
                raise self.StateError

        elif tt == 'ARRAY':
            return ((v,), self._do_after_element())

        else:
            raise self.StateError

    #

    def _do_value(self):
        try:
            tok = yield None
        except GeneratorExit:
            if self._stack:
                raise self.StateError from None
            else:
                raise

        if tok.kind in VALUE_TOKEN_KINDS:
            y, r = self._emit_event(tok.value)
            yield y
            return r

        elif tok.kind == 'LBRACE':
            y, r = self._emit_begin_object()
            yield y
            return r

        elif tok.kind == 'LBRACKET':
            y, r = self._emit_begin_array()
            yield y
            return r

        elif tok.kind == 'RBRACKET':
            y, r = self._emit_end_array()
            yield y
            return r

        else:
            raise self.StateError

    #

    def _emit_begin_object(self):
        self._stack.append('OBJECT')
        return ((BeginObject,), self._do_object_body())

    def _emit_end_object(self):
        if not self._stack:
            raise self.StateError

        tt = self._stack.pop()
        if tt != 'OBJECT':
            raise self.StateError

        return self._emit_event(EndObject)

    def _do_object_body(self):
        try:
            tok = yield None
        except GeneratorExit:
            raise self.StateError from None

        if tok.kind == 'STRING':
            k = tok.value

            try:
                tok = yield None
            except GeneratorExit:
                raise self.StateError from None
            if tok.kind != 'COLON':
                raise self.StateError

            yield (Key(k),)
            self._stack.append('KEY')
            return self._do_value()

        elif tok.kind == 'RBRACE':
            y, r = self._emit_end_object()
            yield y
            return r

        else:
            raise self.StateError

    def _do_after_pair(self):
        try:
            tok = yield None
        except GeneratorExit:
            raise self.StateError from None

        if tok.kind == 'COMMA':
            return self._do_object_body()

        elif tok.kind == 'RBRACE':
            y, r = self._emit_end_object()
            yield y
            return r

        else:
            raise self.StateError

    #

    def _emit_begin_array(self):
        self._stack.append('ARRAY')
        return ((BeginArray,), self._do_value())

    def _emit_end_array(self):
        if not self._stack:
            raise self.StateError

        tt = self._stack.pop()
        if tt != 'ARRAY':
            raise self.StateError

        return self._emit_event(EndArray)

    def _do_after_element(self):
        try:
            tok = yield None
        except GeneratorExit:
            raise self.StateError from None

        if tok.kind == 'COMMA':
            return self._do_value()

        elif tok.kind == 'RBRACKET':
            y, r = self._emit_end_array()
            yield y
            return r

        else:
            raise self.StateError


##


class JsonObjectBuilder(GenMachine[JsonStreamParserEvent, ta.Any]):
    def __init__(
            self,
            *,
            yield_object_lists: bool = False,
    ) -> None:
        self._stack: list[JsonStreamObject | list | Key] = []
        self._yield_object_lists = yield_object_lists

        super().__init__(self._do())

    def _do(self):
        stk = self._stack

        def emit_value(v):
            if not stk:
                return (v,)

            tv = stk[-1]
            if isinstance(tv, Key):
                stk.pop()
                if not stk:
                    raise self.StateError

                tv2 = stk[-1]
                if not isinstance(tv2, JsonStreamObject):
                    raise self.StateError

                tv2.append((tv.key, v))
                return ()

            elif isinstance(tv, list):
                tv.append(v)
                return ()

            else:
                raise self.StateError

        while True:
            try:
                e = yield None
            except GeneratorExit:
                if stk:
                    raise self.StateError from None
                else:
                    raise

            #

            if isinstance(e, SCALAR_VALUE_TYPES):
                if t := emit_value(e):
                    yield t
                continue

            #

            elif e is BeginObject:
                stk.append(JsonStreamObject())
                continue

            elif isinstance(e, Key):
                if not stk or not isinstance(stk[-1], JsonStreamObject):
                    raise self.StateError

                stk.append(e)
                continue

            elif e is EndObject:
                tv: ta.Any
                if not stk or not isinstance(tv := stk.pop(), JsonStreamObject):
                    raise self.StateError

                if not self._yield_object_lists:
                    tv = dict(tv)

                if t := emit_value(tv):
                    yield t
                continue

            #

            elif e is BeginArray:
                stk.append([])
                continue

            elif e is EndArray:
                if not stk or not isinstance(tv := stk.pop(), list):
                    raise self.StateError

                if t := emit_value(tv):
                    yield t
                continue

            #

            else:
                raise TypeError(e)
