import io
import typing as ta


class BufferClosedError(Exception):
    pass


class BufferFullError(Exception):
    pass


class DelimitingBuffer:
    DEFAULT_DELIMITERS: ta.Sequence[bytes] = b'\n'

    def __init__(
            self,
            delimiters: ta.Iterable[bytes] = DEFAULT_DELIMITERS,
            *,
            max_size: int | None = None,
            on_full: ta.Literal['raise', 'yield'] = 'raise',
    ) -> None:
        super().__init__()

        self._delimiters = frozenset(delimiters)
        self._max_size = max_size
        self._on_full = on_full

        self._buf: io.BytesIO | None = io.BytesIO()

    def feed(self, data: bytes | bytearray) -> ta.Generator[bytes, None, None]:
        if (buf := self._buf) is None:
            raise BufferClosedError

        if not data:
            self._buf = None
            if buf.tell():
                yield buf.getvalue()
            return

        # for chunk in chunks:
        #     if os.linesep not in chunk:
        #         buf.write(chunk)
        #     else:
        #         line_chunks = chunk.splitlines()
        #         buf.write(line_chunks[0])
        #         yield buf.getvalue()
        #         if buf.tell() > max_buf_size:
        #             buf.close()
        #             buf = Buf()
        #         else:
        #             buf.seek(0, 0)
        #             buf.truncate()
        #         if len(line_chunks) > 1:
        #             for i in range(1, len(line_chunks) - 1):
        #                 yield line_chunks[i]
        #             buf.write(line_chunks[-1])
        # if buf.tell() > 0:
        #     yield buf.getvalue()

        raise NotImplementedError


def _main() -> None:
    assert list(DelimitingBuffer().feed(b'')) == []


if __name__ == '__main__':
    _main()
