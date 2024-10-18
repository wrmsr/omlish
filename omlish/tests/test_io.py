from ..io import ClosedDelimitingBufferError
from ..io import DelimitingBuffer
from ..io import DelimitingBufferError
from ..io import FullDelimitingBufferError
from ..io import IncompleteDelimitingBufferError


def test_delimiting_buffer():
    def run(*bs, **kwargs):
        buf = DelimitingBuffer(**kwargs)
        out: list = []
        for b in bs:
            out.append(cur := [])
            try:
                for o in buf.feed(b):
                    cur.append(o)  # noqa
            except DelimitingBufferError as e:
                cur.append(type(e))  # type: ignore
                break
        return out

    assert run(b'line1\nline2\nline3\n') == [[b'line1', b'line2', b'line3']]
    assert run(b'line1\nline2\nline3\n', keep_ends=True) == [[b'line1\n', b'line2\n', b'line3\n']]
    assert run(b'line1 line2 line3', b'') == [[], [b'line1 line2 line3']]
    assert run(b'line1\nline2', b'line2\nline3\n') == [[b'line1'], [b'line2line2', b'line3']]
    assert run(b'line1\nline2', b'line2', b'line2\nline3\n') == [[b'line1'], [], [b'line2line2line2', b'line3']]
    assert run(b'12345678901234567890', max_size=10, on_full='raise') == [[FullDelimitingBufferError]]
    assert run(b'12345678901234567890', b'', max_size=10, on_full='yield') == [[b'1234567890', b'1234567890'], []]
    assert run(b'1234567890', max_size=10, on_full='raise') == [[FullDelimitingBufferError]]
    assert run(b'1234567890', max_size=10, on_full='yield') == [[b'1234567890']]
    assert run(b'1234567890', b'', on_incomplete='yield') == [[], [b'1234567890']]
    assert run(b'1234567890', b'', on_incomplete='raise') == [[], [IncompleteDelimitingBufferError]]
    assert run(b'', b'', [[], [ClosedDelimitingBufferError]])
    assert run(b'line1\nline2\rline3\n', delimiters=b'\r\n') == [[b'line1', b'line2', b'line3']]
    assert run(b'line1\nline2\rline3\n', delimiters=b'\r\n', keep_ends=True) == [[b'line1\n', b'line2\r', b'line3\n']]  # noqa
