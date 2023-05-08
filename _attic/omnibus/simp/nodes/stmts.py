import typing as ta

from ... import dataclasses as dc
from .base import Annotated
from .base import Expr
from .base import Ident
from .base import Stmt


class Raise(Stmt):
    value: Expr


class Return(Stmt):
    value: ta.Optional[Expr]


class If(Stmt):
    test: Expr
    then: ta.Sequence[Stmt]
    else_: ta.Optional[ta.Sequence[Stmt]] = dc.field(check=lambda l: l is None or l)


class ForIter(Stmt):
    var: Ident
    iter: Expr
    body: ta.Sequence[Stmt]


class ForRange(Stmt):
    var: Ident
    start: ta.Optional[int] = None
    stop: ta.Optional[int] = None
    step: ta.Optional[int] = None
    body: ta.Sequence[Stmt] = ()


class Break(Stmt):
    pass


class Continue(Stmt):
    pass


class Pass(Stmt):
    pass


class ExprStmt(Stmt):
    expr: Expr


class SetVar(Stmt, Annotated):
    name: Ident
    value: Expr


class SetAttr(Stmt, Annotated):
    obj: Expr
    attr: Ident
    value: Expr


class SetItem(Stmt, Annotated):
    obj: Expr
    idx: Expr
    value: Expr
