import abc
import dataclasses as dc
import enum
import io
import json
import typing as ta

from ... import lang


I = ta.TypeVar('I')


class JsonRendererOut(ta.Protocol):
    def write(self, s: str) -> ta.Any: ...


class AbstractJsonRenderer(lang.Abstract, ta.Generic[I]):
    class State(enum.Enum):
        VALUE = enum.auto()
        KEY = enum.auto()

    @dc.dataclass(frozen=True, kw_only=True)
    class Options:
        indent: int | str | None = None
        separators: tuple[str, str] | None = None
        sort_keys: bool = False
        style: ta.Callable[[ta.Any, 'AbstractJsonRenderer.State'], tuple[str, str]] | None = None

    def __init__(
            self,
            out: JsonRendererOut,
            opts: Options = Options(),
    ) -> None:
        super().__init__()

        self._out = out
        self._opts = opts

        separators = opts.separators
        if isinstance(opts.indent, (str, int)):
            self._indent = (' ' * opts.indent) if isinstance(opts.indent, int) else opts.indent
            self._endl = '\n'
            if separators is None:
                separators = (',', ': ')
        elif opts.indent is None:
            self._indent = self._endl = ''
            if separators is None:
                separators = (', ', ': ')
        else:
            raise TypeError(opts.indent)
        self._comma, self._colon = separators

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

    @abc.abstractmethod
    def render(self, i: I) -> None:
        raise NotImplementedError

    @classmethod
    def render_str(cls, i: I, **kwargs: ta.Any) -> str:
        out = io.StringIO()
        cls(out, cls.Options(**kwargs)).render(i)
        return out.getvalue()


class JsonRenderer(AbstractJsonRenderer[ta.Any]):
    def _render(
            self,
            o: ta.Any,
            state: AbstractJsonRenderer.State = AbstractJsonRenderer.State.VALUE,
    ) -> None:
        if self._opts.style is not None:
            pre, post = self._opts.style(o, state)
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
            if self._opts.sort_keys:
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
