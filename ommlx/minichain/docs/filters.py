import enum
import functools
import typing as ta

from omlish import dataclasses as dc
from omlish import lang

from .docs import FieldRef


##


class Filter(lang.Abstract):
    @property
    def children(self) -> ta.Iterable['Filter']:
        return ()

    def __and__(self, other) -> 'Filter':
        return and_(self, other)

    def __or__(self, other) -> 'Filter':
        return or_(self, other)

    def __neg__(self) -> 'Filter':
        return not_(self)


##


class MultiOp(enum.Enum):
    AND = '&&'
    OR = '||'


@dc.dataclass(frozen=True)
class MultiFilter(Filter, lang.Final):
    op: MultiOp = dc.xfield(check_type=True)
    children: ta.Sequence[Filter] = dc.xfield(
        override=True,
        validate=lambda v: len(v) > 1 and all(isinstance(e, Filter) for e in v),
    )

    def __str__(self) -> str:
        return f'({f" {self.op.value} ".join(map(str, self.children))})'


def multi(op: MultiOp, *children: Filter) -> Filter:
    if len(children) == 1:
        return children[0]
    return MultiFilter(op, children)


and_ = functools.partial(multi, MultiOp.AND)
or_ = functools.partial(multi, MultiOp.OR)


##


@dc.dataclass(frozen=True)
class Not(Filter, lang.Final):
    child: Filter = dc.xfield(check_type=True)

    @property
    def children(self) -> ta.Iterable[Filter]:
        return (self.child,)


def not_(child: Filter) -> Filter:
    if isinstance(child, Not):
        return child.child
    return Not(child)


##


class CmpOp(enum.Enum):
    EQ = '='
    NE = '!='
    LT = '<'
    LE = '<='
    GT = '>'
    GE = '>='


@dc.dataclass(frozen=True)
class Cmp(Filter, lang.Final):
    op: CmpOp = dc.xfield(check_type=True)
    field: FieldRef = dc.xfield(check_type=True)
    value: ta.Any = dc.xfield()

    def __str__(self) -> str:
        return f'{self.field} {self.op.value} {self.value}'


def cmp(op: CmpOp, field: FieldRef, value: ta.Any) -> Filter:
    return Cmp(op, field, value)


eq = functools.partial(cmp, CmpOp.EQ)
ne = functools.partial(cmp, CmpOp.NE)
lt = functools.partial(cmp, CmpOp.LT)
le = functools.partial(cmp, CmpOp.LE)
gt = functools.partial(cmp, CmpOp.GT)
ge = functools.partial(cmp, CmpOp.GE)


def in_(field: FieldRef, *values: ta.Any) -> Filter:
    return or_(*[eq(field, v) for v in values])
