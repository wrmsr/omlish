# ruff: noqa: SLF001
import random
import typing as ta

import pytest

from .... import lang
from .. import _btreeseq_py
from ..btreeseq import BtreeSeq


T = ta.TypeVar('T')


class _BaseBtreeSeqTests:
    impl: ta.Any

    @lang.cached_function
    @classmethod
    def btree_seq_cls(cls) -> type[BtreeSeq]:
        class ImplBtreeSeq(BtreeSeq[T]):
            _backend = cls.impl  # noqa

        return ImplBtreeSeq

    @classmethod
    def new_btree_seq(cls, items: ta.Iterable[T] | None = None) -> BtreeSeq[T]:
        return cls.btree_seq_cls()(
            _root=cls.impl.from_iterable(()) if items is None else cls.impl.from_iterable(items),
        )

    @classmethod
    def _check_seq(cls, s: BtreeSeq, expected: ta.Sequence):
        assert len(s) == len(expected)
        assert list(s) == list(expected)
        assert tuple(s) == tuple(expected)
        assert s.debug == tuple(expected)

        for i, v in enumerate(expected):
            assert s[i] == v
            assert s[i - len(expected)] == v

        if expected:
            with pytest.raises(IndexError):
                s[len(expected)]

            with pytest.raises(IndexError):
                s[-len(expected) - 1]

        else:
            with pytest.raises(IndexError):
                s[0]

            with pytest.raises(IndexError):
                s[-1]

    def test_empty(self):
        s: BtreeSeq = self.new_btree_seq()

        assert len(s) == 0
        assert list(s) == []
        assert s.debug == ()

        with pytest.raises(IndexError):
            s[0]

        assert list(s[:]) == []
        assert list(s[0:0]) == []

    def test_construct_and_index(self):
        s: BtreeSeq = self.new_btree_seq(range(10))

        self._check_seq(s, list(range(10)))

        assert s[0] == 0
        assert s[9] == 9
        assert s[-1] == 9
        assert s[-10] == 0

    def test_slices(self):
        s: BtreeSeq = self.new_btree_seq(range(20))

        assert list(s[:]) == list(range(20))
        assert list(s[3:8]) == list(range(3, 8))
        assert list(s[:5]) == list(range(5))
        assert list(s[15:]) == list(range(15, 20))
        assert list(s[-8:-2]) == list(range(12, 18))
        assert list(s[8:3]) == []

        with pytest.raises(ValueError):  # noqa
            s[::2]

        with pytest.raises(ValueError):  # noqa
            s[::-1]

    def test_append_extend(self):
        s: BtreeSeq = self.new_btree_seq()

        for i in range(20):
            s = s.append(i)

        self._check_seq(s, list(range(20)))

        s = s.extend(range(20, 60))

        self._check_seq(s, list(range(60)))

    def test_splice_insert_middle(self):
        s = self.new_btree_seq(range(10))
        s2 = s.splice(5, 5, [100, 101, 102])

        self._check_seq(s, list(range(10)))
        self._check_seq(s2, [0, 1, 2, 3, 4, 100, 101, 102, 5, 6, 7, 8, 9])

    def test_splice_insert_end(self):
        s = self.new_btree_seq(range(10))
        s2 = s.splice(len(s), len(s), range(10, 20))

        self._check_seq(s2, list(range(20)))

    def test_splice_delete_middle(self):
        s = self.new_btree_seq(range(20))
        s2 = s.splice(7, 13, ())

        self._check_seq(s, list(range(20)))
        self._check_seq(s2, list(range(7)) + list(range(13, 20)))

    def test_splice_delete_prefix(self):
        s = self.new_btree_seq(range(100))
        s2 = s.splice(0, 80, ())

        self._check_seq(s2, list(range(80, 100)))

    def test_splice_delete_suffix(self):
        s = self.new_btree_seq(range(100))
        s2 = s.splice(80, 100, ())

        self._check_seq(s2, list(range(80)))

    def test_splice_replace_same_size(self):
        s = self.new_btree_seq(range(100))
        s2 = s.splice(40, 50, range(1000, 1010))

        expected = list(range(100))
        expected[40:50] = list(range(1000, 1010))

        self._check_seq(s, list(range(100)))
        self._check_seq(s2, expected)

    def test_with(self):
        s = self.new_btree_seq(range(10))
        s2 = s.with_(5, 100)

        self._check_seq(s, list(range(10)))
        self._check_seq(s2, [0, 1, 2, 3, 4, 100, 6, 7, 8, 9])

    def test_without_index(self):
        s = self.new_btree_seq(range(10))
        s2 = s.without(5)

        self._check_seq(s2, [0, 1, 2, 3, 4, 6, 7, 8, 9])

    def test_without_slice(self):
        s = self.new_btree_seq(range(20))
        s2 = s.without(slice(4, 16))

        self._check_seq(s2, list(range(4)) + list(range(16, 20)))

    def test_identical_replace_shares_root(self):
        v = ['boxed']
        s: BtreeSeq[ta.Any] = self.new_btree_seq(range(100))
        s = s.with_(50, v)

        s2 = s.with_(50, v)
        assert s2 is s

        s3 = s.with_(50, ['boxed'])
        assert s3 is not s
        assert s3._root is not s._root

    def test_many_appends(self):
        s: BtreeSeq = self.new_btree_seq()

        for i in range(2000):
            s = s.append(i)

        self._check_seq(s, list(range(2000)))

    def test_iterator_has_next_and_next(self):
        s = self.new_btree_seq(range(3))

        it = iter(s)

        assert it.has_next()
        assert next(it) == 0
        assert it.has_next()
        assert next(it) == 1
        assert it.has_next()
        assert next(it) == 2
        assert not it.has_next()

        with pytest.raises(StopIteration):
            next(it)

    def test_persistence(self):
        versions = []
        s: BtreeSeq = self.new_btree_seq()

        for i in range(100):
            versions.append(s)
            s = s.append(i)

        for i, old in enumerate(versions):
            self._check_seq(old, list(range(i)))

        old = s
        s = s.splice(20, 80, [1000, 1001, 1002])

        self._check_seq(old, list(range(100)))
        self._check_seq(s, list(range(20)) + [1000, 1001, 1002] + list(range(80, 100)))  # noqa

    def test_large_sequential(self):
        s: BtreeSeq = self.new_btree_seq(range(5000))

        self._check_seq(s, list(range(5000)))

        s = s.splice(1000, 4000, range(100))

        self._check_seq(s, list(range(1000)) + list(range(100)) + list(range(4000, 5000)))

        s = s.append(5000)

        self._check_seq(s, list(range(1000)) + list(range(100)) + list(range(4000, 5000)) + [5000])

    def test_random_against_list(self):
        rng = random.Random(0)

        s: BtreeSeq = self.new_btree_seq()
        lst: list = []

        for step in range(2000):
            op = rng.randrange(5)

            if op == 0:
                v = rng.randrange(100000)
                idx = rng.randrange(len(lst) + 1)
                s = s.splice(idx, idx, [v])
                lst[idx:idx] = [v]

            elif op == 1 and lst:
                start = rng.randrange(len(lst))
                stop = rng.randrange(start, len(lst) + 1)
                vals = [rng.randrange(100000) for _ in range(rng.randrange(8))]
                s = s.splice(start, stop, vals)
                lst[start:stop] = vals

            elif op == 2:
                vals = [rng.randrange(100000) for _ in range(rng.randrange(16))]
                s = s.extend(vals)
                lst.extend(vals)

            elif op == 3 and lst:
                n = rng.randrange(len(lst) + 1)
                s = s.splice(0, n, ())
                del lst[:n]

            elif lst:
                idx = rng.randrange(len(lst))
                v = rng.randrange(100000)
                s = s.with_(idx, v)
                lst[idx] = v

            if not step % 25:
                self._check_seq(s, lst)

        self._check_seq(s, lst)


