import typing as ta

from ... import dataclasses as dc
from ... import lang
from .base import Node
from .exprs import CanExpr
from .exprs import Expr
from .exprs import ExprBuilder
from .idents import Ident
from .relations import CanRelation
from .relations import Relation
from .relations import RelationBuilder
from .stmts import Stmt


##


class SelectItem(Node, lang.Final):
    v: Expr
    a: Ident | None = dc.xfield(None, repr_fn=dc.opt_repr)


class Select(Stmt, lang.Final):
    items: ta.Sequence[SelectItem] = dc.xfield(coerce=tuple)
    from_: Relation | None = dc.xfield(None, repr_fn=dc.opt_repr)
    where: Expr | None = dc.xfield(None, repr_fn=dc.opt_repr)


CanSelectItem: ta.TypeAlias = SelectItem | CanExpr


class SelectBuilder(RelationBuilder, ExprBuilder):
    def select_item(self, o: CanSelectItem) -> SelectItem:
        if isinstance(o, SelectItem):
            return o
        else:
            return SelectItem(self.expr(o))

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
