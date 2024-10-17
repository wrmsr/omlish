import enum
import typing as ta

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


class MultiOp(enum.Enum):
    AND = enum.auto()
    OR = enum.auto()


class Multi(Expr, lang.Final):
    op: MultiOp
    cs: ta.Sequence[Expr]


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


class UnaryOp(enum.Enum):
    NOT = enum.auto()


class Unary(Expr, lang.Final):
    op: UnaryOp
    v: Expr


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
    a: Ident | None = None


class SelectItem(Node, lang.Final):
    v: Expr
    a: Ident | None = None


class Select(Stmt, lang.Final):
    its: ta.Sequence[SelectItem]
    fr: Relation | None = None
    wh: Expr | None = None


##


CanLiteral: ta.TypeAlias = Literal | Value
CanExpr: ta.TypeAlias = Expr | CanLiteral
CanSelectItem: ta.TypeAlias = SelectItem | CanExpr


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
        )


##


Q = Builder()


def _main() -> None:
    print(Q.select([Q.literal(1)]))


if __name__ == '__main__':
    _main()
