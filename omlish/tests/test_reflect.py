import collections.abc
import typing as ta

from .. import reflect as rfl


def test_reflect_type():
    assert rfl.reflect(int) == int
    assert rfl.reflect(ta.Union[int, float]) == rfl.Union([int, float])
    assert rfl.reflect(ta.Optional[int]) == rfl.Union([int, type(None)])
    assert rfl.reflect(ta.Sequence[int]) == rfl.Generic(collections.abc.Sequence, [int])
    assert rfl.reflect(ta.Mapping[int, str]) == rfl.Generic(collections.abc.Mapping, [int, str])
    assert rfl.reflect(ta.Mapping[int, ta.Optional[str]]) == rfl.Generic(collections.abc.Mapping, [int, rfl.Union([str, type(None)])])  # noqa
    assert rfl.reflect(ta.Mapping[int, ta.Sequence[ta.Optional[str]]]) == rfl.Generic(collections.abc.Mapping, [int, rfl.Generic(collections.abc.Sequence, [rfl.Union([str, type(None)])])])  # noqa

    assert rfl.reflect(list[int]) == rfl.Generic(list, [int])
    assert rfl.reflect(set[int]) == rfl.Generic(set, [int])
    assert rfl.reflect(dict[int, str]) == rfl.Generic(dict, [int, str])


def test_isinstance_of():
    assert rfl.isinstance_of(rfl.reflect(int))(420)
    assert not rfl.isinstance_of(rfl.reflect(int))('420')

    assert rfl.isinstance_of(rfl.reflect(ta.Sequence[int]))([420, 421])
    assert not rfl.isinstance_of(rfl.reflect(ta.Sequence[int]))([420, '421'])
    assert rfl.isinstance_of(rfl.reflect(ta.Sequence[int]))((420, 421))
    assert not rfl.isinstance_of(rfl.reflect(ta.Sequence[int]))((420, '421'))

    assert rfl.isinstance_of(rfl.reflect(ta.AbstractSet[int]))({420, 421})
    assert not rfl.isinstance_of(rfl.reflect(ta.AbstractSet[int]))({420, '421'})
    assert rfl.isinstance_of(rfl.reflect(ta.AbstractSet[int]))(frozenset([420, 421]))
    assert not rfl.isinstance_of(rfl.reflect(ta.AbstractSet[int]))(frozenset([420, '421']))

    assert rfl.isinstance_of(rfl.reflect(ta.Mapping[int, str]))({420: '421'})
    assert not rfl.isinstance_of(rfl.reflect(ta.Mapping[int, str]))({420: 421})
    assert rfl.isinstance_of(rfl.reflect(ta.Mapping[int, ta.AbstractSet[str]]))({420: {'421'}})
    assert not rfl.isinstance_of(rfl.reflect(ta.Mapping[int, ta.AbstractSet[str]]))({420: [421]})
