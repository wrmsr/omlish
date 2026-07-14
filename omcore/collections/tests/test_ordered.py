import typing as ta

from ..ordered import OrderedFrozenSet
from ..ordered import OrderedSet


def test_ordered_set():
    os: ta.MutableSet[int] = OrderedSet([1, 2])
    assert list(os) == [1, 2]
    os.add(1)
    assert list(os) == [1, 2]
    os.add(3)
    assert list(os) == [1, 2, 3]
    os.remove(2)
    assert list(os) == [1, 3]


def test_ordered_frozen_set():
    s0: ta.AbstractSet[int] = OrderedFrozenSet(range(3))
    assert list(s0) == [0, 1, 2]
