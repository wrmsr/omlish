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


class _WriteBufferStream(io.RawIOBase):
    """Minimal object to pass WriteBuffer flushes into GzipFile"""
    def __init__(self, gzip_file):
        self.gzip_file = gzip_file

    def write(self, data):
        return self.gzip_file._write_raw(data)

    def seekable(self):
        return False

    def writable(self):
        return True


def write32u(output, value):
    # The L format writes the bit pattern correctly whether signed
    # or unsigned.
    output.write(struct.pack("<L", value))


class GzipWriter:
    def __init__(
            self,
            fileobj: ta.Any,
            compresslevel: int = 9,
            filename: str | None = None,
    ) -> None:
        super().__init__()

        self.fileobj = fileobj

        self._init_write(filename)
        self.compress = zlib.compressobj(
            compresslevel,
            zlib.DEFLATED,
            -zlib.MAX_WBITS,
            zlib.DEF_MEM_LEVEL,
            0,
        )
        self._write_mtime = None
        self._buffer_size = 4 * io.DEFAULT_BUFFER_SIZE
        self._buffer = io.BufferedWriter(
            _WriteBufferStream(self),
            buffer_size=self._buffer_size,
        )
        self._write_gzip_header(compresslevel)

    def _init_write(self, filename):
        self.name = filename
        self.crc = zlib.crc32(b"")
        self.size = 0
        self.writebuf = []
        self.bufsize = 0
        self.offset = 0  # Current file offset for seek(), tell(), etc

    def _write_gzip_header(self, compresslevel):
        self.fileobj.write(b'\037\213')             # magic header
        self.fileobj.write(b'\010')                 # compression method
        try:
            # RFC 1952 requires the FNAME field to be Latin-1. Do not
            # include filenames that cannot be represented that way.
            fname = os.path.basename(self.name)
            if not isinstance(fname, bytes):
                fname = fname.encode('latin-1')
            if fname.endswith(b'.gz'):
                fname = fname[:-3]
        except UnicodeEncodeError:
            fname = b''
        flags = 0
        if fname:
            flags = gzip.FNAME
        self.fileobj.write(chr(flags).encode('latin-1'))
        mtime = self._write_mtime
        if mtime is None:
            mtime = time.time()
        write32u(self.fileobj, int(mtime))
        if compresslevel == 9:
            xfl = b'\002'
        elif compresslevel == 1:
            xfl = b'\004'
        else:
            xfl = b'\000'
        self.fileobj.write(xfl)
        self.fileobj.write(b'\377')
        if fname:
            self.fileobj.write(fname + b'\000')


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
