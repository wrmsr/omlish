# ruff: noqa: PT009 PT027
# @omlish-lite
import unittest

from ..errors import NeedMoreData
from ..reading import peek_exact
from ..reading import peek_u8
from ..reading import peek_u16_be
from ..reading import peek_u16_le
from ..reading import peek_u32_be
from ..reading import peek_u32_le
from ..reading import read_bytes
from ..reading import read_u8
from ..reading import read_u16_be
from ..reading import read_u32_be
from ..reading import read_u32_le
from ..reading import take
from ..segmented import SegmentedBytesBuffer


class TestBinaryReadHelpers(unittest.TestCase):
    def test_peek_read_u8(self) -> None:
        b = SegmentedBytesBuffer()
        b.write(b'\x01\x02')
        self.assertEqual(peek_u8(b), 1)
        self.assertEqual(len(b), 2)
        self.assertEqual(read_u8(b), 1)
        self.assertEqual(len(b), 1)
        self.assertEqual(read_u8(b), 2)
        self.assertEqual(len(b), 0)
        with self.assertRaises(NeedMoreData):
            peek_u8(b)

    def test_u16_endianness_across_segments(self) -> None:
        b = SegmentedBytesBuffer()
        b.write(b'\x01')
        b.write(b'\x02')
        self.assertEqual(peek_u16_be(b), 0x0102)
        self.assertEqual(peek_u16_le(b), 0x0201)
        self.assertEqual(read_u16_be(b), 0x0102)
        self.assertEqual(len(b), 0)

    def test_u32_endianness_with_head_offset(self) -> None:
        b = SegmentedBytesBuffer()
        b.write(b'X')            # junk
        b.write(b'\x01\x02')     # spans segments
        b.write(b'\x03\x04')
        b.advance(1)             # create head offset so peek() starts mid-seg

        self.assertEqual(peek_u32_be(b), 0x01020304)
        self.assertEqual(peek_u32_le(b), 0x04030201)
        self.assertEqual(read_u32_be(b), 0x01020304)
        self.assertEqual(len(b), 0)

    def test_need_more_data(self) -> None:
        b = SegmentedBytesBuffer()
        b.write(b'\x01')
        with self.assertRaises(NeedMoreData):
            peek_u16_be(b)
        with self.assertRaises(NeedMoreData):
            read_u32_le(b)

    def test_coalesce_used_without_consuming(self) -> None:
        # Ensures peek helpers do not advance.
        b = SegmentedBytesBuffer()
        b.write(b'\x00\x10\x20\x30')
        self.assertEqual(peek_u32_be(b), 0x00102030)
        self.assertEqual(len(b), 4)
        self.assertEqual(b''.join(bytes(mv) for mv in b.segments()), b'\x00\x10\x20\x30')

    def test_peek_exact_and_take_and_read_bytes(self) -> None:
        b = SegmentedBytesBuffer()
        b.write(b'a')
        b.write(b'bc')
        self.assertEqual(peek_exact(b, 2).tobytes(), b'ab')
        self.assertEqual(len(b), 3)

        v = take(b, 2)
        self.assertEqual(v.tobytes(), b'ab')
        self.assertEqual(len(b), 1)

        self.assertEqual(read_bytes(b, 1), b'c')
        self.assertEqual(len(b), 0)

        with self.assertRaises(NeedMoreData):
            peek_exact(b, 1)
        with self.assertRaises(NeedMoreData):
            take(b, 1)
        with self.assertRaises(NeedMoreData):
            read_bytes(b, 1)
