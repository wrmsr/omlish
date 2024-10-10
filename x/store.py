import enum
import functools
import typing as ta

from omlish import cached
from omlish import collections as col
from omlish import dataclasses as dc
from omlish import lang
from ommlx.minichain.vectors import Vector


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
class FieldRef(lang.Final):
    n: str = dc.xfield(check_type=True)

    def __str__(self) -> str:
        return f':{self.n}'


def f(o: str | FieldRef) -> FieldRef:
    if isinstance(o, FieldRef):
        return o
    return FieldRef(o)


def f_(o: str | FieldRef) -> str:
    if isinstance(o, str):
        return o
    elif isinstance(o, FieldRef):
        return o.n
    else:
        raise TypeError(o)


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


##


@dc.dataclass(frozen=True)
class Dtype(lang.Final):
    name: str
    cls: type


class Dtypes(enum.Enum):
    STR = Dtype('str', str)
    BYTES = Dtype('bytes', bytes)

    INT = Dtype('int', int)
    FLOAT = Dtype('float', float)

    VECTOR = Dtype('vector', Vector)


@dc.dataclass(frozen=True)
class DocField(lang.Final):
    name: str
    dtype: Dtype


@dc.dataclass(frozen=True)
class DocSchema(lang.Final):
    fields: ta.Sequence[DocField] = dc.xfield(validate=lambda v: all(isinstance(e, DocField) for e in v))

    @cached.property
    @dc.init
    def fields_by_name(self) -> ta.Mapping[str, DocField]:
        return col.make_map_by(lambda f: f.name, self.fields, strict=True)  # noqa

    def __getitem__(self, key: str | FieldRef) -> DocField:
        return self.fields_by_name[f_(key)]


@dc.dataclass(frozen=True)
class Doc:
    values: ta.Mapping[str, ta.Any]

    def __getitem__(self, key: str | FieldRef) -> DocField:
        return self.values[f_(key)]


##


def _main() -> None:
    print(f('foo'))
    print(eq(f('foo'), 1) & le(f('bar'), 2))


if __name__ == '__main__':
    _main()
