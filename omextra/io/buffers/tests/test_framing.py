# ruff: noqa: PT009 PT027
# @omlish-lite
import typing as ta
import unittest

from ..errors import BufferTooLarge
from ..errors import FrameTooLarge
from ..framing import LongestMatchDelimiterFramer
from ..segmented import SegmentedBytesBuffer


def _view_bytes(v: ta.Any) -> bytes:
    # Support either naming convention if the caller changes it.
    if hasattr(v, 'tobytes'):
        return ta.cast(bytes, v.tobytes())
    # As a fallback, join segments.
    if hasattr(v, 'segments'):
        return b''.join(bytes(mv) for mv in v.segments())
    raise TypeError(v)


class TestLongestMatchDelimiterFramer(unittest.TestCase):
    def test_overlapping_delims_defers_at_end(self) -> None:
        # delims overlap: '\r' is prefix of '\r\n'
        f = LongestMatchDelimiterFramer([b'\r', b'\r\n'])
        b = SegmentedBytesBuffer()

        b.write(b'abc\r')
        out = f.decode(b)
        self.assertEqual(out, [])
        self.assertEqual(b''.join(bytes(mv) for mv in b.segments()), b'abc\r')

        b.write(b'\nxyz\rq')
        out = f.decode(b)
        self.assertEqual([_view_bytes(v) for v in out], [b'abc', b'xyz'])
        self.assertEqual(b''.join(bytes(mv) for mv in b.segments()), b'q')

    def test_overlapping_delims_final_allows_short(self) -> None:
        f = LongestMatchDelimiterFramer([b'\r', b'\r\n'])
        b = SegmentedBytesBuffer()
        b.write(b'abc\r')

        out = f.decode(b, final=True)
        self.assertEqual([_view_bytes(v) for v in out], [b'abc'])
        self.assertEqual(len(b), 0)

    def test_longest_match_at_same_position(self) -> None:
        f = LongestMatchDelimiterFramer([b'\n', b'\r\n'])
        b = SegmentedBytesBuffer()
        b.write(b'a\r')
        b.write(b'\nb\n')

        out = f.decode(b)
        self.assertEqual([_view_bytes(v) for v in out], [b'a', b'b'])
        self.assertEqual(len(b), 0)

    def test_keep_ends(self) -> None:
        f = LongestMatchDelimiterFramer([b'\n', b'\r\n'], keep_ends=True)
        b = SegmentedBytesBuffer()
        b.write(b'a\r')
        b.write(b'\nb\n')

        out = f.decode(b)
        self.assertEqual([_view_bytes(v) for v in out], [b'a\r\n', b'b\n'])
        self.assertEqual(len(b), 0)

    def test_max_size(self) -> None:
        f = LongestMatchDelimiterFramer([b'\n'], max_size=3)
        b = SegmentedBytesBuffer()
        b.write(b'abcd')  # no delimiter, exceeds max_size
        with self.assertRaises(ValueError):
            f.decode(b)

        # But if delimiter appears within the limit, it's fine.
        b2 = SegmentedBytesBuffer()
        b2.write(b'abc\nxxxx')
        out = f.decode(b2)
        self.assertEqual([_view_bytes(v) for v in out], [b'abc'])
        self.assertEqual(b''.join(bytes(mv) for mv in b2.segments()), b'xxxx')

    def test_longest_match_framer_raises_subclasses(self) -> None:
        f = LongestMatchDelimiterFramer([b'\n'], max_size=3)
        b = SegmentedBytesBuffer()
        b.write(b'abcd')  # no delimiter, exceeds max_size
        with self.assertRaises(BufferTooLarge):
            f.decode(b)

        b2 = SegmentedBytesBuffer()
        b2.write(b'abcd\n')  # delimiter exists but frame payload is too large
        with self.assertRaises(FrameTooLarge):
            f.decode(b2)
