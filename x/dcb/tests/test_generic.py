import inspect
import pprint
import typing as ta

from ..api import api


T = ta.TypeVar('T')
K = ta.TypeVar('K')
V = ta.TypeVar('V')


##


@api.dataclass(frozen=True, generic_init=True)
class Thing(ta.Generic[T]):
    s: set[T]
    # mk: ta.Mapping[K, T]
    # mv: ta.Mapping[T, V]
    # mfk: ta.Mapping[ta.FrozenSet[K], T]
    # mfv: ta.Mapping[T, ta.FrozenSet[V]]
    mk: ta.Mapping[str, T]
    mv: ta.Mapping[T, str]
    mfk: ta.Mapping[frozenset[str], T]
    mfv: ta.Mapping[T, frozenset[str]]


@api.dataclass(frozen=True, generic_init=True)
class IntThing(Thing[int]):
    pass


@api.dataclass(frozen=True, generic_init=True)
class Thing2(Thing[K]):
    pass


@api.dataclass(frozen=True, generic_init=True)
class IntThing2(Thing2[int]):
    pass


def test_generics2():
    print()

    pprint.pprint(dict(inspect.signature(Thing).parameters))

    pprint.pprint(dict(inspect.signature(IntThing).parameters))

    pprint.pprint(dict(inspect.signature(IntThing2).parameters))
