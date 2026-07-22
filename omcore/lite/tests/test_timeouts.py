# ruff: noqa: PT009 PT027
import unittest

from ..timeouts import CompositeTimeout
from ..timeouts import DeadlineTimeout
from ..timeouts import InfiniteTimeout
from ..timeouts import Timeout


class TestTimeouts(unittest.TestCase):
    def test_of(self):
        self.assertIsInstance(Timeout.of(None), InfiniteTimeout)
        self.assertIsInstance(Timeout.of(5), DeadlineTimeout)
        self.assertIsInstance(Timeout.of(5.), DeadlineTimeout)
        self.assertIsInstance(Timeout.of([5, 6]), CompositeTimeout)

        t = Timeout.of(5)
        self.assertIs(Timeout.of(t), t)

    def test_of_str_type_error(self):
        with self.assertRaises(TypeError):
            Timeout.of('5')

        with self.assertRaises(TypeError):
            Timeout.of(b'5')

    def test_empty_composite(self):
        t = Timeout.of(())
        self.assertFalse(t.can_expire)
        self.assertFalse(t.expired())
        self.assertEqual(t.remaining(), float('inf'))
        self.assertEqual(t(), float('inf'))
        self.assertEqual(t.or_('x'), 'x')

    def test_composite(self):
        t = Timeout.of([Timeout.of(5), Timeout.of(None)])
        self.assertTrue(t.can_expire)
        self.assertFalse(t.expired())
        self.assertLessEqual(t.remaining(), 5.)
        self.assertLessEqual(t(), 5.)
