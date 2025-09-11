import io
import typing as ta

from ..rendering import AbstractJsonRenderer
from ..types import SCALAR_TYPES
from .parsing import BeginArray
from .parsing import BeginObject
from .parsing import EndArray
from .parsing import EndObject
from .parsing import Event
from .parsing import Key


##


class StreamJsonRenderer(AbstractJsonRenderer[ta.Iterable[Event]]):
    def __init__(
            self,
            *,
            delimiter: str = '',
            sort_keys: bool = False,
            **kwargs: ta.Any,
    ) -> None:
        if sort_keys:
            raise TypeError('Not yet implemented')

        self._delimiter = delimiter

        super().__init__(**kwargs)

        self._stack: list[tuple[ta.Literal['OBJECT', 'ARRAY'], int]] = []
        self._need_delimit = False

    def _render_value(
            self,
            o: ta.Any,
            state: AbstractJsonRenderer.State = AbstractJsonRenderer.State.VALUE,
    ) -> ta.Iterator[str]:
        if self._style is not None:
            pre, post = self._style(o, state)
            yield pre
        else:
            post = None

        if isinstance(o, SCALAR_TYPES):
            yield self._format_scalar(o)  # type: ignore

        else:
            raise TypeError(o)

        if post:
            yield post

    def _render(self, e: Event) -> ta.Iterator[str]:
        if self._need_delimit:
            yield self._delimiter
            self._need_delimit = False

        if e != EndArray and self._stack and (tt := self._stack[-1])[0] == 'ARRAY':
            if tt[1]:
                yield self._comma
            yield self._get_indent()

            self._stack[-1] = ('ARRAY', tt[1] + 1)

        #

        if e is None or isinstance(e, (str, int, float, bool)):
            yield from self._render_value(e)
            if not self._stack:
                self._need_delimit = True

        #

        elif e is BeginObject:
            self._stack.append(('OBJECT', 0))
            yield '{'
            self._level += 1

        elif isinstance(e, Key):
            if not self._stack or (tt := self._stack.pop())[0] != 'OBJECT':
                raise Exception

            if tt[1]:
                yield self._comma
            yield self._get_indent()
            yield from self._render_value(e.key, AbstractJsonRenderer.State.KEY)
            yield self._colon

            self._stack.append(('OBJECT', tt[1] + 1))

        elif e is EndObject:
            if not self._stack or (tt := self._stack.pop())[0] != 'OBJECT':
                raise Exception

            self._level -= 1
            if tt[1]:
                yield self._get_indent()
            yield '}'
            if not self._stack:
                self._need_delimit = True

        #

        elif e is BeginArray:
            self._stack.append(('ARRAY', 0))
            yield '['
            self._level += 1

        elif e is EndArray:
            if not self._stack or (tt := self._stack.pop())[0] != 'ARRAY':
                raise Exception

            self._level -= 1
            if tt[1]:
                yield self._get_indent()
            yield ']'
            if not self._stack:
                self._need_delimit = True

        #

        else:
            raise TypeError(e)

    def render(self, events: ta.Iterable[Event]) -> ta.Iterator[str]:
        for e in events:
            yield from self._render(e)

    @classmethod
    def render_str(cls, i: ta.Iterable[Event], /, **kwargs: ta.Any) -> str:
        out = io.StringIO()
        for s in cls(**kwargs).render(i):
            out.write(s)
        return out.getvalue()
