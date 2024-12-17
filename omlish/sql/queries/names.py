import functools
import typing as ta

from ... import check
from ... import dataclasses as dc
from ... import lang
from .base import Node
from .idents import CanIdent
from .idents import Ident
from .idents import IdentBuilder
from .idents import as_ident


##


def _coerce_name_parts(o: ta.Iterable[Ident]) -> ta.Sequence[Ident]:
    check.not_isinstance(o, str)
    return check.not_empty(tuple(check.isinstance(e, Ident) for e in o))


class Name(Node, lang.Final):
    ps: ta.Sequence[Ident] = dc.xfield(coerce=_coerce_name_parts)


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


class NameAccessor:
    def __init__(self, n: Name | None = None) -> None:
        super().__init__()
        self.__query_name__ = n

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({self.__query_name__!r})'

    def __getattr__(self, s: str) -> 'NameAccessor':
        check.not_in('.', s)
        check.arg(not s.startswith('__'))
        return NameAccessor(Name([
            *(sn.ps if (sn := self.__query_name__) is not None else []),
            Ident(s),
        ]))


@as_name.register
def _(a: NameAccessor) -> Name:
    return check.not_none(a.__query_name__)


##


CanName: ta.TypeAlias = Name | CanIdent | ta.Sequence[CanIdent] | NameAccessor


class NameBuilder(IdentBuilder):
    def name(self, o: CanName) -> Name:
        return as_name(o)

    @ta.final
    def n(self, o: CanName) -> Name:
        return self.name(o)
