# ruff: noqa: SLF001
import random
import typing as ta

import pytest

from .... import lang
from .. import _btreemap_py
from ..btreemap import BtreeMap


K = ta.TypeVar('K')
V = ta.TypeVar('V')


class _BaseBtreeMapTests:
    impl: ta.Any

    @lang.cached_function
    @classmethod
    def btree_map_cls(cls) -> type[BtreeMap]:
        class ImplBtreeMap(BtreeMap[K, V]):
            _backend = cls.impl  # noqa

        return ImplBtreeMap

    @classmethod
    def new_btree_map(
            cls,
            items: ta.Iterable[tuple[K, V]] | None = None,
            *,
            cmp: ta.Callable[[K, K], int] | None = None,
    ) -> BtreeMap[K, V]:
        m: BtreeMap[K, V] = cls.btree_map_cls()(
            _root=None,
            _cmp=cmp,
        )

        if items is not None:
            for k, v in items:
                m = m.with_(k, v)

        return m

    @classmethod
    def _check_map(cls, m: BtreeMap, expected: ta.Mapping, *, cmp=None):
        pass

    def test_empty(self):
        m: BtreeMap = self.new_btree_map()

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

    def test_insert_and_get(self):
        m: BtreeMap = self.new_btree_map()

        for i in [5, 1, 3, 2, 4]:
            m = m.with_(i, str(i))

        assert len(m) == 5
        assert m[1] == '1'
        assert m[5] == '5'
        assert 3 in m
        assert 6 not in m

        self._check_map(m, {i: str(i) for i in range(1, 6)})

    def test_replace(self):
        m = self.new_btree_map([
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

    def test_get(self):
        m = self.new_btree_map([
            (1, 'a'),
            (2, 'b'),
        ])

        assert m.get(1) == 'a'
        assert m.get(2, 'x') == 'b'
        assert m.get(3) is None
        assert m.get(3, 'x') == 'x'

        e: BtreeMap = self.new_btree_map()
        assert e.get(1) is None
        assert e.get(1, 'x') == 'x'

    def test_identical_value_reinsert_shares_root(self):
        v = ['boxed']
        m: BtreeMap[int, ta.Any] = self.new_btree_map((i, str(i)) for i in range(100))
        m = m.with_(50, v)

        m2 = m.with_(50, v)
        assert m2 is m

        m3 = m.with_(50, ['boxed'])
        assert m3 is not m
        assert m3._root is not m._root

    def test_default(self):
        m = self.new_btree_map([
            (1, 'a'),
        ])

        m2 = m.default(1, 'aa')
        m3 = m2.default(2, 'b')

        assert m2 is m
        assert list(m3.iteritems()) == [
            (1, 'a'),
            (2, 'b'),
        ]

    def test_persistence(self):
        versions = []
        m: BtreeMap = self.new_btree_map()

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

    def test_delete(self):
        m = self.new_btree_map((i, str(i)) for i in range(100))

        for i in range(0, 100, 2):
            m = m.without(i)

        expected = {i: str(i) for i in range(1, 100, 2)}
        self._check_map(m, expected)

        for i in range(0, 100, 2):
            m2 = m.without(i)
            assert m2 is m

        for i in range(1, 100, 2):
            m = m.without(i)

        assert len(m) == 0
        assert list(m.iteritems()) == []

    def test_items_from(self):
        m = self.new_btree_map((i, str(i)) for i in range(10))

        assert list(m.items_from(-1)) == [(i, str(i)) for i in range(10)]
        assert list(m.items_from(0)) == [(i, str(i)) for i in range(10)]
        assert list(m.items_from(4)) == [(i, str(i)) for i in range(4, 10)]
        assert list(m.items_from(45)) == []

    def test_items_from_desc(self):
        m = self.new_btree_map((i, str(i)) for i in range(10))

        assert list(m.items_from_desc(-1)) == []
        assert list(m.items_from_desc(0)) == [(0, '0')]
        assert list(m.items_from_desc(4)) == [(i, str(i)) for i in range(4, -1, -1)]
        assert list(m.items_from_desc(45)) == [(i, str(i)) for i in range(9, -1, -1)]

    def test_key_and_value_iteration(self):
        n = 300
        m = self.new_btree_map((i, str(i)) for i in range(n))

        assert list(m) == list(range(n))
        assert list(m.keys()) == list(range(n))
        assert list(m.values()) == [str(i) for i in range(n)]

        for i in range(0, n, 3):
            m = m.without(i)

        remaining = [i for i in range(n) if i % 3]

        assert list(m) == remaining
        assert list(m.values()) == [str(i) for i in remaining]

        e: BtreeMap = self.new_btree_map()
        assert list(e) == []
        assert list(e.values()) == []

    def test_iterator_has_next_and_next(self):
        m = self.new_btree_map((i, str(i)) for i in range(3))

        it = m.iteritems()

        assert it.has_next()
        assert next(it) == (0, '0')
        assert it.has_next()
        assert next(it) == (1, '1')
        assert it.has_next()
        assert next(it) == (2, '2')
        assert not it.has_next()

        with pytest.raises(StopIteration):
            next(it)

    class _Key:
        __hash__ = None  # type: ignore[assignment]

        def __init__(self, value):
            super().__init__()

            self.value = value

        def __repr__(self):
            return f'_Key({self.value!r})'

    @staticmethod
    def _key_cmp(a, b):
        return (a.value > b.value) - (a.value < b.value)

    def test_custom_comparator_with_unhashable_keys(self):
        m: BtreeMap = self.new_btree_map(cmp=self._key_cmp)

        k1a = self._Key(1)
        k1b = self._Key(1)
        k2 = self._Key(2)

        m = m.with_(k1a, 'a')
        m = m.with_(k2, 'b')

        assert m[k1b] == 'a'

        m = m.with_(k1b, 'aa')

        assert m[k1a] == 'aa'
        assert [v for _, v in m.iteritems()] == ['aa', 'b']

        assert m.get(self._Key(2)) == 'b'
        assert m.get(self._Key(3)) is None
        assert self._Key(1) in m
        assert self._Key(3) not in m

    def test_large_sequential(self):
        m: BtreeMap = self.new_btree_map()

        for i in range(2000):
            m = m.with_(i, str(i))

        self._check_map(m, {i: str(i) for i in range(2000)})

        for i in range(0, 2000, 3):
            m = m.without(i)

        expected = {i: str(i) for i in range(2000) if i % 3}
        self._check_map(m, expected)

    def test_random_against_dict(self):
        rng = random.Random(0)

        m: BtreeMap = self.new_btree_map()
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
                self._check_map(m, d)

    def test_insert_non_split_preserves_branch_count_by_arithmetic(self):
        m = self.new_btree_map((i, str(i)) for i in range(500))

        m2 = m.with_(2500, '2500')

        assert len(m2) == len(m) + 1
        assert m2[2500] == '2500'
        self._check_map(m2, {**{i: str(i) for i in range(500)}, 2500: '2500'})

    def test_delete_non_merge_preserves_branch_count_by_arithmetic(self):
        m = self.new_btree_map((i, str(i)) for i in range(500))

        m2 = m.without(123)

        expected = {i: str(i) for i in range(500)}
        del expected[123]

        assert len(m2) == len(m) - 1
        self._check_map(m2, expected)


class TestPyBtreeMap(_BaseBtreeMapTests):
    impl = _btreemap_py

    @staticmethod
    def _default_cmp(a, b):
        return (a > b) - (a < b)

    @classmethod
    def _check_node(cls, n, cmp):
        if isinstance(n, _btreemap_py._Leaf):
            assert len(n.keys) == len(n.values)
            assert n.count == len(n.keys)
            assert len(n.keys) <= _btreemap_py.MAX_LEAF_LEN

            for a, b in zip(n.keys, n.keys[1:]):
                assert cmp(a, b) < 0

            return n.count, n.keys[0], n.keys[-1]

        assert isinstance(n, _btreemap_py._Branch)
        assert len(n.keys) == len(n.children)
        assert len(n.children) <= _btreemap_py.MAX_BRANCH_LEN

        total = 0
        mins = []
        maxs = []

        for c in n.children:
            cnt, mn, mx = cls._check_node(c, cmp)
            total += cnt
            mins.append(mn)
            maxs.append(mx)

        assert total == n.count
        assert tuple(maxs) == n.keys

        for a, b in zip(maxs, mins[1:]):
            assert cmp(a, b) < 0

        return total, mins[0], maxs[-1]

    @classmethod
    def _check_map(cls, m: BtreeMap, expected: ta.Mapping, *, cmp=None):
        if cmp is None:
            cmp = cls._default_cmp

        items = list(m.iteritems())

        assert len(m) == len(expected)
        assert items == sorted(expected.items(), key=lambda kv: kv[0])
        assert list(m.items()) == items
        assert list(m.values()) == [v for _, v in items]
        assert list(m) == [k for k, _ in items]
        assert list(m.items_desc()) == list(reversed(items))
        assert m.debug == dict(items)

        if m._root is not None:
            cnt, _, _ = cls._check_node(m._root, cmp)
            assert cnt == len(m)

    @classmethod
    def _walk_nodes(cls, n):
        yield n

        if isinstance(n, _btreemap_py._Branch):
            for c in n.children:
                yield from cls._walk_nodes(c)

    @classmethod
    def _branch_nodes(cls, m):
        if m._root is None:
            return []

        return [n for n in cls._walk_nodes(m._root) if isinstance(n, _btreemap_py._Branch)]

    @classmethod
    def _max_depth(cls, n):
        if isinstance(n, _btreemap_py._Leaf):
            return 1

        return 1 + max(cls._max_depth(c) for c in n.children)

    def test_random_deletes_do_not_create_unary_branches(self):
        rng = random.Random(1)

        keys = list(range(5000))
        rng.shuffle(keys)

        m = self.new_btree_map((i, str(i)) for i in keys)

        expected = {
            i: str(i)
            for i in keys
        }

        for i, k in enumerate(keys[:4500]):
            m = m.without(k)
            del expected[k]

            if not i % 100:
                if m._root is not None:
                    for n in self._walk_nodes(m._root):
                        if isinstance(n, _btreemap_py._Branch):
                            assert len(n.children) >= 2

                self._check_map(m, expected)

        self._check_map(m, expected)

    def test_update_reuses_unchanged_branch_keys_tuple(self):
        m = self.new_btree_map((i, str(i)) for i in range(500))

        branches = self._branch_nodes(m)
        assert branches

        # Pick a key that should not be the max of most ancestors.
        m2 = m.with_(123, 'updated')

        reused_any = False

        for b2 in self._branch_nodes(m2):
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

                if b.keys[idx] is _btreemap_py._node_max(b2.children[idx]) and b2.keys is b.keys:
                    reused_any = True
                    break

            if reused_any:
                break

        assert reused_any
        self._check_map(m2, {**{i: str(i) for i in range(500)}, 123: 'updated'})

    def test_no_unary_branches_after_many_deletes(self):
        m = self.new_btree_map((i, str(i)) for i in range(3000))

        for i in range(0, 3000, 2):
            m = m.without(i)

        for i in range(1, 3000, 3):
            m = m.without(i)

        if m._root is not None:
            for n in self._walk_nodes(m._root):
                if isinstance(n, _btreemap_py._Branch):
                    assert len(n.children) >= 2

        deleted = set(range(0, 3000, 2))
        deleted.update(range(1, 3000, 3))

        expected = {
            i: str(i)
            for i in range(3000)
            if i not in deleted
        }

        self._check_map(m, expected)

    def test_delete_compacts_height_eventually(self):
        m = self.new_btree_map((i, str(i)) for i in range(5000))

        assert m._root is not None
        initial_depth = self._max_depth(m._root)

        for i in range(4900):
            m = m.without(i)

        assert m._root is not None
        final_depth = self._max_depth(m._root)

        assert final_depth < initial_depth

        expected = {
            i: str(i)
            for i in range(4900, 5000)
        }

        self._check_map(m, expected)


try:
    from .. import _btreemap  # type: ignore
except ImportError:
    pass
else:
    class TestCBtreeMap(_BaseBtreeMapTests):
        impl = _btreemap
