import copy

from .. import iterators as its
from .. import lang


def test_unique():
    es = [copy.deepcopy(e) for e in its.UniqueIterator('abcabcaaadea')]
    assert es == [
        its.UniqueItem(idx=0, item='a', stats=its.UniqueStats(key='a', num_seen=1, first_idx=0, last_idx=0), out=lang.just('a')),  # noqa
        its.UniqueItem(idx=1, item='b', stats=its.UniqueStats(key='b', num_seen=1, first_idx=1, last_idx=1), out=lang.just('b')),  # noqa
        its.UniqueItem(idx=2, item='c', stats=its.UniqueStats(key='c', num_seen=1, first_idx=2, last_idx=2), out=lang.just('c')),  # noqa
        its.UniqueItem(idx=3, item='a', stats=its.UniqueStats(key='a', num_seen=2, first_idx=0, last_idx=3), out=lang.empty()),  # noqa
        its.UniqueItem(idx=4, item='b', stats=its.UniqueStats(key='b', num_seen=2, first_idx=1, last_idx=4), out=lang.empty()),  # noqa
        its.UniqueItem(idx=5, item='c', stats=its.UniqueStats(key='c', num_seen=2, first_idx=2, last_idx=5), out=lang.empty()),  # noqa
        its.UniqueItem(idx=6, item='a', stats=its.UniqueStats(key='a', num_seen=3, first_idx=0, last_idx=6), out=lang.empty()),  # noqa
        its.UniqueItem(idx=7, item='a', stats=its.UniqueStats(key='a', num_seen=4, first_idx=0, last_idx=7), out=lang.empty()),  # noqa
        its.UniqueItem(idx=8, item='a', stats=its.UniqueStats(key='a', num_seen=5, first_idx=0, last_idx=8), out=lang.empty()),  # noqa
        its.UniqueItem(idx=9, item='d', stats=its.UniqueStats(key='d', num_seen=1, first_idx=9, last_idx=9), out=lang.just('d')),  # noqa
        its.UniqueItem(idx=10, item='e', stats=its.UniqueStats(key='e', num_seen=1, first_idx=10, last_idx=10), out=lang.just('e')),  # noqa
        its.UniqueItem(idx=11, item='a', stats=its.UniqueStats(key='a', num_seen=6, first_idx=0, last_idx=11), out=lang.empty()),  # noqa
    ]
