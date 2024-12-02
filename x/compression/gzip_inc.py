import gzip
import os.path
import struct
import time
import typing as ta
import zlib

from .utils import read_exact


COMPRESS_LEVEL_FAST = 1
COMPRESS_LEVEL_TRADEOFF = 6
COMPRESS_LEVEL_BEST = 9


##


class IncrementalGzipReader:
    def _read_gzip_header(self) -> ta.Generator[int, bytes, int | None]:
        """
        Read a gzip header from `fp` and progress to the end of the header.

        Returns last mtime if header was present or None otherwise.
        """

        magic = yield 2
        if magic == b'':
            return None

        if magic != b'\037\213':
            raise gzip.BadGzipFile('Not a gzipped file (%r)' % magic)

        buf = yield 8
        method, flag, last_mtime = struct.unpack('<BBIxx', buf)
        if method != 8:
            raise gzip.BadGzipFile('Unknown compression method')

        if flag & gzip.FEXTRA:
            # Read & discard the extra field, if present
            buf = yield 2
            extra_len, = struct.unpack('<H', buf)
            if extra_len:
                yield extra_len

        if flag & gzip.FNAME:
            # Read and discard a null-terminated string containing the filename
            while True:
                s = yield 1
                if not s or s == b'\000':
                    break

        if flag & gzip.FCOMMENT:
            # Read and discard a null-terminated string containing a comment
            while True:
                s = yield 1
                if not s or s==b'\000':
                    break

        if flag & gzip.FHCRC:
            yield 2  # Read & discard the 16-bit header CRC

        return last_mtime


class IncrementalGzipWriter:
    def __init__(
            self,
            *,
            compresslevel: int = COMPRESS_LEVEL_BEST,
            name: str | None = None,
            mtime: float | None = None,
    ) -> None:
        super().__init__()

        self._name = name or ''
        self._compresslevel = compresslevel
        self._mtime = mtime

    def _write_gzip_header(self) -> ta.Generator[bytes, None, None]:
        yield '\037\213'  # magic header
        yield '\010'  # compression method

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
        yield chr(flags).encode('latin-1')

        mtime = self._mtime
        if mtime is None:
            mtime = time.time()
        yield struct.pack('<L', int(mtime))

        if self._compresslevel == COMPRESS_LEVEL_BEST:
            xfl = b'\002'
        elif self._compresslevel == COMPRESS_LEVEL_FAST:
            xfl = b'\004'
        else:
            xfl = b'\000'
        yield xfl

        yield b'\377'

        if fname:
            yield fname + b'\000'

    def gen(self) -> ta.Generator[bytes, bytes | None, None]:
        crc = zlib.crc32(b'')
        size = 0
        offset = 0  # Current file offset for seek(), tell(), etc

        compress = zlib.compressobj(
            self._compresslevel,
            zlib.DEFLATED,
            -zlib.MAX_WBITS,
            zlib.DEF_MEM_LEVEL,
            0,
        )

        yield from self._write_gzip_header()

        while True:
            data = yield
            if not data:
                break

            # Called by our self._buffer underlying BufferedWriterDelegate.
            if isinstance(data, (bytes, bytearray)):
                length = len(data)
            else:
                # accept any data that supports the buffer protocol
                data = memoryview(data)
                length = data.nbytes

            if length > 0:
                yield compress.compress(data)
                size += length
                crc = zlib.crc32(data, crc)
                offset += length

        if (fl := compress.flush()):
            yield fl

        yield struct.pack('<L', crc)
        # size may exceed 2 GiB, or even 4 GiB
        yield struct.pack('<L', size & 0xffffffff)

        yield b''
