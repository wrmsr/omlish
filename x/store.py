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


class CompositeFilter(Filter, lang.Abstract):
    pass


@dc.dataclass(frozen=True)
class And(CompositeFilter, lang.Final):
    children: ta.Sequence[Filter] = dc.xfield(override=True, validate=lambda v: all(isinstance(e, Filter) for e in v))


@dc.dataclass(frozen=True)
class Or(CompositeFilter, lang.Final):
    children: ta.Sequence[Filter] = dc.xfield(override=True, validate=lambda v: all(isinstance(e, Filter) for e in v))


@dc.dataclass(frozen=True)
class Not(CompositeFilter, lang.Final):
    child: Filter = dc.xfield(check_type=True)

    @property
    def children(self) -> ta.Iterable[Filter]:
        return (self.child,)


def and_(*children: Filter) -> Filter:
    if len(children) == 1:
        return children[0]
    return And(children)


def or_(*children: Filter) -> Filter:
    if len(children) == 1:
        return children[0]
    return Or(children)


def not_(child: Filter) -> Filter:
    if isinstance(child, Not):
        return child.child
    return Not(child)


#


@dc.dataclass(frozen=True)
class Field(lang.Final):
    n: str = dc.xfield(check_type=True)

    def __str__(self) -> str:
        return f'f:{self.n}'


def f(f: str | Field) -> Field:  # noqa
    if isinstance(f, Field):
        return f
    return Field(f)


class Op(enum.Enum):
    EQ = '='
    NE = '!='
    LT = '<'
    LE = '<='
    GT = '>'
    GE = '>='


@dc.dataclass
class Cmp(Filter, lang.Final):
    op: Op = dc.xfield(check_type=True)
    field: Field = dc.xfield(check_type=True)
    value: ta.Any = dc.field()


def eq(field: Field, value: ta.Any) -> Filter:
    return Cmp(Op.EQ, field, value)


def ne(field: Field, value: ta.Any) -> Filter:
    return Cmp(Op.NE, field, value)


def lt(field: Field, value: ta.Any) -> Filter:
    return Cmp(Op.LT, field, value)


def le(field: Field, value: ta.Any) -> Filter:
    return Cmp(Op.LE, field, value)


def gt(field: Field, value: ta.Any) -> Filter:
    return Cmp(Op.GT, field, value)


def ge(field: Field, value: ta.Any) -> Filter:
    return Cmp(Op.GE, field, value)


##


def _main() -> None:
    print(f('foo'))
    print(eq(f('foo'), 1) & le(f('bar'), 2))


if __name__ == '__main__':
    _main()
