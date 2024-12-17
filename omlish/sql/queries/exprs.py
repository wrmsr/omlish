"""
TODO:
 - case
 - cast / ::
"""
import typing as ta

from ... import lang
from .base import Node
from .base import Value
from .idents import IdentLike
from .names import CanName
from .names import Name
from .names import NameBuilder
from .names import NameLike


##


class Expr(Node, lang.Abstract):
    pass


#


class Literal(Expr, lang.Final):
    v: Value


#


class NameExpr(Expr, lang.Final):
    n: Name


##


CanLiteral: ta.TypeAlias = Literal | Value
CanExpr: ta.TypeAlias = Expr | CanName | CanLiteral


class ExprBuilder(NameBuilder):
    def literal(self, o: CanLiteral) -> Literal:
        if isinstance(o, Literal):
            return o
        elif isinstance(o, Node):
            raise TypeError(o)
        else:
            return Literal(o)

    @ta.final
    def l(self, o: CanLiteral) -> Literal:  # noqa
        return self.literal(o)

    #

    def expr(self, o: CanExpr) -> Expr:
        if isinstance(o, Expr):
            return o
        elif isinstance(o, (NameLike, IdentLike)):
            return NameExpr(self.name(o))
        else:
            return self.literal(o)

    @ta.final
    def e(self, o: CanExpr) -> Expr:
        return self.expr(o)
