# ruff: noqa: PT009
import unittest

from ..maybes import Maybe


class TestMaybes(unittest.TestCase):
    def test_maybes(self):
        m: Maybe[int] = Maybe.just(5)
        self.assertTrue(m.present)
        self.assertEqual(m.must(), 5)

        m = Maybe.empty()
        self.assertFalse(m.present)

    def test_maybes2(self):
        m = Maybe.just(10)
        self.assertEqual(m.must(), 10)

        m2 = Maybe.just(Maybe.just(10))
        self.assertEqual(m2.must().must(), 10)

        m2 = Maybe.just(Maybe.empty())
        self.assertFalse(m2.must().present)

    def test_cmp_ord(self):
        self.assertTrue(Maybe.empty() < Maybe.just(1))
        self.assertTrue(Maybe.just(1) < Maybe.just(2))
        self.assertFalse(Maybe.just(1) > Maybe.just(2))
        self.assertFalse(Maybe.just(2) < Maybe.just(2))
        self.assertFalse(Maybe.just(2) < Maybe.just(1))
