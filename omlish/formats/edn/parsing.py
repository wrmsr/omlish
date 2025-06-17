# ruff: noqa: PYI055 UP007
"""
TODO:
 - \u0123 in strings
 - https://clojure.org/reference/reader
 - reader meta - ^:foo
 - read table
"""
import dataclasses as dc
import datetime
import enum
import io
import re
import typing as ta

from ... import check
from ...funcs.genmachine import GenMachine
from .lexing import Position
from .lexing import StreamLexer
from .lexing import Token
from .values import Char
from .values import Collection
from .values import Keyword
from .values import List
from .values import Map
from .values import Set
from .values import Symbol
from .values import Tagged
from .values import Vector


##


WORD_CONST_VALUES: ta.Mapping[str, ta.Any] = {
    'true': True,
    'false': False,
    'nil': None,

    '##Inf': float('inf'),
    '##-Inf': float('-inf'),
    '##NaN': float('nan'),
}


STRING_ESCAPE_MAP: ta.Mapping[str, str] = {
    '"': '"',
    '\\': '\\',
    'b': '\b',
    'f': '\f',
    'n': '\n',
    'r': '\r',
    't': '\t',
}


CHAR_ESCAPE_MAP: ta.Mapping[str, str] = {
    'backspace': '\b',
    'formfeed': '\f',
    'newline': '\n',
    'return': '\r',
    'space': ' ',
    'tab': '\t',
}


##


@dc.dataclass()
class StreamParseError(Exception):
    message: str

    pos: Position | None = None


@dc.dataclass(frozen=True)
class MetaMaker:
    fn: ta.Callable[..., ta.Any]

    def __call__(self, *args: ta.Any, meta: ta.Any | None = None) -> ta.Any:
        return self.fn(*args, meta=meta)


