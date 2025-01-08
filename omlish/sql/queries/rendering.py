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
import dataclasses as dc
import io
import typing as ta

from ... import dispatch
from ... import lang
from ..params import ParamStyle
from ..params import make_params_preparer
from .base import Node
from .binary import Binary
from .binary import BinaryOp
from .binary import BinaryOps
from .exprs import Literal
from .exprs import NameExpr
from .idents import Ident
from .inserts import Insert
from .inserts import Values
from .multi import Multi
from .multi import MultiKind
from .names import Name
from .params import Param
from .relations import Join
from .relations import JoinKind
from .relations import Table
from .selects import Select
from .selects import SelectItem
from .unary import Unary
from .unary import UnaryOp
from .unary import UnaryOps


@dc.dataclass(frozen=True)
class RenderedQuery(lang.Final):
    s: str
    args: lang.Args


class Renderer(lang.Abstract):
    def __init__(
            self,
            out: ta.TextIO,
            *,
            param_style: ParamStyle | None = None,
    ) -> None:
        super().__init__()
        self._out = out
        self._param_style = param_style if param_style is not None else self.default_param_style

        self._params_preparer = make_params_preparer(self._param_style)

    default_param_style: ta.ClassVar[ParamStyle] = ParamStyle.PYFORMAT

    def args(self) -> lang.Args:
        return self._params_preparer.prepare()

    @dispatch.method
    def render(self, o: ta.Any) -> None:
        raise TypeError(o)

    @classmethod
    def render_str(cls, o: ta.Any, *args: ta.Any, **kwargs: ta.Any) -> RenderedQuery:
        out = io.StringIO()
        pp = cls(out, *args, **kwargs)
        pp.render(o)
        return RenderedQuery(out.getvalue(), pp.args())


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

    @Renderer.render.register
    def render_param(self, o: Param) -> None:
        self._out.write(self._params_preparer.add(o.n if o.n is not None else id(o)))

    # idents

    @Renderer.render.register
    def render_ident(self, o: Ident) -> None:
        self._out.write(f'"{o.s}"')

    # inserts

    @Renderer.render.register
    def render_values(self, o: Values) -> None:
        self._out.write('values (')
        for i, v in enumerate(o.vs):
            if i:
                self._out.write(', ')
            self.render(v)
        self._out.write(')')

    @Renderer.render.register
    def render_insert(self, o: Insert) -> None:
        self._out.write('insert into ')
        self.render(o.into)
        self._out.write(' (')
        for i, c in enumerate(o.columns):
            if i:
                self._out.write(', ')
            self.render(c)
        self._out.write(') ')
        self.render(o.data)

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

    JOIN_KIND_TO_STR: ta.ClassVar[ta.Mapping[JoinKind, str]] = {
        JoinKind.DEFAULT: 'join',
        JoinKind.INNER: 'inner join',
        JoinKind.LEFT: 'left join',
        JoinKind.LEFT_OUTER: 'left outer join',
        JoinKind.RIGHT: 'right join',
        JoinKind.RIGHT_OUTER: 'right outer join',
        JoinKind.FULL: 'full join',
        JoinKind.FULL_OUTER: 'full outer join',
        JoinKind.CROSS: 'cross join',
        JoinKind.NATURAL: 'natural join',
    }

    @Renderer.render.register
    def render_join(self, o: Join) -> None:
        self.render(o.l)
        self._out.write(' ')
        self._out.write(self.JOIN_KIND_TO_STR[o.k])
        self._out.write(' ')
        self.render(o.r)
        if o.c is not None:
            self._out.write(' on ')
            self.render(o.c)

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


def render(n: Node, **kwargs: ta.Any) -> RenderedQuery:
    return StdRenderer.render_str(n, **kwargs)
