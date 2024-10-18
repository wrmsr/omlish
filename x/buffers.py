"""
TODO:
 - tell
 - peek
"""
import io
import typing as ta


class BufferClosedError(Exception):
    pass


class BufferFullError(Exception):
    pass


class DelimitingBuffer:
    DEFAULT_DELIMITERS: bytes = b'\n'

    def __init__(
            self,
            delimiters: ta.Iterable[bytes] = DEFAULT_DELIMITERS,
            *,
            keep_ends: bool = False,
            max_size: int | None = None,
            on_full: ta.Literal['raise', 'yield'] = 'raise',
    ) -> None:
        super().__init__()

        self._delimiters = frozenset(delimiters)
        self._keep_ends = keep_ends
        self._max_size = max_size
        self._on_full = on_full

        self._buf: io.BytesIO | None = io.BytesIO()

    def _find_delim(self, data: bytes | bytearray, i: int) -> int | None:
        for d in self._delimiters:
            if (p := data.find(d, i)) >= 0:
                return p
        return None

    def feed(self, data: bytes | bytearray) -> ta.Generator[bytes, None, None]:
        if (buf := self._buf) is None:
            raise BufferClosedError

        if not data:
            self._buf = None
            if buf.tell():
                yield buf.getvalue()
            return

        l = len(data)
        i = 0
        while i < l:
            if (p := self._find_delim(data, i)) is None:
                break

            if self._keep_ends:
                n = p + 1
            else:
                n = p
                p += 1

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
            self._buf.write(data[i:])
            return

        while i < l:
            remaining_data_len = l - i
            required_capacity = remaining_data_len + buf.tell()
            if required_capacity < self._max_size:
                buf.write(data[i:])
                return

            if self._on_full == 'raise':
                raise BufferFullError

            elif self._on_full == 'yield':
                raise NotImplementedError

            else:
                raise ValueError(f'Unknown on_full value: {self._on_full!r}')


def test_delimiting_buffer():
    def run(*bs):
        buf = DelimitingBuffer()
        return [list(buf.feed(b)) for b in bs]

    assert run(b'line1\nline2\nline3\n') == [[b'line1', b'line2', b'line3']]

    # Test 2: No delimiter in data
    print("\nTest 2: No delimiter in data")
    buf = DelimitingBuffer()
    data = b'line1 line2 line3'
    outputs = list(buf.feed(data))
    # Should be empty, as no delimiter yet
    print(outputs)
    # Now feed empty data to close the buffer
    outputs += list(buf.feed(b''))
    print(outputs)
    # Expected: [b'line1 line2 line3']

    # Test 3: max_size with on_full='raise'
    print("\nTest 3: max_size with on_full='raise'")
    buf = DelimitingBuffer(max_size=10, on_full='raise')
    data = b'1234567890'
    outputs = list(buf.feed(data))
    print(outputs)
    # Expected: []
    try:
        outputs += list(buf.feed(b'1'))
    except BufferFullError:
        print("BufferFullError raised as expected")
    else:
        print("BufferFullError was not raised")

    # Test 4: max_size with on_full='yield'
    print("\nTest 4: max_size with on_full='yield'")
    buf = DelimitingBuffer(max_size=10, on_full='yield')
    data = b'1234567890'
    outputs = list(buf.feed(data))
    print(outputs)
    # Expected: []
    outputs += list(buf.feed(b'1'))
    print(outputs)
    # Expected: [b'1234567890']

    # Test 5: partial delimiter at buffer end
    print("\nTest 5: Partial delimiter at buffer end")
    buf = DelimitingBuffer(delimiters=[b'END'])
    data = b'some data EN'
    outputs = list(buf.feed(data))
    print(outputs)
    # Expected: []
    outputs += list(buf.feed(b'D more data'))
    print(outputs)
    # Expected: [b'some data END']

    # Test 6: Multiple delimiters
    print("\nTest 6: Multiple delimiters")
    buf = DelimitingBuffer(delimiters=[b'\n', b'END'])
    data = b'line1\nline2ENDline3\n'
    outputs = list(buf.feed(data))
    print(outputs)
    # Expected: [b'line1\n', b'line2END', b'line3\n']


# Run tests
test_delimiting_buffer()
