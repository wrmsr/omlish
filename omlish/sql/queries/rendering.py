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
import typing as ta

from ... import dispatch
from ... import lang
from ...text import parts as tp
from ..params import ParamStyle
from ..params import make_params_preparer
from .base import Node
from .binary import Binary
from .binary import BinaryOp
from .binary import BinaryOps
from .exprs import Literal
from .exprs import NameExpr
from .exprs import ParamExpr
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
from .selects import AllSelectItem
from .selects import ExprSelectItem
from .selects import Select
from .unary import Unary
from .unary import UnaryOp
from .unary import UnaryOps


@dc.dataclass(frozen=True)
class RenderedQueryParts(lang.Final):
    p: tp.Part
    args: lang.Args


@dc.dataclass(frozen=True)
class RenderedQuery(lang.Final):
    s: str
    args: lang.Args


class Renderer(lang.Abstract):
    def __init__(
            self,
            *,
            param_style: ParamStyle | None = None,
    ) -> None:
        super().__init__()

        self._param_style = param_style if param_style is not None else self.default_param_style

        self._params_preparer = make_params_preparer(self._param_style)

    default_param_style: ta.ClassVar[ParamStyle] = ParamStyle.PYFORMAT

    def args(self) -> lang.Args:
        return self._params_preparer.prepare()

    @dispatch.method
    def render(self, o: ta.Any) -> tp.Part:
        raise TypeError(o)

    @classmethod
    def render_query_parts(cls, o: ta.Any, *args: ta.Any, **kwargs: ta.Any) -> RenderedQueryParts:
        r = cls(*args, **kwargs)
        return RenderedQueryParts(
            r.render(o),
            r.args(),
        )

    @classmethod
    def render_query(cls, o: ta.Any, *args: ta.Any, **kwargs: ta.Any) -> RenderedQuery:
        rqp = cls.render_query_parts(o, *args, **kwargs)
        return RenderedQuery(
            tp.render(rqp.p),
            rqp.args,
        )


class StdRenderer(Renderer):
    # parens

    NEEDS_PAREN_TYPES: ta.AbstractSet[type[Node]] = {
        Binary,
        # IsNull,
        # SelectExpr,
    }

    def needs_paren(self, node: Node) -> bool:
        return type(node) in self.NEEDS_PAREN_TYPES

    def paren(self, node: Node) -> tp.Part:
        return tp.Wrap(self.render(node)) if self.needs_paren(node) else self.render(node)

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
    def render_binary(self, o: Binary) -> tp.Part:
        return [
            self.paren(o.l),
            self.BINARY_OP_TO_STR[o.op],
            self.paren(o.r),
        ]

    # exprs

    @Renderer.render.register
    def render_literal(self, o: Literal) -> tp.Part:
        return repr(o.v)

    @Renderer.render.register
    def render_name_expr(self, o: NameExpr) -> tp.Part:
        return self.render(o.n)

    @Renderer.render.register
    def render_param_expr(self, o: ParamExpr) -> tp.Part:
        return self.render(o.p)

    # idents

    @Renderer.render.register
    def render_ident(self, o: Ident) -> tp.Part:
        return f'"{o.s}"'

    # inserts

    @Renderer.render.register
    def render_values(self, o: Values) -> tp.Part:
        return [
            'values',
            tp.Wrap(tp.List([self.render(v) for v in o.vs])),
        ]

    @Renderer.render.register
    def render_insert(self, o: Insert) -> tp.Part:
        return [
            'insert into',
            self.render(o.into),
            tp.Wrap(tp.List([self.render(c) for c in o.columns])),
            self.render(o.data),
        ]

    # multis

    MULTI_KIND_TO_STR: ta.ClassVar[ta.Mapping[MultiKind, str]] = {
        MultiKind.AND: 'and',
        MultiKind.OR: 'or',
    }

    @Renderer.render.register
    def render_multi(self, o: Multi) -> tp.Part:
        return tp.Wrap(tp.List(
            [self.render(e) for e in o.es],
            delimiter=' ' + self.MULTI_KIND_TO_STR[o.k],  # FIXME: Part
        ))

    # names

    @Renderer.render.register
    def render_name(self, o: Name) -> tp.Part:
        out: list[tp.Part] = []
        for n, i in enumerate(o.ps):
            if n:
                out.append('.')
            out.append(self.render(i))
        return tp.Concat(out)

    # params

    @Renderer.render.register
    def render_param(self, o: Param) -> tp.Part:
        return self._params_preparer.add(o.n if o.n is not None else id(o))

    # relations

    @Renderer.render.register
    def render_table(self, o: Table) -> tp.Part:
        return [
            self.render(o.n),
            *(['as', self.render(o.a)] if o.a is not None else []),
        ]

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
    def render_join(self, o: Join) -> tp.Part:
        return [
            self.render(o.l),
            self.JOIN_KIND_TO_STR[o.k],
            self.render(o.r),
            *(['on', self.render(o.c)] if o.c is not None else []),
        ]

    # selects

    @Renderer.render.register
    def render_all_select_item(self, o: AllSelectItem) -> tp.Part:
        return '*'

    @Renderer.render.register
    def render_expr_select_item(self, o: ExprSelectItem) -> tp.Part:
        return [
            self.render(o.v),
            *(['as', self.render(o.a)] if o.a is not None else []),
        ]

    @Renderer.render.register
    def render_select(self, o: Select) -> tp.Part:
        return [
            'select',
            tp.List([self.render(i) for i in o.items]),
            *(['from', self.render(o.from_)] if o.from_ is not None else []),
            *(['where', self.render(o.where)] if o.where is not None else []),
        ]

    # unary

    UNARY_OP_TO_STR: ta.ClassVar[ta.Mapping[UnaryOp, tuple[str, str]]] = {
        UnaryOps.NOT: ('not ', ''),
        UnaryOps.IS_NULL: ('', ' is null'),
        UnaryOps.IS_NOT_NULL: ('', ' is not null'),

        UnaryOps.POS: ('+', ''),
        UnaryOps.NEG: ('-', ''),
    }

    @Renderer.render.register
    def render_unary(self, o: Unary) -> tp.Part:
        pfx, sfx = self.UNARY_OP_TO_STR[o.op]
        return tp.Concat([
            pfx,
            self.render(o.v),
            sfx,
        ])


def render_parts(n: Node, **kwargs: ta.Any) -> RenderedQueryParts:
    return StdRenderer.render_query_parts(n, **kwargs)


def render(n: Node, **kwargs: ta.Any) -> RenderedQuery:
    return StdRenderer.render_query(n, **kwargs)
