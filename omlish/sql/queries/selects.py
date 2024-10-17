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
    its: ta.Sequence[SelectItem] = dc.xfield(coerce=tuple)
    fr: Relation | None = dc.xfield(None, repr_fn=dc.opt_repr)
    wh: Expr | None = dc.xfield(None, repr_fn=dc.opt_repr)


CanSelectItem: ta.TypeAlias = SelectItem | CanExpr


class SelectBuilder(ExprBuilder, RelationBuilder):
    def select_item(self, o: CanSelectItem) -> SelectItem:
        if isinstance(o, SelectItem):
            return o
        else:
            return SelectItem(self.expr(o))

    def select(
            self,
            its: ta.Sequence[CanSelectItem],
            fr: CanRelation | None = None,
            wh: CanExpr | None = None,
    ) -> Select:
        return Select(
            [self.select_item(i) for i in its],
            fr=self.relation(fr) if fr is not None else None,
            wh=self.expr(wh) if wh is not None else None,
        )
