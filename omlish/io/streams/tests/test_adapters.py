# ruff: noqa: PT009 PT027
# @omlish-lite
import io
import unittest

from ..adapters import BytesIoByteStreamBuffer
from ..adapters import ByteStreamBufferReaderAdapter
from ..adapters import ByteStreamBufferWriterAdapter
from ..errors import NeedMoreDataByteStreamBufferError
from ..segmented import SegmentedByteStreamBuffer


class TestIoAdapters(unittest.TestCase):
    def test_bytesbuffer_reader_adapter_raise(self) -> None:
        b = SegmentedByteStreamBuffer()
        a = ByteStreamBufferReaderAdapter(b, policy='raise')

        with self.assertRaises(NeedMoreDataByteStreamBufferError):
            a.read(1)

        b.write(b'xy')
        self.assertEqual(a.read(1), b'x')
        self.assertEqual(a.read(1), b'y')

        with self.assertRaises(NeedMoreDataByteStreamBufferError):
            a.read(1)

    def test_bytesbuffer_reader_adapter_return_partial(self) -> None:
        b = SegmentedByteStreamBuffer()
        a = ByteStreamBufferReaderAdapter(b, policy='return_partial')

        self.assertEqual(a.read(3), b'')  # nothing available

        b.write(b'hi')
        self.assertEqual(a.read(3), b'hi')  # partial
        self.assertEqual(a.read(1), b'')  # empty now

    def test_bytesbuffer_reader_adapter_block(self) -> None:
        b = SegmentedByteStreamBuffer()

        chunks = [b'ab', b'cd', b'']  # last indicates EOF
        it = iter(chunks)

        def fill() -> bool:
            try:
                c = next(it)
            except StopIteration:
                return False
            if not c:
                return False
            b.write(c)
            return True

        a = ByteStreamBufferReaderAdapter(b, policy='block', fill=fill)

        self.assertEqual(a.read(3), b'abc')
        self.assertEqual(a.read(2), b'd')  # EOF, partial remaining
        self.assertEqual(a.read(1), b'')   # EOF, nothing left

    def test_bytesbuffer_reader_adapter_readall_block(self) -> None:
        b = SegmentedByteStreamBuffer()
        chunks = [b'aa', b'bb', b'cc', b'']
        it = iter(chunks)

        def fill() -> bool:
            try:
                c = next(it)
            except StopIteration:
                return False
            if not c:
                return False
            b.write(c)
            return True

        a = ByteStreamBufferReaderAdapter(b, policy='block', fill=fill)
        self.assertEqual(a.readall(), b'aabbcc')
        self.assertEqual(a.readall(), b'')

    def test_bytesbuffer_writer_adapter_bytes_and_view(self) -> None:
        out = io.BytesIO()
        w = ByteStreamBufferWriterAdapter(out)

        w.write(b'abc')

        b = SegmentedByteStreamBuffer()
        b.write(b'de')
        b.write(b'f')
        v = b.split_to(3)  # view over b"def"
        w.write(v)

        self.assertEqual(out.getvalue(), b'abcdef')

    def test_bytesiobytesbuffer_basic(self) -> None:
        b = BytesIoByteStreamBuffer()
        self.assertEqual(len(b), 0)
        self.assertEqual(bytes(b.peek()), b'')

        b.write(b'hello')
        self.assertEqual(len(b), 5)
        self.assertEqual(bytes(b.peek()), b'hello')

        v = b.split_to(2)
        # SegmentedByteStreamBufferView supports t_bytes in our earlier impl; accept either name here.
        self.assertEqual(v.tobytes(), b'he')

        self.assertEqual(bytes(b.peek()), b'llo')
        b.advance(2)
        self.assertEqual(bytes(b.peek()), b'o')

    def test_bytesiobytesbuffer_getbuffer_pinning_raises(self) -> None:
        b = BytesIoByteStreamBuffer()
        b.write(b'x' * 4)

        mv = b.peek()  # exported view pins BytesIO against resizing
        self.assertEqual(len(mv), 4)

        # Force a resize/grow; should raise BufferError due to pinned buffer.
        with self.assertRaises(BufferError):
            b.write(b'y' * 1024)

    def test_bytesiobytesbuffer_find_rfind(self) -> None:
        b = BytesIoByteStreamBuffer()
        b.write(b'01234567')

        # Basic find/rfind
        self.assertEqual(b.find(b'23'), 2)
        self.assertEqual(b.rfind(b'23'), 2)

        # Find with start/end bounds
        self.assertEqual(b.find(b'23', 3), -1)
        self.assertEqual(b.find(b'23', 0, 3), -1)
        self.assertEqual(b.find(b'45', 4, 7), 4)

        # Empty pattern edge case
        self.assertEqual(b.find(b''), 0)
        self.assertEqual(b.rfind(b''), len(b))

        # After advance
        b.advance(2)  # readable now "234567"
        self.assertEqual(b.find(b'23'), 0)
        self.assertEqual(b.find(b'67'), 4)
        self.assertEqual(b.rfind(b'67'), 4)
        self.assertEqual(b.rfind(b'23'), 0)

        # Not found
        self.assertEqual(b.find(b'99'), -1)
        self.assertEqual(b.rfind(b'99'), -1)

    def test_bytesiobytesbuffer_coalesce(self) -> None:
        b = BytesIoByteStreamBuffer()
        b.write(b'abcdef')

        # Coalesce prefix
        mv = b.coalesce(3)
        self.assertEqual(mv.tobytes(), b'abc')
        self.assertEqual(len(b), 6)  # non-consuming

        # Coalesce after advance
        b.advance(2)
        mv = b.coalesce(2)
        self.assertEqual(mv.tobytes(), b'cd')
        self.assertEqual(len(b), 4)

        # Coalesce all
        mv = b.coalesce(4)
        self.assertEqual(mv.tobytes(), b'cdef')

        # Empty coalesce
        mv = b.coalesce(0)
        self.assertEqual(len(mv), 0)

    def test_bytesiobytesbuffer_coalesce_errors(self) -> None:
        b = BytesIoByteStreamBuffer()
        b.write(b'abc')

        # Negative n
        with self.assertRaises(ValueError):
            b.coalesce(-1)

        # n too large
        with self.assertRaises(ValueError):
            b.coalesce(10)

    def test_bytesiobytesbuffer_reserve_commit(self) -> None:
        b = BytesIoByteStreamBuffer()
        mv = b.reserve(5)
        mv[:3] = b'xyz'
        b.commit(3)
        self.assertEqual(len(b), 3)
        self.assertEqual(b.peek().tobytes(), b'xyz')

        # Now test find/coalesce work correctly after reserve/commit
        self.assertEqual(b.find(b'yz'), 1)
        self.assertEqual(b.coalesce(2).tobytes(), b'xy')
