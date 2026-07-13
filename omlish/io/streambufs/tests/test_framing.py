# ruff: noqa: PT009 PT027
# @omlish-lite
import typing as ta
import unittest

from ..errors import BufferTooLargeByteStreamBufferError
from ..errors import FrameTooLargeByteStreamBufferError
from ..framing import LengthFieldByteStreamFrameDecoder
from ..framing import LongestMatchDelimiterByteStreamFrameDecoder
from ..linear import LinearByteStreamBuffer
from ..segmented import SegmentedByteStreamBuffer


def _view_bytes(v: ta.Any) -> bytes:
    if hasattr(v, 'tobytes'):
        return ta.cast(bytes, v.tobytes())
    # As a fallback, join segments.
    if hasattr(v, 'segments'):
        return b''.join(bytes(mv) for mv in v.segments())
    raise TypeError(v)


class TestLongestMatchDelimiterByteStreamFramer(unittest.TestCase):
    def test_overlapping_delims_defers_at_end(self) -> None:
        # delims overlap: '\r' is prefix of '\r\n'
        f = LongestMatchDelimiterByteStreamFrameDecoder([b'\r', b'\r\n'])
        b = SegmentedByteStreamBuffer()

        b.write(b'abc\r')
        out = f.decode(b)
        self.assertEqual(out, [])
        self.assertEqual(b''.join(bytes(mv) for mv in b.segments()), b'abc\r')

        b.write(b'\nxyz\rq')
        out = f.decode(b)
        self.assertEqual([_view_bytes(v) for v in out], [b'abc', b'xyz'])
        self.assertEqual(b''.join(bytes(mv) for mv in b.segments()), b'q')

    def test_overlapping_delims_final_allows_short(self) -> None:
        f = LongestMatchDelimiterByteStreamFrameDecoder([b'\r', b'\r\n'])
        b = SegmentedByteStreamBuffer()
        b.write(b'abc\r')

        out = f.decode(b, final=True)
        self.assertEqual([_view_bytes(v) for v in out], [b'abc'])
        self.assertEqual(len(b), 0)

    def test_longest_match_at_same_position(self) -> None:
        f = LongestMatchDelimiterByteStreamFrameDecoder([b'\n', b'\r\n'])
        b = SegmentedByteStreamBuffer()
        b.write(b'a\r')
        b.write(b'\nb\n')

        out = f.decode(b)
        self.assertEqual([_view_bytes(v) for v in out], [b'a', b'b'])
        self.assertEqual(len(b), 0)

    def test_keep_ends(self) -> None:
        f = LongestMatchDelimiterByteStreamFrameDecoder([b'\n', b'\r\n'], keep_ends=True)
        b = SegmentedByteStreamBuffer()
        b.write(b'a\r')
        b.write(b'\nb\n')

        out = f.decode(b)
        self.assertEqual([_view_bytes(v) for v in out], [b'a\r\n', b'b\n'])
        self.assertEqual(len(b), 0)

    def test_max_size(self) -> None:
        f = LongestMatchDelimiterByteStreamFrameDecoder([b'\n'], max_size=3)
        b = SegmentedByteStreamBuffer()
        b.write(b'abcd')  # no delimiter, exceeds max_size
        with self.assertRaises(ValueError):
            f.decode(b)

        # But if delimiter appears within the limit, it's fine.
        b2 = SegmentedByteStreamBuffer()
        b2.write(b'abc\nxxxx')
        out = f.decode(b2)
        self.assertEqual([_view_bytes(v) for v in out], [b'abc'])
        self.assertEqual(b''.join(bytes(mv) for mv in b2.segments()), b'xxxx')

    def test_longest_match_framer_raises_subclasses(self) -> None:
        f = LongestMatchDelimiterByteStreamFrameDecoder([b'\n'], max_size=3)
        b = SegmentedByteStreamBuffer()
        b.write(b'abcd')  # no delimiter, exceeds max_size
        with self.assertRaises(BufferTooLargeByteStreamBufferError):
            f.decode(b)

        b2 = SegmentedByteStreamBuffer()
        b2.write(b'abcd\n')  # delimiter exists but frame payload is too large
        with self.assertRaises(FrameTooLargeByteStreamBufferError):
            f.decode(b2)


