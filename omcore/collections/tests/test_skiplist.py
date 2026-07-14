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
    assert list(lst.iter_desc()) == list(reversed(range(100)))

    lst.remove(42)

    assert lst.find(41) == 41
    assert lst.find(42) is None
    assert lst.find(43) == 43
    no42 = sorted(set(range(100)) - {42})
    assert list(lst.iter()) == list(no42)
    assert list(lst.iter_desc()) == list(reversed(no42))


def test_skiplistdict():
    dct: SkipListDict[int | float, str] = SkipListDict()
    dct[4] = 'd'
    dct[2] = 'b'
    dct[5] = 'e'

    assert dct[2] == 'b'
    assert list(dct) == [2, 4, 5]
    assert list(dct.items()) == [(2, 'b'), (4, 'd'), (5, 'e')]
    assert list(dct.items_desc()) == [(5, 'e'), (4, 'd'), (2, 'b')]

    assert list(dct.items_from(3.9)) == [(4, 'd'), (5, 'e')]
    assert list(dct.items_from(4)) == [(4, 'd'), (5, 'e')]
    assert list(dct.items_from(4.1)) == [(5, 'e')]

    assert list(dct.items_from_desc(4.1)) == [(4, 'd'), (2, 'b')]
    assert list(dct.items_from_desc(4)) == [(4, 'd'), (2, 'b')]
    assert list(dct.items_from_desc(3.9)) == [(2, 'b')]


def test_sorted_list_dict():
    assert dict(SkipListDict()) == {}
    assert dict(SkipListDict({3: 4, 1: 2})) == {1: 2, 3: 4}


def test_skiplist_reverse_iteration():
    sl: SkipList = SkipList()
    values = [10, 5, 20, 15]
    for v in values:
        sl.add(v)

    # Test forward
    assert list(sl.iter()) == [5, 10, 15, 20]
    # Test backward (This would have failed or been extremely slow before)
    assert list(sl.iter_desc()) == [20, 15, 10, 5]


def test_skiplist_prev_pointer_integrity():
    sl: SkipList = SkipList()
    sl.add(10)
    sl.add(20)
    sl.add(15)  # Insert in middle

    # Manually verify the chain
    node_20 = sl._find(20)  # noqa
    node_15 = sl._find(15)  # noqa
    node_10 = sl._find(10)  # noqa

    assert node_20.prev == node_15  # type: ignore
    assert node_15.prev == node_10  # type: ignore

    sl.remove(15)
    # After removal, 20.prev should point back to 10
    assert node_20.prev == node_10  # type: ignore


def test_skiplist_tail_updates():
    sl: SkipList = SkipList()
    sl.add(10)
    assert sl._tail.value == 10  # noqa
    sl.add(20)
    assert sl._tail.value == 20  # noqa
    sl.remove(20)
    assert sl._tail.value == 10  # noqa
    sl.add(5)  # Adding smaller than tail shouldn't change tail
    assert sl._tail.value == 10  # noqa
