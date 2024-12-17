"""
TODO:
 - enable type checking
 - standardize names (+in g4): Expr not expression, Stmt not statement, Value not val, Rel not rel?
 - enforce field types (children in seqs only)

Visitors / Tools:
 - graphviz gen
"""
import abc
import collections.abc
import enum
import typing as ta

from omnibus import check
from omnibus import collections as col
from omnibus import dataclasses as dc
from omnibus import nodal
from omnibus import properties

from ...types import QualifiedName
from ...utils import build_dc_repr
from ...utils import build_enum_value_map


T = ta.TypeVar('T')
SelfNode = ta.TypeVar('SelfNode', bound='Node')
NodeGen = ta.Generator['Node', None, None]
NodeMapper = ta.Callable[['Node'], 'Node']
NoneType = type(None)


class Annotation(nodal.Annotation):
    pass


class Node(nodal.Nodal['Node', Annotation], repr=False, sealed='package'):
    __repr__ = build_dc_repr


class Expr(Node, abstract=True):
    pass


class Stmt(Node, abstract=True):
    pass


class Identifier(Expr):
    name: str = dc.field(check=lambda o: isinstance(o, str) and o)

    @classmethod
    def of(cls, obj: ta.Union['Identifier', str]) -> 'Identifier':
        if isinstance(obj, Identifier):
            return cls(obj.name)
        elif isinstance(obj, str):
            return cls(obj)
        else:
            raise TypeError(obj)


class QualifiedNameNode(Expr):
    parts: ta.Sequence[Identifier] = dc.field(coerce=col.seq)

    @properties.cached
    @property
    def name(self) -> QualifiedName:
        return QualifiedName(tuple(p.name for p in self.parts))

    @classmethod
    def of(
            cls,
            obj: ta.Union[
                'QualifiedNameNode',
                QualifiedName,
                ta.Iterable[ta.Union[Identifier, str]],
            ]
    ) -> 'QualifiedNameNode':
        if isinstance(obj, QualifiedNameNode):
            return cls([Identifier.of(p) for p in obj.parts])
        elif isinstance(obj, QualifiedName):
            return cls([Identifier(p) for p in obj])
        elif isinstance(obj, str):
            raise TypeError(obj)
        elif isinstance(obj, collections.abc.Iterable):
            return cls([Identifier.of(p) for p in check.not_isinstance(obj, str)])
        else:
            raise TypeError(obj)


class Primitive(Expr, ta.Generic[T], abstract=True):

    @abc.abstractproperty
    def value(self) -> T:
        raise NotImplementedError


class Number(Primitive[T], abstract=True):
    pass


class Integer(Number[int]):
    value: int


class Decimal(Number[str]):
    value: str


class Float(Number[str]):
    value: str


class String(Primitive[str]):
    value: str


class Null(Primitive[NoneType]):
    value = None


class ETrue(Primitive[bool]):
    value = True


class EFalse(Primitive[bool]):
    value = False


class StarExpr(Expr):
    pass


class TypeSpec(Node):
    name: Identifier
    args: ta.Sequence[Expr] = dc.field((), coerce=col.seq)


class Direction(enum.Enum):
    ASC = 'asc'
    DESC = 'desc'


DIRECTION_MAP: ta.Mapping[str, Direction] = build_enum_value_map(Direction)


class FirstOrLast(enum.Enum):
    FIRST = 'first'
    LAST = 'last'


class SortItem(Node):
    value: Expr
    direction: ta.Optional[Direction] = None
    nulls: ta.Optional[FirstOrLast] = None


class SetQuantifier(enum.Enum):
    DISTINCT = 'distinct'
    EXCEPT = 'except'
    ALL = 'all'


SET_QUANTIFIER_MAP: ta.Mapping[str, SetQuantifier] = build_enum_value_map(SetQuantifier)
