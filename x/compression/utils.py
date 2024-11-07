import io
import struct
import typing as ta


def write32u(output: ta.IO, value: int) -> None:
    # The L format writes the bit pattern correctly whether signed or unsigned.
    output.write(struct.pack('<L', value))


def read_exact(fp: ta.Any, n: int) -> bytes:
    """
    Read exactly *n* bytes from `fp`

    This method is required because fp may be unbuffered, i.e. return short reads.
    """

    data = fp.read(n)
    while len(data) < n:
        b = fp.read(n - len(data))
        if not b:
            raise EOFError("Compressed file ended before the end-of-stream marker was reached")
        data += b
    return data


class PaddedFile:
    """
    Minimal read-only file object that prepends a string to the contents of an actual file. Shouldn't be used outside of
    gzip.py, as it lacks essential functionality.
    """

    def __init__(self, f: ta.Any, prepend: bytes = b'') -> None:
        super().__init__()
        self._buffer = prepend
        self._length = len(prepend)
        self._file = f
        self._read = 0

    def read(self, size: int) -> bytes:
        if self._read is None:
            return self._file.read(size)

        if self._read + size <= self._length:
            read = self._read
            self._read += size
            return self._buffer[read:self._read]

        read = self._read
        self._read = None
        return self._buffer[read:] + self._file.read(size-self._length+read)

    def prepend(self, prepend: bytes = b'') -> None:
        if self._read is None:
            self._buffer = prepend
        else:  # Assume data was read since the last prepend() call
            self._read -= len(prepend)
            return
        self._length = len(self._buffer)
        self._read = 0

    def seek(self, off: int) -> int:
        self._read = None
        self._buffer = None
        return self._file.seek(off)

    def seekable(self) -> bool:
        return True  # Allows fast-forwarding even in unseekable streams


class BufferedWriterDelegate(io.RawIOBase):
    def __init__(self, write: ta.Callable[[bytes], int]) -> None:
        super().__init__()
        self._write = write

    def write(self, data: bytes) -> int:
        return self._write(data)

    def seekable(self) -> bool:
        return False

    def writable(self) -> bool:
        return True
