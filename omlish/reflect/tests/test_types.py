# ruff: noqa: UP006 UP007 UP045
import collections.abc
import dataclasses as dc
import pprint
import typing as ta

import pytest

from ... import check
from ... import reflect as rfl


T = ta.TypeVar('T')

K = ta.TypeVar('K')
K_co = ta.TypeVar('K_co', covariant=True)
K_contra = ta.TypeVar('K_contra', contravariant=True)

V = ta.TypeVar('V')
V_co = ta.TypeVar('V_co', covariant=True)
V_contra = ta.TypeVar('V_contra', contravariant=True)

P = ta.ParamSpec('P')

_0, _1, _2, _3 = rfl.types._KNOWN_SPECIAL_TYPE_VARS[:4]  # noqa


def assert_generic_full_eq(l: ta.Any, r: rfl.GenericLike) -> None:
    assert check.isinstance(rfl.type_(l), rfl.GenericLike).full_eq(r)


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


def test_newtype():
    Username = ta.NewType('Username', str)  # noqa
    rty = rfl.type_(Username)
    assert isinstance(rty, rfl.NewType)
    assert rty.ty is str


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


def test_annotated():
    rfl.type_(ta.Annotated[int, 'foo'])


def test_normalize_generic():
    @dc.dataclass(frozen=True)
    class Foo(ta.Sequence[int]):
        l: list[int]

        def __iter__(self):
            return iter(self.l)

        def __len__(self):
            return len(self.l)

        def __getitem__(self, item):
            return self.l[item]

    assert rfl.type_(Foo) is Foo


def test_tuples():
    assert_generic_full_eq(rfl.type_(ta.Tuple[int, str]), rfl.Generic(tuple, (int, str), (_0, _1), ta.Tuple[int, str]))
    assert_generic_full_eq(rfl.type_(tuple[int, str]), rfl.Generic(tuple, (int, str), (_0, _1), tuple[int, str]))
    assert rfl.type_(tuple) is tuple

    with pytest.raises(TypeError):
        rfl.type_(ta.Tuple)  # FIXME
    with pytest.raises(TypeError):
        rfl.type_(tuple[int, ...])  # FIXME


def test_literal():
    assert set(check.isinstance(rfl.type_(ta.Literal['a', 'b', 'c']), rfl.Literal).args) == {'a', 'b', 'c'}


def test_protocol():
    assert_generic_full_eq(rfl.type_(ta.Protocol[K, V]), rfl.Protocol(ta.Protocol, (K, V), (K, V), ta.Protocol[K, V]))

    #

    class P(ta.Protocol[K_co, V_co]):
        pass

    assert_generic_full_eq(rfl.type_(P), rfl.Protocol(P, (K_co, V_co), (K_co, V_co), P))

    #

    assert_generic_full_eq(rfl.type_(P[int, str]), rfl.Protocol(P, (int, str), (K_co, V_co), P[int, str]))
    assert_generic_full_eq(rfl.type_(P[int, T]), rfl.Protocol(P, (int, T), (K_co, V_co), P[int, T]))  # type: ignore

    assert_generic_full_eq(rfl.type_(P[int, ta.Sequence[str]]), rfl.Protocol(P, (int, rfl.type_(ta.Sequence[str])), (K_co, V_co), P[int, ta.Sequence[str]]))  # noqa

    #

    # class C0(P[int, str]):
    #     pass
    #
    # assert_generic_full_eq(rfl.type_(C0), rfl.Protocol(C0, (int, str), (K, V), C0))
    #
    # #
    #
    # class C1(P[int, T]):
    #     pass
    #
    # assert_generic_full_eq(rfl.type_(C1), rfl.Protocol(C0, (int, T), (K, V), C0))


def test_defaults():
    assert_generic_full_eq(rfl.type_(ta.Generator[int]), rfl.Generic(collections.abc.Generator, (int, type(None), type(None)), (_0, _1, _2), ta.Generator[int]))  # noqa
