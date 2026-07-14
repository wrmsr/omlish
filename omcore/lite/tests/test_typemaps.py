# ruff: noqa: PT009
import unittest

from ..typemaps import DynamicTypeMap
from ..typemaps import TypeMap


class TestTypeMap(unittest.TestCase):
    def test_basic_get_and_indexing(self):
        class A:
            pass

        class B(A):
            pass

        class C:
            pass

        a = A()
        b = B()
        c = C()

        tm = TypeMap([a, b, c])

        # length, iteration, and items order
        self.assertEqual(len(tm), 3)
        self.assertEqual(list(iter(tm)), [a, b, c])
        self.assertEqual(list(tm.items), [a, b, c])

        # exact type lookups
        self.assertIs(tm.get(A), a)
        self.assertIs(tm[A], a)
        self.assertIs(tm.get(B), b)
        self.assertIs(tm[B], b)
        self.assertIs(tm.get(C), c)
        self.assertIs(tm[C], c)

        # get_any with single base and with tuple of bases
        any_a = tm.get_any(A)
        self.assertEqual(tuple(any_a), (a, b))
        # cached result identity should be stable
        self.assertIs(tm.get_any(A), any_a)

        any_ac = tm.get_any((A, C))
        self.assertEqual(tuple(any_ac), (a, b, c))
        # cached result identity should be stable
        self.assertIs(tm.get_any((A, C)), any_ac)

    def test_duplicate_type_raises(self):
        # Same runtime type twice should raise
        with self.assertRaises(ValueError):
            TypeMap([1, 2])

    def test_of_helper(self):
        class A:
            pass

        a = A()
        lst = [a]

        tm1 = TypeMap.of(lst)
        self.assertIsInstance(tm1, TypeMap)

        tm2 = TypeMap.of(tm1)
        self.assertIs(tm2, tm1)


class TestDynamicTypeMap(unittest.TestCase):
    def test_basic_and_cache(self):
        class A:
            pass

        class B(A):
            pass

        class C:
            pass

        a1 = A()
        b1 = B()
        c1 = C()
        b2 = B()
        a2 = A()

        dtm = DynamicTypeMap([a1, b1, c1, b2, a2])

        # Query by base class A picks A and all subclasses B, preserving order
        got_a = dtm[A]
        self.assertEqual(got_a, [a1, b1, b2, a2])
        # Cache identity should be reused for same key
        self.assertIs(dtm[A], got_a)

        # Query by subclass B
        got_b = dtm[B]
        self.assertEqual(got_b, [b1, b2])
        self.assertIs(dtm[B], got_b)

        # Query by unrelated C
        got_c = dtm[C]
        self.assertEqual(got_c, [c1])
        self.assertIs(dtm[C], got_c)

    def test_weak_cache_flag(self):
        class A:
            pass

        a = A()
        dtm = DynamicTypeMap([a], weak=True)
        self.assertTrue(dtm.is_weak)

        got = dtm[A]
        self.assertEqual(got, [a])
        # Identity should be stable across repeated lookups while the key is alive
        self.assertIs(dtm[A], got)
