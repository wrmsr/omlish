import typing as ta

from ... import dataclasses as dc
from ... import lang
from .exprs import CanExpr
from .exprs import Expr
from .exprs import ExprBuilder
from .idents import CanIdent
from .idents import Ident
from .relations import CanRelation
from .relations import Relation
from .relations import RelationBuilder
from .selects import Select
from .stmts import Stmt


##


class Values(dc.Frozen, lang.Final):
    vs: ta.Sequence[Expr] = dc.xfield(coerce=tuple)


class Insert(Stmt, lang.Final):
    columns: ta.Sequence[Ident] = dc.xfield(coerce=tuple)
    into: Relation
    data: Values | Select


CanValues: ta.TypeAlias = Values | ta.Sequence[CanExpr]


class InsertBuilder(RelationBuilder, ExprBuilder):
    def values(self, vs: CanValues) -> Values:
        if isinstance(vs, Values):
            return vs
        else:
            return Values(tuple(self.expr(v) for v in vs))

    def insert(
            self,
            columns: ta.Sequence[CanIdent],
            into: CanRelation,
            data: Select | Values | ta.Sequence[CanExpr],
    ) -> Insert:
        return Insert(
            columns=tuple(self.ident(c) for c in columns),
            into=self.relation(into),
            data=data if isinstance(data, Select) else self.values(data),
        )
