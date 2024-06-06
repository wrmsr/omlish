import collections.abc
import pprint  # noqa
import typing as ta

from .. import reflect as rfl


K = ta.TypeVar('K')
V = ta.TypeVar('V')
T = ta.TypeVar('T')
U = ta.TypeVar('U')

_0, _1, _2, _3 = rfl._KNOWN_SPECIAL_TYPE_VARS[:4]  # noqa


def test_simple_reflect_type():
    assert rfl.type_(int) == int
    assert rfl.type_(ta.Union[int, float]) == rfl.Union(frozenset([int, float]))
    assert rfl.type_(ta.Optional[int]) == rfl.Union(frozenset([int, type(None)]))

    assert rfl.type_(ta.Sequence[int]) == rfl.Generic(collections.abc.Sequence, (int,), (_0,), ta.Sequence[int])
    assert rfl.type_(ta.Mapping[int, str]) == rfl.Generic(collections.abc.Mapping, (int, str), (_0, _1), ta.Mapping[int, str])  # noqa
    assert rfl.type_(ta.Mapping[int, ta.Optional[str]]) == rfl.Generic(collections.abc.Mapping, (int, rfl.Union(frozenset([str, type(None)]))), (_0, _1), ta.Mapping[int, ta.Optional[str]])  # noqa
    assert rfl.type_(ta.Mapping[int, ta.Sequence[ta.Optional[str]]]) == rfl.Generic(collections.abc.Mapping, (int, rfl.Generic(collections.abc.Sequence, (rfl.Union(frozenset([str, type(None)])),), (_0,), ta.Sequence[ta.Optional[str]])), (_0, _1), ta.Mapping[int, ta.Sequence[ta.Optional[str]]])  # noqa

    assert rfl.type_(list[int]) == rfl.Generic(list, (int,), (_0,), list[int])
    assert rfl.type_(set[int]) == rfl.Generic(set, (int,), (_0,), set[int])
    assert rfl.type_(dict[int, str]) == rfl.Generic(dict, (int, str), (_0, _1), dict[int, str])

    assert rfl.type_(list) == list
    assert rfl.type_(ta.List) == rfl.Generic(list, (_0,), (_0,), ta.List)
    assert rfl.type_(list[int]) == rfl.Generic(list, (int,), (_0,), list[int])
    assert rfl.type_(ta.List[int]) == rfl.Generic(list, (int,), (_0,), ta.List[int])


def test_new_unions():
    assert rfl.type_(int | None) == rfl.Union(frozenset([int, type(None)]))


def test_partial_generics():
    print()

    for ty in [
        ta.Mapping[int, V],
        ta.Mapping[K, int],
        ta.Mapping[int, ta.Set[V]],
    ]:
        print(ty)

        bt = rfl.type_(ty)
        print(bt)

        class B(ty[T]):
            pass

        class C(B[str]):
            pass

        ct = rfl.type_(C)
        print(ct)

        cm = rfl.generic_mro(C)
        pprint.pprint(cm)

        print()


def test_simple_isinstance_of():
    assert rfl.isinstance_of(rfl.type_(int))(420)
    assert not rfl.isinstance_of(rfl.type_(int))('420')

    assert rfl.isinstance_of(rfl.type_(ta.Sequence[int]))([420, 421])
    assert not rfl.isinstance_of(rfl.type_(ta.Sequence[int]))([420, '421'])
    assert rfl.isinstance_of(rfl.type_(ta.Sequence[int]))((420, 421))
    assert not rfl.isinstance_of(rfl.type_(ta.Sequence[int]))((420, '421'))

    assert rfl.isinstance_of(rfl.type_(ta.AbstractSet[int]))({420, 421})
    assert not rfl.isinstance_of(rfl.type_(ta.AbstractSet[int]))({420, '421'})
    assert rfl.isinstance_of(rfl.type_(ta.AbstractSet[int]))(frozenset([420, 421]))
    assert not rfl.isinstance_of(rfl.type_(ta.AbstractSet[int]))(frozenset([420, '421']))

    assert rfl.isinstance_of(rfl.type_(ta.Mapping[int, str]))({420: '421'})
    assert not rfl.isinstance_of(rfl.type_(ta.Mapping[int, str]))({420: 421})
    assert rfl.isinstance_of(rfl.type_(ta.Mapping[int, ta.AbstractSet[str]]))({420: {'421'}})
    assert not rfl.isinstance_of(rfl.type_(ta.Mapping[int, ta.AbstractSet[str]]))({420: [421]})


def test_extended_reflect_type():
    class A(ta.Generic[T]):
        a: T

    class B(ta.Generic[T]):
        b: T

    class C(A[U]):
        pass

    class D(C[str], B[int]):
        pass

    class E(A[int]):
        pass

    class F(A):
        pass

    class G(ta.Generic[T, U]):
        a: T
        b: U

    print()

    import pprint

    for ty in [
        A,
        A[str],
        B,
        B[int],
        C,
        C[str],
        D,
        E,
        F,
        G,
        G[int, str],
        C[B[int]],
        C[C[int]],
    ]:
        print(ty)
        pprint.pprint(rfl.generic_mro(ty))
        print()
