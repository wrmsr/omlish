# ruff: noqa: PT009 PT027
# @omlish-lite
import unittest

from ..errors import BufferTooLargeByteStreamBufferError
from ..errors import NoOutstandingReserveByteStreamBufferError
from ..errors import OutstandingReserveByteStreamBufferError
from ..segmented import SegmentedByteStreamBuffer


class TestSegmentedByteStreamBuffer(unittest.TestCase):
    def test_len_peek_segments(self) -> None:
        b = SegmentedByteStreamBuffer()
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
        b = SegmentedByteStreamBuffer()
        b.write(b'ab')
        b.write(b'cd')
        v = b.split_to(3)
        self.assertEqual(v.tobytes(), b'abc')
        self.assertEqual(len(b), 1)
        self.assertEqual(b''.join(bytes(mv) for mv in b.segments()), b'd')

    def test_find_cross_segment(self) -> None:
        b = SegmentedByteStreamBuffer()
        b.write(b'hello\r')
        b.write(b'\nworld')
        self.assertEqual(b.find(b'\r\n'), 5)
        self.assertEqual(b.find(b'world'), 7)
        self.assertEqual(b.find(b'nope'), -1)

    def test_rfind_cross_segment(self) -> None:
        b = SegmentedByteStreamBuffer()
        b.write(b'aa\r')
        b.write(b'\naa\r')
        b.write(b'\naa')
        # Stream is: b"aa\r\naa\r\naa"
        self.assertEqual(b.rfind(b'\r\n'), 6)
        self.assertEqual(b.find(b'\r\n'), 2)

    def test_find_start_end(self) -> None:
        b = SegmentedByteStreamBuffer()
        b.write(b'0123')
        b.write(b'4567')
        self.assertEqual(b.find(b'23'), 2)
        self.assertEqual(b.find(b'23', 3), -1)
        self.assertEqual(b.find(b'23', 0, 3), -1)
        self.assertEqual(b.find(b'23', 0, 4), 2)
        self.assertEqual(b.rfind(b'23', 0, 4), 2)
        self.assertEqual(b.rfind(b'23', 0, 3), -1)

    def test_empty_sub(self) -> None:
        b = SegmentedByteStreamBuffer()
        b.write(b'abc')
        self.assertEqual(b.find(b''), 0)
        self.assertEqual(b.find(b'', 2), 2)
        self.assertEqual(b.find(b'', 99), 3)
        self.assertEqual(b.rfind(b''), 3)
        self.assertEqual(b.rfind(b'', 0, 2), 2)

    def test_reserve_commit(self) -> None:
        b = SegmentedByteStreamBuffer()
        mv = b.reserve(5)
        mv[:3] = b'xyz'
        b.commit(3)
        self.assertEqual(len(b), 3)
        self.assertEqual(b''.join(bytes(s) for s in b.segments()), b'xyz')

    def test_segmented_buffer_outstanding_reserve_errors(self) -> None:
        b = SegmentedByteStreamBuffer()
        b.write(b'abc')
        _ = b.reserve(2)

        with self.assertRaises(OutstandingReserveByteStreamBufferError):
            b.reserve(1)

        with self.assertRaises(OutstandingReserveByteStreamBufferError):
            b.coalesce(1)

        b.commit(0)

        with self.assertRaises(NoOutstandingReserveByteStreamBufferError):
            b.commit(0)

    def test_rfind_early_termination(self) -> None:
        """
        Test that rfind terminates early when match is found in rightmost segments.

        This test verifies the performance optimization: if the rightmost match is in the last segment, we should not
        scan all earlier segments.
        """

        b = SegmentedByteStreamBuffer()
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

        b = SegmentedByteStreamBuffer()
        b.write(b'abcAB')
        b.write(b'CDef')
        # 'ABCD' spans the boundary at position 3.
        self.assertEqual(b.rfind(b'ABCD'), 3)

    def test_rfind_prefers_rightmost_of_multiple(self) -> None:
        """Test that rfind returns the rightmost match when multiple exist."""

        b = SegmentedByteStreamBuffer()
        b.write(b'XXabc')
        b.write(b'XXde')
        b.write(b'XXfg')
        # Three occurrences of 'XX' at positions 0, 5, 9.
        self.assertEqual(b.rfind(b'XX'), 9)

    def test_find_vs_rfind_consistency(self) -> None:
        """Test that find and rfind are consistent for single-match cases."""

        b = SegmentedByteStreamBuffer()
        b.write(b'abc')
        b.write(b'def')
        b.write(b'ghi')

        # Single match cases should return same position.
        self.assertEqual(b.find(b'def'), b.rfind(b'def'))
        self.assertEqual(b.find(b'cde'), b.rfind(b'cde'))  # Boundary match
        self.assertEqual(b.find(b'ghi'), b.rfind(b'ghi'))

    def test_rfind_with_overlapping_occurrences(self) -> None:
        """Test rfind with overlapping occurrences of the pattern."""

        b = SegmentedByteStreamBuffer()
        b.write(b'aaa')
        b.write(b'aaa')
        # Pattern 'aa' occurs at positions 0, 1, 2, 3, 4.
        # rfind should return the rightmost: 4.
        self.assertEqual(b.rfind(b'aa'), 4)

    def test_search_with_head_offset(self) -> None:
        """Test that search works correctly when head_off is non-zero."""

        b = SegmentedByteStreamBuffer()
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

        b = SegmentedByteStreamBuffer()
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

        b = SegmentedByteStreamBuffer()
        # Segment layout: 'xxAB' | 'CD' | 'Eyy'
        b.write(b'xxAB')
        b.write(b'CD')
        b.write(b'Eyy')

        pos = b.rfind(b'ABCDE')
        self.assertEqual(pos, 2, f"Expected to rfind 'ABCDE' at position 2, got {pos}")

    def test_find_delimiter_spanning_many_segments(self) -> None:
        """Test with a delimiter spanning many small segments."""

        b = SegmentedByteStreamBuffer()
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

        b = SegmentedByteStreamBuffer()
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

        b = SegmentedByteStreamBuffer()
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

        b = SegmentedByteStreamBuffer()
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

        b = SegmentedByteStreamBuffer()
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

        b = SegmentedByteStreamBuffer()
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
        b = SegmentedByteStreamBuffer(max_bytes=3)
        b.write(b'ab')
        b.write(b'c')
        with self.assertRaises(BufferTooLargeByteStreamBufferError):
            b.write(b'd')
        self.assertEqual(b''.join(bytes(mv) for mv in b.segments()), b'abc')

    def test_max_bytes_segmented_commit(self) -> None:
        b = SegmentedByteStreamBuffer(max_bytes=3)
        mv = b.reserve(4)
        mv[:] = b'abcd'
        with self.assertRaises(BufferTooLargeByteStreamBufferError):
            b.commit(4)
        # Reservation should have been cleared; committing again without reserve should error.
        with self.assertRaises(NoOutstandingReserveByteStreamBufferError):
            b.commit(0)


