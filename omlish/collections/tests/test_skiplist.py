import random

from ..skiplist import SkipList
from ..skiplist import SkipListDict


def test_skiplist():
    lst: SkipList[int] = SkipList()

    nums = list(range(100))
    random.Random(42).shuffle(nums)
    for i in nums:
        lst.add(i)

    assert lst.find(42) == 42
    assert lst.find(100) is None
    assert list(lst.iter()) == list(range(100))
    assert list(lst.riter()) == list(reversed(range(100)))

    lst.remove(42)

    assert lst.find(41) == 41
    assert lst.find(42) is None
    assert lst.find(43) == 43
    no42 = sorted(set(range(100)) - {42})
    assert list(lst.iter()) == list(no42)
    assert list(lst.riter()) == list(reversed(no42))


def test_skiplistdict():
    dct: SkipListDict[int | float, str] = SkipListDict()
    dct[4] = 'd'
    dct[2] = 'b'
    dct[5] = 'e'

    assert dct[2] == 'b'
    assert list(dct) == [2, 4, 5]
    assert list(dct.items()) == [(2, 'b'), (4, 'd'), (5, 'e')]
    assert list(dct.ritems()) == [(5, 'e'), (4, 'd'), (2, 'b')]

    assert list(dct.itemsfrom(3.9)) == [(4, 'd'), (5, 'e')]
    assert list(dct.itemsfrom(4)) == [(4, 'd'), (5, 'e')]
    assert list(dct.itemsfrom(4.1)) == [(5, 'e')]

    assert list(dct.ritemsfrom(4.1)) == [(4, 'd'), (2, 'b')]
    assert list(dct.ritemsfrom(4)) == [(4, 'd'), (2, 'b')]
    assert list(dct.ritemsfrom(3.9)) == [(2, 'b')]


def test_sorted_list_dict():
    assert dict(SkipListDict()) == {}
    assert dict(SkipListDict({3: 4, 1: 2})) == {1: 2, 3: 4}
