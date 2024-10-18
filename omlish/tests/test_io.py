import dataclasses as dc
import io
import typing as ta

from .. import check


@dc.dataclass(frozen=True)
class DelimitingBufferError(Exception):
    buffer: 'DelimitingBuffer'


class ClosedDelimitingBufferError(DelimitingBufferError):
    pass


class FullDelimitingBufferError(DelimitingBufferError):
    pass


class IncompleteDelimitingBufferError(DelimitingBufferError):
    pass


class DelimitingBuffer:
    """
    https://github.com/python-trio/trio/issues/796 :|
    """

    DEFAULT_DELIMITERS: bytes = b'\n'

    def __init__(
            self,
            delimiters: ta.Iterable[int] = DEFAULT_DELIMITERS,
            *,
            keep_ends: bool = False,
            max_size: int | None = None,
            on_full: ta.Literal['raise', 'yield'] = 'raise',
            on_incomplete: ta.Literal['raise', 'yield'] = 'yield',
    ) -> None:
        super().__init__()

        self._delimiters = frozenset(check.isinstance(d, int) for d in delimiters)
        self._keep_ends = keep_ends
        self._max_size = max_size
        self._on_full = on_full
        self._on_incomplete = on_incomplete

        self._buf: io.BytesIO | None = io.BytesIO()

    @property
    def is_closed(self) -> bool:
        return self._buf is None

    def tell(self) -> int:
        if (buf := self._buf) is None:
            raise ClosedDelimitingBufferError(self)
        return buf.tell()

    def peek(self) -> bytes:
        if (buf := self._buf) is None:
            raise ClosedDelimitingBufferError(self)
        return buf.getvalue()

    def _find_delim(self, data: bytes | bytearray, i: int) -> int | None:
        r = None  # type: int | None
        for d in self._delimiters:
            if (p := data.find(d, i)) >= 0:
                if r is None or p < r:
                    r = p
        return r

    def _append_and_reset(self, chunk: bytes) -> bytes:
        buf = check.not_none(self._buf)
        if not buf.tell():
            return chunk

        buf.write(chunk)
        ret = buf.getvalue()
        buf.seek(0)
        return ret

    def feed(self, data: bytes | bytearray) -> ta.Generator[bytes, None, None]:
        if (buf := self._buf) is None:
            raise ClosedDelimitingBufferError(self)

        if not data:
            self._buf = None

            if buf.tell():
                if self._on_incomplete == 'raise':
                    raise IncompleteDelimitingBufferError(self)

                elif self._on_incomplete == 'yield':
                    yield buf.getvalue()

                else:
                    raise ValueError(f'Unknown on_incomplete value: {self._on_incomplete!r}')

            return

        l = len(data)
        i = 0
        while i < l:
            if (p := self._find_delim(data, i)) is None:
                break

            n = p + 1
            if self._keep_ends:
                p = n

            yield self._append_and_reset(data[i:p])

            i = n

        if i >= l:
            return

        if self._max_size is None:
            buf.write(data[i:])
            return

        while i < l:
            remaining_data_len = l - i
            remaining_buf_capacity = self._max_size - buf.tell()

            if remaining_data_len < remaining_buf_capacity:
                buf.write(data[i:])
                return

            if self._on_full == 'raise':
                raise FullDelimitingBufferError(self)

            elif self._on_full == 'yield':
                p = i + remaining_buf_capacity

                yield self._append_and_reset(data[i:p])

                i = p

            else:
                raise ValueError(f'Unknown on_full value: {self._on_full!r}')


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
