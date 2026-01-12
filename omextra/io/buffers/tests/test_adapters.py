# ruff: noqa: PT009 PT027
# @omlish-lite
import io
import unittest

from ..adapters import BytesBufferReaderAdapter
from ..adapters import BytesBufferWriterAdapter
from ..adapters import BytesIoBytesBuffer
from ..adapters import FileLikeBufferedBytesReader
from ..adapters import FileLikeRawBytesReader
from ..errors import NeedMoreData
from ..segmented import SegmentedBytesBuffer


class TestIoAdapters(unittest.TestCase):
    def test_filelike_raw_bytes_reader_prefers_read1(self) -> None:
        bio = io.BytesIO(b'abcdef')
        br = io.BufferedReader(bio, buffer_size=2)
        r = FileLikeRawBytesReader(br)

        self.assertEqual(r.read1(1), b'a')
        self.assertEqual(r.read1(2), b'bc')
        self.assertEqual(r.read1(10), b'def')
        self.assertEqual(r.read1(1), b'')

    def test_filelike_buffered_bytes_reader_readall_fallback(self) -> None:
        bio = io.BytesIO(b'abcdef')
        r = FileLikeBufferedBytesReader(bio)

        self.assertEqual(r.read(2), b'ab')
        self.assertEqual(r.readall(), b'cdef')
        self.assertEqual(r.readall(), b'')

    def test_bytesbuffer_reader_adapter_raise(self) -> None:
        b = SegmentedBytesBuffer()
        a = BytesBufferReaderAdapter(b, policy='raise')

        with self.assertRaises(NeedMoreData):
            a.read(1)

        b.write(b'xy')
        self.assertEqual(a.read(1), b'x')
        self.assertEqual(a.read(1), b'y')

        with self.assertRaises(NeedMoreData):
            a.read(1)

    def test_bytesbuffer_reader_adapter_return_partial(self) -> None:
        b = SegmentedBytesBuffer()
        a = BytesBufferReaderAdapter(b, policy='return_partial')

        self.assertEqual(a.read(3), b'')  # nothing available

        b.write(b'hi')
        self.assertEqual(a.read(3), b'hi')  # partial
        self.assertEqual(a.read(1), b'')  # empty now

    def test_bytesbuffer_reader_adapter_block(self) -> None:
        b = SegmentedBytesBuffer()

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

        a = BytesBufferReaderAdapter(b, policy='block', fill=fill)

        self.assertEqual(a.read(3), b'abc')
        self.assertEqual(a.read(2), b'd')  # EOF, partial remaining
        self.assertEqual(a.read(1), b'')   # EOF, nothing left

    def test_bytesbuffer_reader_adapter_readall_block(self) -> None:
        b = SegmentedBytesBuffer()
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

        a = BytesBufferReaderAdapter(b, policy='block', fill=fill)
        self.assertEqual(a.readall(), b'aabbcc')
        self.assertEqual(a.readall(), b'')

    def test_bytesbuffer_writer_adapter_bytes_and_view(self) -> None:
        out = io.BytesIO()
        w = BytesBufferWriterAdapter(out)

        w.write(b'abc')

        b = SegmentedBytesBuffer()
        b.write(b'de')
        b.write(b'f')
        v = b.split_to(3)  # view over b"def"
        w.write(v)

        self.assertEqual(out.getvalue(), b'abcdef')

    def test_bytesiobytesbuffer_basic(self) -> None:
        b = BytesIoBytesBuffer()
        self.assertEqual(len(b), 0)
        self.assertEqual(bytes(b.peek()), b'')

        b.write(b'hello')
        self.assertEqual(len(b), 5)
        self.assertEqual(bytes(b.peek()), b'hello')

        v = b.split_to(2)
        # SegmentedBytesView supports t_bytes in our earlier impl; accept either name here.
        self.assertEqual(v.tobytes(), b'he')

        self.assertEqual(bytes(b.peek()), b'llo')
        b.advance(2)
        self.assertEqual(bytes(b.peek()), b'o')

    def test_bytesiobytesbuffer_getbuffer_pinning_raises(self) -> None:
        b = BytesIoBytesBuffer()
        b.write(b'x' * 4)

        mv = b.peek()  # exported view pins BytesIO against resizing
        self.assertEqual(len(mv), 4)

        # Force a resize/grow; should raise RuntimeError due to pinned buffer.
        with self.assertRaises(RuntimeError):
            b.write(b'y' * 1024)

        # Drop view to avoid leaking pinning into later tests.
        del mv
