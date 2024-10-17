import enum
import typing as ta

from omlish import check
from omlish import lang
from omlish import dataclasses as dc


##


Value: ta.TypeAlias = ta.Any


##


class Node(dc.Data, lang.Abstract):
    pass


class Builder(lang.Abstract):
    pass


##


class Ident(Node, lang.Final):
    s: str


CanIdent: ta.TypeAlias = Ident | str


class IdentBuilder(Builder):
    def ident(self, o: CanIdent) -> Ident:
        if isinstance(o, Ident):
            return o
        elif isinstance(o, str):
            return Ident(o)
        else:
            raise TypeError(o)


##


class Expr(Node, lang.Abstract):
    pass


class Literal(Expr, lang.Final):
    v: Value


class IdentExpr(Expr, lang.Final):
    i: Ident


CanLiteral: ta.TypeAlias = Literal | Value
CanExpr: ta.TypeAlias = Expr | Ident | CanLiteral


class ExprBuilder(Builder):
    def literal(self, o: CanLiteral) -> Literal:
        if isinstance(o, Literal):
            return o
        elif isinstance(o, Node):
            raise TypeError(o)
        else:
            return Literal(o)

    def expr(self, o: CanExpr) -> Expr:
        if isinstance(o, Expr):
            return o
        elif isinstance(o, Ident):
            return IdentExpr(o)
        else:
            return self.literal(o)


##


class UnaryOp(enum.Enum):
    NOT = enum.auto()


class Unary(Expr, lang.Final):
    op: UnaryOp
    v: Expr


class UnaryBuilder(ExprBuilder):
    def unary(self, op: UnaryOp, v: CanExpr) -> Unary:
        return Unary(op, self.expr(v))

    def not_(self, v: CanExpr) -> Unary:
        return self.unary(UnaryOp.NOT, v)


##


class BinaryOp(enum.Enum):
    ADD = enum.auto()
    SUB = enum.auto()

    EQ = enum.auto()
    NE = enum.auto()


class Binary(Expr, lang.Final):
    op: BinaryOp
    l: Expr
    r: Expr


class BinaryBuilder(ExprBuilder):
    def binary(self, op: BinaryOp, *es: CanExpr) -> Expr:
        check.not_empty(es)
        l = self.expr(es[0])
        for r in es[1:]:
            l = Binary(op, l, self.expr(r))
        return l

    def add(self, *es: CanExpr) -> Expr:
        return self.binary(BinaryOp.ADD, *es)

    def sub(self, *es: CanExpr) -> Expr:
        return self.binary(BinaryOp.SUB, *es)

    def eq(self, *es: CanExpr) -> Expr:
        return self.binary(BinaryOp.EQ, *es)

    def ne(self, *es: CanExpr) -> Expr:
        return self.binary(BinaryOp.NE, *es)


##


class MultiOp(enum.Enum):
    AND = enum.auto()
    OR = enum.auto()


class Multi(Expr, lang.Final):
    op: MultiOp
    es: ta.Sequence[Expr]


class MultiBuilder(ExprBuilder):
    def multi(self, op: MultiOp, *es: CanExpr) -> Expr:
        check.not_empty(es)
        if len(es) == 1:
            return self.expr(es[0])
        else:
            return Multi(op, [self.expr(e) for e in es])

    def and_(self, *es: CanExpr) -> Expr:
        return self.multi(MultiOp.AND, *es)

    def or_(self, *es: CanExpr) -> Expr:
        return self.multi(MultiOp.OR, *es)


##


class Stmt(Node, lang.Abstract):
    pass


class ExprStmt(Stmt, lang.Final):
    pass


CanStmt: ta.TypeAlias = Stmt | CanExpr


class StmtBuilder(ExprBuilder):
    def stmt(self, o: CanStmt) -> Stmt:
        if isinstance(o, Stmt):
            return o
        else:
            return ExprStmt(self.expr(o))


##


class Relation(Node, lang.Abstract):
    pass


class Table(Relation, lang.Final):
    n: Ident
    a: Ident | None = dc.xfield(None, repr_fn=dc.opt_repr)


CanRelation: ta.TypeAlias = Relation | CanIdent


class RelationBuilder(IdentBuilder):
    def relation(self, o: CanRelation) -> Relation:
        if isinstance(o, Relation):
            return o
        else:
            return Relation(self.ident(o))


##


class SelectItem(Node, lang.Final):
    v: Expr
    a: Ident | None = dc.xfield(None, repr_fn=dc.opt_repr)


class Select(Stmt, lang.Final):
    its: ta.Sequence[SelectItem]
    fr: Relation | None = dc.xfield(None, repr_fn=dc.opt_repr)
    wh: Expr | None = dc.xfield(None, repr_fn=dc.opt_repr)


CanSelectItem: ta.TypeAlias = SelectItem | CanExpr


class SelectBuilder(RelationBuilder, ExprBuilder):
    def select_item(self, o: CanSelectItem) -> SelectItem:
        if isinstance(o, SelectItem):
            return o
        else:
            return SelectItem(self.expr(o))

    def select(
            self,
            its: ta.Sequence[CanSelectItem],
            fr: Relation | None = None,
            wh: Expr | None = None,
    ) -> Select:
        return Select(
            [self.select_item(i) for i in its],
            fr=self.relation(fr) if fr is not None else None,
            wh=self.expr(wh) if wh is not None else None,
        )


##


class StdBuilder(
    SelectBuilder,
    RelationBuilder,
    StmtBuilder,
    MultiBuilder,
    BinaryBuilder,
    UnaryBuilder,
    ExprBuilder,
    IdentBuilder,
    Builder,
):
    pass


##


Q = StdBuilder()


def _main() -> None:
    print(Q.select(
        [
            Q.literal(1),
        ],
        wh=Q.and_(
            Q.eq(1, 2),
        )
    ))


if __name__ == '__main__':
    _main()
