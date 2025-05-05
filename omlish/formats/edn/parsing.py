"""
TODO:
 - https://clojure.org/reference/reader
 - reader meta - ^:foo
 - read table
"""
# https://github.com/jorinvo/edn-data/blob/1e5824f63803eb58f35e98839352000053d47115/test/parse.test.ts
import dataclasses as dc
import datetime
import enum
import re
import typing as ta

from ... import check
from .values import Char
from .values import Keyword
from .values import List
from .values import Map
from .values import Set
from .values import Symbol
from .values import Tagged
from .values import Vector


##


@dc.dataclass(frozen=True)
class MetaMaker:
    fn: ta.Callable[..., ta.Any]

    def __call__(self, *args: ta.Any, meta: ta.Any | None = None) -> ta.Any:
        return self.fn(*args, meta=meta)


class Parser:
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
        super().__init__()

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

        self._stack: list[tuple[Parser._ParseMode | Parser._StackItem, ta.Any]] = []
        self._mode: Parser._ParseMode = Parser._ParseMode.IDLE
        self._buffer = ''
        self._result: ta.Any = self._UNDEFINED

    #

    class _UNDEFINED:  # noqa
        def __new__(cls, *args, **kwargs):  # noqa
            raise TypeError

    class _ParseMode(enum.Enum):
        IDLE = 0
        STRING = 1
        ESCAPE = 2
        COMMENT = 3

    class _StackItem(enum.Enum):
        LIST = 0
        VECTOR = 1
        SET = 2
        MAP = 3
        TAG = 4

    #

    def _stack_push(self, key: _ParseMode | _StackItem, arg: ta.Any) -> None:
        self._stack.append((key, arg))

    def _stack_pop(self) -> tuple[_ParseMode | _StackItem, ta.Any]:
        return self._stack.pop()

    def _stack_peek(self) -> tuple[_ParseMode | _StackItem, ta.Any]:
        return self._stack[-1]

    #

    def _update_stack(self) -> None:
        if not self._stack or self._result is self._UNDEFINED:
            return

        stack_item, prev_state = self._stack_peek()

        if stack_item == Parser._StackItem.LIST:
            prev_state.append(self._result)

        elif stack_item == Parser._StackItem.VECTOR:
            prev_state.append(self._result)

        elif stack_item == Parser._StackItem.SET:
            prev_state.append(self._result)

        elif stack_item == Parser._StackItem.MAP:
            if len(prev_state[1]) > 0:
                prev_state[0].append([prev_state[1].pop(), self._result])
            else:
                prev_state[1].append(self._result)

        elif stack_item == Parser._StackItem.TAG:
            self._stack_pop()

            if prev_state == '_':
                self._result = self._UNDEFINED

            elif (tag_handler := self._tag_handlers.get(prev_state)) is not None:
                self._result = tag_handler(self._result)

            else:
                self._result = Tagged(prev_state, self._result)

            self._update_stack()
            return

        # TODO: else error
        # Reset result after updating stack
        self._result = self._UNDEFINED

    #

    _INT_PAT = re.compile(r'^[-+]?(0|[1-9][0-9]*)$')
    _BIGINT_PAT = re.compile(r'^[-+]?(0|[1-9][0-9]*)N$')
    _FLOAT_PAT = re.compile(r'^[-+]?(0|[1-9][0-9]*)(\.[0-9]+)?([eE][+-]?(0|[1-9][0-9]*))?M?$')

    def _match_buffer(self) -> None:
        if self._buffer == 'nil':
            self._result = None

        elif self._buffer == 'true':
            self._result = True

        elif self._buffer == 'false':
            self._result = False

        elif self._buffer.startswith(':'):
            # Keyword
            self._result = self._keyword_maker(self._buffer[1:])

        elif self._buffer.startswith('#'):
            # Tag
            self._stack_push(Parser._StackItem.TAG, self._buffer[1:])
            self._result = self._UNDEFINED

        elif self._INT_PAT.match(self._buffer):
            # Int
            self._result = int(self._buffer)

        elif self._FLOAT_PAT.match(self._buffer):
            # Float
            self._result = float(self._buffer)

        elif self._BIGINT_PAT.match(self._buffer):
            # BigInt
            self._result = int(self._buffer[:-1])  # In Python we don't need special handling for bigint

        elif self._buffer.startswith('\\'):
            # Char
            check.state(len(self._buffer) > 1)
            if self._buffer == '\\space':
                c = ' '
            elif self._buffer == '\\newline':
                c = '\n'
            elif self._buffer == '\\return':
                c = '\r'
            elif self._buffer == '\\tab':
                c = '\t'
            elif self._buffer == '\\\\':
                c = '\\'
            elif self._buffer.startswith('\\u'):
                check.state(len(self._buffer) == 6)
                c = chr(int(self._buffer[2:], 16))
            else:
                check.state(len(self._buffer) == 2)
                c = self._buffer[1:]

            self._result = self._char_maker(c)

        elif self._buffer:
            # Symbol
            self._result = self._symbol_maker(self._buffer)

        self._buffer = ''

    #

    _SPACE_CHARS: ta.ClassVar[ta.AbstractSet[str]] = frozenset([',', ' ', '\t', '\n', '\r'])

    _STRING_ESCAPE_MAP: ta.ClassVar[ta.Mapping[str, str]] = {
        't': '\t',
        'r': '\r',
        'n': '\n',
        '\\': '\\',
        '"': '"',
    }

    def _parse_one(self, char: str) -> None:
        check.arg(len(char) == 1)

        if self._mode == Parser._ParseMode.IDLE:
            if char == '"':
                self._match_buffer()
                self._update_stack()
                self._mode = Parser._ParseMode.STRING
                self._buffer = ''
                return

            if char == ';':
                self._mode = Parser._ParseMode.COMMENT
                return

            if char in self._SPACE_CHARS:
                self._match_buffer()
                self._update_stack()
                return

            if char == '}':
                self._match_buffer()
                self._update_stack()

                if self._stack:
                    stack_item, prev_state = self._stack_pop()

                    if stack_item == Parser._StackItem.MAP:
                        check.empty(prev_state[1])
                        self._result = self._map_maker(prev_state[0])

                    else:  # Set
                        # FIXME:
                        # check.state(stack_item == Parser._StackItem.SET)
                        self._result = self._set_maker(prev_state)

                self._update_stack()
                return

            if char == ']':
                self._match_buffer()
                self._update_stack()
                stack_item, prev_state = self._stack_pop()
                self._result = self._vector_maker(tuple(prev_state))
                self._update_stack()
                return

            if char == ')':
                self._match_buffer()
                self._update_stack()
                stack_item, prev_state = self._stack_pop()
                self._result = self._list_maker(prev_state)
                self._update_stack()
                return

            if char == '[':
                self._match_buffer()
                self._update_stack()
                self._stack_push(Parser._StackItem.VECTOR, [])
                return

            if char == '(':
                self._match_buffer()
                self._update_stack()
                self._stack_push(Parser._StackItem.LIST, [])
                return

            state_plus_char = self._buffer + char
            if state_plus_char == '#_':
                self._stack_push(Parser._StackItem.TAG, char)
                self._result = self._UNDEFINED
                self._buffer = ''
                return

            if state_plus_char.endswith('#{'):
                self._buffer = self._buffer[:-1]  # Remove the '#'
                self._match_buffer()
                self._update_stack()
                self._stack_push(Parser._StackItem.SET, [])
                self._buffer = ''
                return

            if char == '{':
                self._match_buffer()
                self._update_stack()
                self._stack_push(Parser._StackItem.MAP, [[], []])
                self._buffer = ''
                return

            self._buffer += char
            return

        elif self._mode == Parser._ParseMode.STRING:  # noqa
            if char == '\\':
                self._stack_push(self._mode, self._buffer)
                self._mode = Parser._ParseMode.ESCAPE
                self._buffer = ''
                return

            if char == '"':
                self._mode = Parser._ParseMode.IDLE
                self._result = self._buffer
                self._update_stack()
                self._buffer = ''
                return

            self._buffer += char

        elif self._mode == Parser._ParseMode.ESCAPE:
            # TODO what should happen when escaping other char
            escaped_char = self._STRING_ESCAPE_MAP.get(char, char)
            stack_item, prev_state = self._stack_pop()
            self._mode = check.isinstance(stack_item, Parser._ParseMode)
            self._buffer = prev_state + escaped_char

        elif self._mode == Parser._ParseMode.COMMENT:
            if char == '\n':
                self._mode = Parser._ParseMode.IDLE

        else:
            raise RuntimeError(self._mode)

    #

    def parse_gen(self) -> ta.Generator[list[ta.Any], str, None]:
        i = -1
        values: list[ta.Any] = []
        while True:
            try:
                src = yield values
            except GeneratorExit:
                raise RuntimeError('Unexpected end of input') from None

            values = []
            if not src:
                break

            for char in src:
                i += 1

                if not self._stack and self._result is not self._UNDEFINED:
                    values.append(self._result)
                    self._result = self._UNDEFINED

                self._parse_one(char)

        if i >= 0:
            self._match_buffer()
            self._update_stack()

        check.state(not self._stack)

        if self._result is not self._UNDEFINED:
            yield [self._result]
        else:
            yield []

    def parse_list(self, src: str) -> list[ta.Any]:
        if not src:
            return []

        gen = self.parse_gen()
        next(gen)
        values = [
            *gen.send(src),
            *gen.send(''),
        ]
        gen.close()
        return values


#


def parse_list(src: str, **kwargs: ta.Any) -> list[ta.Any]:
    """Parse an edn string and return the corresponding Python object."""

    parser = Parser(**kwargs)
    return parser.parse_list(src)


def parse(src: str, **kwargs: ta.Any) -> ta.Any | None:
    values = parse_list(src, **kwargs)
    if not values:
        return None
    return check.single(values)
