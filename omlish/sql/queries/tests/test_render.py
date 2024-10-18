"""
TODO:
 - text.parts
"""
import io
import typing as ta

from .. import Q
from .... import dispatch
from .... import lang
from ..exprs import Literal
from ..idents import Ident
from ..names import Name
from ..relations import Table
from ..selects import Select
from ..selects import SelectItem


class Renderer(lang.Abstract):
    def __init__(self, out: ta.TextIO) -> None:
        super().__init__()
        self._out = out

    @dispatch.method
    def render(self, o: ta.Any) -> None:
        raise TypeError(o)

    @classmethod
    def render_str(cls, o: ta.Any, *args: ta.Any, **kwargs: ta.Any) -> str:
        out = io.StringIO()
        cls(out, *args, **kwargs).render(o)
        return out.getvalue()


class StandardRenderer(Renderer):
    # exprs

    @Renderer.render.register
    def render_literal(self, o: Literal) -> None:
        self._out.write(repr(o.v))

    # idents

    @Renderer.render.register
    def render_ident(self, o: Ident) -> None:
        self._out.write(f'"{o.s}"')

    # names

    @Renderer.render.register
    def render_name(self, o: Name) -> None:
        for n, i in enumerate(o.ps):
            if n:
                self._out.write('.')
            self.render(i)

    # relations

    @Renderer.render.register
    def render_table(self, o: Table) -> None:
        self.render(o.n)
        if o.a is not None:
            self._out.write(' as ')
            self.render(o.a)

    # selects

    @Renderer.render.register
    def render_select_item(self, o: SelectItem) -> None:
        self.render(o.v)
        if o.a is not None:
            self._out.write(' as ')
            self.render(o.a)

    @Renderer.render.register
    def render_select(self, o: Select) -> None:
        self._out.write('select ')
        for i, it in enumerate(o.items):
            if i:
                self._out.write(', ')
            self.render(it)
        if o.from_ is not None:
            self._out.write(' from ')
            self.render(o.from_)
        if o.where:
            self._out.write(' where ')
            self.render(o.where)


def test_render():
    query = Q.select(
        [
            1,
        ],
        'foo',
        Q.and_(
            Q.eq(Q.i('foo'), 1),
            Q.ne(Q.i('bar'), Q.add(Q.i('baz'), 2)),
        ),
    )

    print(StandardRenderer.render_str(query))
