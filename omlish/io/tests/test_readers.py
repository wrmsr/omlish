# ruff: noqa: PT009 PT027
# @omlish-lite
import io
import unittest

from ..readers import FileLikeBufferedBytesReader
from ..readers import FileLikeRawBytesReader


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