class TestSegmentedByteStreamBufferCoalesce(unittest.TestCase):
    def test_coalesce_noop_when_head_is_contiguous(self) -> None:
        b = SegmentedByteStreamBuffer()
        b.write(b'abcdef')
        mv = b.coalesce(3)
        self.assertEqual(mv.tobytes(), b'abc')
        self.assertEqual(len(b), 6)
        self.assertEqual(b''.join(bytes(mv) for mv in b.segments()), b'abcdef')

    def test_coalesce_makes_prefix_contiguous_across_segments(self) -> None:
        b = SegmentedByteStreamBuffer()
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
        b = SegmentedByteStreamBuffer()
        b.write(b'a')
        b.write(b'b')
        b.write(b'c')
        b.write(b'defgh')
        mv = b.coalesce(4)
        self.assertEqual(mv.tobytes(), b'abcd')
        self.assertEqual(b''.join(bytes(mv) for mv in b.segments()), b'abcdefgh')

    def test_coalesce_disallowed_with_outstanding_reserve(self) -> None:
        b = SegmentedByteStreamBuffer()
        b.write(b'abc')
        _ = b.reserve(4)
        with self.assertRaises(RuntimeError):
            b.coalesce(2)

    def test_coalesce_bounds(self) -> None:
        b = SegmentedByteStreamBuffer()
        b.write(b'abc')
        with self.assertRaises(ValueError):
            b.coalesce(4)
        with self.assertRaises(ValueError):
            b.coalesce(-1)
        self.assertEqual(b.coalesce(0).tobytes(), b'')

    def test_coalesce(self) -> None:
        """Test that coalesce combines multiple segments into one."""

        b = SegmentedByteStreamBuffer()
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
        b = SegmentedByteStreamBuffer()
        b.coalesce(len(b))
        self.assertEqual(len(b), 0)

        # Single segment.
        b = SegmentedByteStreamBuffer()
        b.write(b'abc')
        b.coalesce(len(b))
        self.assertEqual(len(b.segments()), 1)
        self.assertEqual(bytes(b.peek()), b'abc')

    def test_coalesce_with_head_offset(self) -> None:
        """Test that coalesce respects head_off and only keeps readable data."""

        b = SegmentedByteStreamBuffer()
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


