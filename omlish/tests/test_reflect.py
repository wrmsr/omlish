import collections.abc
import pprint
import typing as ta

import pytest

from .. import check
from .. import reflect as rfl


K = ta.TypeVar('K')
V = ta.TypeVar('V')
T = ta.TypeVar('T')
U = ta.TypeVar('U')

P = ta.ParamSpec('P')

_0, _1, _2, _3 = rfl._KNOWN_SPECIAL_TYPE_VARS[:4]  # noqa


def assert_generic_full_eq(l: ta.Any, r: rfl.Generic) -> None:
    assert check.isinstance(rfl.type_(l), rfl.Generic).full_eq(r)


def test_simple_reflect_type():
    assert rfl.type_(int) is int
    assert rfl.type_(ta.Union[int, float]) == rfl.Union(frozenset([int, float]))  # noqa
    assert rfl.type_(ta.Optional[int]) == rfl.Union(frozenset([int, type(None)]))  # noqa

    assert_generic_full_eq(ta.Sequence[int], rfl.Generic(collections.abc.Sequence, (int,), (_0,), ta.Sequence[int]))
    assert_generic_full_eq(ta.Mapping[int, str], rfl.Generic(collections.abc.Mapping, (int, str), (_0, _1), ta.Mapping[int, str]))  # noqa
    assert_generic_full_eq(ta.Mapping[int, ta.Optional[str]], rfl.Generic(collections.abc.Mapping, (int, rfl.Union(frozenset([str, type(None)]))), (_0, _1), ta.Mapping[int, ta.Optional[str]]))  # noqa
    assert_generic_full_eq(ta.Mapping[int, ta.Sequence[ta.Optional[str]]], rfl.Generic(collections.abc.Mapping, (int, rfl.Generic(collections.abc.Sequence, (rfl.Union(frozenset([str, type(None)])),), (_0,), ta.Sequence[ta.Optional[str]])), (_0, _1), ta.Mapping[int, ta.Sequence[ta.Optional[str]]]))  # noqa

    assert_generic_full_eq(list[int], rfl.Generic(list, (int,), (_0,), list[int]))
    assert_generic_full_eq(set[int], rfl.Generic(set, (int,), (_0,), set[int]))
    assert_generic_full_eq(dict[int, str], rfl.Generic(dict, (int, str), (_0, _1), dict[int, str]))

    assert rfl.type_(list) is list
    assert_generic_full_eq(ta.List, rfl.Generic(list, (_0,), (_0,), ta.List))  # noqa
    assert_generic_full_eq(list[int], rfl.Generic(list, (int,), (_0,), list[int]))
    assert_generic_full_eq(ta.List[int], rfl.Generic(list, (int,), (_0,), ta.List[int]))  # noqa


def test_new_unions():
    assert rfl.type_(int | None) == rfl.Union(frozenset([int, type(None)]))
    assert rfl.type_(int | float) == rfl.Union(frozenset([int, float]))


def test_partial_generics():
    print()

    for ty in [
        ta.Mapping[int, V],  # type: ignore
        ta.Mapping[K, int],  # type: ignore
        ta.Mapping[int, ta.Set[V]],  # type: ignore  # noqa
    ]:
        print(ty)

        bt = rfl.type_(ty)
        print(bt)

        class B(ty[T]):  # type: ignore
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


def test_newtype():
    Username = ta.NewType('Username', str)  # noqa
    print(rfl.type_(Username))


def test_callable():
    assert_generic_full_eq(ta.Callable[[], int], rfl.Generic(collections.abc.Callable, (int,), (_0,), ta.Callable[[], int]))  # type: ignore  # noqa
    assert_generic_full_eq(ta.Callable[[int], None], rfl.Generic(collections.abc.Callable, (int, type(None)), (_0, _1), ta.Callable[[int], None]))  # type: ignore  # noqa
    assert_generic_full_eq(ta.Callable[[int, float], str], rfl.Generic(collections.abc.Callable, (int, float, str), (_0, _1, _2), ta.Callable[[int, float], str]))  # type: ignore  # noqa

    with pytest.raises(TypeError):
        rfl.type_(ta.Callable[..., int])
    with pytest.raises(TypeError):
        rfl.type_(ta.Callable[[int, ...], str])
    with pytest.raises(TypeError):
        rfl.type_(ta.Callable[P, str])


def test_generic_type():
    assert_generic_full_eq(type[int], rfl.Generic(type, (int,), (_0,), type[int]))
    assert rfl.type_(type) is type
