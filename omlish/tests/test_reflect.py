import collections.abc
import typing as ta

from .. import reflect as rfl


def test_reflect_type():
    assert rfl.type_(int) == int
    assert rfl.type_(ta.Union[int, float]) == rfl.Union(frozenset([int, float]))
    assert rfl.type_(ta.Optional[int]) == rfl.Union(frozenset([int, type(None)]))
    assert rfl.type_(ta.Sequence[int]) == rfl.Generic(collections.abc.Sequence, (int,))
    assert rfl.type_(ta.Mapping[int, str]) == rfl.Generic(collections.abc.Mapping, (int, str))
    assert rfl.type_(ta.Mapping[int, ta.Optional[str]]) == rfl.Generic(collections.abc.Mapping, (int, rfl.Union(frozenset([str, type(None)]))))  # noqa
    assert rfl.type_(ta.Mapping[int, ta.Sequence[ta.Optional[str]]]) == rfl.Generic(collections.abc.Mapping, (int, rfl.Generic(collections.abc.Sequence, (rfl.Union(frozenset([str, type(None)])),))))  # noqa

    assert rfl.type_(list[int]) == rfl.Generic(list, (int,))
    assert rfl.type_(set[int]) == rfl.Generic(set, (int,))
    assert rfl.type_(dict[int, str]) == rfl.Generic(dict, (int, str))


def test_isinstance_of():
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
