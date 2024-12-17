import enum
import typing as ta

from omnibus import collections as col
from omnibus import dataclasses as dc

from ...utils import build_enum_value_map
from .base import Expr
from .base import Identifier
from .base import Node
from .base import String
from .base import TypeSpec


class BinaryOp(enum.Enum):
    AND = 'and'
    OR = 'or'

    EQ = '='
    NE = '!='
    NEX = '<>'
    LT = '<'
    LTE = '<='
    GT = '>'
    GTE = '>='

    ADD = '+'
    SUB = '-'
    MUL = '*'
    DIV = '/'
    MOD = '%'
    CONCAT = '||'


BINARY_OP_MAP: ta.Mapping[str, BinaryOp] = build_enum_value_map(BinaryOp)


LOGIC_OPS: ta.AbstractSet[BinaryOp] = frozenset([
    BinaryOp.AND,
    BinaryOp.OR,
])


CMP_OPS: ta.AbstractSet[BinaryOp] = frozenset([
    BinaryOp.EQ,
    BinaryOp.NE,
    BinaryOp.NEX,
    BinaryOp.LT,
    BinaryOp.LTE,
    BinaryOp.GT,
    BinaryOp.GTE,
])


ARITH_OPS: ta.AbstractSet[BinaryOp] = frozenset([
    BinaryOp.ADD,
    BinaryOp.SUB,
    BinaryOp.MUL,
    BinaryOp.DIV,
    BinaryOp.MOD,
    BinaryOp.CONCAT,
])


class BinaryExpr(Expr):
    left: Expr
    op: BinaryOp
    right: Expr


class UnaryOp(enum.Enum):
    NOT = 'not'

    PLUS = '+'
    MINUS = '-'


UNARY_OP_MAP: ta.Mapping[str, UnaryOp] = build_enum_value_map(UnaryOp)


class UnaryExpr(Expr):
    op: UnaryOp
    value: Expr


class IntervalUnit(enum.Enum):
    SECOND = 'second'
    MINUTE = 'minute'
    HOUR = 'hour'
    DAY = 'day'
    MONTH = 'month'
    YEAR = 'year'


INTERVAL_UNIT_MAP: ta.Mapping[str, IntervalUnit] = build_enum_value_map(IntervalUnit)


class Interval(Expr):
    value: Expr
    unit: ta.Optional[IntervalUnit] = None


class CaseItem(Node):
    when: Expr
    then: Expr


class Case(Expr):
    value: ta.Optional[Expr]
    items: ta.Sequence[CaseItem] = dc.field(coerce=col.seq)
    default: ta.Optional[Expr] = None


class Cast(Expr):
    value: Expr
    type: TypeSpec


class CastCall(Expr):
    value: Expr
    type: TypeSpec


class Traversal(Expr):
    value: Expr
    keys: ta.Sequence[Expr] = dc.field(coerce=col.seq)


class IsNull(Expr):
    value: Expr
    not_: bool = False


class LikeKind(enum.Enum):
    LIKE = 'like'
    ILIKE = 'ilike'
    RLIKE = 'rlike'


LIKE_KIND_MAP: ta.Mapping[str, LikeKind] = build_enum_value_map(LikeKind)


class Like(Expr):
    kind: LikeKind
    value: Expr
    patterns: ta.Sequence[Expr] = dc.field(coerce=col.seq)
    not_: bool = False
    any: bool = False
    escape: ta.Optional[Expr] = None


class Date(Expr):
    value: String


class Extract(Expr):
    part: Identifier
    value: Expr


class InList(Expr):
    needle: Expr
    haystack: ta.Sequence[Expr] = dc.field(coerce=col.seq)
    not_: bool = False


class Between(Expr):
    value: Expr
    lower: Expr
    upper: Expr


class Var(Expr):
    name: str


class Param(Expr):
    name: str
