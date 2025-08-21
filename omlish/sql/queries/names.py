import abc
import functools
import typing as ta

from ... import cached
from ... import check
from ... import dataclasses as dc
from ... import lang
from ..qualifiedname import QualifiedName
from .base import HasQn
from .base import Node
from .idents import CanIdent
from .idents import Ident
from .idents import IdentBuilder
from .idents import as_ident


##


class NameLike(abc.ABC):  # noqa
    pass


##


def _coerce_name_parts(o: ta.Iterable[Ident]) -> ta.Sequence[Ident]:
    check.not_isinstance(o, str)
    return check.not_empty(tuple(check.isinstance(e, Ident) for e in o))


class Name(Node, NameLike, HasQn, lang.Final):
    ps: ta.Sequence[Ident] = dc.xfield(coerce=_coerce_name_parts)

    @cached.property
    def qn(self) -> QualifiedName:
        return QualifiedName(tuple(p.s for p in self.ps))


##


@functools.singledispatch
def as_name(o: ta.Any) -> Name:
    if isinstance(o, ta.Sequence):
        return Name([as_ident(p) for p in o])
    else:
        raise TypeError(o)


@as_name.register
def _(n: Name) -> Name:
    return n


@as_name.register
def _(o: Ident | str) -> Name:
    return Name([as_ident(o)])


##


CanName: ta.TypeAlias = ta.Union[
    NameLike,
    Name,
    CanIdent,
    ta.Sequence[CanIdent],
    'NameAccessor',
]


class NameAccessor(NameLike, lang.Final):
    def __init__(self, ps: tuple[str, ...] = ()) -> None:
        super().__init__()

        self.__query_name_parts__ = ps

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({self.__query_name_parts__!r})'

    def __getattr__(self, s: str) -> 'NameAccessor':
        return NameAccessor((*self.__query_name_parts__, s))

    def __call__(self, o: CanName) -> Name:
        n = as_name(o)
        if (ps := self.__query_name_parts__):
            n = Name(tuple(*tuple(Ident(p) for p in ps), *n.ps))  # type: ignore[arg-type]
        return n


@as_name.register
def _(a: NameAccessor) -> Name:
    return Name(tuple(Ident(p) for p in a.__query_name_parts__))


##


class NameBuilder(IdentBuilder):
    @ta.final
    def name(self, o: CanName) -> Name:
        return as_name(o)

    @ta.final
    @property
    def n(self) -> NameAccessor:
        return NameAccessor()
