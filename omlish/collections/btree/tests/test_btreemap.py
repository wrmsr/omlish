import random
import typing as ta

import pytest

from .._btreemap_py import MAX_BRANCH_LEN
from .._btreemap_py import MAX_LEAF_LEN
from ..btreemap import BtreeMap
from ..btreemap import _Branch
from ..btreemap import _Leaf
from ..btreemap import _node_max
from ..btreemap import new_btree_map


def _default_cmp(a, b):
    return (a > b) - (a < b)


def _check_node(n, cmp):
    if isinstance(n, _Leaf):
        assert len(n.keys) == len(n.values)
        assert n.count == len(n.keys)
        assert len(n.keys) <= MAX_LEAF_LEN

        for a, b in zip(n.keys, n.keys[1:]):
            assert cmp(a, b) < 0

        return n.count, n.keys[0], n.keys[-1]

    assert isinstance(n, _Branch)
    assert len(n.keys) == len(n.children)
    assert len(n.children) <= MAX_BRANCH_LEN

    total = 0
    mins = []
    maxs = []

    for c in n.children:
        cnt, mn, mx = _check_node(c, cmp)
        total += cnt
        mins.append(mn)
        maxs.append(mx)

    assert total == n.count
    assert tuple(maxs) == n.keys

    for a, b in zip(maxs, mins[1:]):
        assert cmp(a, b) < 0

    return total, mins[0], maxs[-1]


def _check_map(m: BtreeMap, expected: ta.Mapping, *, cmp=None):
    if cmp is None:
        cmp = _default_cmp

    items = list(m.iteritems())

    assert len(m) == len(expected)
    assert items == sorted(expected.items(), key=lambda kv: kv[0])
    assert list(m.items()) == items
    assert list(m.values()) == [v for _, v in items]
    assert list(m) == [k for k, _ in items]
    assert list(m.items_desc()) == list(reversed(items))
    assert m.debug == dict(items)

    if m._root is not None:  # noqa
        cnt, _, _ = _check_node(m._root, cmp)  # noqa
        assert cnt == len(m)


def test_empty():
    m: BtreeMap = new_btree_map()

    assert len(m) == 0
    assert list(m) == []
    assert list(m.iteritems()) == []
    assert list(m.items()) == []
    assert list(m.values()) == []
    assert list(m.items_desc()) == []
    assert list(m.items_from(0)) == []
    assert list(m.items_from_desc(0)) == []
    assert 0 not in m

    with pytest.raises(KeyError):
        m[0]


def test_insert_and_get():
    m: BtreeMap = new_btree_map()

    for i in [5, 1, 3, 2, 4]:
        m = m.with_(i, str(i))

    assert len(m) == 5
    assert m[1] == '1'
    assert m[5] == '5'
    assert 3 in m
    assert 6 not in m

    _check_map(m, {i: str(i) for i in range(1, 6)})


def test_replace():
    m = new_btree_map([
        (1, 'a'),
        (2, 'b'),
    ])

    m2 = m.with_(1, 'aa')

    assert m[1] == 'a'
    assert m2[1] == 'aa'
    assert list(m2.iteritems()) == [
        (1, 'aa'),
        (2, 'b'),
    ]


def test_default():
    m = new_btree_map([
        (1, 'a'),
    ])

    m2 = m.default(1, 'aa')
    m3 = m2.default(2, 'b')

    assert m2 is m
    assert list(m3.iteritems()) == [
        (1, 'a'),
        (2, 'b'),
    ]


def test_persistence():
    versions = []
    m: BtreeMap = new_btree_map()

    for i in range(100):
        versions.append(m)
        m = m.with_(i, str(i))

    for i, old in enumerate(versions):
        assert len(old) == i
        assert list(old.iteritems()) == [(j, str(j)) for j in range(i)]

    old = m

    for i in range(50):
        m = m.without(i)

    assert len(old) == 100
    assert list(old.iteritems()) == [(i, str(i)) for i in range(100)]
    assert list(m.iteritems()) == [(i, str(i)) for i in range(50, 100)]


def test_delete():
    m = new_btree_map((i, str(i)) for i in range(100))

    for i in range(0, 100, 2):
        m = m.without(i)

    expected = {i: str(i) for i in range(1, 100, 2)}
    _check_map(m, expected)

    for i in range(0, 100, 2):
        m2 = m.without(i)
        assert m2 is m

    for i in range(1, 100, 2):
        m = m.without(i)

    assert len(m) == 0
    assert list(m.iteritems()) == []


def test_items_from():
    m = new_btree_map((i, str(i)) for i in range(10))

    assert list(m.items_from(-1)) == [(i, str(i)) for i in range(10)]
    assert list(m.items_from(0)) == [(i, str(i)) for i in range(10)]
    assert list(m.items_from(4)) == [(i, str(i)) for i in range(4, 10)]
    assert list(m.items_from(45)) == []


def test_items_from_desc():
    m = new_btree_map((i, str(i)) for i in range(10))

    assert list(m.items_from_desc(-1)) == []
    assert list(m.items_from_desc(0)) == [(0, '0')]
    assert list(m.items_from_desc(4)) == [(i, str(i)) for i in range(4, -1, -1)]
    assert list(m.items_from_desc(45)) == [(i, str(i)) for i in range(9, -1, -1)]


def test_iterator_has_next_and_next():
    m = new_btree_map((i, str(i)) for i in range(3))

    it = m.iteritems()

    assert it.has_next()
    assert it.next() == (0, '0')
    assert it.has_next()
    assert it.next() == (1, '1')
    assert it.has_next()
    assert it.next() == (2, '2')
    assert not it.has_next()

    with pytest.raises(StopIteration):
        it.next()


