"""
TODO:
 - genmachine...
"""
import enum
import io
import json
import typing as ta

from ... import lang
from .stream import BeginArray
from .stream import BeginObject
from .stream import EndArray
from .stream import EndObject
from .stream import JsonStreamParserEvent
from .stream import Key


class AbstractJsonRenderer(lang.Abstract):
    class State(enum.Enum):
        VALUE = enum.auto()
        KEY = enum.auto()

    def __init__(
            self,
            out: ta.TextIO,
            *,
            indent: int | str | None = None,
            separators: tuple[str, str] | None = None,
            sort_keys: bool = False,
            style: ta.Callable[[ta.Any, State], tuple[str, str]] | None = None,
    ) -> None:
        super().__init__()

        self._out = out
        if isinstance(indent, (str, int)):
            self._indent = (' ' * indent) if isinstance(indent, int) else indent
            self._endl = '\n'
            if separators is None:
                separators = (',', ': ')
        elif indent is None:
            self._indent = self._endl = ''
            if separators is None:
                separators = (', ', ': ')
        else:
            raise TypeError(indent)
        self._comma, self._colon = separators
        self._sort_keys = sort_keys
        self._style = style

        self._level = 0

    _literals: ta.ClassVar[ta.Mapping[ta.Any, str]] = {
        True: 'true',
        False: 'false',
        None: 'null',
    }

    def _write(self, s: str) -> None:
        if s:
            self._out.write(s)

    def _write_indent(self) -> None:
        if self._indent:
            self._write(self._endl)
            if self._level:
                self._write(self._indent * self._level)


class JsonRenderer(AbstractJsonRenderer):
    def _render(
            self,
            o: ta.Any,
            state: AbstractJsonRenderer.State = AbstractJsonRenderer.State.VALUE,
    ) -> None:
        if self._style is not None:
            pre, post = self._style(o, state)
            self._write(pre)
        else:
            post = None

        if o is None or isinstance(o, bool):
            self._write(self._literals[o])

        elif isinstance(o, (str, int, float)):
            self._write(json.dumps(o))

        elif isinstance(o, ta.Mapping):
            self._write('{')
            self._level += 1
            items = list(o.items())
            if self._sort_keys:
                items.sort(key=lambda t: t[0])
            for i, (k, v) in enumerate(items):
                if i:
                    self._write(self._comma)
                self._write_indent()
                self._render(k, JsonRenderer.State.KEY)
                self._write(self._colon)
                self._render(v)
            self._level -= 1
            if o:
                self._write_indent()
            self._write('}')

        elif isinstance(o, ta.Sequence):
            self._write('[')
            self._level += 1
            for i, e in enumerate(o):
                if i:
                    self._write(self._comma)
                self._write_indent()
                self._render(e)
            self._level -= 1
            if o:
                self._write_indent()
            self._write(']')

        else:
            raise TypeError(o)

        if post:
            self._write(post)

    def render(self, o: ta.Any) -> None:
        self._render(o)

    @classmethod
    def render_str(cls, o: ta.Any, **kwargs: ta.Any) -> str:
        out = io.StringIO()
        cls(out, **kwargs).render(o)
        return out.getvalue()


class StreamJsonRenderer(AbstractJsonRenderer):
    def __init__(
            self,
            out: ta.TextIO,
            **kwargs: ta.Any,
    ) -> None:
        super().__init__(out, **kwargs)

        self._stack: list[tuple[ta.Literal['OBJECT', 'ARRAY'], int]] = []

    def render(self, e: JsonStreamParserEvent) -> None:
        # if self._style is not None:
        #     pre, post = self._style(o, state)
        #     self._write(pre)
        # else:
        #     post = None

        if e != EndArray and self._stack and (tt := self._stack[-1])[0] == 'ARRAY':
            if tt[1]:
                self._write(self._comma)
            self._write_indent()

        if e is None or isinstance(e, bool):
            self._write(self._literals[e])

        elif isinstance(e, (str, int, float)):
            self._write(json.dumps(e))

        #

        elif e is BeginObject:
            self._stack.append(('OBJECT', 0))
            self._write('{')
            self._level += 1

        elif isinstance(e, Key):
            if not self._stack or (tt := self._stack.pop())[0] != 'OBJECT':
                raise Exception

            if tt[1]:
                self._write(self._comma)
            self._write_indent()
            self._write(json.dumps(e.key))
            self._write(self._colon)

            self._stack.append(('OBJECT', tt[1] + 1))

        elif e is EndObject:
            if not self._stack or (tt := self._stack.pop())[0] != 'OBJECT':
                raise Exception

            self._level -= 1
            if tt[1]:
                self._write_indent()
            self._write('}')

        #

        elif e is BeginArray:
            self._stack.append(('ARRAY', 0))
            self._write('[')
            self._level += 1

        elif e is EndArray:
            if not self._stack or (tt := self._stack.pop())[0] != 'ARRAY':
                raise Exception

            self._level -= 1
            if tt[1]:
                self._write_indent()
            self._write(']')

        #

        else:
            raise TypeError(e)
