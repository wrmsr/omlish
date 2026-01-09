# ruff: noqa: PT009
# @omlish-lite
import asyncio
import unittest

from ..buffers import DelimitingBuffer as Db
from ..buffers import IncrementalWriteBuffer as Iwb
from ..buffers import ReadableListBuffer as Rlb


class TestDelimitingBuffer(unittest.TestCase):
    def test_delimiting_buffer_old(self):
        def run(*bs, **kwargs):
            buf = Db(**kwargs)
            out: list = []
            for b in bs:
                out.append(cur := [])
                try:
                    for o in buf.feed(b):
                        cur.append(o)  # noqa
                except Db.Error as e:
                    cur.append(type(e))  # type: ignore
                    break
            return out

        assert run(b'line1\nline2\nline3\n') == [[b'line1', b'line2', b'line3']]
        assert run(b'12', b'345\n2', b'34\n') == [[], [b'12345'], [b'234']]
        assert run(b'line1\nline2\nline3\n', keep_ends=True) == [[b'line1\n', b'line2\n', b'line3\n']]
        assert run(b'line1 line2 line3', b'') == [[], [Db.Incomplete(b'line1 line2 line3')]]
        assert run(b'line1\nline2', b'line2\nline3\n') == [[b'line1'], [b'line2line2', b'line3']]
        assert run(b'line1\nline2', b'line2', b'line2\nline3\n') == [[b'line1'], [], [b'line2line2line2', b'line3']]
        assert run(b'12345678901234567890', max_size=10) == [[Db.Incomplete(b'1234567890'), Db.Incomplete(b'1234567890')]]  # noqa
        assert run(b'12345678901234567890', b'', max_size=10) == [[Db.Incomplete(b'1234567890'), Db.Incomplete(b'1234567890')], []]  # noqa
        assert run(b'1234567890123456789', b'0', b'', max_size=10) == [[Db.Incomplete(b'1234567890')], [Db.Incomplete(b'1234567890')], []]  # noqa
        assert run(b'123456789012345678', b'9', b'0', b'', max_size=10) == [[Db.Incomplete(b'1234567890')], [], [Db.Incomplete(b'1234567890')], []]  # noqa
        assert run(b'123456789012345678', b'9', b'', max_size=10) == [[Db.Incomplete(b'1234567890')], [], [Db.Incomplete(b'123456789')]]  # noqa
        assert run(b'1234567890', max_size=10) == [[Db.Incomplete(b'1234567890')]]
        assert run(b'1234567890', b'') == [[], [Db.Incomplete(b'1234567890')]]
        assert run(b'', b'', [[], [Db.ClosedError]])

        assert run(b'line1\nline2\rline3\n', delimiters=b'\r\n') == [[b'line1', b'line2', b'line3']]
        assert run(b'line1\nline2\rline3\n', delimiters=b'\r\n', keep_ends=True) == [[b'line1\n', b'line2\r', b'line3\n']]  # noqa

        assert run(b'line1\nline2\r\nline3\n\r', b'', delimiters=[b'\r\n',]) == [[b'line1\nline2'], [Db.Incomplete(b'line3\n\r')]]  # noqa

        assert run(b'line1\nline2\r\nline3\n\r', b'', delimiters=[b'\n', b'\r\n']) == [[b'line1', b'line2', b'line3'], [Db.Incomplete(b'\r')]]  # noqa

        # FIXME:
        # assert run(b'line1\nline2\r\nline3\n\r', b'', delimiters=[b'\r', b'\r\n']) == [[b'line1', b'line2', b'line3'], [Db.Incomplete(b'\r')]]  # noqa

    def test_delimiting_buffer(self):
        def run(*bs, **kwargs):
            buf = Db(**kwargs)
            out = []
            for b in bs:
                cur: list = []
                out.append(cur)
                try:
                    cur.extend(buf.feed(b))
                except Db.Error as e:
                    cur.append(type(e))
            return out

        assert run(b'') == [[]]
        assert run(b'line1\n') == [[b'line1']]
        assert run(b'line1\nline2\n') == [[b'line1', b'line2']]
        assert run(b'line1\nline2\nline3\n') == [[b'line1', b'line2', b'line3']]
        assert run(b'line1\nline2\nline3\n\r', b'') == [[b'line1', b'line2', b'line3'], [Db.Incomplete(b'\r')]]
        assert run(b'line1\nline2\r\nline3\n\r', b'') == [[b'line1', b'line2\r', b'line3'], [Db.Incomplete(b'\r')]]
        assert run(b'a' * 10, max_size=5) == [[Db.Incomplete(b'a' * 5) for _ in range(2)]]

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
