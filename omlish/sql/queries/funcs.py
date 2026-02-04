import operator
import typing as ta

from ... import dataclasses as dc
from ... import lang
from ... import marshal as msh
from .exprs import CanExpr
from .exprs import Expr
from .exprs import ExprBuilder
from .keywords import Keyword
from .keywords import Star
from .names import CanName
from .names import Name


##


FuncArg: ta.TypeAlias = ta.Union[  # noqa
    Expr,
    Star,
]


class Func(Expr, lang.Final):
    name: Keyword | Name
    args: ta.Sequence[FuncArg] = dc.xfield((), coerce=tuple, repr_fn=lang.truthy_repr) | msh.with_field_options(omit_if=operator.not_)  # noqa


CanFuncArg: ta.TypeAlias = FuncArg | CanExpr


class FuncBuilder(ExprBuilder):
    def func_arg(self, o: CanFuncArg) -> FuncArg:
        return o if isinstance(o, Star) else self.expr(o)

    def func(
            self,
            func: Keyword | CanName,
            *args: CanFuncArg,
    ) -> Func:
        return Func(
            func if isinstance(func, Keyword) else self.name(func),
            tuple(map(self.func_arg, args)),
        )