class TestPyBtreeSeq(_BaseBtreeSeqTests):
    impl = _btreeseq_py

    @classmethod
    def _check_node(cls, n):
        if isinstance(n, _btreeseq_py._Leaf):
            assert n.count == len(n.items)
            assert n.height == 0
            assert 0 < len(n.items) <= _btreeseq_py.MAX_LEAF_LEN
            return n.count

        assert isinstance(n, _btreeseq_py._Branch)
        assert len(n.children) == len(n.offsets)
        assert len(n.children) >= 2
        assert len(n.children) <= _btreeseq_py.MAX_BRANCH_LEN
        assert n.count == n.offsets[-1]
        assert n.height == 1 + max(c.height for c in n.children)

        total = 0
        base = 0

        for c, off in zip(n.children, n.offsets):
            assert c.count == off - base
            base = off
            total += cls._check_node(c)

        assert total == n.count

        return total

    @classmethod
    def _check_seq(cls, s: BtreeSeq, expected: ta.Sequence):
        super()._check_seq(s, expected)

        if s._root is not None:
            assert cls._check_node(s._root) == len(s)

    @classmethod
    def _walk_nodes(cls, n):
        yield n

        if isinstance(n, _btreeseq_py._Branch):
            for c in n.children:
                yield from cls._walk_nodes(c)

    @classmethod
    def _max_depth(cls, n):
        if isinstance(n, _btreeseq_py._Leaf):
            return 1

        return 1 + max(cls._max_depth(c) for c in n.children)

    def test_append_depth_stays_logarithmic(self):
        s: BtreeSeq = self.new_btree_seq()

        for i in range(4000):
            s = s.append(i)

        assert self._max_depth(s._root) <= 6
        self._check_seq(s, list(range(4000)))

    def test_prepend_depth_stays_logarithmic(self):
        s: BtreeSeq = self.new_btree_seq()

        for i in range(4000):
            s = s.splice(0, 0, (i,))

        assert self._max_depth(s._root) <= 6
        self._check_seq(s, list(range(3999, -1, -1)))

    def test_no_unary_branches_after_many_prefix_deletes(self):
        s = self.new_btree_seq(range(3000))

        for _ in range(30):
            s = s.splice(0, 50, ())

        if s._root is not None:
            for n in self._walk_nodes(s._root):
                if isinstance(n, _btreeseq_py._Branch):
                    assert len(n.children) >= 2

        self._check_seq(s, list(range(1500, 3000)))

    def test_same_size_replace_preserves_length_and_shape_reasonably(self):
        s = self.new_btree_seq(range(1000))
        root = s._root

        s2 = s.splice(400, 600, range(10000, 10200))

        assert len(s2) == len(s)
        assert s2._root is not root

        expected = list(range(1000))
        expected[400:600] = list(range(10000, 10200))

        self._check_seq(s2, expected)


try:
    from .. import _btreeseq  # type: ignore
except ImportError:
    pass
else:
    class TestCBtreeSeq(_BaseBtreeSeqTests):
        impl = _btreeseq
