import unittest

from ..bytes import memoryview_to_bytes
from ..bytes import memoryview_to_bytes_strict


class TestBytes(unittest.TestCase):
    def test_mv_to_b(self):
        b = b'abcd1234'
        mv = memoryview(b)
        b2 = memoryview_to_bytes(mv)  # noqa
        assert b2 is b

    def test_mv_to_b_non_contiguous(self):
        b = b'abcd1234'

        # Non-contiguous views must yield the view's actual content, not the backing object.
        for mv in [
            memoryview(b)[::-1],
            memoryview(b)[::2],
            memoryview(bytearray(b))[::-1],
        ]:
            assert memoryview_to_bytes(mv) == mv.tobytes()
            assert memoryview_to_bytes_strict(mv) == mv.tobytes()

        assert memoryview_to_bytes(memoryview(b)[2:6]) == b'cd12'
        assert memoryview_to_bytes(memoryview(b)[::1]) is b

    def test_mv_to_b_strict(self):
        b = b'abcd1234'
        assert memoryview_to_bytes_strict(memoryview(b)) is b

        ba = bytearray(b)
        r = memoryview_to_bytes_strict(memoryview(ba))
        assert type(r) is bytes
        assert r == b
