import typing as ta

from ... import lang
from .base import Node
from .exprs import CanExpr
from .exprs import ExprBuilder


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
