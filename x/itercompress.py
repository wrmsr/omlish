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
import sys
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

COMPRESS_LEVEL_FAST = 1
COMPRESS_LEVEL_TRADEOFF = 6
COMPRESS_LEVEL_BEST = 9


class GzipWriter:
    def __init__(
            self,
            fileobj: ta.Any,
            *,
            compresslevel: int = COMPRESS_LEVEL_BEST,
            name: str | None = None,
            mtime: float | None = None,
            buffer_size: int = 4 * io.DEFAULT_BUFFER_SIZE,
    ) -> None:
        super().__init__()

        self._fileobj: ta.Any | None = fileobj
        self._name = name or ''
        self._compresslevel = compresslevel
        self._mtime = mtime
        self._buffer_size = buffer_size

        self._crc = zlib.crc32(b"")
        self._size = 0
        self._offset = 0  # Current file offset for seek(), tell(), etc

        self._compress = zlib.compressobj(
            self._compresslevel,
            zlib.DEFLATED,
            -zlib.MAX_WBITS,
            zlib.DEF_MEM_LEVEL,
            0,
        )

        self._buffer = io.BufferedWriter(
            _BufferedWriterDelegate(self._write_raw),
            buffer_size=self._buffer_size,
        )

        self._write_gzip_header()

    def __enter__(self) -> ta.Self:
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def _write_gzip_header(self) -> None:
        self._fileobj.write(b'\037\213')  # magic header
        self._fileobj.write(b'\010')  # compression method

        try:
            # RFC 1952 requires the FNAME field to be Latin-1. Do not include filenames that cannot be represented that
            # way.
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

        mtime = self._mtime
        if mtime is None:
            mtime = time.time()
        write32u(self._fileobj, int(mtime))

        if self._compresslevel == COMPRESS_LEVEL_BEST:
            xfl = b'\002'
        elif self._compresslevel == COMPRESS_LEVEL_FAST:
            xfl = b'\004'
        else:
            xfl = b'\000'
        self._fileobj.write(xfl)

        self._fileobj.write(b'\377')

        if fname:
            self._fileobj.write(fname + b'\000')

    def _check_not_closed(self) -> None:
        if self.closed:
            raise ValueError("I/O operation on closed file")

    @property
    def closed(self) -> bool:
        return self._fileobj is None

    def close(self) -> None:
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

    def write(self, data: bytes) -> int:
        self._check_not_closed()

        if self._fileobj is None:
            raise ValueError("write() on closed GzipFile object")

        return self._buffer.write(data)

    def _write_raw(self, data: bytes) -> int:
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


###


