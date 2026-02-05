import operator
import typing as ta

from ... import dataclasses as dc
from ... import lang
from ... import marshal as msh
from .exprs import CanExpr
from .exprs import Expr
from .exprs import ExprBuilder
from .keywords import CanKeyword
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


class FuncArgsAccessor:
    def __init__(self, fb: 'FuncBuilder', k: CanKeyword) -> None:
        self.__fb = fb
        self.__k = k

    def __call__(self, *args: CanExpr) -> Func:
        return self.__fb.func(self.__fb.keyword(self.__k), *args)


class FuncAccessor:
    def __init__(self, fb: 'FuncBuilder') -> None:
        self.__fb = fb

    def __getattr__(self, k: CanKeyword) -> FuncArgsAccessor:
        return FuncArgsAccessor(self.__fb, k)


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

    @property
    def f(self) -> FuncAccessor:
        return FuncAccessor(self)
