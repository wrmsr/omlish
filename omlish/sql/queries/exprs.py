"""
TODO:
 - case
 - cast / ::
 - explicit null? already wrapped in non-null Literal node
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
from .params import CanParam
from .params import Param
from .params import ParamBuilder


##


class Expr(Node, lang.Abstract):
    pass


#


class Literal(Expr, lang.Final):
    v: Value


#


class NameExpr(Expr, lang.Final):
    n: Name


#


class ParamExpr(Expr, lang.Final):
    p: Param


##


CanLiteral: ta.TypeAlias = Literal | Value
CanExpr: ta.TypeAlias = Expr | CanParam | CanName | CanLiteral


class ExprBuilder(ParamBuilder, NameBuilder):
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
        elif isinstance(o, Param):
            return ParamExpr(o)
        elif isinstance(o, (NameLike, IdentLike)):
            return NameExpr(self.name(o))
        else:
            return self.literal(o)

    @ta.final
    def e(self, o: CanExpr) -> Expr:
        return self.expr(o)