class StreamParser(GenMachine[Token, ta.Any]):
    DEFAULT_TAG_HANDLERS: ta.ClassVar[ta.Mapping[str, ta.Callable[..., ta.Any]]] = {
        'inst': lambda val: datetime.datetime.fromisoformat(val) if isinstance(val, str) else None,
    }

    def __init__(
            self,
            *,
            keyword_maker: ta.Callable[..., ta.Any] = MetaMaker(Keyword),
            char_maker: ta.Callable[..., ta.Any] = MetaMaker(Char),
            symbol_maker: ta.Callable[..., ta.Any] = MetaMaker(Symbol),

            list_maker: ta.Callable[..., ta.Any] = MetaMaker(List.new),
            vector_maker: ta.Callable[..., ta.Any] = MetaMaker(Vector.new),
            set_maker: ta.Callable[..., ta.Any] = MetaMaker(Set.new),
            map_maker: ta.Callable[..., ta.Any] = MetaMaker(Map.new),

            tag_handlers: ta.Mapping[str, ta.Callable[..., ta.Any]] | None = None,
    ) -> None:
        self._keyword_maker = keyword_maker
        self._char_maker = char_maker
        self._symbol_maker = symbol_maker

        self._list_maker = list_maker
        self._vector_maker = vector_maker
        self._set_maker = set_maker
        self._map_maker = map_maker

        self._tag_handlers = {
            **self.DEFAULT_TAG_HANDLERS,
            **(tag_handlers or {}),
        }

        self._stack: list[
            tuple[
                ta.Union[
                    type[Collection],
                    StreamParser._StackSpecial,
                ],
                list[ta.Any],
            ],
        ] = []

        super().__init__(self._do_main())

    class _StackSpecial(enum.Enum):  # noqa
        DISCARD = enum.auto()
        TAG = enum.auto()

    def _emit_value(self, value: ta.Any) -> tuple[ta.Any, ...]:
        while self._stack and self._stack[-1][0] is StreamParser._StackSpecial.TAG:
            cc, cl = self._stack.pop()
            ts = check.non_empty_str(check.single(cl))
            value = Tagged(ts, value)

        if not self._stack:
            return (value,)

        cc, cl = self._stack[-1]

        if cc is StreamParser._StackSpecial.DISCARD:
            check.empty(cl)
            self._stack.pop()
            return ()

        elif cc is StreamParser._StackSpecial.TAG:
            ts = check.non_empty_str(check.single(cl))
            self._stack.pop()
            tv = Tagged(ts, value)
            return (tv,)

        elif cc is Map:
            if cl and len(cl[-1]) < 2:
                cl[-1] = (*cl[-1], value)
            else:
                cl.append((value,))
            return ()

        elif isinstance(cc, type) and issubclass(cc, Collection):
            cl.append(value)
            return ()

        else:
            raise RuntimeError(cc)

    def _do_main(self):
        while True:
            tok: Token
            try:
                tok = yield None  # noqa
            except GeneratorExit:
                if self._stack:
                    raise StreamParseError('Expected value') from None
                else:
                    raise

            # ignored

            if tok.kind in ('SPACE', 'COMMENT'):
                continue

            # scalars

            value: ta.Any

            if tok.kind == 'STRING':
                value = self._parse_string(tok)

            elif tok.kind == 'CHAR':
                value = self._parse_char(tok)

            elif tok.kind == 'WORD':
                if tok.src.startswith('#'):
                    # FIXME: more dispatching
                    self._stack.append((StreamParser._StackSpecial.TAG, [tok.src[1:]]))
                    continue

                else:
                    value = self._parse_word(tok)

            # open

            elif tok.kind == 'LPAREN':
                self._stack.append((List, []))
                continue

            elif tok.kind == 'LBRACKET':
                self._stack.append((Vector, []))
                continue

            elif tok.kind == 'HASH_LBRACE':
                self._stack.append((Set, []))
                continue

            elif tok.kind == 'LBRACE':
                self._stack.append((Map, []))
                continue

            elif tok.kind == 'HASH_UNDERSCORE':
                self._stack.append((StreamParser._StackSpecial.DISCARD, []))
                continue

            # close

            elif tok.kind == 'RPAREN':
                cc, cl = self._stack.pop()
                check.state(cc is List)
                value = self._list_maker(cl)

            elif tok.kind == 'RBRACKET':
                cc, cl = self._stack.pop()
                check.state(cc is Vector)
                value = self._vector_maker(cl)

            elif tok.kind == 'RBRACE':
                cc, cl = self._stack.pop()

                if cc is Set:
                    value = self._set_maker(cl)

                elif cc is Map:
                    if cl and len(cl[-1]) != 2:
                        raise RuntimeError('Mismatched map entries')
                    value = self._map_maker(cl)

                else:
                    raise RuntimeError(cc)

            # nyi

            elif tok.kind == 'META':
                raise NotImplementedError

            elif tok.kind == 'QUOTE':
                raise NotImplementedError

            # failure

            else:
                raise ValueError(tok.kind)

            # emit

            if (ev := self._emit_value(value)):
                yield ev

    def _parse_string(self, tok: Token) -> str:
        check.state(tok.kind == 'STRING')
        src = tok.src
        check.state(src[0] == '"')
        check.state(src[-1] == '"')
        check.state(len(src) > 1)

        p = 1
        end = len(src) - 1
        if src.find('\\', p, end) < 0:
            return src[1:-1]

        sb = io.StringIO()
        while True:
            if (n := src.find('\\', p, end)) < 0:
                sb.write(src[p:end])
                break

            sb.write(src[p:n])
            p = n + 1
            check.state(p < end)
            x = src[p]
            p += 1

            if x == 'u':
                check.state(p < end - 4)
                r = chr(int(src[p:p + 4], 16))
                p += 4

            else:
                r = STRING_ESCAPE_MAP[x]

            sb.write(r)

        return sb.getvalue()

    def _parse_char(self, tok: Token) -> ta.Any:
        check.state(tok.kind == 'CHAR')
        src = tok.src
        check.state(len(src) > 1)
        check.state(src.startswith('\\'))

        if len(src) == 2:
            c = src[1]

        elif src[1] == 'u':
            check.state(len(src) == 6)
            c = chr(int(src[2:], 16))  # noqa

        elif src[1] == 'o':
            # \oXXX -> octal
            raise NotImplementedError

        else:
            c = CHAR_ESCAPE_MAP[src[1:]]

        return self._char_maker(c)

    _INT_PAT = re.compile(r'[-+]?(0|[1-9][0-9]*)N?')
    _FLOAT_PAT = re.compile(r'[-+]?(0|[1-9][0-9]*)(\.[0-9]+)?([eE][+-]?(0|[1-9][0-9]*))?M?')

    def _parse_word(self, tok: Token) -> ta.Any:
        check.state(tok.kind == 'WORD')
        src = tok.src
        check.non_empty_str(src)
        check.state(not src.startswith('#'))

        if src in WORD_CONST_VALUES:
            return WORD_CONST_VALUES[src]

        elif src.startswith(':'):
            return self._keyword_maker(src[1:])

        elif self._INT_PAT.fullmatch(src):
            # FIXME: numbers lol
            # 2r101010, 052, 8r52, 0x2a, 36r16, and 42 are all the same Long.
            # Floating point numbers are read as Doubles; with M suffix they are read as BigDecimals.
            # Ratios are supported, e.g. 22/7.
            if src.endswith('N'):
                return int(src[:-1])

            else:
                return int(src)

        elif self._FLOAT_PAT.fullmatch(src):
            return float(src)

        else:
            return self._symbol_maker(src)


##


def parse_list(src: str, **kwargs: ta.Any) -> list[ta.Any]:
    r: list[ta.Any] = []
    with StreamLexer() as l:
        with StreamParser(**kwargs) as p:
            for c in [*src, '']:
                for t in l(c):
                    for o in p(t):
                        r.append(o)  # noqa
    return r


def parse(src: str, **kwargs: ta.Any) -> ta.Any | None:
    values = parse_list(src, **kwargs)
    if not values:
        return None
    return check.single(values)
