import collections.abc
import typing as ta

from ... import dataclasses as dc
from ... import lang
from ... import marshal as msh
from .base import Node
from .exprs import CanExpr
from .exprs import Expr
from .exprs import ExprBuilder
from .idents import CanIdent
from .idents import Ident
from .relations import CanRelation
from .relations import Relation
from .relations import RelationBuilder
from .stmts import Stmt


##


class Fields(Node, lang.Final):
    kvs: ta.Sequence[tuple[Ident, Expr]] = dc.xfield(coerce=tuple)


class Update(Stmt, lang.Final):
    relation: Relation = dc.xfield(repr_fn=lang.opt_repr) | msh.with_field_options(name='from', omit_if=lang.is_none)
    fields: Fields
    # from_: Relation = dc.xfield(repr_fn=lang.opt_repr) | msh.with_field_options(name='from', omit_if=lang.is_none)
    where: Expr | None = dc.xfield(None, repr_fn=lang.opt_repr) | msh.with_field_options(omit_if=lang.is_none)


CanFields: ta.TypeAlias = Fields | ta.Sequence[tuple[CanIdent, CanExpr]] | ta.Mapping[CanIdent, CanExpr]


class UpdateBuilder(RelationBuilder, ExprBuilder):
    def fields(self, fs: CanFields) -> Fields:
        if isinstance(fs, Fields):
            return fs
        elif isinstance(fs, collections.abc.Mapping):
            return Fields(tuple((self.ident(k), self.expr(v)) for k, v in fs.items()))
        elif isinstance(fs, collections.abc.Sequence):
            return Fields(tuple((self.ident(k), self.expr(v)) for k, v in fs))
        else:
            raise TypeError(fs)

    def update(
            self,
            relation: CanRelation,
            fields: Fields | CanFields,
            # from_: CanRelation | None = None,
            where: CanExpr | None = None,
    ) -> Update:
        return Update(
            relation=self.relation(relation),
            fields=fields if isinstance(fields, Fields) else self.fields(fields),
            where=self.expr(where) if where is not None else None,
        )
