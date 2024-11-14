import abc
import enum
import io
import json
import typing as ta

from ... import lang
from . import consts
from .types import SCALAR_TYPES
from .types import Scalar


I = ta.TypeVar('I')

MULTILINE_SEPARATORS = consts.Separators(',', ': ')


##


class AbstractJsonRenderer(lang.Abstract, ta.Generic[I]):
    class State(enum.Enum):
        VALUE = enum.auto()
        KEY = enum.auto()

    def __init__(
            self,
            indent: int | str | None = None,
            separators: tuple[str, str] | None = None,
            sort_keys: bool = False,
            style: ta.Callable[[ta.Any, State], tuple[str, str]] | None = None,
            ensure_ascii: bool = True,
    ) -> None:
        super().__init__()

        self._sort_keys = sort_keys
        self._style = style
        self._ensure_ascii = ensure_ascii

        if isinstance(indent, (str, int)):
            self._indent = (' ' * indent) if isinstance(indent, int) else indent
            self._endl = '\n'
            if separators is None:
                separators = MULTILINE_SEPARATORS
        elif indent is None:
            self._indent = self._endl = ''
            if separators is None:
                separators = consts.PRETTY_SEPARATORS
        else:
            raise TypeError(indent)
        self._comma, self._colon = separators

        self._level = 0
        self._indent_cache: dict[int, str] = {}

    _literals: ta.ClassVar[ta.Mapping[ta.Any, str]] = {
        True: 'true',
        False: 'false',
        None: 'null',
    }

    def _get_indent(self) -> str:
        if not self._indent:
            return ''

        if not self._level:
            return self._endl

        try:
            return self._indent_cache[self._level]
        except KeyError:
            pass

        ret = self._endl + (self._indent * self._level)
        self._indent_cache[self._level] = ret
        return ret

    def _format_scalar(self, o: Scalar) -> str:
        if o is None or isinstance(o, bool):
            return self._literals[o]

        elif isinstance(o, (str, int, float)):
            return json.dumps(o, ensure_ascii=self._ensure_ascii)

        else:
            raise TypeError(o)

    @classmethod
    @abc.abstractmethod
    def render_str(cls, i: I, /, **kwargs: ta.Any) -> str:
        raise NotImplementedError


##


class JsonRendererOut(ta.Protocol):
    def write(self, s: str) -> ta.Any: ...


class JsonRenderer(AbstractJsonRenderer[ta.Any]):
    def __init__(
            self,
            out: JsonRendererOut,
            **kwargs: ta.Any,
    ) -> None:
        super().__init__(**kwargs)

        self._out = out

    def _write(self, s: str) -> None:
        if s:
            self._out.write(s)

    def _write_indent(self) -> None:
        self._write(self._get_indent())

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

        if isinstance(o, SCALAR_TYPES):
            self._write(self._format_scalar(o))  # type: ignore

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
                self._render(k, AbstractJsonRenderer.State.KEY)
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
    def render_str(cls, i: ta.Any, /, **kwargs: ta.Any) -> str:
        out = io.StringIO()
        cls(out, **kwargs).render(i)
        return out.getvalue()
