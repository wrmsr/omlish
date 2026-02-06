# ruff: noqa: PT009 PT027
# @omlish-lite
import unittest

from ..direct import DirectByteStreamBuffer
from ..framing import LongestMatchDelimiterByteStreamFrameDecoder


class TestDirectByteStreamBuffer(unittest.TestCase):
    def test_construction_from_bytes(self) -> None:
        data = b'hello world'
        buf = DirectByteStreamBuffer(data)
        self.assertEqual(len(buf), 11)
        self.assertEqual(bytes(buf.peek()), b'hello world')
        self.assertEqual(buf.find(b'l'), 2)

    def test_construction_from_bytearray(self) -> None:
        data = bytearray(b'hello world')
        buf = DirectByteStreamBuffer(data)
        self.assertEqual(len(buf), 11)
        self.assertEqual(bytes(buf.peek()), b'hello world')
        self.assertEqual(buf.find(b'l'), 2)

    def test_construction_from_memoryview(self) -> None:
        data = memoryview(b'hello world')
        buf = DirectByteStreamBuffer(data)
        self.assertEqual(len(buf), 11)
        self.assertEqual(bytes(buf.peek()), b'hello world')
        self.assertEqual(buf.find(b'l'), 2)

    def test_empty_buffer(self) -> None:
        buf = DirectByteStreamBuffer(b'')
        self.assertEqual(len(buf), 0)
        self.assertEqual(bytes(buf.peek()), b'')
        self.assertEqual(buf.segments(), ())

    def test_peek_and_segments(self) -> None:
        buf = DirectByteStreamBuffer(b'test data')
        mv = buf.peek()
        self.assertEqual(bytes(mv), b'test data')

        segs = buf.segments()
        self.assertEqual(len(segs), 1)
        self.assertEqual(bytes(segs[0]), b'test data')

    def test_advance(self) -> None:
        buf = DirectByteStreamBuffer(b'hello world')
        buf.advance(6)
        self.assertEqual(len(buf), 5)
        self.assertEqual(bytes(buf.peek()), b'world')

        buf.advance(5)
        self.assertEqual(len(buf), 0)
        self.assertEqual(bytes(buf.peek()), b'')

    def test_advance_validation(self) -> None:
        buf = DirectByteStreamBuffer(b'test')
        with self.assertRaises(ValueError):
            buf.advance(-1)
        with self.assertRaises(ValueError):
            buf.advance(5)

    def test_split_to(self) -> None:
        buf = DirectByteStreamBuffer(b'hello world')
        view = buf.split_to(5)
        self.assertEqual(view.tobytes(), b'hello')
        self.assertEqual(len(buf), 6)
        self.assertEqual(bytes(buf.peek()), b' world')

    def test_split_to_zero(self) -> None:
        buf = DirectByteStreamBuffer(b'test')
        view = buf.split_to(0)
        self.assertEqual(view.tobytes(), b'')
        self.assertEqual(len(buf), 4)

    def test_split_to_all(self) -> None:
        buf = DirectByteStreamBuffer(b'test')
        view = buf.split_to(4)
        self.assertEqual(view.tobytes(), b'test')
        self.assertEqual(len(buf), 0)

    def test_split_to_validation(self) -> None:
        buf = DirectByteStreamBuffer(b'test')
        with self.assertRaises(ValueError):
            buf.split_to(-1)
        with self.assertRaises(ValueError):
            buf.split_to(5)

    def test_find_basic(self) -> None:
        buf = DirectByteStreamBuffer(b'hello world')
        self.assertEqual(buf.find(b'world'), 6)
        self.assertEqual(buf.find(b'hello'), 0)
        self.assertEqual(buf.find(b'o'), 4)
        self.assertEqual(buf.find(b'missing'), -1)

    def test_find_empty_needle(self) -> None:
        buf = DirectByteStreamBuffer(b'test')
        self.assertEqual(buf.find(b''), 0)
        self.assertEqual(buf.find(b'', 2), 2)

    def test_find_with_start_end(self) -> None:
        buf = DirectByteStreamBuffer(b'abcabcabc')
        self.assertEqual(buf.find(b'abc'), 0)
        self.assertEqual(buf.find(b'abc', 1), 3)
        self.assertEqual(buf.find(b'abc', 4), 6)
        self.assertEqual(buf.find(b'abc', 0, 2), -1)
        self.assertEqual(buf.find(b'abc', 0, 3), 0)

    def test_find_after_advance(self) -> None:
        buf = DirectByteStreamBuffer(b'hello world')
        buf.advance(6)
        self.assertEqual(buf.find(b'world'), 0)
        self.assertEqual(buf.find(b'hello'), -1)

    def test_rfind_basic(self) -> None:
        buf = DirectByteStreamBuffer(b'abcabcabc')
        self.assertEqual(buf.rfind(b'abc'), 6)
        self.assertEqual(buf.rfind(b'b'), 7)
        self.assertEqual(buf.rfind(b'missing'), -1)

    def test_rfind_empty_needle(self) -> None:
        buf = DirectByteStreamBuffer(b'test')
        self.assertEqual(buf.rfind(b''), 4)
        self.assertEqual(buf.rfind(b'', 0, 2), 2)

    def test_rfind_with_start_end(self) -> None:
        buf = DirectByteStreamBuffer(b'abcabcabc')
        self.assertEqual(buf.rfind(b'abc'), 6)
        self.assertEqual(buf.rfind(b'abc', 0, 6), 3)
        self.assertEqual(buf.rfind(b'abc', 0, 3), 0)
        self.assertEqual(buf.rfind(b'abc', 7), -1)

    def test_coalesce(self) -> None:
        buf = DirectByteStreamBuffer(b'test data')
        mv = buf.coalesce(4)
        self.assertEqual(bytes(mv), b'test')
        # Non-consuming
        self.assertEqual(len(buf), 9)

    def test_coalesce_zero(self) -> None:
        buf = DirectByteStreamBuffer(b'test')
        mv = buf.coalesce(0)
        self.assertEqual(bytes(mv), b'')

    def test_coalesce_all(self) -> None:
        buf = DirectByteStreamBuffer(b'test')
        mv = buf.coalesce(4)
        self.assertEqual(bytes(mv), b'test')

    def test_coalesce_validation(self) -> None:
        buf = DirectByteStreamBuffer(b'test')
        with self.assertRaises(ValueError):
            buf.coalesce(-1)
        with self.assertRaises(ValueError):
            buf.coalesce(5)

    def test_segments_after_advance(self) -> None:
        buf = DirectByteStreamBuffer(b'hello world')
        buf.advance(6)
        segs = buf.segments()
        self.assertEqual(len(segs), 1)
        self.assertEqual(bytes(segs[0]), b'world')

    def test_segments_empty_after_full_advance(self) -> None:
        buf = DirectByteStreamBuffer(b'test')
        buf.advance(4)
        segs = buf.segments()
        self.assertEqual(segs, ())

    def test_integration_with_framer(self) -> None:
        """Test that DirectByteStreamBuffer works with LongestMatchDelimiterByteStreamFramer."""

        data = b'line1\r\nline2\r\nline3\r\n'
        buf = DirectByteStreamBuffer(data)

        framer = LongestMatchDelimiterByteStreamFrameDecoder([b'\r\n'])
        frames = framer.decode(buf, final=True)

        self.assertEqual(len(frames), 3)
        self.assertEqual(frames[0].tobytes(), b'line1')
        self.assertEqual(frames[1].tobytes(), b'line2')
        self.assertEqual(frames[2].tobytes(), b'line3')

    def test_integration_with_framer_partial(self) -> None:
        """Test framer with incomplete data."""

        data = b'line1\r\nline2\r\npartial'
        buf = DirectByteStreamBuffer(data)

        framer = LongestMatchDelimiterByteStreamFrameDecoder([b'\r\n'])
        frames = framer.decode(buf)

        self.assertEqual(len(frames), 2)
        self.assertEqual(frames[0].tobytes(), b'line1')
        self.assertEqual(frames[1].tobytes(), b'line2')
        # 'partial' remains in buffer
        self.assertEqual(bytes(buf.peek()), b'partial')

    def test_http_request_parsing(self) -> None:
        """Real-world example: parsing HTTP request headers."""

        data = b'GET /path HTTP/1.1\r\nHost: example.com\r\nUser-Agent: test\r\n\r\nbody data'
        buf = DirectByteStreamBuffer(data)

        # Find end of headers
        pos = buf.find(b'\r\n\r\n')
        self.assertNotEqual(pos, -1)

        # Extract headers
        headers_view = buf.split_to(pos)
        self.assertEqual(headers_view.tobytes(), b'GET /path HTTP/1.1\r\nHost: example.com\r\nUser-Agent: test')

        # Skip the \r\n\r\n
        buf.advance(4)

        # Remaining is body
        self.assertEqual(bytes(buf.peek()), b'body data')

    def test_multiple_operations(self) -> None:
        """Test chaining multiple operations."""

        buf = DirectByteStreamBuffer(b'abcdefghijklmnop')

        # Find 'def'
        pos = buf.find(b'def')
        self.assertEqual(pos, 3)

        # Split to 'def'
        view1 = buf.split_to(pos)
        self.assertEqual(view1.tobytes(), b'abc')

        # Advance past 'def'
        buf.advance(3)

        # Find 'jkl'
        pos = buf.find(b'jkl')
        self.assertEqual(pos, 3)

        # Remaining should be 'ghijklmnop'
        self.assertEqual(bytes(buf.peek()), b'ghijklmnop')

    def test_find_optimization_with_bytes(self) -> None:
        """Test that find() optimizes for bytes underlying data."""

        data = b'x' * 1000 + b'needle' + b'y' * 1000
        buf = DirectByteStreamBuffer(data)

        # Should find without materializing the entire buffer
        pos = buf.find(b'needle')
        self.assertEqual(pos, 1000)

    def test_find_optimization_with_bytearray(self) -> None:
        """Test that find() optimizes for bytearray underlying data."""

        data = bytearray(b'x' * 1000 + b'needle' + b'y' * 1000)
        buf = DirectByteStreamBuffer(data)

        # Should find without materializing the entire buffer
        pos = buf.find(b'needle')
        self.assertEqual(pos, 1000)

    def test_rfind_optimization_with_bytes(self) -> None:
        """Test that rfind() optimizes for bytes underlying data."""

        data = b'needle' + b'x' * 1000 + b'needle'
        buf = DirectByteStreamBuffer(data)

        # Should find rightmost without materializing twice
        pos = buf.rfind(b'needle')
        self.assertEqual(pos, 1006)

    def test_view_stability(self) -> None:
        """Test that split_to views remain valid after buffer operations."""

        buf = DirectByteStreamBuffer(b'part1-part2-part3')

        view1 = buf.split_to(5)
        buf.advance(1)  # skip '-'
        view2 = buf.split_to(5)
        buf.advance(1)  # skip '-'
        view3 = buf.split_to(5)

        # All views should remain valid
        self.assertEqual(view1.tobytes(), b'part1')
        self.assertEqual(view2.tobytes(), b'part2')
        self.assertEqual(view3.tobytes(), b'part3')

    def test_external_mutation_of_bytearray(self) -> None:
        """
        Test that external mutation of underlying bytearray is visible.

        This documents the behavior - we don't defensively copy, so external mutations are visible.
        """

        data = bytearray(b'mutable data')
        buf = DirectByteStreamBuffer(data)

        # Initial state
        self.assertEqual(bytes(buf.peek()), b'mutable data')

        # External mutation
        data[0] = ord('M')

        # Mutation is visible through buffer
        self.assertEqual(bytes(buf.peek()), b'Mutable data')

    def test_slice_of_memoryview(self) -> None:
        """Test that we can construct from a sliced memoryview."""

        data = b'prefix-ACTUAL_DATA-suffix'
        mv_slice = memoryview(data)[7:18]  # 'ACTUAL_DATA'
        buf = DirectByteStreamBuffer(mv_slice)

        self.assertEqual(len(buf), 11)
        self.assertEqual(bytes(buf.peek()), b'ACTUAL_DATA')