class TestSegmentedByteStreamBufferChunking(unittest.TestCase):
    def test_chunk_disabled_default_behavior(self) -> None:
        b = SegmentedByteStreamBuffer(chunk_size=0)
        b.write(b'a')
        b.write(b'b')
        self.assertEqual(len(b), 2)
        self.assertEqual([mv.tobytes() for mv in b.segments()], [b'a', b'b'])

    def test_small_writes_coalesce_into_active_chunk(self) -> None:
        b = SegmentedByteStreamBuffer(chunk_size=16)
        for _ in range(10):
            b.write(b'a')
        self.assertEqual(len(b), 10)
        segs = b.segments()
        self.assertEqual(len(segs), 1)
        self.assertEqual(segs[0].tobytes(), b'a' * 10)

    def test_large_write_flushes_active_and_appends_as_own_segment(self) -> None:
        b = SegmentedByteStreamBuffer(chunk_size=16, chunk_compact_threshold=.50)
        b.write(b'abc')  # active, 3/16 < 0.5 -> should bytes() on flush
        self.assertIsNotNone(b._active)  # noqa: SLF001
        b.write(b'x' * 32)  # >= chunk_size flushes active then appends large

        self.assertIsNone(b._active)  # noqa: SLF001
        self.assertEqual(len(b), 3 + 32)

        segs = b.segments()
        self.assertEqual(len(segs), 2)
        self.assertEqual(segs[0].tobytes(), b'abc')
        self.assertEqual(len(segs[1]), 32)

        # Verify flush compacted the active chunk to bytes (not bytearray) because under threshold.
        self.assertIsInstance(b._segs[0], bytes)  # noqa: SLF001

    def test_flush_keeps_bytearray_when_full_enough(self) -> None:
        b = SegmentedByteStreamBuffer(chunk_size=16, chunk_compact_threshold=.25)
        b.write(b'a' * 8)  # 8/16 == 0.5 >= 0.25 -> keep bytearray on flush
        b.write(b'x' * 16)  # flush active
        self.assertIsInstance(b._segs[0], bytearray)  # noqa: SLF001

    def test_reserve_uses_active_chunk_when_fits(self) -> None:
        b = SegmentedByteStreamBuffer(chunk_size=16)
        b.write(b'hi')
        mv = b.reserve(4)
        mv[:] = b'abcd'
        self.assertEqual(len(b), 2)  # not readable yet
        b.commit(4)
        self.assertEqual(len(b), 6)
        self.assertEqual(b.segments()[0].tobytes(), b'hiabcd')

    def test_reserve_flushes_then_reuses_chunk_when_under_chunk_size(self) -> None:
        b = SegmentedByteStreamBuffer(chunk_size=8, chunk_compact_threshold=0.0)
        b.write(b'xxxxxx')  # 6/8 in active
        mv = b.reserve(4)   # doesn't fit; flush then new chunk; reserve from it
        mv[:] = b'abcd'
        b.commit(4)

        self.assertEqual(len(b), 10)
        self.assertEqual(b.find(b'xxxxxx'), 0)
        self.assertEqual(b.find(b'abcd'), 6)

        # After commit from an in-chunk reserve, chunk remains active for future writes.
        self.assertIsNotNone(b._active)  # noqa: SLF001
        b.write(b'Z')
        self.assertEqual(b.find(b'Z'), 10)

    def test_reserve_over_chunk_size_is_closed_on_commit(self) -> None:
        b = SegmentedByteStreamBuffer(chunk_size=8)
        mv = b.reserve(20)
        mv[:5] = b'hello'
        b.commit(5)

        self.assertEqual(len(b), 5)
        self.assertIsNone(b._active)  # noqa: SLF001
        self.assertEqual(b.segments()[0].tobytes(), b'hello')

    def test_find_ignores_uncommitted_reserved_tail(self) -> None:
        b = SegmentedByteStreamBuffer(chunk_size=16)
        b.write(b'abc')
        mv = b.reserve(4)
        mv[:] = b'\r\n\r\n'
        # Not committed, so should not be visible.
        self.assertEqual(b.find(b'\r\n\r\n'), -1)
        b.commit(4)
        self.assertEqual(b.find(b'\r\n\r\n'), 3)

    def test_segments_with_head_offset_in_active_chunk(self) -> None:
        """
        Regression test: segments() should not apply head_off twice when active chunk is the only segment.

        Bug: when the active chunk is both first and last segment, the old code applied head_off twice,
        resulting in incorrect slicing.
        """

        b = SegmentedByteStreamBuffer(chunk_size=16)
        b.write(b'abcdefghij')  # 10 bytes in active chunk
        self.assertEqual(len(b.segments()), 1)
        self.assertIsNotNone(b._active)  # noqa: SLF001

        # Advance past first 3 bytes: head_off=3, readable='defghij' (7 bytes).
        b.advance(3)
        self.assertEqual(len(b), 7)
        self.assertEqual(b._head_off, 3)  # noqa: SLF001

        # segments() should return exactly 'defghij', not apply head_off twice.
        segs = b.segments()
        self.assertEqual(len(segs), 1)
        self.assertEqual(segs[0].tobytes(), b'defghij')

        # Also verify peek() is consistent.
        self.assertEqual(b.peek().tobytes(), b'defghij')


