import typing as ta

from ... import reflect as rfl
from .isinstance import isinstance_of


def test_simple_isinstance_of():
    assert isinstance_of(rfl.type_(int))(420)
    assert not isinstance_of(rfl.type_(int))('420')

    assert isinstance_of(rfl.type_(ta.Sequence[int]))([420, 421])
    assert not isinstance_of(rfl.type_(ta.Sequence[int]))([420, '421'])
    assert isinstance_of(rfl.type_(ta.Sequence[int]))((420, 421))
    assert not isinstance_of(rfl.type_(ta.Sequence[int]))((420, '421'))

    assert isinstance_of(rfl.type_(ta.AbstractSet[int]))({420, 421})
    assert not isinstance_of(rfl.type_(ta.AbstractSet[int]))({420, '421'})
    assert isinstance_of(rfl.type_(ta.AbstractSet[int]))(frozenset([420, 421]))
    assert not isinstance_of(rfl.type_(ta.AbstractSet[int]))(frozenset([420, '421']))

    assert isinstance_of(rfl.type_(ta.Mapping[int, str]))({420: '421'})
    assert not isinstance_of(rfl.type_(ta.Mapping[int, str]))({420: 421})
    assert isinstance_of(rfl.type_(ta.Mapping[int, ta.AbstractSet[str]]))({420: {'421'}})
    assert not isinstance_of(rfl.type_(ta.Mapping[int, ta.AbstractSet[str]]))({420: [421]})
