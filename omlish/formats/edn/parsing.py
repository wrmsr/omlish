"""
TODO:
 - reader meta - ^:foo
"""
# https://github.com/jorinvo/edn-data/blob/1e5824f63803eb58f35e98839352000053d47115/test/parse.test.ts
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
from .values import TaggedVal
from .values import Vector


##


class ListParser:
    DEFAULT_TAG_HANDLERS: ta.ClassVar[ta.Mapping[str, ta.Callable[..., ta.Any]]] = {
        'inst': lambda val: datetime.datetime.fromisoformat(val) if isinstance(val, str) else None,
    }

    def __init__(
            self,
            *,
            keyword_maker: ta.Callable[..., ta.Any] = Keyword,
            char_maker: ta.Callable[..., ta.Any] = Char,
            symbol_maker: ta.Callable[..., ta.Any] = Symbol,

            list_maker: ta.Callable[..., ta.Any] = List.new,
            vector_maker: ta.Callable[..., ta.Any] = Vector.new,
            set_maker: ta.Callable[..., ta.Any] = Set.new,
            map_maker: ta.Callable[..., ta.Any] = Map.new,

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

        self._stack: list[tuple[ListParser._ParseMode | ListParser._StackItem, ta.Any]] = []
        self._mode: ListParser._ParseMode = ListParser._ParseMode.IDLE
        self._state = ''
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
        VECTOR = 0
        LIST = 1
        MAP = 2
        SET = 3
        TAG = 4

    #

    def _update_stack(self) -> None:
        if not self._stack or self._result is self._UNDEFINED:
            return

        stack_item, prev_state = self._stack[-1]

        if stack_item == ListParser._StackItem.VECTOR:
            prev_state.append(self._result)

        elif stack_item == ListParser._StackItem.LIST:
            prev_state.append(self._result)

        elif stack_item == ListParser._StackItem.SET:
            prev_state.append(self._result)

        elif stack_item == ListParser._StackItem.MAP:
            if len(prev_state[1]) > 0:
                prev_state[0].append([prev_state[1].pop(), self._result])
            else:
                prev_state[1].append(self._result)

        elif stack_item == ListParser._StackItem.TAG:
            self._stack.pop()

            if prev_state == '_':
                self._result = self._UNDEFINED

            else:
                tag_handler = self._tag_handlers.get(prev_state)
                if tag_handler:
                    self._result = tag_handler(self._result)
                else:
                    self._result = TaggedVal(prev_state, self._result)

            self._update_stack()
            return

        # TODO: else error
        # Reset result after updating stack
        self._result = self._UNDEFINED

    #

    _INT_PAT = re.compile(r'^[-+]?(0|[1-9][0-9]*)$')
    _BIGINT_PAT = re.compile(r'^[-+]?(0|[1-9][0-9]*)N$')
    _FLOAT_PAT = re.compile(r'^[-+]?(0|[1-9][0-9]*)(\.[0-9]+)?([eE][+-]?(0|[1-9][0-9]*))?M?$')

    def _match(self) -> None:
        if self._state == 'nil':
            self._result = None

        elif self._state == 'true':
            self._result = True

        elif self._state == 'false':
            self._result = False

        elif self._state.startswith(':'):
            # Keyword
            self._result = self._keyword_maker(self._state[1:])

        elif self._state.startswith('#'):
            # Tag
            self._stack.append((ListParser._StackItem.TAG, self._state[1:]))
            self._result = self._UNDEFINED

        elif self._INT_PAT.match(self._state):
            # Int
            self._result = int(self._state)

        elif self._FLOAT_PAT.match(self._state):
            # Float
            self._result = float(self._state)

        elif self._BIGINT_PAT.match(self._state):
            # BigInt
            self._result = int(self._state[:-1])  # In Python we don't need special handling for bigint

        elif self._state.startswith('\\'):
            # Char
            check.state(len(self._state) > 1)
            if self._state == '\\space':
                c = ' '
            elif self._state == '\\newline':
                c = '\n'
            elif self._state == '\\return':
                c = '\r'
            elif self._state == '\\tab':
                c = '\t'
            elif self._state == '\\\\':
                c = '\\'
            elif self._state.startswith('\\u'):
                check.state(len(self._state) == 6)
                c = chr(int(self._state[2:], 16))
            else:
                check.state(len(self._state) == 2)
                c = self._state[1:]

            self._result = self._char_maker(c)

        elif self._state:
            # Symbol
            self._result = self._symbol_maker(self._state)

        self._state = ''

    #

    _SPACE_CHARS: ta.ClassVar[ta.AbstractSet[str]] = frozenset([',', ' ', '\t', '\n', '\r'])

    _STRING_ESCAPE_MAP: ta.ClassVar[ta.Mapping[str, str]] = {
        't': '\t',
        'r': '\r',
        'n': '\n',
        '\\': '\\',
        '"': '"',
    }

    def parse(self, src: str) -> list[ta.Any]:
        values = []

        i = -1
        for i in range(len(src)):
            if not self._stack and self._result is not self._UNDEFINED:
                values.append(self._result)
                self._result = self._UNDEFINED

            char = src[i]

            if self._mode == ListParser._ParseMode.IDLE:
                if char == '"':
                    self._match()
                    self._update_stack()
                    self._mode = ListParser._ParseMode.STRING
                    self._state = ''
                    continue

                if char == ';':
                    self._mode = ListParser._ParseMode.COMMENT
                    continue

                if char in self._SPACE_CHARS:
                    self._match()
                    self._update_stack()
                    continue

                if char == '}':
                    self._match()
                    self._update_stack()

                    if self._stack:
                        stack_item, prev_state = self._stack.pop()

                        if stack_item == ListParser._StackItem.MAP:
                            check.empty(prev_state[1])
                            self._result = self._map_maker(prev_state[0])

                        else:  # Set
                            # FIXME:
                            # check.state(stack_item == ListParser._StackItem.SET)
                            self._result = self._set_maker(prev_state)

                    self._update_stack()
                    continue

                if char == ']':
                    self._match()
                    self._update_stack()
                    stack_item, prev_state = self._stack.pop()
                    self._result = self._vector_maker(tuple(prev_state))
                    self._update_stack()
                    continue

                if char == ')':
                    self._match()
                    self._update_stack()
                    stack_item, prev_state = self._stack.pop()
                    self._result = self._list_maker(prev_state)
                    self._update_stack()
                    continue

                if char == '[':
                    self._match()
                    self._update_stack()
                    self._stack.append((ListParser._StackItem.VECTOR, []))
                    continue

                if char == '(':
                    self._match()
                    self._update_stack()
                    self._stack.append((ListParser._StackItem.LIST, []))
                    continue

                state_plus_char = self._state + char
                if state_plus_char == '#_':
                    self._stack.append((ListParser._StackItem.TAG, char))
                    self._result = self._UNDEFINED
                    self._state = ''
                    continue

                if state_plus_char.endswith('#{'):
                    self._state = self._state[:-1]  # Remove the '#'
                    self._match()
                    self._update_stack()
                    self._stack.append((ListParser._StackItem.SET, []))
                    self._state = ''
                    continue

                if char == '{':
                    self._match()
                    self._update_stack()
                    self._stack.append((ListParser._StackItem.MAP, [[], []]))
                    self._state = ''
                    continue

                self._state += char
                continue

            elif self._mode == ListParser._ParseMode.STRING:  # noqa
                if char == '\\':
                    self._stack.append((self._mode, self._state))
                    self._mode = ListParser._ParseMode.ESCAPE
                    self._state = ''
                    continue

                if char == '"':
                    self._mode = ListParser._ParseMode.IDLE
                    self._result = self._state
                    self._update_stack()
                    self._state = ''
                    continue

                self._state += char

            elif self._mode == ListParser._ParseMode.ESCAPE:
                # TODO what should happen when escaping other char
                escaped_char = self._STRING_ESCAPE_MAP.get(char, char)
                stack_item, prev_state = self._stack.pop()
                self._mode = check.isinstance(stack_item, ListParser._ParseMode)
                self._state = prev_state + escaped_char

            elif self._mode == ListParser._ParseMode.COMMENT:
                if char == '\n':
                    self._mode = ListParser._ParseMode.IDLE

            else:
                raise RuntimeError(self._mode)

        if i >= 0:
            self._match()
            self._update_stack()

        check.state(not self._stack)

        if self._result is not self._UNDEFINED:
            values.append(self._result)
        return values


#


def parse_list(src: str, **kwargs: ta.Any) -> list[ta.Any]:
    """Parse an edn string and return the corresponding Python object."""

    parser = ListParser(**kwargs)
    return parser.parse(src)


def parse(src: str, **kwargs: ta.Any) -> ta.Any | None:
    values = parse_list(src, **kwargs)
    if not values:
        return None
    return check.single(values)
