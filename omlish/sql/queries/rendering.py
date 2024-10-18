"""
TODO:
 - minimal parens
 - text.parts
 - QuoteStyle
 - ParamStyle

==

def needs_parens(self, e: Expr) -> bool:
    if isinstance(e, (Literal, Ident, Name)):
        return True
    elif isinstance(e, Expr):
        return False
    else:
        raise TypeError(e)
"""
import io
import typing as ta

from ... import dispatch
from ... import lang
from .base import Node
from .binary import Binary
from .binary import BinaryOp
from .binary import BinaryOps
from .exprs import Literal
from .exprs import NameExpr
from .idents import Ident
from .multi import Multi
from .multi import MultiKind
from .names import Name
from .relations import Table
from .selects import Select
from .selects import SelectItem
from .unary import Unary
from .unary import UnaryOp
from .unary import UnaryOps


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


class StdRenderer(Renderer):
    # binary

    BINARY_OP_TO_STR: ta.ClassVar[ta.Mapping[BinaryOp, str]] = {
        BinaryOps.EQ: '=',
        BinaryOps.NE: '!=',
        BinaryOps.LT: '<',
        BinaryOps.LE: '<=',
        BinaryOps.GT: '>',
        BinaryOps.GE: '>=',

        BinaryOps.ADD: '+',
        BinaryOps.SUB: '-',
        BinaryOps.MUL: '*',
        BinaryOps.DIV: '/',
        BinaryOps.MOD: '%',

        BinaryOps.CONCAT: '||',
    }

    @Renderer.render.register
    def render_binary(self, o: Binary) -> None:
        self._out.write('(')
        self.render(o.l)
        self._out.write(f' {self.BINARY_OP_TO_STR[o.op]} ')
        self.render(o.r)
        self._out.write(')')

    # exprs

    @Renderer.render.register
    def render_literal(self, o: Literal) -> None:
        self._out.write(repr(o.v))

    @Renderer.render.register
    def render_name_expr(self, o: NameExpr) -> None:
        self.render(o.n)

    # idents

    @Renderer.render.register
    def render_ident(self, o: Ident) -> None:
        self._out.write(f'"{o.s}"')

    # multis

    MULTI_KIND_TO_STR: ta.ClassVar[ta.Mapping[MultiKind, str]] = {
        MultiKind.AND: 'and',
        MultiKind.OR: 'or',

    }

    @Renderer.render.register
    def render_multi(self, o: Multi) -> None:
        d = f' {self.MULTI_KIND_TO_STR[o.k]} '
        self._out.write('(')
        for i, e in enumerate(o.es):
            if i:
                self._out.write(d)
            self.render(e)
        self._out.write(')')

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

    # unary

    UNARY_OP_TO_STR: ta.ClassVar[ta.Mapping[UnaryOp, tuple[str, str]]] = {
        UnaryOps.NOT: ('not ', ''),
        UnaryOps.IS_NULL: ('', ' is null'),
        UnaryOps.IS_NOT_NULL: ('', ' is not null'),

        UnaryOps.POS: ('+', ''),
        UnaryOps.NEG: ('-', ''),
    }

    @Renderer.render.register
    def render_unary(self, o: Unary) -> None:
        pfx, sfx = self.UNARY_OP_TO_STR[o.op]
        self._out.write(pfx)
        self.render(o.v)
        self._out.write(sfx)


def render(n: Node) -> str:
    return StdRenderer.render_str(n)
