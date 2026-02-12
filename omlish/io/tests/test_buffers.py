# ruff: noqa: PT009
# @omlish-lite
import asyncio
import unittest

from ..buffers import IncrementalWriteBuffer as Iwb
from ..buffers import ReadableListBuffer as Rlb


class TestReadableListBuffer(unittest.TestCase):
    def test_readable_list_buffer_basic(self):
        buf = Rlb()
        buf.feed(b'abcd')
        assert len(buf) == 4
        assert buf.read() == b'abcd'
        assert len(buf) == 0
        assert buf.read() == b''

        buf = Rlb()
        buf.feed(b'abcd')
        assert len(buf) == 4
        assert buf.read(3) == b'abc'
        assert len(buf) == 1
        assert buf.read(3) is None
        assert buf.read() == b'd'
        assert len(buf) == 0
        assert buf.read() == b''

    def test_readable_list_buffer_len_bookkeeping(self):
        buf = Rlb()
        buf.feed(b'abc')
        buf.feed(b'defg')
        assert len(buf) == 7
        assert buf.read(4) == b'abcd'
        assert len(buf) == 3
        assert buf.read() == b'efg'
        assert len(buf) == 0

    def test_buffered_reader_short_read_at_eof(self):
        class Raw:
            def __init__(self, parts):
                self._parts = list(parts)

            def read1(self, n=-1):
                if not self._parts:
                    return b''
                return self._parts.pop(0)

        buf = Rlb()
        r = buf.new_buffered_reader(Raw([b'abc', b'']), chunk_size=8)

        # Ask for more than available; should return the partial bytes at EOF, not b''.
        assert r.read(5) == b'abc'
        assert r.read(1) == b''


class TestIncrementalWriteBuffer(unittest.TestCase):
    def test_incremental_write_buffer_partial_write(self):
        data = b'abcdef'
        iw = Iwb(data, write_size=3)

        sent = bytearray()

        def fn(b):
            # First call: partial
            if not sent:
                sent.extend(b[:2])
                return 2
            # Subsequent calls: write all
            sent.extend(b)
            return len(b)

        assert iw.write(fn) == 2
        assert bytes(sent) == b'ab'
        assert iw._pos == 2  # noqa
        assert iw.rem == 4

        assert iw.write(fn) == 4
        assert bytes(sent) == b'abcdef'
        assert iw.rem == 0

    def test_incremental_write_buffer_short_write_is_sticky(self):
        data = b'abcdefghij'
        iw = Iwb(data, write_size=4)  # chunks: abcd, efgh, ij

        calls = []

        def fn(b):
            calls.append(bytes(b))
            return 1  # always short write

        assert iw.write(fn) == 1
        assert calls == [b'abcd']
        assert iw._pos == 1  # noqa
        assert iw.rem == len(data) - 1

        calls.clear()
        assert iw.write(fn) == 1
        # should continue with remainder of first chunk ('bcd'), not move to next chunk
        assert calls == [b'bcd']


class TestAsyncBufferedReader(unittest.IsolatedAsyncioTestCase):
    async def test_async_buffered_reader_short_read_at_eof(self):
        class Raw:
            def __init__(self, parts):
                self._parts = list(parts)

            async def read1(self, n=-1):
                await asyncio.sleep(0)
                if not self._parts:
                    return b''
                return self._parts.pop(0)

        buf = Rlb()
        r = buf.new_async_buffered_reader(Raw([b'abc', b'']), chunk_size=8)

        assert await r.read(5) == b'abc'
        assert await r.read(1) == b''
