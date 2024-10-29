import json
import typing as ta

from ..render import AbstractJsonRenderer
from ..render import JsonRendererOut
from .parse import BeginArray
from .parse import BeginObject
from .parse import EndArray
from .parse import EndObject
from .parse import JsonStreamParserEvent
from .parse import Key


##


class StreamJsonRenderer(AbstractJsonRenderer[ta.Iterable[JsonStreamParserEvent]]):
    def __init__(
            self,
            out: JsonRendererOut,
            *,
            delimiter: str = '',
            sort_keys: bool = False,
            **kwargs: ta.Any,
    ) -> None:
        if sort_keys:
            raise TypeError('Not yet implemented')

        self._delimiter = delimiter

        super().__init__(out, **kwargs)

        self._stack: list[tuple[ta.Literal['OBJECT', 'ARRAY'], int]] = []
        self._need_delimit = False

    def _render_value(
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

        else:
            raise TypeError(o)

        if post:
            self._write(post)

    def _render(self, e: JsonStreamParserEvent) -> None:
        if self._need_delimit:
            self._write(self._delimiter)
            self._need_delimit = False

        if e != EndArray and self._stack and (tt := self._stack[-1])[0] == 'ARRAY':
            if tt[1]:
                self._write(self._comma)
            self._write_indent()

            self._stack[-1] = ('ARRAY', tt[1] + 1)

        #

        if e is None or isinstance(e, (str, int, float, bool)):
            self._render_value(e)
            if not self._stack:
                self._need_delimit = True

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
            self._render_value(e.key, AbstractJsonRenderer.State.KEY)
            self._write(self._colon)

            self._stack.append(('OBJECT', tt[1] + 1))

        elif e is EndObject:
            if not self._stack or (tt := self._stack.pop())[0] != 'OBJECT':
                raise Exception

            self._level -= 1
            if tt[1]:
                self._write_indent()
            self._write('}')
            if not self._stack:
                self._need_delimit = True

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
            if not self._stack:
                self._need_delimit = True

        #

        else:
            raise TypeError(e)

    def render(self, events: ta.Iterable[JsonStreamParserEvent]) -> None:
        for e in events:
            self._render(e)
