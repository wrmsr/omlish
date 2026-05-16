import unittest

from ..bytes import memoryview_to_bytes


class TestBytes(unittest.TestCase):
    def test_mv_to_b(self):
        b = b'abcd1234'
        mv = memoryview(b)
        b2 = memoryview_to_bytes(mv)  # noqa
        assert b2 is b
