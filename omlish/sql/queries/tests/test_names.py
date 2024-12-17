import functools
import typing as ta

from .... import check
from ..names import Name
from ..idents import Ident


##


@functools.singledispatch
def as_ident(o: ta.Any) -> Ident:
    raise TypeError(o)


@as_ident.register
def _(i: Ident) -> Ident:
    return i


@as_ident.register
def _(s: str) -> Ident:
    return Ident(s)


##


@functools.singledispatch
def as_name(o: ta.Any) -> Name:
    if isinstance(o, ta.Sequence):
        return Name([as_ident(p) for p in o])
    else:
        raise TypeError(o)


@as_name.register
def _(n: Name) -> Name:
    raise n


@as_name.register
def _(o: Ident | str) -> Name:
    return Name([as_ident(o)])


##


class NameAccessor:
    def __init__(self, s: str) -> None:
        super().__init__()
        self.__s = s

    def __getattr__(self, s: str) -> 'NameAccessor':
        check.not_in('.', s)
        check.arg(not s.startswith('__'))
        return NameAccessor('.'.join([self.__s, s]))


def test_name_accessor():
    pass
