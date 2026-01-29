# ruff: noqa: PT009 PT027
# @omlish-lite
import unittest

from ..errors import NeedMoreDataByteStreamBufferError
from ..reading import ByteStreamBufferReader
from ..segmented import SegmentedByteStreamBuffer


class TestBinaryReadHelpers(unittest.TestCase):
    def test_peek_read_u8(self) -> None:
        b = SegmentedByteStreamBuffer()
        br = ByteStreamBufferReader(b)
        b.write(b'\x01\x02')
        self.assertEqual(br.peek_u8(), 1)
        self.assertEqual(len(b), 2)
        self.assertEqual(br.read_u8(), 1)
        self.assertEqual(len(b), 1)
        self.assertEqual(br.read_u8(), 2)
        self.assertEqual(len(b), 0)
        with self.assertRaises(NeedMoreDataByteStreamBufferError):
            br.peek_u8()

    def test_u16_endianness_across_segments(self) -> None:
        b = SegmentedByteStreamBuffer()
        br = ByteStreamBufferReader(b)
        b.write(b'\x01')
        b.write(b'\x02')
        self.assertEqual(br.peek_u16_be(), 0x0102)
        self.assertEqual(br.peek_u16_le(), 0x0201)
        self.assertEqual(br.read_u16_be(), 0x0102)
        self.assertEqual(len(b), 0)

    def test_u32_endianness_with_head_offset(self) -> None:
        b = SegmentedByteStreamBuffer()
        br = ByteStreamBufferReader(b)
        b.write(b'X')            # junk
        b.write(b'\x01\x02')     # spans segments
        b.write(b'\x03\x04')
        b.advance(1)             # create head offset so peek() starts mid-seg

        self.assertEqual(br.peek_u32_be(), 0x01020304)
        self.assertEqual(br.peek_u32_le(), 0x04030201)
        self.assertEqual(br.read_u32_be(), 0x01020304)
        self.assertEqual(len(b), 0)

    def test_need_more_data(self) -> None:
        b = SegmentedByteStreamBuffer()
        br = ByteStreamBufferReader(b)
        b.write(b'\x01')
        with self.assertRaises(NeedMoreDataByteStreamBufferError):
            br.peek_u16_be()
        with self.assertRaises(NeedMoreDataByteStreamBufferError):
            br.read_u32_le()

    def test_coalesce_used_without_consuming(self) -> None:
        # Ensures peek helpers do not advance.
        b = SegmentedByteStreamBuffer()
        br = ByteStreamBufferReader(b)
        b.write(b'\x00\x10\x20\x30')
        self.assertEqual(br.peek_u32_be(), 0x00102030)
        self.assertEqual(len(b), 4)
        self.assertEqual(b''.join(bytes(mv) for mv in b.segments()), b'\x00\x10\x20\x30')

    def test_peek_exact_and_take_and_read_bytes(self) -> None:
        b = SegmentedByteStreamBuffer()
        br = ByteStreamBufferReader(b)
        b.write(b'a')
        b.write(b'bc')
        self.assertEqual(br.peek_exact(2).tobytes(), b'ab')
        self.assertEqual(len(b), 3)

        v = br.take(2)
        self.assertEqual(v.tobytes(), b'ab')
        self.assertEqual(len(b), 1)

        self.assertEqual(br.read_bytes(1), b'c')
        self.assertEqual(len(b), 0)

        with self.assertRaises(NeedMoreDataByteStreamBufferError):
            br.peek_exact(1)
        with self.assertRaises(NeedMoreDataByteStreamBufferError):
            br.take(1)
        with self.assertRaises(NeedMoreDataByteStreamBufferError):
            br.read_bytes(1)