class DecompressReader(io.RawIOBase):
    """Adapts the decompressor API to a RawIOBase reader API"""

    def readable(self):
        return True

    def __init__(self, fp, decomp_factory, trailing_error=(), **decomp_args):
        self._fp = fp
        self._eof = False
        self._pos = 0  # Current offset in decompressed stream

        # Set to size of decompressed stream once it is known, for SEEK_END
        self._size = -1

        # Save the decompressor factory and arguments.
        # If the file contains multiple compressed streams, each stream will need a separate decompressor object. A new
        # decompressor object is also needed when implementing a backwards seek().
        self._decomp_factory = decomp_factory
        self._decomp_args = decomp_args
        self._decompressor = self._decomp_factory(**self._decomp_args)

        # Exception class to catch from decompressor signifying invalid
        # trailing data to ignore
        self._trailing_error = trailing_error

    def close(self):
        self._decompressor = None
        return super().close()

    def seekable(self):
        return self._fp.seekable()

    def readinto(self, b):
        with memoryview(b) as view, view.cast("B") as byte_view:
            data = self.read(len(byte_view))
            byte_view[:len(data)] = data
        return len(data)

    def read(self, size=-1):
        if size < 0:
            return self.readall()

        if not size or self._eof:
            return b""
        data = None  # Default if EOF is encountered
        # Depending on the input data, our call to the decompressor may not return any data. In this case, try again
        # after reading another block.
        while True:
            if self._decompressor.eof:
                rawblock = (self._decompressor.unused_data or self._fp.read(io.DEFAULT_BUFFER_SIZE))
                if not rawblock:
                    break
                # Continue to next stream.
                self._decompressor = self._decomp_factory(
                    **self._decomp_args)
                try:
                    data = self._decompressor.decompress(rawblock, size)
                except self._trailing_error:
                    # Trailing data isn't a valid compressed stream; ignore it.
                    break
            else:
                if self._decompressor.needs_input:
                    rawblock = self._fp.read(io.DEFAULT_BUFFER_SIZE)
                    if not rawblock:
                        raise EOFError("Compressed file ended before the end-of-stream marker was reached")
                else:
                    rawblock = b""
                data = self._decompressor.decompress(rawblock, size)
            if data:
                break
        if not data:
            self._eof = True
            self._size = self._pos
            return b""
        self._pos += len(data)
        return data

    def readall(self):
        chunks = []
        # sys.maxsize means the max length of output buffer is unlimited, so that the whole input buffer can be
        # decompressed within one .decompress() call.
        while data := self.read(sys.maxsize):
            chunks.append(data)

        return b"".join(chunks)

    # Rewind the file to the beginning of the data stream.
    def _rewind(self):
        self._fp.seek(0)
        self._eof = False
        self._pos = 0
        self._decompressor = self._decomp_factory(**self._decomp_args)

    def seek(self, offset, whence=io.SEEK_SET):
        # Recalculate offset as an absolute file position.
        if whence == io.SEEK_SET:
            pass
        elif whence == io.SEEK_CUR:
            offset = self._pos + offset
        elif whence == io.SEEK_END:
            # Seeking relative to EOF - we need to know the file's size.
            if self._size < 0:
                while self.read(io.DEFAULT_BUFFER_SIZE):
                    pass
            offset = self._size + offset
        else:
            raise ValueError("Invalid value for whence: {}".format(whence))

        # Make it so that offset is the number of bytes to skip forward.
        if offset < self._pos:
            self._rewind()
        else:
            offset -= self._pos

        # Read and discard data until we reach the desired position.
        while offset > 0:
            data = self.read(min(io.DEFAULT_BUFFER_SIZE, offset))
            if not data:
                break
            offset -= len(data)

        return self._pos

    def tell(self):
        """Return the current file position."""
        return self._pos


class _PaddedFile:
    """
    Minimal read-only file object that prepends a string to the contents of an actual file. Shouldn't be used outside of
    gzip.py, as it lacks essential functionality.
    """

    def __init__(self, f, prepend=b''):
        self._buffer = prepend
        self._length = len(prepend)
        self.file = f
        self._read = 0

    def read(self, size):
        if self._read is None:
            return self.file.read(size)
        if self._read + size <= self._length:
            read = self._read
            self._read += size
            return self._buffer[read:self._read]
        else:
            read = self._read
            self._read = None
            return self._buffer[read:] + \
                self.file.read(size-self._length+read)

    def prepend(self, prepend=b''):
        if self._read is None:
            self._buffer = prepend
        else:  # Assume data was read since the last prepend() call
            self._read -= len(prepend)
            return
        self._length = len(self._buffer)
        self._read = 0

    def seek(self, off):
        self._read = None
        self._buffer = None
        return self.file.seek(off)

    def seekable(self):
        return True  # Allows fast-forwarding even in unseekable streams


def _read_exact(fp, n):
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


def _read_gzip_header(fp):
    """
    Read a gzip header from `fp` and progress to the end of the header.

    Returns last mtime if header was present or None otherwise.
    """

    magic = fp.read(2)
    if magic == b'':
        return None

    if magic != b'\037\213':
        raise gzip.BadGzipFile('Not a gzipped file (%r)' % magic)

    (method, flag, last_mtime) = struct.unpack("<BBIxx", _read_exact(fp, 8))
    if method != 8:
        raise gzip.BadGzipFile('Unknown compression method')

    if flag & gzip.FEXTRA:
        # Read & discard the extra field, if present
        extra_len, = struct.unpack("<H", _read_exact(fp, 2))
        _read_exact(fp, extra_len)
    if flag & gzip.FNAME:
        # Read and discard a null-terminated string containing the filename
        while True:
            s = fp.read(1)
            if not s or s==b'\000':
                break
    if flag & gzip.FCOMMENT:
        # Read and discard a null-terminated string containing a comment
        while True:
            s = fp.read(1)
            if not s or s==b'\000':
                break
    if flag & gzip.FHCRC:
        _read_exact(fp, 2)     # Read & discard the 16-bit header CRC
    return last_mtime


