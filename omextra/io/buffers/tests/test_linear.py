# ruff: noqa: PT009 PT027
# @omlish-lite
import unittest

from ..errors import BufferTooLarge
from ..errors import NoOutstandingReserve
from ..errors import OutstandingReserve
from ..linear import LinearBytesBuffer


class TestLinearBytesBuffer(unittest.TestCase):
    def test_basic_write_peek_segments(self) -> None:
        b = LinearBytesBuffer()
        b.write(b'abc')
        b.write(b'def')
        self.assertEqual(len(b), 6)
        self.assertEqual(b.peek().tobytes(), b'abcdef')
        self.assertEqual(b''.join(bytes(mv) for mv in b.segments()), b'abcdef')

    def test_advance_and_compact(self) -> None:
        b = LinearBytesBuffer()
        b.write(b'a' * 100)
        b.advance(100)
        self.assertEqual(len(b), 0)
        self.assertEqual(b.peek().tobytes(), b'')

    def test_find_rfind_with_offsets(self) -> None:
        b = LinearBytesBuffer()
        b.write(b'01234567')
        self.assertEqual(b.find(b'23'), 2)
        self.assertEqual(b.rfind(b'23'), 2)
        self.assertEqual(b.find(b'23', 3), -1)
        self.assertEqual(b.find(b'23', 0, 3), -1)
        self.assertEqual(b.find(b''), 0)
        self.assertEqual(b.rfind(b''), len(b))

        b.advance(2)  # readable now "234567"
        self.assertEqual(b.find(b'23'), 0)
        self.assertEqual(b.find(b'67'), 4)
        self.assertEqual(b.rfind(b'67'), 4)

    def test_split_to_consumes_and_returns_stable_view(self) -> None:
        b = LinearBytesBuffer()
        b.write(b'ab')
        b.write(b'cd')
        v = b.split_to(3)
        self.assertEqual(v.tobytes(), b'abc')
        self.assertEqual(len(b), 1)
        self.assertEqual(b.peek().tobytes(), b'd')

    def test_reserve_commit(self) -> None:
        b = LinearBytesBuffer()
        mv = b.reserve(5)
        mv[:3] = b'xyz'
        b.commit(3)
        self.assertEqual(len(b), 3)
        self.assertEqual(b.peek().tobytes(), b'xyz')

    def test_reserve_blocks_ops(self) -> None:
        b = LinearBytesBuffer()
        b.write(b'abc')
        _ = b.reserve(2)
        with self.assertRaises(OutstandingReserve):
            b.write(b'x')
        with self.assertRaises(OutstandingReserve):
            b.coalesce(1)
        with self.assertRaises(OutstandingReserve):
            b.advance(1)
        with self.assertRaises(OutstandingReserve):
            b.split_to(1)
        b.commit(0)
        with self.assertRaises(NoOutstandingReserve):
            b.commit(0)

    def test_coalesce(self) -> None:
        b = LinearBytesBuffer()
        b.write(b'abcdef')
        self.assertEqual(b.coalesce(3).tobytes(), b'abc')
        b.advance(2)
        self.assertEqual(b.coalesce(2).tobytes(), b'cd')

    def test_max_bytes_linear_write(self) -> None:
        b = LinearBytesBuffer(max_bytes=3)
        b.write(b'ab')
        b.write(b'c')
        with self.assertRaises(BufferTooLarge):
            b.write(b'd')
        self.assertEqual(b.peek().tobytes(), b'abc')

    def test_max_bytes_linear_commit(self) -> None:
        b = LinearBytesBuffer(max_bytes=3)
        mv = b.reserve(4)
        mv[:] = b'abcd'
        with self.assertRaises(BufferTooLarge):
            b.commit(4)
        self.assertEqual(len(b), 0)

    def test_max_bytes_respects_consumption(self) -> None:
        b = LinearBytesBuffer(max_bytes=3)
        b.write(b'abc')
        b.advance(2)
        b.write(b'de')  # len now 1 + 2 == 3 ok
        self.assertEqual(b.peek().tobytes(), b'cde')
