# ruff: noqa: PT009 PT027
# @omlish-lite
import unittest

from ..spilling import SpillingBytesBuffer


class TestSpillingBytesBuffer(unittest.TestCase):
    def test_adaptive_spills_and_preserves_bytes(self) -> None:
        ab = SpillingBytesBuffer(initial_capacity=16, spill_threshold=64)

        ab.write(b'hello')
        self.assertEqual(len(ab), 5)
        self.assertEqual(ab.peek().tobytes(), b'hello')

        ab.write(b' world')
        self.assertEqual(ab.peek().tobytes(), b'hello world')

        # Force spill.
        ab.write(b'x' * 128)
        self.assertEqual(len(ab), len(b'hello world') + 128)

        # Ensure stream-correctness across operations.
        i = ab.find(b' world')
        self.assertEqual(i, 5)

        v = ab.split_to(11)
        self.assertEqual(v.tobytes(), b'hello world')
        self.assertEqual(len(ab), 128)

        ab.advance(64)
        self.assertEqual(len(ab), 64)

        ab.write(b'zzz')
        self.assertEqual(len(ab), 67)
        self.assertEqual(ab.rfind(b'zzz'), 64)

    def test_reserve_commit(self) -> None:
        ab = SpillingBytesBuffer(initial_capacity=16, spill_threshold=64)

        mv = ab.reserve(10)
        mv[:4] = b'abcd'
        ab.commit(4)

        self.assertEqual(len(ab), 4)
        self.assertEqual(ab.peek().tobytes(), b'abcd')