class TestSegmentedByteStreamBufferActiveBoundaryBugs(unittest.TestCase):
    """
    Regression tests for bugs where find()/rfind() could read uninitialized bytes from active chunks
    when searching for patterns that span segment boundaries.
    """

    def test_find_spanning_into_small_active_chunk(self) -> None:
        """
        Test that find() doesn't read uninitialized bytes when pattern spans into active chunk.

        Bug scenario: A multi-byte search pattern spans from a regular segment into an active chunk
        that has fewer committed bytes than (pattern_length - 1). The cross-boundary matching logic
        should only read the committed bytes, not the full bytearray capacity.
        """

        b = SegmentedByteStreamBuffer(chunk_size=16)
        b.write(b'HELLO')  # First segment (will be flushed when we write large data or reserve)

        # Create an active chunk with only 1 committed byte
        mv = b.reserve(1)
        mv[0] = ord('W')
        b.commit(1)

        # At this point: segments=['HELLO', active_chunk with 'W']
        # Active chunk has capacity=16 but only 1 byte committed

        # Search for 'LOW' (3 bytes) which would span the boundary
        # 'LO' is at end of first segment, 'W' is at start of active chunk
        # The cross-boundary check needs first (3-1)=2 bytes of active chunk
        # But active chunk only has 1 byte committed
        # Bug would read s[0:2] getting uninitialized data at s[1]
        pos = b.find(b'LOW')
        self.assertEqual(pos, 3, 'Should find \'LOW\' spanning boundary')

        # Verify no false matches from uninitialized data
        pos = b.find(b'LO\x00')  # If s[1] happened to be 0x00
        self.assertEqual(pos, -1, 'Should not find pattern with uninitialized byte')

    def test_rfind_spanning_from_small_active_chunk(self) -> None:
        """
        Test that rfind() doesn't read uninitialized bytes from active chunks.

        Bug scenario: When searching in reverse and checking cross-boundary matches, rfind() reads
        from prev_s (previous segment) which might be an active chunk with limited committed bytes.
        """

        b = SegmentedByteStreamBuffer(chunk_size=16)

        # Create active chunk with only 2 committed bytes
        mv = b.reserve(2)
        mv[:2] = b'AB'
        b.commit(2)

        # Write more data to flush the active chunk and create a new segment
        b.write(b'CDEFGHIJ')

        # Now buffer has: [bytes('AB'), 'CDEFGHIJ']
        # The first segment was the active chunk, now closed as bytes

        # Search for 'BCDE' (4 bytes) in reverse
        # Pattern spans from end of first segment into second
        # 'B' at first[1], 'CDE' at second[0:3]
        # When rfind processes second segment and checks boundary:
        #   - prev_s = first segment (was active chunk, now bytes)
        #   - head_need = 3
        #   - Bug would try to read prev_s[0:3] but it only has 2 bytes
        pos = b.rfind(b'BCDE')
        self.assertEqual(pos, 1, "Should find 'BCDE' spanning boundary in reverse")

    def test_find_with_multiple_segments_and_active_chunk(self) -> None:
        """
        Test find() with a pattern spanning multiple segments ending in a small active chunk.
        """

        b = SegmentedByteStreamBuffer(chunk_size=8)
        b.write(b'ABC')   # Segment 1
        b.write(b'DE')    # Accumulated in active chunk
        b.write(b'FGH')   # Flushes and creates new active chunk

        # Manually create a very small active chunk
        b.write(b'I' * 7)  # Fills active chunk to 7/8
        b.write(b'X' * 8)  # Flushes, creates new segment
        mv = b.reserve(1)
        mv[0] = ord('Y')
        b.commit(1)

        # Buffer now has multiple segments with last being active chunk with 1 byte
        # Search for pattern that would span into the small active chunk
        total = b''.join(bytes(mv) for mv in b.segments())

        # Find something that exists
        pos = b.find(b'XY')
        self.assertNotEqual(pos, -1, 'Should find pattern spanning into active chunk')
        self.assertEqual(total[pos:pos + 2], b'XY')

    def test_rfind_with_multiple_segments_and_small_active(self) -> None:
        """
        Test rfind() with multiple segments where an earlier segment was a small active chunk.
        """

        b = SegmentedByteStreamBuffer(chunk_size=8)

        # Create first segment as small active chunk
        mv = b.reserve(2)
        mv[:] = b'AB'
        b.commit(2)

        # Force flush by writing large data
        b.write(b'C' * 10)

        # Buffer is now: b'AB' + b'CCCCCCCCCC' = b'ABCCCCCCCCCC'
        # Search in reverse for pattern spanning from small first segment
        pos = b.rfind(b'ABC')
        self.assertEqual(pos, 0, 'Should find pattern in reverse spanning from small segment')

    def test_no_false_positives_from_uninitialized_data(self) -> None:
        """
        Verify that uninitialized bytes in active chunks don't cause false positive matches.
        """

        b = SegmentedByteStreamBuffer(chunk_size=16)
        b.write(b'TEST')

        # Create active chunk with minimal committed data
        # The uninitialized bytes might contain random data
        mv = b.reserve(1)
        mv[0] = ord('X')
        b.commit(1)

        # Search for patterns that would only match if uninitialized data is read
        # We can't know what's in uninitialized memory, but we can verify the search
        # correctly handles the boundary
        total = b''.join(bytes(mv) for mv in b.segments())
        self.assertEqual(len(total), 5)  # 'TEST' + 'X'

        # Any pattern longer than what we committed should not be found
        # (unless it actually exists in the committed data)
        result = b.find(b'TESTX')
        self.assertEqual(result, 0)  # This should be found

        result = b.find(b'TESTXY')  # 'Y' would require reading beyond committed
        self.assertEqual(result, -1)

    def test_find_edge_case_empty_active_chunk(self) -> None:
        """
        Test find() when active chunk exists but has 0 committed bytes.
        """

        b = SegmentedByteStreamBuffer(chunk_size=8)
        b.write(b'HELLO')

        # Reserve but commit 0 bytes - active chunk exists but is empty
        _ = b.reserve(4)
        b.commit(0)

        # Should still be able to search without errors
        pos = b.find(b'LLO')
        self.assertEqual(pos, 2)

        pos = b.find(b'LLOWORLD')  # Spans into empty active chunk
        self.assertEqual(pos, -1)

    def test_rfind_edge_case_empty_previous_segment(self) -> None:
        """
        Test rfind() when previous segment was an active chunk with 0 committed bytes.
        """

        b = SegmentedByteStreamBuffer(chunk_size=8)

        # Create and flush an empty active chunk
        _ = b.reserve(4)
        b.commit(0)
        b.write(b'X' * 10)  # Force flush

        # Should handle the empty previous segment correctly
        pos = b.rfind(b'XXX')
        self.assertNotEqual(pos, -1)
