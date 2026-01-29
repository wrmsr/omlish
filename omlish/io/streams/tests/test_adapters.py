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

        # Force a resize/grow; should raise RuntimeError due to pinned buffer.
        with self.assertRaises(RuntimeError):
            b.write(b'y' * 1024)

        # Drop view to avoid leaking pinning into later tests.
        del mv
