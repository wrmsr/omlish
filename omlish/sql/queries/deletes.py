from ... import dataclasses as dc
from ... import lang
from ... import marshal as msh
from .exprs import CanExpr
from .exprs import Expr
from .exprs import ExprBuilder
from .relations import CanRelation
from .relations import Relation
from .relations import RelationBuilder
from .stmts import Stmt


##


class Delete(Stmt, lang.Final):
    from_: Relation | None = dc.xfield(None, repr_fn=lang.opt_repr) | msh.with_field_options(name='from', omit_if=lang.is_none)  # noqa
    where: Expr | None = dc.xfield(None, repr_fn=lang.opt_repr) | msh.with_field_options(omit_if=lang.is_none)


class DeleteBuilder(RelationBuilder, ExprBuilder):
    def delete(
            self,
            from_: CanRelation | None = None,
            where: CanExpr | None = None,
    ) -> Delete:
        return Delete(
            from_=self.relation(from_) if from_ is not None else None,
            where=self.expr(where) if where is not None else None,
        )
