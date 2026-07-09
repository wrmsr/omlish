import typing as ta

from ... import reflect as rfl
from .isinstance import isinstance_of


def test_simple_isinstance_of():
    assert isinstance_of(rfl.typeof(int))(420)
    assert not isinstance_of(rfl.typeof(int))('420')

    assert isinstance_of(rfl.typeof(ta.Sequence[int]))([420, 421])
    assert not isinstance_of(rfl.typeof(ta.Sequence[int]))([420, '421'])
    assert isinstance_of(rfl.typeof(ta.Sequence[int]))((420, 421))
    assert not isinstance_of(rfl.typeof(ta.Sequence[int]))((420, '421'))

    assert isinstance_of(rfl.typeof(ta.AbstractSet[int]))({420, 421})
    assert not isinstance_of(rfl.typeof(ta.AbstractSet[int]))({420, '421'})
    assert isinstance_of(rfl.typeof(ta.AbstractSet[int]))(frozenset([420, 421]))
    assert not isinstance_of(rfl.typeof(ta.AbstractSet[int]))(frozenset([420, '421']))

    assert isinstance_of(rfl.typeof(ta.Mapping[int, str]))({420: '421'})
    assert not isinstance_of(rfl.typeof(ta.Mapping[int, str]))({420: 421})
    assert isinstance_of(rfl.typeof(ta.Mapping[int, ta.AbstractSet[str]]))({420: {'421'}})
    assert not isinstance_of(rfl.typeof(ta.Mapping[int, ta.AbstractSet[str]]))({420: [421]})
