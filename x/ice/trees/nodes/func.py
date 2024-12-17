import enum
import typing as ta

from omnibus import collections as col
from omnibus import dataclasses as dc

from .base import Expr
from .base import Identifier
from .base import Node
from .base import QualifiedNameNode
from .base import SetQuantifier
from .base import SortItem


class Precedence(enum.Enum):
    PRECEDING = 'preceding'
    FOLLOWING = 'following'


class FrameBound(Node, abstract=True):
    pass


class NumFrameBound(FrameBound):
    num: int
    precedence: Precedence


class UnboundedFrameBound(FrameBound):
    precedence: Precedence


class CurrentRowFrameBound(FrameBound):
    pass


class Frame(Node, abstract=True):
    pass


class RowsOrRange(enum.Enum):
    ROWS = 'rows'
    RANGE = 'range'


class SingleFrame(Frame):
    rows_or_range: RowsOrRange
    bound: FrameBound


class DoubleFrame(Frame):
    rows_or_range: RowsOrRange
    min: FrameBound
    max: FrameBound


class Over(Node):
    partition_by: ta.Sequence[Expr] = dc.field((), coerce=col.seq)
    order_by: ta.Sequence[SortItem] = dc.field((), coerce=col.seq)
    frame: ta.Optional[Frame] = None


class Kwarg(Node):
    name: Identifier
    value: Expr


class IgnoreOrRespect(enum.Enum):
    IGNORE = 'ignore'
    RESPECT = 'respect'


class FunctionCall(Node):
    name: QualifiedNameNode
    args: ta.Sequence[Expr] = dc.field((), coerce=col.seq)
    kwargs: ta.Sequence[Kwarg] = dc.field((), coerce=col.seq)
    set_quantifier: ta.Optional[SetQuantifier] = None
    nulls: ta.Optional[IgnoreOrRespect] = None
    within_group: ta.Sequence[SortItem] = dc.field((), coerce=col.seq)
    over: ta.Optional[Over] = None


class FunctionCallExpr(Expr):
    call: FunctionCall
