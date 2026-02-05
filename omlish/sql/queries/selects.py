import typing as ta

from ... import dataclasses as dc
from ... import lang
from ... import marshal as msh
from .base import Node
from .exprs import CanExpr
from .exprs import Expr
from .exprs import ExprBuilder
from .idents import Ident
from .keywords import Star
from .relations import CanRelation
from .relations import Relation
from .relations import RelationBuilder
from .stmts import Stmt


##


class SelectItem(Node, lang.Abstract):
    pass


class AllSelectItem(SelectItem, lang.Final):
    pass


class ExprSelectItem(SelectItem, lang.Final):
    v: Expr
    a: Ident | None = dc.xfield(None, repr_fn=lang.opt_repr) | msh.with_field_options(omit_if=lang.is_none)


##


class Select(Stmt, lang.Final):
    items: ta.Sequence[SelectItem] = dc.xfield(coerce=tuple)
    from_: Relation | None = dc.xfield(None, repr_fn=lang.opt_repr) | msh.with_field_options(name='from', omit_if=lang.is_none)  # noqa
    where: Expr | None = dc.xfield(None, repr_fn=lang.opt_repr) | msh.with_field_options(omit_if=lang.is_none)


class SelectExpr(Expr, lang.Final):
    s: Select


class SelectRelation(Relation, lang.Final):
    s: Select


##


CanSelectItem: ta.TypeAlias = SelectItem | Star | CanExpr


class SelectBuilder(RelationBuilder, ExprBuilder):
    def select_item(self, o: CanSelectItem) -> SelectItem:
        if isinstance(o, SelectItem):
            return o
        elif isinstance(o, Star):
            return AllSelectItem()
        else:
            return ExprSelectItem(self.expr(o))

    def select(
            self,
            items: ta.Sequence[CanSelectItem],
            from_: CanRelation | None = None,
            where: CanExpr | None = None,
    ) -> Select:
        return Select(
            tuple(self.select_item(i) for i in items),
            from_=self.relation(from_) if from_ is not None else None,
            where=self.expr(where) if where is not None else None,
        )
