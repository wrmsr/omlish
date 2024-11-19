import unittest

from ..maybes import Maybe


class TestMaybes(unittest.TestCase):
    def test_maybes(self):
        m: Maybe[int] = Maybe.just(5)
        self.assertTrue(m.present)
        self.assertEqual(m.must(), 5)

        m = Maybe.empty()
        self.assertFalse(m.present)
