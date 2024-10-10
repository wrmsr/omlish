import enum
import typing as ta

from omlish import dataclasses as dc
from omlish import lang


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


#


class MultiOp(enum.Enum):
    AND = '&&'
    OR = '||'


@dc.dataclass(frozen=True)
class MultiFilter(Filter, lang.Final):
    op: MultiOp = dc.xfield(check_type=True)
    children: ta.Sequence[Filter] = dc.xfield(override=True, validate=lambda v: all(isinstance(e, Filter) for e in v))

    def __str__(self) -> str:
        raise NotImplementedError


def multi_(op: MultiOp, *children: Filter) -> Filter:
    if len(children) == 1:
        return children[0]
    return MultiFilter(op, children)


def and_(*children: Filter) -> Filter:
    return multi_(MultiOp.AND, *children)


def or_(*children: Filter) -> Filter:
    return multi_(MultiOp.OR, *children)


#


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


#


@dc.dataclass(frozen=True)
class Field(lang.Final):
    n: str = dc.xfield(check_type=True)

    def __str__(self) -> str:
        return f':{self.n}'


def f(f: str | Field) -> Field:  # noqa
    if isinstance(f, Field):
        return f
    return Field(f)


class CmpOp(enum.Enum):
    EQ = '='
    NE = '!='
    LT = '<'
    LE = '<='
    GT = '>'
    GE = '>='


@dc.dataclass
class Cmp(Filter, lang.Final):
    op: CmpOp = dc.xfield(check_type=True)
    field: Field = dc.xfield(check_type=True)
    value: ta.Any = dc.field()

    def __str__(self) -> str:
        return f'{self.field} {self.op.value} {self.value}'


def cmp(op: CmpOp, field: Field, value: ta.Any) -> Filter:
    return Cmp(op, field, value)


def eq(field: Field, value: ta.Any) -> Filter:
    return cmp(CmpOp.EQ, field, value)


def ne(field: Field, value: ta.Any) -> Filter:
    return cmp(CmpOp.NE, field, value)


def lt(field: Field, value: ta.Any) -> Filter:
    return cmp(CmpOp.LT, field, value)


def le(field: Field, value: ta.Any) -> Filter:
    return cmp(CmpOp.LE, field, value)


def gt(field: Field, value: ta.Any) -> Filter:
    return cmp(CmpOp.GT, field, value)


def ge(field: Field, value: ta.Any) -> Filter:
    return cmp(CmpOp.GE, field, value)


##


def _main() -> None:
    print(f('foo'))
    print(eq(f('foo'), 1) & le(f('bar'), 2))


if __name__ == '__main__':
    _main()
