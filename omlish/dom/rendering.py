import io
import textwrap
import typing as ta

from .. import check
from .. import dataclasses as dc
from .. import dispatch
from .. import lang
from .content import Dom
from .content import iter_content


if ta.TYPE_CHECKING:
    import markupsafe as ms

    _HAS_MARKUPSAFE = True

else:
    ms = lang.proxy_import('markupsafe')

    _HAS_MARKUPSAFE = lang.can_import('markupsafe')


##


@dc.dataclass()
class InvalidTagError(Exception):
    pass


@dc.dataclass()
class StrForbiddenError(Exception):
    pass


class Renderer:
    def __init__(
            self,
            sb: io.StringIO | None,
            *,
            forbid_str: bool = False,
            escape: ta.Callable[[str], str] | None = None,
            indent: str | int | None = None,
            indent_string_content: bool = False,
    ) -> None:
        super().__init__()

        if sb is None:
            sb = io.StringIO()
        self._sb = sb

        self._forbid_str = forbid_str
        self._escape_fn = escape
        if isinstance(indent, int):
            indent = ' ' * indent
        self._indent_unit: str | None = indent
        self._indent_string_content = indent_string_content

        self._level = 0
        self._indent_cache: dict[int, str] = {}

    @classmethod
    def render_to_str(cls, o: ta.Any, **kwargs: ta.Any) -> str:
        sb = io.StringIO()
        cls(sb, **kwargs).render(o)
        return sb.getvalue()

    #

    def _escape(self, s: str) -> str:
        if _HAS_MARKUPSAFE and isinstance(s, ms.Markup):
            return s
        if type(s) is not str:
            raise TypeError(s)
        if (fn := self._escape_fn) is None:
            return s
        return fn(s)

    def _check_tag(self, s: str) -> str:
        if self._escape(s) != s:
            raise InvalidTagError(s)
        return s

    #

    def _indent_str(self) -> str | None:
        if not (s := self._indent_unit):
            return None
        try:
            return self._indent_cache[self._level]
        except KeyError:
            pass
        ls = self._indent_cache[self._level] = s * self._level
        return ls

    def _write_indent(self) -> None:
        if (s := self._indent_str()):
            self._sb.write(s)

    #

    @dispatch.method(instance_cache=True)
    def render(self, o: ta.Any) -> None:
        raise TypeError(o)

    #

    def _write_string_content(self, s: str) -> None:
        if self._indent_string_content and (ls := self._indent_str()):
            s = textwrap.indent(s, ls)
        self._sb.write(s)

    @render.register  # noqa
    def _render_str(self, s: str) -> None:
        if self._forbid_str:
            raise StrForbiddenError(s)
        self._write_string_content(s)

    @render.register  # noqa
    def _render_sequence(self, l: ta.Sequence) -> None:
        for e in l:
            self.render(e)

    #

    if _HAS_MARKUPSAFE:
        @render.register
        def _render_markup(self, m: ms.Markup) -> None:
            self._write_string_content(m)

    #

    def _render_tag(self, tag: str) -> None:
        self._sb.write(self._check_tag(tag))

    def _render_attr_key(self, k: str) -> None:
        self._sb.write(self._check_tag(k))

    def _render_attr_value(self, v: ta.Any) -> None:
        self._sb.write('"')
        self._sb.write(check.isinstance(v, str))  # FIXME
        self._sb.write('"')

    @render.register  # noqa
    def _render_dom(self, n: Dom) -> None:
        self._write_indent()

        self._sb.write('<')
        self._render_tag(n.tag)

        for k, v in (n.attrs or {}).items():
            self._sb.write(' ')
            self._render_attr_key(k)
            if v is not None:
                self._sb.write('=')
                self._render_attr_value(v)

        i = -1
        for i, c in enumerate(iter_content(n.body)):
            if not i:
                self._sb.write('>')

            if self._indent_unit:
                self._sb.write('\n')

            self._level += 1
            self.render(c)
            self._level -= 1

        if i >= 0:
            if self._indent_unit:
                self._sb.write('\n')
                self._write_indent()

            self._sb.write('</')
            self._render_tag(n.tag)
            self._sb.write('>')

        else:
            self._sb.write(' />')


render = Renderer.render_to_str
