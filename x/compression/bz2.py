import bz2
import io
import typing as ta

from .reader import DecompressReader


class Bz2Reader:
    def __init__(self, fp: ta.Any) -> None:
        super().__init__()

        self._fp = fp
        self._closed = False

        raw = DecompressReader(
            self._fp,
            bz2.BZ2Decompressor,
            trailing_error=OSError,
        )

        self._buffer = io.BufferedReader(raw)

    @property
    def closed(self):
        return self._closed

    def _check_not_closed(self) -> None:
        if self.closed:
            raise ValueError('I/O operation on closed file')

    def close(self):
        if self._closed:
            return

        try:
            self._buffer.close()
        finally:
            self._fp = None
            self._closed = True
            self._buffer = None

    def fileno(self):
        self._check_not_closed()
        return self._fp.fileno()

    def readable(self):
        self._check_not_closed()
        return True

    def writable(self):
        return False

    def peek(self, n=0):
        return self._buffer.peek(n)

    def read(self, size=-1):
        return self._buffer.read(size)

    def read1(self, size=-1):
        if size < 0:
            size = io.DEFAULT_BUFFER_SIZE
        return self._buffer.read1(size)

    def readinto(self, b):
        return self._buffer.readinto(b)

    def readline(self, size=-1):
        if not isinstance(size, int):
            if not hasattr(size, '__index__'):
                raise TypeError('Integer argument expected')
            size = size.__index__()
        return self._buffer.readline(size)

    def readlines(self, size=-1):
        if not isinstance(size, int):
            if not hasattr(size, '__index__'):
                raise TypeError('Integer argument expected')
            size = size.__index__()
        return self._buffer.readlines(size)

    def tell(self):
        self._check_not_closed()
        return self._buffer.tell()


class Bz2Writer:
    def __init__(
            self,
            fp: ta.Any,
            *,
            compresslevel: int = 9,
    ) -> None:
        super().__init__()

        self._fp = fp
        self._closed = False

        self._compressor = bz2.BZ2Compressor(compresslevel)

        self._pos = 0

    @property
    def closed(self):
        return self._closed

    def _check_not_closed(self) -> None:
        if self.closed:
            raise ValueError('I/O operation on closed file')

    def close(self):
        if self._closed:
            return

        try:
            self._fp.write(self._compressor.flush())
            self._compressor = None
        finally:
            self._fp = None
            self._closed = True

    def fileno(self):
        self._check_not_closed()
        return self._fp.fileno()

    def writable(self):
        self._check_not_closed()
        return True

    def write(self, data):
        if isinstance(data, (bytes, bytearray)):
            length = len(data)
        else:
            # accept any data that supports the buffer protocol
            data = memoryview(data)
            length = data.nbytes

        compressed = self._compressor.compress(data)
        self._fp.write(compressed)
        self._pos += length
        return length

    def tell(self):
        self._check_not_closed()
        return self._pos
