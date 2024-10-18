"""
TODO:
 - case
 - cast / ::
"""
import typing as ta

from ... import lang
from .base import Node
from .base import Value
from .idents import Ident
from .names import CanName
from .names import Name
from .names import NameBuilder


##


class Expr(Node, lang.Abstract):
    pass


class Literal(Expr, lang.Final):
    v: Value


class NameExpr(Expr, lang.Final):
    n: Name


class Param(Expr, lang.Final):
    n: str | None = None

    def __repr__(self) -> str:
        if self.n is not None:
            return f'{self.__class__.__name__}({self.n!r})'
        else:
            return f'{self.__class__.__name__}(@{hex(id(self))[2:]})'

    def __eq__(self, other):
        if not isinstance(other, Param):
            return False
        if self.n is None and other.n is None:
            return self is other
        else:
            return self.n == other.n


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
        elif isinstance(o, (Name, Ident)):
            return NameExpr(self.name(o))
        else:
            return self.literal(o)

    @ta.final
    def e(self, o: CanExpr) -> Expr:
        return self.expr(o)

    #

    def param(self, n: str | None = None) -> Param:
        return Param(n)

    @ta.final
    def p(self, n: str | None = None) -> Param:
        return self.param(n)