class _Key:
    __hash__ = None  # type: ignore[assignment]

    def __init__(self, value):
        super().__init__()

        self.value = value

    def __repr__(self):
        return f'_Key({self.value!r})'


def _key_cmp(a, b):
    return (a.value > b.value) - (a.value < b.value)


def test_custom_comparator_with_unhashable_keys():
    m: BtreeMap = new_btree_map(cmp=_key_cmp)

    k1a = _Key(1)
    k1b = _Key(1)
    k2 = _Key(2)

    m = m.with_(k1a, 'a')
    m = m.with_(k2, 'b')

    assert m[k1b] == 'a'

    m = m.with_(k1b, 'aa')

    assert m[k1a] == 'aa'
    assert [v for _, v in m.iteritems()] == ['aa', 'b']


def test_large_sequential():
    m: BtreeMap = new_btree_map()

    for i in range(2000):
        m = m.with_(i, str(i))

    _check_map(m, {i: str(i) for i in range(2000)})

    for i in range(0, 2000, 3):
        m = m.without(i)

    expected = {i: str(i) for i in range(2000) if i % 3}
    _check_map(m, expected)


def test_random_against_dict():
    rng = random.Random(0)

    m: BtreeMap = new_btree_map()
    d = {}

    for step in range(5000):
        op = rng.randrange(3)
        k = rng.randrange(250)

        if op == 0:
            v = rng.randrange(100000)
            m = m.with_(k, v)
            d[k] = v

        elif op == 1:
            m = m.without(k)
            d.pop(k, None)

        else:
            v = rng.randrange(100000)
            m = m.default(k, v)
            d.setdefault(k, v)

        if not step % 50:
            _check_map(m, d)


def _walk_nodes(n):
    yield n

    if isinstance(n, _Branch):
        for c in n.children:
            yield from _walk_nodes(c)


def _branch_nodes(m):
    if m._root is None:  # noqa
        return []

    return [n for n in _walk_nodes(m._root) if isinstance(n, _Branch)]  # noqa


def _max_depth(n):
    if isinstance(n, _Leaf):
        return 1

    return 1 + max(_max_depth(c) for c in n.children)


def test_update_reuses_unchanged_branch_keys_tuple():
    m = new_btree_map((i, str(i)) for i in range(500))

    branches = _branch_nodes(m)
    assert branches

    # Pick a key that should not be the max of most ancestors.
    m2 = m.with_(123, 'updated')

    reused_any = False

    for b2 in _branch_nodes(m2):
        for b in branches:
            if len(b.children) != len(b2.children):
                continue

            diffs = [
                i
                for i, (a, c) in enumerate(zip(b.children, b2.children))
                if a is not c
            ]

            if len(diffs) != 1:
                continue

            idx = diffs[0]

            if b.keys[idx] is _node_max(b2.children[idx]) and b2.keys is b.keys:
                reused_any = True
                break

        if reused_any:
            break

    assert reused_any
    _check_map(m2, {**{i: str(i) for i in range(500)}, 123: 'updated'})


def test_insert_non_split_preserves_branch_count_by_arithmetic():
    m = new_btree_map((i, str(i)) for i in range(500))

    m2 = m.with_(2500, '2500')

    assert len(m2) == len(m) + 1
    assert m2[2500] == '2500'
    _check_map(m2, {**{i: str(i) for i in range(500)}, 2500: '2500'})


def test_delete_non_merge_preserves_branch_count_by_arithmetic():
    m = new_btree_map((i, str(i)) for i in range(500))

    m2 = m.without(123)

    expected = {i: str(i) for i in range(500)}
    del expected[123]

    assert len(m2) == len(m) - 1
    _check_map(m2, expected)


def test_no_unary_branches_after_many_deletes():
    m = new_btree_map((i, str(i)) for i in range(3000))

    for i in range(0, 3000, 2):
        m = m.without(i)

    for i in range(1, 3000, 3):
        m = m.without(i)

    if m._root is not None:  # noqa
        for n in _walk_nodes(m._root):  # noqa
            if isinstance(n, _Branch):
                assert len(n.children) >= 2

    deleted = set(range(0, 3000, 2))
    deleted.update(range(1, 3000, 3))

    expected = {
        i: str(i)
        for i in range(3000)
        if i not in deleted
    }

    _check_map(m, expected)


def test_delete_compacts_height_eventually():
    m = new_btree_map((i, str(i)) for i in range(5000))

    assert m._root is not None  # noqa
    initial_depth = _max_depth(m._root)  # noqa

    for i in range(4900):
        m = m.without(i)

    assert m._root is not None  # noqa
    final_depth = _max_depth(m._root)  # noqa

    assert final_depth < initial_depth

    expected = {
        i: str(i)
        for i in range(4900, 5000)
    }

    _check_map(m, expected)


def test_random_deletes_do_not_create_unary_branches():
    rng = random.Random(1)

    keys = list(range(5000))
    rng.shuffle(keys)

    m = new_btree_map((i, str(i)) for i in keys)

    expected = {
        i: str(i)
        for i in keys
    }

    for i, k in enumerate(keys[:4500]):
        m = m.without(k)
        del expected[k]

        if not i % 100:
            if m._root is not None:  # noqa
                for n in _walk_nodes(m._root):  # noqa
                    if isinstance(n, _Branch):
                        assert len(n.children) >= 2

            _check_map(m, expected)

    _check_map(m, expected)
