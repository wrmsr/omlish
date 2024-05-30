import collections.abc
import typing as ta

from .. import reflect as rfl


_0, _1, _2, _3 = rfl._KNOWN_SPECIAL_TYPE_VARS[:4]  # noqa


def test_simple_reflect_type():
    assert rfl.type_(int) == int
    assert rfl.type_(ta.Union[int, float]) == \
           rfl.Union(frozenset([int, float]))
    assert rfl.type_(ta.Optional[int]) == \
           rfl.Union(frozenset([int, type(None)]))
    assert rfl.type_(ta.Sequence[int]) == \
           rfl.Generic(collections.abc.Sequence, (int,), (_0,), ta.Sequence[int])
    assert rfl.type_(ta.Mapping[int, str]) == \
           rfl.Generic(collections.abc.Mapping, (int, str), (_0, _1), ta.Mapping[int, str])
    assert rfl.type_(ta.Mapping[int, ta.Optional[str]]) == \
           rfl.Generic(collections.abc.Mapping, (int, rfl.Union(frozenset([str, type(None)]))), (_0, _1), ta.Mapping[int, ta.Optional[str]])  # noqa
    assert rfl.type_(ta.Mapping[int, ta.Sequence[ta.Optional[str]]]) == \
           rfl.Generic(collections.abc.Mapping, (int, rfl.Generic(collections.abc.Sequence, (rfl.Union(frozenset([str, type(None)])),), (_0,), ta.Sequence[ta.Optional[str]])), (_0, _1), ta.Mapping[int, ta.Sequence[ta.Optional[str]]])  # noqa

    assert rfl.type_(list[int]) == rfl.Generic(list, (int,), (_0,), list[int])
    assert rfl.type_(set[int]) == rfl.Generic(set, (int,), (_0,), set[int])
    assert rfl.type_(dict[int, str]) == rfl.Generic(dict, (int, str), (_0, _1), dict[int, str])

    assert rfl.type_(list) == list
    assert rfl.type_(ta.List) == rfl.Generic(list, (_0,), (_0,), ta.List)
    assert rfl.type_(list[int]) == rfl.Generic(list, (int,), (_0,), list[int])
    assert rfl.type_(ta.List[int]) == rfl.Generic(list, (int,), (_0,), ta.List[int])


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


T = ta.TypeVar('T')
U = ta.TypeVar('U')
V = ta.TypeVar('V')


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

    def rec(obj):
        rty = rfl.type_(obj)
        print(rty)
        if (cty := rfl.get_concrete_type(rty)) is not None:
            for b in rfl.get_original_bases(cty):
                rec(b)

    import pprint

    from .. import c3

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
    ]:
        # rec(ty)
        # print()
        mro = c3.mro(
            rfl.type_(ty),
            get_bases=rfl.get_reflected_bases,
            is_subclass=lambda l, r: issubclass(rfl.get_concrete_type(l), rfl.get_concrete_type(r)),
        )
        pprint.pprint(mro)
        print()
