# ruff: noqa: UP006 UP007
# @omlish-lite
"""
TODO:
 - raw
 - blocks / inheritance
"""
import dataclasses as dc
import io
import re
import typing as ta

from ..lite.cached import cached_nullary
from ..lite.check import check
from ..lite.maybes import Maybe


##


@dc.dataclass(frozen=True)
class MinjaTemplateParam:
    name: str
    default: Maybe[ta.Any] = Maybe.empty()

    def __post_init__(self) -> None:
        check.arg(self.name.isidentifier())

    @classmethod
    def of(cls, obj: ta.Union[str, 'MinjaTemplateParam']) -> 'MinjaTemplateParam':
        if isinstance(obj, MinjaTemplateParam):
            return obj
        elif isinstance(obj, str):
            return MinjaTemplateParam.new(obj)
        else:
            raise TypeError(obj)

    @classmethod
    def new(cls, name: str, *defaults: ta.Any) -> 'MinjaTemplateParam':
        dfl: Maybe[ta.Any]
        if defaults:
            [dv] = defaults
            dfl = Maybe.just(dv)
        else:
            dfl = Maybe.empty()
        return cls(name, dfl)


class MinjaTemplate:
    def __init__(
            self,
            fn: ta.Callable,
            params: ta.Sequence[MinjaTemplateParam],
    ) -> None:
        super().__init__()

        self._fn = fn
        self._params = params

    @property
    def params(self) -> ta.Sequence[MinjaTemplateParam]:
        return self._params

    def __call__(self, **kwargs: ta.Any) -> str:
        return self._fn(**kwargs)


##


class MinjaTemplateCompiler:
    """
    Compiles a template string into a Python function. The returned function takes a dictionary 'context' and returns
    the rendered string.

    Supported syntax:
    - Literal text remains literal.
    - {{ expr }}: Evaluates 'expr' in the given context and writes its str() to output.
    - {% code %}: Executes the given Python code (e.g. 'for x in items:'), must be terminated appropriately.
    - {% endfor %} to close for loops.
    - {% endif %} to close if blocks.
    - {# comment #}: Ignored completely.
    """

    DEFAULT_INDENT: str = ' ' * 4

    def __init__(
            self,
            src: str,
            params: ta.Sequence[ta.Union[str, MinjaTemplateParam]],
            *,
            indent: str = DEFAULT_INDENT,
    ) -> None:
        super().__init__()

        check.not_isinstance(params, str)

        self._src = check.isinstance(src, str)
        self._params = [
            MinjaTemplateParam.of(p)
            for p in params
        ]
        check.unique(p.name for p in self._params)
        self._indent_str: str = check.non_empty_str(indent)

        self._stack: ta.List[ta.Literal['for', 'if']] = []

    #

    _TAG_PAT = re.compile(
        r'({{.*?}}|{%.*?%}|{#.*?#})',
        flags=re.DOTALL,
    )

    @classmethod
    def _split_tags(cls, src: str) -> ta.List[ta.Tuple[str, str]]:
        raw = cls._TAG_PAT.split(src)

        #

        parts: ta.List[ta.Tuple[str, str]] = []
        for s in raw:
            if not s:
                continue

            for g, l, r in [
                ('{', '{{', '}}'),
                ('%', '{%', '%}'),
                ('#', '{#', '#}'),
            ]:
                if s.startswith(l) and s.endswith(r):
                    parts.append((g, s[len(l):-len(r)]))
                    break
            else:
                parts.append(('', s))

        #

        for i, (g, s) in enumerate(parts):
            if s.startswith('-'):
                if i > 0:
                    lg, ls = parts[i - 1]
                    parts[i - 1] = (lg, ls.rstrip())
                s = s[1:].lstrip()

            if s.endswith('-'):
                if i < len(parts) - 1:
                    rg, rs = parts[i + 1]
                    parts[i + 1] = (rg, rs.lstrip())
                s = s[:-1].rstrip()

            parts[i] = (g, s)

        #

        parts = [(g, s) for g, s in parts if g or s]

        #

        return parts

    #

    def _indent(self, line: str, ofs: int = 0) -> str:
        return self._indent_str * (len(self._stack) + 1 + ofs) + line

    #

    _RENDER_FN_NAME = '__render'

    class Rendered(ta.NamedTuple):
        src: str
        ns: ta.Dict[str, ta.Any]

    @cached_nullary
    def render(self) -> Rendered:
        lines: ta.List[str] = []

        ns: ta.Dict[str, ta.Any] = {
            '__StringIO': io.StringIO,
        }

        parts = self._split_tags(self._src)

        if not self._params:
            lines.append(f'def {self._RENDER_FN_NAME}():')
        else:
            lines.append(f'def {self._RENDER_FN_NAME}(')
            for p in self._params:
                if p.default.present:
                    check.not_in(p.name, ns)
                    ns[p.name] = p.default.must()
                    lines.append(self._indent(f'{p.name}={p.name},'))
                else:
                    lines.append(self._indent(f'{p.name},'))
            lines.append('):')

        lines.append(self._indent('__output = __StringIO()'))

        for g, s in parts:
            if g == '{':
                expr = s.strip()
                lines.append(self._indent(f'__output.write(str({expr}))'))

            elif g == '%':
                stmt = s.strip()

                if stmt.startswith('for '):
                    lines.append(self._indent(stmt + ':'))
                    self._stack.append('for')
                elif stmt.startswith('endfor'):
                    check.equal(self._stack.pop(), 'for')

                elif stmt.startswith('if '):
                    lines.append(self._indent(stmt + ':'))
                    self._stack.append('if')
                elif stmt.startswith('elif '):
                    check.equal(self._stack[-1], 'if')
                    lines.append(self._indent(stmt + ':', -1))
                elif stmt.strip() == 'else':
                    check.equal(self._stack[-1], 'if')
                    lines.append(self._indent('else:', -1))
                elif stmt.startswith('endif'):
                    check.equal(self._stack.pop(), 'if')

                else:
                    lines.append(self._indent(stmt))

            elif g == '#':
                pass

            elif not g:
                if s:
                    safe_text = s.replace('"""', '\\"""')
                    lines.append(self._indent(f'__output.write("""{safe_text}""")'))

            else:
                raise KeyError(g)

        check.empty(self._stack)

        lines.append(self._indent('return __output.getvalue()'))

        return self.Rendered('\n'.join(lines), ns)

    #

    @classmethod
    def _make_fn(
            cls,
            name: str,
            src: str,
            ns: ta.Optional[ta.Mapping[str, ta.Any]] = None,
    ) -> ta.Callable:
        glo: dict = {}
        if ns:
            glo.update(ns)
        exec(src, glo)
        return glo[name]

    #

    @cached_nullary
    def compile(self) -> MinjaTemplate:
        rendered = self.render()

        render_fn = self._make_fn(
            self._RENDER_FN_NAME,
            rendered.src,
            rendered.ns,
        )

        return MinjaTemplate(
            render_fn,
            self._params,
        )


##


def compile_minja_template(
        src: str,
        params: ta.Sequence[ta.Union[str, MinjaTemplateParam]] = (),
) -> MinjaTemplate:
    return MinjaTemplateCompiler(src, params).compile()


def render_minja_template(src: str, **kwargs: ta.Any) -> str:
    tmpl = compile_minja_template(src, list(kwargs))
    return tmpl(**kwargs)
