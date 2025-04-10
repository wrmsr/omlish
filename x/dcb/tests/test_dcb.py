"""
TODO:
 - ! spec goes to json !
  - 'spec'? 'inspection'? 'template'?
  - I like 'spec' for the canonical form
  - 'analysis'? 'config'? what's, like, 'primed and ready to compile'?
  - 'preprocess'?
 - !!! can re-use ONLY SPECIFIC PARTS !!!
  - fine-grained compile caching, overriding, ...
 - if this works out, go hog wild with injection, won't be used 90% of the time...
"""
import dataclasses as dc
import inspect
import pprint
import typing as ta

from .. import api


T = ta.TypeVar('T')
K = ta.TypeVar('K')
V = ta.TypeVar('V')


##


@api.dataclass(frozen=True, order=True)
class A:
    i: int
    s: str = api.field(repr_fn=lambda s: f'{s}!', override=True)
    d: int = api.field(default=5, coerce=int)
    l: ta.Sequence = api.field(
        default_factory=tuple,
        repr_priority=-1,
        validate=lambda l: not (l and len(l) == 2),
    )

    @api.init
    def _init_foo(self) -> None:
        print('hi!')


def test_dcb():
    assert getattr(dc, 'is_dataclass')(A)  # mypy blackhole

    print(inspect.signature(A))

    a = A(5, 'hi')  # type: ignore[call-arg]
    print(a)

    assert hash(a) == hash(A(5, 'hi'))  # type: ignore[call-arg]

    assert A(4, 'hi') < a  # type: ignore[call-arg,operator]

    match a:
        case A(i, s):  # type: ignore[misc]
            print(f'{i=} {s=}')  # type: ignore[unreachable]
        case _:
            raise RuntimeError


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
