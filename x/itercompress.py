"""
TODO:
 - https://docs.python.org/3/library/zlib.html#zlib.compressobj
"""
import contextlib
import gzip
import io
import os.path
import random
import string
import struct
import time
import typing as ta
import zlib


def generate_random_text(size: int) -> str:
    chars = string.ascii_letters + string.digits + string.punctuation
    return ''.join(random.choices(chars, k=size))


def run_decompress(gz_bytes: bytes) -> bytes:
    fileobj = io.BytesIO(gz_bytes)

    with contextlib.closing(gzip._GzipReader(fileobj)) as raw:  # noqa
        with contextlib.closing(io.BufferedReader(raw)) as buffer:
            out_buf = io.BytesIO()
            while out := buffer.read(0x1000):
                out_buf.write(out)

    return out_buf.getvalue()


class _BufferedWriterDelegate(io.RawIOBase):
    def __init__(self, write: ta.Callable[[bytes], int]):
        super().__init__()
        self._write = write

    def write(self, data: bytes) -> int:
        return self._write(data)

    def seekable(self) -> bool:
        return False

    def writable(self) -> bool:
        return True


def write32u(output, value):
    # The L format writes the bit pattern correctly whether signed or unsigned.
    output.write(struct.pack('<L', value))


class GzipWriter:
    def __init__(
            self,
            fileobj: ta.Any,
            *,
            compresslevel: int = 9,
            name: str | None = None,
            buffer_size: int = 4 * io.DEFAULT_BUFFER_SIZE,
            mtime: float | None = None,
    ) -> None:
        super().__init__()

        self._fileobj: ta.Any | None = fileobj

        self._name = name or ''
        self._crc = zlib.crc32(b"")
        self._size = 0
        self._offset = 0  # Current file offset for seek(), tell(), etc

        self._compress = zlib.compressobj(
            compresslevel,
            zlib.DEFLATED,
            -zlib.MAX_WBITS,
            zlib.DEF_MEM_LEVEL,
            0,
        )
        self._write_mtime = mtime
        self._buffer_size = buffer_size
        self._buffer = io.BufferedWriter(
            _BufferedWriterDelegate(self._write_raw),
            buffer_size=self._buffer_size,
        )
        self._write_gzip_header(compresslevel)

    def __enter__(self) -> ta.Self:
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def _write_gzip_header(self, compresslevel):
        self._fileobj.write(b'\037\213')             # magic header
        self._fileobj.write(b'\010')                 # compression method
        try:
            # RFC 1952 requires the FNAME field to be Latin-1. Do not
            # include filenames that cannot be represented that way.
            fname = os.path.basename(self._name)
            if not isinstance(fname, bytes):
                fname = fname.encode('latin-1')
            if fname.endswith(b'.gz'):
                fname = fname[:-3]
        except UnicodeEncodeError:
            fname = b''
        flags = 0
        if fname:
            flags = gzip.FNAME
        self._fileobj.write(chr(flags).encode('latin-1'))
        mtime = self._write_mtime
        if mtime is None:
            mtime = time.time()
        write32u(self._fileobj, int(mtime))
        if compresslevel == 9:
            xfl = b'\002'
        elif compresslevel == 1:
            xfl = b'\004'
        else:
            xfl = b'\000'
        self._fileobj.write(xfl)
        self._fileobj.write(b'\377')
        if fname:
            self._fileobj.write(fname + b'\000')

    def _check_not_closed(self):
        if self.closed:
            raise ValueError("I/O operation on closed file")

    @property
    def closed(self):
        return self._fileobj is None

    def close(self):
        fileobj = self._fileobj
        if fileobj is None:
            return
        try:
            self._buffer.flush()
            fileobj.write(self._compress.flush())
            write32u(fileobj, self._crc)
            # self.size may exceed 2 GiB, or even 4 GiB
            write32u(fileobj, self._size & 0xffffffff)
        finally:
            self._fileobj = None

    def write(self,data):
        self._check_not_closed()

        if self._fileobj is None:
            raise ValueError("write() on closed GzipFile object")

        return self._buffer.write(data)

    def _write_raw(self, data):
        # Called by our self._buffer underlying _BufferedWriterDelegate.
        if isinstance(data, (bytes, bytearray)):
            length = len(data)
        else:
            # accept any data that supports the buffer protocol
            data = memoryview(data)
            length = data.nbytes

        if length > 0:
            self._fileobj.write(self._compress.compress(data))
            self._size += length
            self._crc = zlib.crc32(data, self._crc)
            self._offset += length

        return length


def run_compress(in_bytes: bytes) -> bytes:
    gz_buf = io.BytesIO()
    with GzipWriter(gz_buf) as gf:
        gf.write(in_bytes)
    return gz_buf.getvalue()


def _main() -> None:
    in_bytes = generate_random_text(0x100_000).encode('utf-8')

    gz_buf = io.BytesIO()
    with gzip.GzipFile(fileobj=gz_buf, mode='wb') as gf:
        gf.write(in_bytes)
    gz_bytes = gz_buf.getvalue()
    assert len(gz_bytes) < len(in_bytes)

    out_bytes = run_decompress(gz_bytes)
    assert out_bytes == in_bytes

    gz_bytes2 = run_compress(in_bytes)
    out_bytes2 = run_decompress(gz_bytes2)
    assert out_bytes2 == in_bytes


if __name__ == '__main__':
    _main()
