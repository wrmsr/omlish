import dataclasses as dc
import typing as ta

from .... import lang
from ....funcs.genmachine import GenMachine
from .errors import JsonStreamError
from .lexing import CONST_IDENT_VALUES
from .lexing import SCALAR_VALUE_TYPES
from .lexing import VALUE_TOKEN_KINDS
from .lexing import Position
from .lexing import ScalarValue
from .lexing import Token


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


Event: ta.TypeAlias = ta.Union[  # noqa
    type[BeginObject],
    Key,
    type[EndObject],

    type[BeginArray],
    type[EndArray],

    ScalarValue,
]


class Events(lang.Namespace):
    BeginObject = BeginObject
    Key = Key
    EndObject = EndObject

    BeginArray = BeginArray
    EndArray = EndArray


##


def yield_parser_events(obj: ta.Any) -> ta.Iterator[Event]:
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


##


@dc.dataclass()
class JsonStreamParseError(JsonStreamError):
    message: str

    pos: Position | None = None


class JsonStreamObject(list):
    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({super().__repr__()})'


class JsonStreamParser(GenMachine[Token, Event]):
    def __init__(
            self,
            *,
            allow_trailing_commas: bool = False,

            allow_extended_idents: bool = False,
    ) -> None:
        self._allow_trailing_commas = allow_trailing_commas

        self._allow_extended_idents = allow_extended_idents

        self._stack: list[ta.Literal['OBJECT', 'KEY', 'ARRAY']] = []

        super().__init__(self._do_value())

    #

    def _next_tok(self):
        while True:
            tok = yield None

            if tok.kind != 'SPACE' and tok.kind != 'COMMENT':
                return tok

    #

    def _emit_event(self, v):
        if not self._stack:
            return ((v,), self._do_value())

        tt = self._stack[-1]
        if tt == 'KEY':
            self._stack.pop()
            if not self._stack:
                raise JsonStreamParseError('Unexpected key')

            tt2 = self._stack[-1]
            if tt2 == 'OBJECT':
                return ((v,), self._do_after_pair())

            else:
                raise JsonStreamParseError('Unexpected key')

        elif tt == 'ARRAY':
            return ((v,), self._do_after_element())

        else:
            raise JsonStreamParseError(f'Unexpected value: {v!r}')

    #

    def _do_value(self, *, must_be_present: bool = False):
        try:
            tok = yield from self._next_tok()
        except GeneratorExit:
            if self._stack:
                raise JsonStreamParseError('Expected value') from None
            else:
                raise
        # except Exception as e:
        #     raise

        if tok.kind in VALUE_TOKEN_KINDS:
            y, r = self._emit_event(tok.value)
            yield y
            return r

        elif tok.kind == 'IDENT':
            try:
                cv = CONST_IDENT_VALUES[tok.value]
            except KeyError:
                raise JsonStreamParseError('Expected value', tok.pos) from None
            y, r = self._emit_event(cv)
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

        elif must_be_present:
            raise JsonStreamParseError('Expected value', tok.pos)

        elif tok.kind == 'RBRACKET':
            y, r = self._emit_end_array()
            yield y
            return r

        else:
            raise JsonStreamParseError('Expected value', tok.pos)

    #

    def _emit_begin_object(self):
        self._stack.append('OBJECT')
        return ((BeginObject,), self._do_object_body())

    def _emit_end_object(self):
        if not self._stack:
            raise JsonStreamParseError('Unexpected end object')

        tt = self._stack.pop()
        if tt != 'OBJECT':
            raise JsonStreamParseError('Unexpected end object')

        return self._emit_event(EndObject)

    def _do_object_body(self, *, must_be_present: bool = False):
        try:
            tok = yield from self._next_tok()
        except GeneratorExit:
            raise JsonStreamParseError('Expected object body') from None

        if tok.kind == 'STRING' or (self._allow_trailing_commas and tok.kind == 'IDENT'):
            k = tok.value

            try:
                tok = yield from self._next_tok()
            except GeneratorExit:
                raise JsonStreamParseError('Expected key') from None
            if tok.kind != 'COLON':
                raise JsonStreamParseError('Expected colon', tok.pos)

            yield (Key(k),)
            self._stack.append('KEY')
            return self._do_value()

        elif must_be_present:
            raise JsonStreamParseError('Expected value', tok.pos)

        elif tok.kind == 'RBRACE':
            y, r = self._emit_end_object()
            yield y
            return r

        else:
            raise JsonStreamParseError('Expected value', tok.pos)

    def _do_after_pair(self):
        try:
            tok = yield from self._next_tok()
        except GeneratorExit:
            raise JsonStreamParseError('Expected continuation') from None

        if tok.kind == 'COMMA':
            return self._do_object_body(must_be_present=not self._allow_trailing_commas)

        elif tok.kind == 'RBRACE':
            y, r = self._emit_end_object()
            yield y
            return r

        else:
            raise JsonStreamParseError('Expected continuation', tok.pos)

    #

    def _emit_begin_array(self):
        self._stack.append('ARRAY')
        return ((BeginArray,), self._do_value())

    def _emit_end_array(self):
        if not self._stack:
            raise JsonStreamParseError('Expected end array')

        tt = self._stack.pop()
        if tt != 'ARRAY':
            raise JsonStreamParseError('Unexpected end array')

        return self._emit_event(EndArray)

    def _do_after_element(self):
        try:
            tok = yield from self._next_tok()
        except GeneratorExit:
            raise JsonStreamParseError('Expected continuation') from None

        if tok.kind == 'COMMA':
            return self._do_value(must_be_present=not self._allow_trailing_commas)

        elif tok.kind == 'RBRACKET':
            y, r = self._emit_end_array()
            yield y
            return r

        else:
            raise JsonStreamParseError('Expected continuation', tok.pos)
