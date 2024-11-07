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

from .reader import DecompressReader
from .utils import BufferedWriterDelegate
from .utils import PaddedFile
from .utils import read_exact
from .utils import write32u


##


COMPRESS_LEVEL_FAST = 1
COMPRESS_LEVEL_TRADEOFF = 6
COMPRESS_LEVEL_BEST = 9

READ_BUFFER_SIZE = 128 * 1024


##


def _read_gzip_header(fp: ta.IO) -> int | None:
    """
    Read a gzip header from `fp` and progress to the end of the header.

    Returns last mtime if header was present or None otherwise.
    """

    magic = fp.read(2)
    if magic == b'':
        return None

    if magic != b'\037\213':
        raise gzip.BadGzipFile('Not a gzipped file (%r)' % magic)

    (method, flag, last_mtime) = struct.unpack('<BBIxx', read_exact(fp, 8))
    if method != 8:
        raise gzip.BadGzipFile('Unknown compression method')

    if flag & gzip.FEXTRA:
        # Read & discard the extra field, if present
        extra_len, = struct.unpack('<H', read_exact(fp, 2))
        read_exact(fp, extra_len)

    if flag & gzip.FNAME:
        # Read and discard a null-terminated string containing the filename
        while True:
            s = fp.read(1)
            if not s or s == b'\000':
                break

    if flag & gzip.FCOMMENT:
        # Read and discard a null-terminated string containing a comment
        while True:
            s = fp.read(1)
            if not s or s==b'\000':
                break

    if flag & gzip.FHCRC:
        read_exact(fp, 2)  # Read & discard the 16-bit header CRC

    return last_mtime


class GzipReader(DecompressReader):
    def __init__(self, fp: ta.Any) -> None:
        super().__init__(
            PaddedFile(fp),
            zlib._ZlibDecompressor,  # noqa  # FIXME: zlib.decompressobj
            wbits=-zlib.MAX_WBITS,
        )

        # Set flag indicating start of a new member
        self._new_member = True
        self._last_mtime = None

    _crc: int
    _stream_size: int

    def _init_read(self) -> None:
        self._crc = zlib.crc32(b'')
        self._stream_size = 0  # Decompressed size of unconcatenated stream

    def _read_gzip_header(self) -> bool:
        last_mtime = _read_gzip_header(self._fp)
        if last_mtime is None:
            return False
        self._last_mtime = last_mtime
        return True

    def read(self, size: int = -1) -> bytes:
        if size < 0:
            return self.readall()

        # size=0 is special because decompress(max_length=0) is not supported
        if not size:
            return b''

        # For certain input data, a single call to decompress() may not return any data. In this case, retry until we
        # get some data or reach EOF.
        while True:
            if self._decompressor.eof:
                # Ending case: we've come to the end of a member in the file, so finish up this member, and read a new
                # gzip header. Check the CRC and file size, and set the flag so we read a new member
                self._read_eof()
                self._new_member = True
                self._decompressor = self._decomp_factory(
                    **self._decomp_args)

            if self._new_member:
                # If the _new_member flag is set, we have to jump to the next member, if there is one.
                self._init_read()
                if not self._read_gzip_header():
                    self._size = self._pos
                    return b''
                self._new_member = False

            # Read a chunk of data from the file
            if self._decompressor.needs_input:
                buf = self._fp.read(READ_BUFFER_SIZE)
                uncompress = self._decompressor.decompress(buf, size)
            else:
                uncompress = self._decompressor.decompress(b'', size)

            if self._decompressor.unused_data != b'':
                # Prepend the already read bytes to the fileobj so they can be seen by _read_eof() and
                # _read_gzip_header()
                self._fp.prepend(self._decompressor.unused_data)

            if uncompress != b'':
                break
            if buf == b'':
                raise EOFError('Compressed file ended before the end-of-stream marker was reached')

        self._crc = zlib.crc32(uncompress, self._crc)
        self._stream_size += len(uncompress)
        self._pos += len(uncompress)
        return uncompress

    def _read_eof(self) -> None:
        # We've read to the end of the file.
        # We check that the computed CRC and size of the uncompressed data matches the stored values.  Note that the
        # size stored is the true file size mod 2**32.
        crc32, isize = struct.unpack('<II', read_exact(self._fp, 8))
        if crc32 != self._crc:
            raise gzip.BadGzipFile('CRC check failed %s != %s' % (hex(crc32), hex(self._crc)))
        elif isize != (self._stream_size & 0xffffffff):
            raise gzip.BadGzipFile('Incorrect length of data produced')

        # Gzip files can be padded with zeroes and still have archives. Consume all zero bytes and set the file position
        # to the first non-zero byte. See http://www.gzip.org/#faq8
        c = b'\x00'
        while c == b'\x00':
            c = self._fp.read(1)
        if c:
            self._fp.prepend(c)

    def _rewind(self) -> None:
        super()._rewind()
        self._new_member = True


##


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

        self._crc = zlib.crc32(b'')
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
            BufferedWriterDelegate(self._write_raw),
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

    @property
    def closed(self) -> bool:
        return self._fileobj is None

    def _check_not_closed(self) -> None:
        if self.closed:
            raise ValueError('I/O operation on closed file')

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
            raise ValueError('write() on closed GzipFile object')

        return self._buffer.write(data)

    def _write_raw(self, data: bytes) -> int:
        # Called by our self._buffer underlying BufferedWriterDelegate.
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