READ_BUFFER_SIZE = 128 * 1024


class GzipReader(DecompressReader):
    def __init__(self, fp):
        super().__init__(
            _PaddedFile(fp),
            zlib._ZlibDecompressor,  # noqa
            wbits=-zlib.MAX_WBITS,
        )

        # Set flag indicating start of a new member
        self._new_member = True
        self._last_mtime = None

    def _init_read(self):
        self._crc = zlib.crc32(b"")
        self._stream_size = 0  # Decompressed size of unconcatenated stream

    def _read_gzip_header(self):
        last_mtime = _read_gzip_header(self._fp)
        if last_mtime is None:
            return False
        self._last_mtime = last_mtime
        return True

    def read(self, size=-1):
        if size < 0:
            return self.readall()
        # size=0 is special because decompress(max_length=0) is not supported
        if not size:
            return b""

        # For certain input data, a single
        # call to decompress() may not return
        # any data. In this case, retry until we get some data or reach EOF.
        while True:
            if self._decompressor.eof:
                # Ending case: we've come to the end of a member in the file,
                # so finish up this member, and read a new gzip header.
                # Check the CRC and file size, and set the flag so we read
                # a new member
                self._read_eof()
                self._new_member = True
                self._decompressor = self._decomp_factory(
                    **self._decomp_args)

            if self._new_member:
                # If the _new_member flag is set, we have to
                # jump to the next member, if there is one.
                self._init_read()
                if not self._read_gzip_header():
                    self._size = self._pos
                    return b""
                self._new_member = False

            # Read a chunk of data from the file
            if self._decompressor.needs_input:
                buf = self._fp.read(READ_BUFFER_SIZE)
                uncompress = self._decompressor.decompress(buf, size)
            else:
                uncompress = self._decompressor.decompress(b"", size)

            if self._decompressor.unused_data != b"":
                # Prepend the already read bytes to the fileobj so they can
                # be seen by _read_eof() and _read_gzip_header()
                self._fp.prepend(self._decompressor.unused_data)

            if uncompress != b"":
                break
            if buf == b"":
                raise EOFError("Compressed file ended before the end-of-stream marker was reached")

        self._crc = zlib.crc32(uncompress, self._crc)
        self._stream_size += len(uncompress)
        self._pos += len(uncompress)
        return uncompress

    def _read_eof(self):
        # We've read to the end of the file
        # We check that the computed CRC and size of the uncompressed data matches the stored values.  Note that the
        # size stored is the true file size mod 2**32.
        crc32, isize = struct.unpack("<II", _read_exact(self._fp, 8))
        if crc32 != self._crc:
            raise gzip.BadGzipFile("CRC check failed %s != %s" % (hex(crc32), hex(self._crc)))
        elif isize != (self._stream_size & 0xffffffff):
            raise gzip.BadGzipFile("Incorrect length of data produced")

        # Gzip files can be padded with zeroes and still have archives. Consume all zero bytes and set the file position
        # to the first non-zero byte. See http://www.gzip.org/#faq8
        c = b"\x00"
        while c == b"\x00":
            c = self._fp.read(1)
        if c:
            self._fp.prepend(c)

    def _rewind(self):
        super()._rewind()
        self._new_member = True


def run_decompress2(gz_bytes: bytes) -> bytes:
    fileobj = io.BytesIO(gz_bytes)

    with contextlib.closing(GzipReader(fileobj)) as raw:  # noqa
        with contextlib.closing(io.BufferedReader(raw)) as buffer:
            out_buf = io.BytesIO()
            while out := buffer.read(0x1000):
                out_buf.write(out)

    return out_buf.getvalue()


##


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
