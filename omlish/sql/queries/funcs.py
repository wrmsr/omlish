import operator
import typing as ta

from ... import dataclasses as dc
from ... import lang
from ... import marshal as msh
from .exprs import CanExpr
from .exprs import Expr
from .exprs import ExprBuilder
from .keywords import Keyword
from .names import CanName
from .names import Name


##


class Func(Expr, lang.Final):
    func: Keyword | Name
    args: ta.Sequence[Expr] = dc.xfield((), coerce=tuple, repr_fn=lang.truthy_repr) | msh.with_field_options(omit_if=operator.not_)  # noqa


class FuncBuilder(ExprBuilder):
    def func(
            self,
            func: Keyword | CanName,
            *args: CanExpr,
    ) -> Func:
        return Func(
            func if isinstance(func, Keyword) else self.name(func),
            tuple(map(self.expr, args)),
        )
