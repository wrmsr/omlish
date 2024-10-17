import enum
import typing as ta

from omlish import check
from omlish import lang
from omlish import dataclasses as dc


##


Ident: ta.TypeAlias = str
Value: ta.TypeAlias = ta.Any


##


class Node(dc.Data, lang.Abstract):
    pass


##


class Expr(Node, lang.Abstract):
    pass


#


class Literal(Expr, lang.Final):
    v: Value


#


class UnaryOp(enum.Enum):
    NOT = enum.auto()


class Unary(Expr, lang.Final):
    op: UnaryOp
    v: Expr


#


class BinaryOp(enum.Enum):
    ADD = enum.auto()
    SUB = enum.auto()

    EQ = enum.auto()
    NE = enum.auto()


class Binary(Expr, lang.Final):
    op: BinaryOp
    l: Expr
    r: Expr

#


class MultiOp(enum.Enum):
    AND = enum.auto()
    OR = enum.auto()


class Multi(Expr, lang.Final):
    op: MultiOp
    es: ta.Sequence[Expr]


##


class Stmt(Node, lang.Abstract):
    pass


class ExprStmt(Stmt, lang.Final):
    pass


#


class Relation(Node, lang.Abstract):
    pass


class Table(Relation, lang.Final):
    n: Ident
    a: Ident | None = dc.xfield(None, repr_fn=dc.opt_repr)


class SelectItem(Node, lang.Final):
    v: Expr
    a: Ident | None = dc.xfield(None, repr_fn=dc.opt_repr)


class Select(Stmt, lang.Final):
    its: ta.Sequence[SelectItem]
    fr: Relation | None = dc.xfield(None, repr_fn=dc.opt_repr)
    wh: Expr | None = dc.xfield(None, repr_fn=dc.opt_repr)


##


CanLiteral: ta.TypeAlias = Literal | Value
CanExpr: ta.TypeAlias = Expr | CanLiteral
CanSelectItem: ta.TypeAlias = SelectItem | CanExpr
CanRelation: ta.TypeAlias = Relation | Ident


class Builder:
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
        else:
            return self.literal(o)

    #

    def unary(self, op: UnaryOp, v: CanExpr) -> Unary:
        return Unary(op, self.expr(v))

    def not_(self, v: CanExpr) -> Unary:
        return self.unary(UnaryOp.NOT, v)

    #

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

    #

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

    #

    def select_item(self, o: CanSelectItem) -> SelectItem:
        if isinstance(o, SelectItem):
            return o
        else:
            return SelectItem(self.expr(o))

    def relation(self, o: CanRelation) -> Relation:
        if isinstance(o, Relation):
            return o
        elif isinstance(o, Ident):
            return Relation(o)
        else:
            raise TypeError(o)

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


Q = Builder()


def _main() -> None:
    print(Q.select([Q.literal(1)]))


if __name__ == '__main__':
    _main()