class TestLengthFieldFrameDecoder(unittest.TestCase):
    def test_basic_u32_be_two_frames_segmented(self) -> None:
        # Frame format: [u32_be length_of_payload][payload]
        dec = LengthFieldByteStreamFrameDecoder(
            length_field_offset=0,
            length_field_length=4,
            byteorder='big',
            length_adjustment=0,
            initial_bytes_to_strip=4,  # strip the length field
            max_frame_length=1024,
        )

        b = SegmentedByteStreamBuffer()
        # Two frames: "hi", "world"
        raw = (
            (2).to_bytes(4, 'big') + b'hi' +
            (5).to_bytes(4, 'big') + b'world'
        )

        # Feed in awkward chunks to exercise segmentation.
        for c in (raw[:3], raw[3:9], raw[9:13], raw[13:]):
            b.write(c)
            out = dec.decode(b)
            # collect progressively
            for v in out:
                if hasattr(v, 'to_bytes'):
                    data = v.to_bytes()  # noqa
                else:
                    data = v.tobytes()  # noqa
                # first decode call may return none until enough is buffered
                # so append to a list below
            # We'll decode again at end.

        # Decode remaining
        outs = dec.decode(b)  # noqa
        all_outs = []
        # The earlier loop didn't collect; do a straightforward decode from scratch:
        b2 = SegmentedByteStreamBuffer()
        for c in (raw[:3], raw[3:9], raw[9:13], raw[13:]):
            b2.write(c)
            for v in dec.decode(b2):
                all_outs.append(v.to_bytes() if hasattr(v, 'to_bytes') else v.tobytes())

        self.assertEqual(all_outs, [b'hi', b'world'])
        self.assertEqual(len(b2), 0)

    def test_u16_le_with_header_and_strip(self) -> None:
        # Frame: [type:u8][len:u16_le payload_length][payload]
        dec = LengthFieldByteStreamFrameDecoder(
            length_field_offset=1,
            length_field_length=2,
            byteorder='little',
            length_adjustment=0,
            initial_bytes_to_strip=3,  # strip type + len
            max_frame_length=64,
        )

        b = SegmentedByteStreamBuffer()
        frame = b'\x7f' + (3).to_bytes(2, 'little') + b'abc'
        b.write(frame)
        out = dec.decode(b)
        self.assertEqual(len(out), 1)
        v = out[0]
        self.assertEqual(v.to_bytes() if hasattr(v, 'to_bytes') else v.tobytes(), b'abc')
        self.assertEqual(len(b), 0)

    def test_length_adjustment_includes_trailer(self) -> None:
        # Frame: [u8 len_of_payload][payload][crc:u2]  (crc length included via adjustment)
        dec = LengthFieldByteStreamFrameDecoder(
            length_field_offset=0,
            length_field_length=1,
            byteorder='big',
            length_adjustment=2,       # include crc
            initial_bytes_to_strip=1,   # strip len byte
            max_frame_length=64,
        )

        b = SegmentedByteStreamBuffer()
        raw = bytes([3]) + b'abc' + b'ZZ'  # crc placeholder
        b.write(raw)
        out = dec.decode(b)
        self.assertEqual(len(out), 1)
        v = out[0]
        self.assertEqual(v.to_bytes() if hasattr(v, 'to_bytes') else v.tobytes(), b'abcZZ')
        self.assertEqual(len(b), 0)

    def test_incomplete_frame_returns_empty(self) -> None:
        dec = LengthFieldByteStreamFrameDecoder(
            length_field_length=4,
            initial_bytes_to_strip=4,
            max_frame_length=64,
        )
        b = SegmentedByteStreamBuffer()
        b.write((10).to_bytes(4, 'big') + b'abc')  # need 10 bytes payload; only 3 provided
        out = dec.decode(b)
        self.assertEqual(out, [])
        self.assertEqual(len(b), 7)

    def test_frame_too_large(self) -> None:
        dec = LengthFieldByteStreamFrameDecoder(
            length_field_length=4,
            initial_bytes_to_strip=4,
            max_frame_length=8,
        )
        b = SegmentedByteStreamBuffer()
        b.write((10).to_bytes(4, 'big') + b'0123456789')
        with self.assertRaises(FrameTooLargeByteStreamBufferError):
            dec.decode(b)

    def test_linear_backend(self) -> None:
        dec = LengthFieldByteStreamFrameDecoder(
            length_field_length=2,
            byteorder='big',
            initial_bytes_to_strip=2,
            max_frame_length=128,
        )
        b = LinearByteStreamBuffer()
        raw = (4).to_bytes(2, 'big') + b'data'
        b.write(raw[:1])
        self.assertEqual(dec.decode(b), [])
        b.write(raw[1:])
        out = dec.decode(b)
        self.assertEqual(len(out), 1)
        v = out[0]
        self.assertEqual(v.to_bytes() if hasattr(v, 'to_bytes') else v.tobytes(), b'data')
        self.assertEqual(len(b), 0)
