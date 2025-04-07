# ruff: noqa: PT009
# @omlish-lite
import unittest

from ..buffers import DelimitingBuffer as Db


class TestDelimitingBuffer(unittest.TestCase):
    def test_delimiting_buffer(self):
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
