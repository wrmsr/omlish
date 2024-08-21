import typing as ta

from ... import reflect as rfl


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
