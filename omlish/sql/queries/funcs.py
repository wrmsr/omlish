import typing as ta

from ... import dataclasses as dc
from ... import lang
from .exprs import CanExpr
from .exprs import Expr
from .exprs import ExprBuilder
from .names import CanName
from .names import Name


##


class Func(Expr, lang.Final):
    name: Name
    args: ta.Sequence[Expr] = dc.xfield(coerce=tuple)


class FuncBuilder(ExprBuilder):
    def func(self, n: CanName, *args: CanExpr) -> Func:
        return Func(
            self.name(n),
            *map(self.expr, args),
        )
