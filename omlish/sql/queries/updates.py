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


class Field(Node, lang.Final):
    c: Ident
    v: Expr


class Fields(Node, lang.Final):
    fields: ta.Sequence[Field] = dc.xfield(coerce=tuple)


class Update(Stmt, lang.Final):
    into: Relation
    fields: Fields
    # from_: Relation = dc.xfield(repr_fn=lang.opt_repr) | msh.with_field_options(name='from', omit_if=lang.is_none)
    where: Expr | None = dc.xfield(None, repr_fn=lang.opt_repr) | msh.with_field_options(omit_if=lang.is_none)


CanField: ta.TypeAlias = Field | tuple[CanIdent, CanExpr]

CanFields: ta.TypeAlias = ta.Union[  # noqa
    Fields,
    ta.Mapping[CanIdent, CanExpr],
    ta.Sequence[CanField],
]


class UpdateBuilder(RelationBuilder, ExprBuilder):
    def field(self, f: CanField) -> Field:
        if isinstance(f, Field):
            return f
        elif isinstance(f, tuple):
            c, v = f
            return Field(
                self.ident(c),
                self.expr(v),
            )
        else:
            raise TypeError(f)

    def fields(self, fs: CanFields) -> Fields:
        if isinstance(fs, Fields):
            return fs
        elif isinstance(fs, collections.abc.Mapping):
            return Fields(tuple(self.field(i) for i in fs.items()))
        elif isinstance(fs, collections.abc.Sequence):
            return Fields(tuple(self.field(i) for i in fs))
        else:
            raise TypeError(fs)

    def update(
            self,
            into: CanRelation,
            fields: Fields | CanFields,
            *,
            # from_: CanRelation | None = None,
            where: CanExpr | None = None,
    ) -> Update:
        return Update(
            into=self.relation(into),
            fields=self.fields(fields),
            where=self.expr(where) if where is not None else None,
        )
