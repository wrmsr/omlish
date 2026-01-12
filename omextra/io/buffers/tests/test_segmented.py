# ruff: noqa: PT009 PT027
# @omlish-lite
import unittest

from ..errors import BufferTooLarge
from ..errors import NoOutstandingReserve
from ..errors import OutstandingReserve
from ..segmented import SegmentedBytesBuffer


class TestSegmentedBytesBuffer(unittest.TestCase):
    def test_len_peek_segments(self) -> None:
        b = SegmentedBytesBuffer()
        self.assertEqual(len(b), 0)
        self.assertEqual(bytes(b.peek()), b'')
        self.assertEqual(b.segments(), ())

        b.write(b'abc')
        b.write(b'def')
        self.assertEqual(len(b), 6)
        self.assertEqual(bytes(b.peek()), b'abc')
        self.assertEqual(b''.join(bytes(mv) for mv in b.segments()), b'abcdef')

        b.advance(2)
        self.assertEqual(len(b), 4)
        self.assertEqual(bytes(b.peek()), b'c')
        self.assertEqual(b''.join(bytes(mv) for mv in b.segments()), b'cdef')

    def test_split_to_view(self) -> None:
        b = SegmentedBytesBuffer()
        b.write(b'ab')
        b.write(b'cd')
        v = b.split_to(3)
        self.assertEqual(v.tobytes(), b'abc')
        self.assertEqual(len(b), 1)
        self.assertEqual(b''.join(bytes(mv) for mv in b.segments()), b'd')

    def test_find_cross_segment(self) -> None:
        b = SegmentedBytesBuffer()
        b.write(b'hello\r')
        b.write(b'\nworld')
        self.assertEqual(b.find(b'\r\n'), 5)
        self.assertEqual(b.find(b'world'), 7)
        self.assertEqual(b.find(b'nope'), -1)

    def test_rfind_cross_segment(self) -> None:
        b = SegmentedBytesBuffer()
        b.write(b'aa\r')
        b.write(b'\naa\r')
        b.write(b'\naa')
        # Stream is: b"aa\r\naa\r\naa"
        self.assertEqual(b.rfind(b'\r\n'), 6)
        self.assertEqual(b.find(b'\r\n'), 2)

    def test_find_start_end(self) -> None:
        b = SegmentedBytesBuffer()
        b.write(b'0123')
        b.write(b'4567')
        self.assertEqual(b.find(b'23'), 2)
        self.assertEqual(b.find(b'23', 3), -1)
        self.assertEqual(b.find(b'23', 0, 3), -1)
        self.assertEqual(b.find(b'23', 0, 4), 2)
        self.assertEqual(b.rfind(b'23', 0, 4), 2)
        self.assertEqual(b.rfind(b'23', 0, 3), -1)

    def test_empty_sub(self) -> None:
        b = SegmentedBytesBuffer()
        b.write(b'abc')
        self.assertEqual(b.find(b''), 0)
        self.assertEqual(b.find(b'', 2), 2)
        self.assertEqual(b.find(b'', 99), 3)
        self.assertEqual(b.rfind(b''), 3)
        self.assertEqual(b.rfind(b'', 0, 2), 2)

    def test_reserve_commit(self) -> None:
        b = SegmentedBytesBuffer()
        mv = b.reserve(5)
        mv[:3] = b'xyz'
        b.commit(3)
        self.assertEqual(len(b), 3)
        self.assertEqual(b''.join(bytes(s) for s in b.segments()), b'xyz')

    def test_segmented_buffer_outstanding_reserve_errors(self) -> None:
        b = SegmentedBytesBuffer()
        b.write(b'abc')
        _ = b.reserve(2)

        with self.assertRaises(OutstandingReserve):
            b.reserve(1)

        with self.assertRaises(OutstandingReserve):
            b.coalesce(1)

        b.commit(0)

        with self.assertRaises(NoOutstandingReserve):
            b.commit(0)

    def test_rfind_early_termination(self) -> None:
        """
        Test that rfind terminates early when match is found in rightmost segments.

        This test verifies the performance optimization: if the rightmost match is in the last segment, we should not
        scan all earlier segments.
        """

        b = SegmentedBytesBuffer()
        # Create many segments with lots of data.
        for _ in range(100):
            b.write(b'x' * 100)
        # Add a pattern in the last segment.
        b.write(b'xFINDMEx')

        # The pattern 'FINDME' should be found near the end.
        pos = b.rfind(b'FINDME')
        self.assertEqual(pos, 10001)  # 100 segments * 100 bytes + 1

        # Verify it's actually at that position by checking context.
        view = b.split_to(pos + 6)
        tail = view.tobytes()[-6:]
        self.assertEqual(tail, b'FINDME')

    def test_rfind_with_boundary_match_rightmost(self) -> None:
        """Test that rfind correctly finds a boundary match when it's the rightmost."""

        b = SegmentedBytesBuffer()
        b.write(b'abcAB')
        b.write(b'CDef')
        # 'ABCD' spans the boundary at position 3.
        self.assertEqual(b.rfind(b'ABCD'), 3)

    def test_rfind_prefers_rightmost_of_multiple(self) -> None:
        """Test that rfind returns the rightmost match when multiple exist."""

        b = SegmentedBytesBuffer()
        b.write(b'XXabc')
        b.write(b'XXde')
        b.write(b'XXfg')
        # Three occurrences of 'XX' at positions 0, 5, 9.
        self.assertEqual(b.rfind(b'XX'), 9)

    def test_find_vs_rfind_consistency(self) -> None:
        """Test that find and rfind are consistent for single-match cases."""

        b = SegmentedBytesBuffer()
        b.write(b'abc')
        b.write(b'def')
        b.write(b'ghi')

        # Single match cases should return same position.
        self.assertEqual(b.find(b'def'), b.rfind(b'def'))
        self.assertEqual(b.find(b'cde'), b.rfind(b'cde'))  # Boundary match
        self.assertEqual(b.find(b'ghi'), b.rfind(b'ghi'))

    def test_rfind_with_overlapping_occurrences(self) -> None:
        """Test rfind with overlapping occurrences of the pattern."""

        b = SegmentedBytesBuffer()
        b.write(b'aaa')
        b.write(b'aaa')
        # Pattern 'aa' occurs at positions 0, 1, 2, 3, 4.
        # rfind should return the rightmost: 4.
        self.assertEqual(b.rfind(b'aa'), 4)

    def test_search_with_head_offset(self) -> None:
        """Test that search works correctly when head_off is non-zero."""

        b = SegmentedBytesBuffer()
        b.write(b'discardABCDEF')
        b.write(b'GHIJ')

        # Advance past 'discard', leaving 'ABCDEFGHIJ'.
        b.advance(7)

        self.assertEqual(b.find(b'ABCD'), 0)
        self.assertEqual(b.rfind(b'GHIJ'), 6)
        self.assertEqual(b.find(b'EFGH'), 4)  # Boundary match

    def test_find_delimiter_spanning_three_segments(self) -> None:
        """
        Test finding a delimiter that spans more than 2 segments.

        Current implementation may not handle this case correctly due to the rolling window approach which only checks
        adjacent segment boundaries.
        """

        b = SegmentedBytesBuffer()
        # Create segments where a 5-byte delimiter 'ABCDE' spans 3 segments.
        # Segment layout: 'xxAB' | 'CD' | 'Eyy'
        b.write(b'xxAB')
        b.write(b'CD')
        b.write(b'Eyy')

        # The delimiter 'ABCDE' starts at position 2 and spans segments 0, 1, 2.
        pos = b.find(b'ABCDE')
        self.assertEqual(pos, 2, f"Expected to find 'ABCDE' at position 2, got {pos}")

    def test_rfind_delimiter_spanning_three_segments(self) -> None:
        """Test rfind with a delimiter spanning more than 2 segments."""

        b = SegmentedBytesBuffer()
        # Segment layout: 'xxAB' | 'CD' | 'Eyy'
        b.write(b'xxAB')
        b.write(b'CD')
        b.write(b'Eyy')

        pos = b.rfind(b'ABCDE')
        self.assertEqual(pos, 2, f"Expected to rfind 'ABCDE' at position 2, got {pos}")

    def test_find_delimiter_spanning_many_segments(self) -> None:
        """Test with a delimiter spanning many small segments."""

        b = SegmentedBytesBuffer()
        # Create 10 segments of 2 bytes each, with a 5-byte delimiter in the middle.
        # Layout: 'xx' | 'xA' | 'BC' | 'DE' | 'xx' | 'xx' | 'xx' | 'xx' | 'xx' | 'xx'
        b.write(b'xx')
        b.write(b'xA')
        b.write(b'BC')
        b.write(b'DE')
        for _ in range(6):
            b.write(b'xx')

        # 'ABCDE' starts at position 3 and spans segments 1, 2, 3.
        pos = b.find(b'ABCDE')
        self.assertEqual(pos, 3, f"Expected to find 'ABCDE' at position 3, got {pos}")

    def test_rfind_delimiter_spanning_many_segments(self) -> None:
        """Test rfind with a delimiter spanning many small segments."""

        b = SegmentedBytesBuffer()
        # Layout: 'xx' | 'xA' | 'BC' | 'DE' | 'xx' | 'xx' | 'xx' | 'xx' | 'xx' | 'xx'
        b.write(b'xx')
        b.write(b'xA')
        b.write(b'BC')
        b.write(b'DE')
        for _ in range(6):
            b.write(b'xx')

        pos = b.rfind(b'ABCDE')
        self.assertEqual(pos, 3, f"Expected to rfind 'ABCDE' at position 3, got {pos}")

    def test_find_multiple_delimiters_spanning_segments(self) -> None:
        """Test find with multiple occurrences of a multi-segment-spanning delimiter."""

        b = SegmentedBytesBuffer()
        # Two occurrences of 'ABC': one spanning segments, one not.
        # Layout: 'xA' | 'BC' | 'yy' | 'ABC' | 'z'
        b.write(b'xA')
        b.write(b'BC')
        b.write(b'yy')
        b.write(b'ABC')
        b.write(b'z')

        # First occurrence at position 1, spanning segments 0-1.
        pos = b.find(b'ABC')
        self.assertEqual(pos, 1, f"Expected to find first 'ABC' at position 1, got {pos}")

        # Second occurrence at position 6, within a single segment.
        pos2 = b.find(b'ABC', 2)
        self.assertEqual(pos2, 6, f"Expected to find second 'ABC' at position 6, got {pos2}")

    def test_rfind_multiple_delimiters_spanning_segments(self) -> None:
        """Test rfind with multiple occurrences of a multi-segment-spanning delimiter."""

        b = SegmentedBytesBuffer()
        # Layout: 'xA' | 'BC' | 'yy' | 'ABC' | 'z'
        b.write(b'xA')
        b.write(b'BC')
        b.write(b'yy')
        b.write(b'ABC')
        b.write(b'z')

        # rfind should return the rightmost occurrence at position 6.
        pos = b.rfind(b'ABC')
        self.assertEqual(pos, 6, f"Expected to rfind rightmost 'ABC' at position 6, got {pos}")

    def test_find_with_start_end_spanning_segments(self) -> None:
        """Test find with start/end bounds when delimiter spans segments."""

        b = SegmentedBytesBuffer()
        # Layout: 'AB' | 'CD' | 'EF' | 'AB' | 'CD' | 'EF'
        b.write(b'AB')
        b.write(b'CD')
        b.write(b'EF')
        b.write(b'AB')
        b.write(b'CD')
        b.write(b'EF')

        # 'ABCDEF' occurs at positions 0 and 6.
        # Full search should find first at 0.
        self.assertEqual(b.find(b'ABCDEF'), 0)

        # Search starting from position 1 should find second at 6.
        self.assertEqual(b.find(b'ABCDEF', 1), 6)

        # Search with end=5 should not find any (first ends at 6, second starts at 6).
        self.assertEqual(b.find(b'ABCDEF', 0, 5), -1)

        # Search with end=6 should find first (which starts at 0 and ends at 6).
        self.assertEqual(b.find(b'ABCDEF', 0, 6), 0)

    def test_rfind_with_start_end_spanning_segments(self) -> None:
        """Test rfind with start/end bounds when delimiter spans segments."""

        b = SegmentedBytesBuffer()
        # Layout: 'AB' | 'CD' | 'EF' | 'AB' | 'CD' | 'EF'
        b.write(b'AB')
        b.write(b'CD')
        b.write(b'EF')
        b.write(b'AB')
        b.write(b'CD')
        b.write(b'EF')

        # 'ABCDEF' occurs at positions 0 and 6.
        # Full search should find rightmost at 6.
        self.assertEqual(b.rfind(b'ABCDEF'), 6)

        # Search ending at position 6 should find first at 0 (second starts at 6, so not in range).
        self.assertEqual(b.rfind(b'ABCDEF', 0, 6), 0)

        # Search starting from position 7 should not find any.
        self.assertEqual(b.rfind(b'ABCDEF', 7), -1)

        # Search from 1 to end should find second at 6.
        self.assertEqual(b.rfind(b'ABCDEF', 1), 6)

    def test_max_bytes_segmented_write(self) -> None:
        b = SegmentedBytesBuffer(max_bytes=3)
        b.write(b'ab')
        b.write(b'c')
        with self.assertRaises(BufferTooLarge):
            b.write(b'd')
        self.assertEqual(b''.join(bytes(mv) for mv in b.segments()), b'abc')

    def test_max_bytes_segmented_commit(self) -> None:
        b = SegmentedBytesBuffer(max_bytes=3)
        mv = b.reserve(4)
        mv[:] = b'abcd'
        with self.assertRaises(BufferTooLarge):
            b.commit(4)
        # Reservation should have been cleared; committing again without reserve should error.
        with self.assertRaises(NoOutstandingReserve):
            b.commit(0)


