import typing as ta

from ... import dataclasses as dc
from ... import lang
from ... import marshal as msh
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


class SelectItem(Node, lang.Abstract):
    pass


class AllSelectItem(SelectItem, lang.Final):
    pass


class ExprSelectItem(SelectItem, lang.Final):
    v: Expr
    a: Ident | None = dc.xfield(None, repr_fn=dc.opt_repr) | msh.with_field_metadata(omit_if=lang.is_none)


##


class Select(Stmt, lang.Final):
    items: ta.Sequence[SelectItem] = dc.xfield(coerce=tuple)
    from_: Relation | None = dc.xfield(None, repr_fn=dc.opt_repr) | msh.with_field_metadata(name='from', omit_if=lang.is_none)  # noqa
    where: Expr | None = dc.xfield(None, repr_fn=dc.opt_repr) | msh.with_field_metadata(omit_if=lang.is_none)


CanSelectItem: ta.TypeAlias = SelectItem | CanExpr


class SelectBuilder(RelationBuilder, ExprBuilder):
    @property
    def star(self) -> AllSelectItem:
        return AllSelectItem()

    def select_item(self, o: CanSelectItem) -> SelectItem:
        if isinstance(o, SelectItem):
            return o
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
