import typing as ta

from .base import Expr
from .base import Ident
from .base import Node
from .ops import BinOp
from .ops import BoolOp
from .ops import CmpOp
from .ops import UnaryOp


class Const(Expr):
    value: ta.Any


class GetVar(Expr):
    name: Ident


class GetAttr(Expr):
    obj: Expr
    attr: Ident


class GetItem(Expr):
    obj: Expr
    idx: Expr


class BinExpr(Expr):
    left: Expr
    op: BinOp
    right: Expr


class BoolExpr(Expr):
    left: Expr
    op: BoolOp
    right: Expr


class CmpExpr(Expr):
    left: Expr
    op: CmpOp
    right: Expr


class UnaryExpr(Expr):
    op: UnaryOp
    value: Expr


class Keyword(Node):
    name: ta.Optional[Ident]
    value: Expr


class Call(Expr):
    fn: Expr
    args: ta.Sequence[Expr]
    keywords: ta.Sequence[Keyword] = ()


class Starred(Expr):
    value: Expr