class TestSegmentedBytesBufferCoalesce(unittest.TestCase):
    def test_coalesce_noop_when_head_is_contiguous(self) -> None:
        b = SegmentedBytesBuffer()
        b.write(b'abcdef')
        mv = b.coalesce(3)
        self.assertEqual(mv.tobytes(), b'abc')
        self.assertEqual(len(b), 6)
        self.assertEqual(b''.join(bytes(mv) for mv in b.segments()), b'abcdef')

    def test_coalesce_makes_prefix_contiguous_across_segments(self) -> None:
        b = SegmentedBytesBuffer()
        b.write(b'ab')
        b.write(b'cdef')
        mv = b.coalesce(3)
        self.assertEqual(mv.tobytes(), b'abc')

        # Non-consuming.
        self.assertEqual(len(b), 6)
        self.assertEqual(b''.join(bytes(mv) for mv in b.segments()), b'abcdef')

        # Now peek must include at least 3 bytes contiguously.
        self.assertGreaterEqual(len(b.peek()), 3)
        self.assertEqual(b.peek()[:3].tobytes(), b'abc')

    def test_coalesce_spans_many_segments(self) -> None:
        b = SegmentedBytesBuffer()
        b.write(b'a')
        b.write(b'b')
        b.write(b'c')
        b.write(b'defgh')
        mv = b.coalesce(4)
        self.assertEqual(mv.tobytes(), b'abcd')
        self.assertEqual(b''.join(bytes(mv) for mv in b.segments()), b'abcdefgh')

    def test_coalesce_disallowed_with_outstanding_reserve(self) -> None:
        b = SegmentedBytesBuffer()
        b.write(b'abc')
        _ = b.reserve(4)
        with self.assertRaises(RuntimeError):
            b.coalesce(2)

    def test_coalesce_bounds(self) -> None:
        b = SegmentedBytesBuffer()
        b.write(b'abc')
        with self.assertRaises(ValueError):
            b.coalesce(4)
        with self.assertRaises(ValueError):
            b.coalesce(-1)
        self.assertEqual(b.coalesce(0).tobytes(), b'')

    def test_coalesce(self) -> None:
        """Test that coalesce combines multiple segments into one."""

        b = SegmentedBytesBuffer()
        b.write(b'abc')
        b.write(b'def')
        b.write(b'ghi')

        # Should have 3 segments.
        self.assertEqual(len(b.segments()), 3)
        self.assertEqual(len(b), 9)

        b.coalesce(len(b))

        # After coalescing, should have 1 segment with same total length.
        self.assertEqual(len(b.segments()), 1)
        self.assertEqual(len(b), 9)
        self.assertEqual(bytes(b.peek()), b'abcdefghi')

        # Searches should still work correctly.
        self.assertEqual(b.find(b'def'), 3)
        self.assertEqual(b.rfind(b'ghi'), 6)

    def test_coalesce_empty_or_single_segment(self) -> None:
        """Test that coalesce is a no-op for empty or single-segment buffers."""

        # Empty buffer.
        b = SegmentedBytesBuffer()
        b.coalesce(len(b))
        self.assertEqual(len(b), 0)

        # Single segment.
        b = SegmentedBytesBuffer()
        b.write(b'abc')
        b.coalesce(len(b))
        self.assertEqual(len(b.segments()), 1)
        self.assertEqual(bytes(b.peek()), b'abc')

    def test_coalesce_with_head_offset(self) -> None:
        """Test that coalesce respects head_off and only keeps readable data."""

        b = SegmentedBytesBuffer()
        b.write(b'discardABC')
        b.write(b'DEF')
        b.advance(7)  # Skip 'discard', leaving 'ABCDEF'

        self.assertEqual(len(b), 6)

        b.coalesce(len(b))

        # Should have coalesced only the readable portion.
        self.assertEqual(len(b.segments()), 1)
        self.assertEqual(len(b), 6)
        self.assertEqual(bytes(b.peek()), b'ABCDEF')
        self.assertEqual(b._head_off, 0)  # noqa
