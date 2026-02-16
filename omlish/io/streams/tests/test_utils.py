import unittest

from ..utils import ByteStreamBuffers


class TestUtils(unittest.TestCase):
    def test_mv_to_b(self):
        b = b'abcd1234'
        mv = memoryview(b)
        b2 = ByteStreamBuffers.memoryview_to_bytes(mv)  # noqa
        assert b2 is b
