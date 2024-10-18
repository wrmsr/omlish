"""
https://github.com/python-trio/trio/issues/796 :|

TODO:
 - tell
 - peek
"""
import dataclasses as dc
import io
import typing as ta


@dc.dataclass(frozen=True)
class DelimitingBufferError(Exception):
    buffer: 'DelimitingBuffer'


class DelimitingBufferClosedError(DelimitingBufferError):
    pass


class DelimitingBufferFullError(DelimitingBufferError):
    pass


class DelimitingBufferIncompleteError(DelimitingBufferError):
    pass


class DelimitingBuffer:
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

        self._delimiters = frozenset(delimiters)
        self._keep_ends = keep_ends
        self._max_size = max_size
        self._on_full = on_full
        self._on_incomplete = on_incomplete

        self._buf: io.BytesIO | None = io.BytesIO()

    def _find_delim(self, data: bytes | bytearray, i: int) -> int | None:
        for d in self._delimiters:
            if (p := data.find(d, i)) >= 0:
                return p
        return None

    def feed(self, data: bytes | bytearray) -> ta.Generator[bytes, None, None]:
        if (buf := self._buf) is None:
            raise DelimitingBufferClosedError(self)

        if not data:
            self._buf = None

            if buf.tell():
                if self._on_incomplete == 'raise':
                    raise DelimitingBufferIncompleteError(self)

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

            c = data[i:p]
            if buf.tell():
                buf.write(c)
                yield buf.getvalue()
                buf.seek(0)
            else:
                yield c

            i = n

        if i >= l:
            return

        if self._max_size is None:
            buf.write(data[i:])
            return

        while i < l:
            remaining_data_len = l - i
            required_capacity = remaining_data_len + buf.tell()
            if required_capacity < self._max_size:
                buf.write(data[i:])
                return

            if self._on_full == 'raise':
                raise DelimitingBufferFullError(self)

            elif self._on_full == 'yield':
                raise NotImplementedError

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
    assert run(b'line1 line2 line3', b'') == [[], [b'line1 line2 line3']]
    assert run(b'1234567890', max_size=10, on_full='raise') == [[DelimitingBufferFullError]]
