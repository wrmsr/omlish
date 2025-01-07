# PYTHON SOFTWARE FOUNDATION LICENSE VERSION 2
# --------------------------------------------
#
# 1. This LICENSE AGREEMENT is between the Python Software Foundation ("PSF"), and the Individual or Organization
# ("Licensee") accessing and otherwise using this software ("Python") in source or binary form and its associated
# documentation.
#
# 2. Subject to the terms and conditions of this License Agreement, PSF hereby grants Licensee a nonexclusive,
# royalty-free, world-wide license to reproduce, analyze, test, perform and/or display publicly, prepare derivative
# works, distribute, and otherwise use Python alone or in any derivative version, provided, however, that PSF's License
# Agreement and PSF's notice of copyright, i.e., "Copyright (c) 2001, 2002, 2003, 2004, 2005, 2006, 2007, 2008, 2009,
# 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017 Python Software Foundation; All Rights Reserved" are retained in Python
# alone or in any derivative version prepared by Licensee.
#
# 3. In the event Licensee prepares a derivative work that is based on or incorporates Python or any part thereof, and
# wants to make the derivative work available to others as provided herein, then Licensee hereby agrees to include in
# any such work a brief summary of the changes made to Python.
#
# 4. PSF is making Python available to Licensee on an "AS IS" basis.  PSF MAKES NO REPRESENTATIONS OR WARRANTIES,
# EXPRESS OR IMPLIED.  BY WAY OF EXAMPLE, BUT NOT LIMITATION, PSF MAKES NO AND DISCLAIMS ANY REPRESENTATION OR WARRANTY
# OF MERCHANTABILITY OR FITNESS FOR ANY PARTICULAR PURPOSE OR THAT THE USE OF PYTHON WILL NOT INFRINGE ANY THIRD PARTY
# RIGHTS.
#
# 5. PSF SHALL NOT BE LIABLE TO LICENSEE OR ANY OTHER USERS OF PYTHON FOR ANY INCIDENTAL, SPECIAL, OR CONSEQUENTIAL
# DAMAGES OR LOSS AS A RESULT OF MODIFYING, DISTRIBUTING, OR OTHERWISE USING PYTHON, OR ANY DERIVATIVE THEREOF, EVEN IF
# ADVISED OF THE POSSIBILITY THEREOF.
#
# 6. This License Agreement will automatically terminate upon a material breach of its terms and conditions.
#
# 7. Nothing in this License Agreement shall be deemed to create any relationship of agency, partnership, or joint
# venture between PSF and Licensee.  This License Agreement does not grant permission to use PSF trademarks or trade
# name in a trademark sense to endorse or promote products or services of Licensee, or any third party.
#
# 8. By copying, installing or otherwise using Python, Licensee agrees to be bound by the terms and conditions of this
# License Agreement.
import dataclasses as dc
import functools
import os.path
import struct
import time
import typing as ta

from ... import cached
from ... import check
from ... import lang
from ..coro import BytesSteppedCoro
from ..coro import BytesSteppedReaderCoro
from ..coro.readers import PrependableBytesCoroReader
from .base import Compression
from .base import IncrementalCompression
from .codecs import make_compression_codec
from .codecs import make_compression_lazy_loaded_codec


if ta.TYPE_CHECKING:
    import gzip
    import zlib
else:
    gzip = lang.proxy_import('gzip')
    zlib = lang.proxy_import('zlib')


##


COMPRESS_LEVEL_FAST = 1
COMPRESS_LEVEL_TRADEOFF = 6
COMPRESS_LEVEL_BEST = 9


@dc.dataclass(frozen=True, kw_only=True)
class GzipCompression(Compression, IncrementalCompression):
    level: int = COMPRESS_LEVEL_BEST

    mtime: float | None = None

    def compress(self, d: bytes) -> bytes:
        return gzip.compress(
            d,
            self.level,
            mtime=self.mtime,
        )

    def decompress(self, d: bytes) -> bytes:
        return gzip.decompress(
            d,
        )

    def compress_incremental(self) -> BytesSteppedCoro[None]:
        return lang.nextgen(IncrementalGzipCompressor(
            level=self.level,
            mtime=self.mtime,
        )())

    def decompress_incremental(self) -> BytesSteppedReaderCoro[None]:
        return IncrementalGzipDecompressor()()


##


@cached.function
def _zero_crc() -> int:
    return zlib.crc32(b'')


##


class IncrementalGzipCompressor:
    def __init__(
            self,
            *,
            level: int = COMPRESS_LEVEL_BEST,
            name: str | bytes | None = None,
            mtime: float | None = None,
    ) -> None:
        super().__init__()

        self._name = name or ''
        self._level = level
        self._mtime = mtime

    def _write_gzip_header(self) -> ta.Generator[bytes, None, None]:
        check.none((yield b'\037\213'))  # magic header
        check.none((yield b'\010'))  # compression method

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
        check.none((yield chr(flags).encode('latin-1')))

        mtime = self._mtime
        if mtime is None:
            mtime = time.time()
        check.none((yield struct.pack('<L', int(mtime))))

        if self._level == COMPRESS_LEVEL_BEST:
            xfl = b'\002'
        elif self._level == COMPRESS_LEVEL_FAST:
            xfl = b'\004'
        else:
            xfl = b'\000'
        check.none((yield xfl))

        check.none((yield b'\377'))

        if fname:
            check.none((yield fname + b'\000'))

    def __call__(self) -> BytesSteppedCoro:
        crc = _zero_crc()
        size = 0
        offset = 0  # Current file offset for seek(), tell(), etc
        wrote_header = False

        compress = zlib.compressobj(
            self._level,
            zlib.DEFLATED,
            -zlib.MAX_WBITS,
            zlib.DEF_MEM_LEVEL,
            0,
        )

        while True:
            data: ta.Any = check.isinstance((yield None), bytes)

            if not wrote_header:
                yield from self._write_gzip_header()
                wrote_header = True

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
                if (fl := compress.compress(data)):
                    check.none((yield fl))
                size += length
                crc = zlib.crc32(data, crc)
                offset += length

        if (fl := compress.flush()):
            check.none((yield fl))

        yield struct.pack('<L', crc)
        # size may exceed 2 GiB, or even 4 GiB
        yield struct.pack('<L', size & 0xffffffff)

        yield b''


##


class IncrementalGzipDecompressor:
    def __init__(self) -> None:
        super().__init__()

        self._factory = functools.partial(
            zlib.decompressobj,
            wbits=-zlib.MAX_WBITS,
        )

    def _read_gzip_header(
            self,
            rdr: PrependableBytesCoroReader,
    ) -> ta.Generator[int | None, bytes, int | None]:
        magic = yield from rdr.read(2)
        if magic == b'':
            return None

        if magic != b'\037\213':
            raise gzip.BadGzipFile(f'Not a gzipped file ({magic!r})')

        buf = yield from rdr.read(8)
        method, flag, last_mtime = struct.unpack('<BBIxx', buf)
        if method != 8:
            raise gzip.BadGzipFile('Unknown compression method')

        if flag & gzip.FEXTRA:
            # Read & discard the extra field, if present
            buf = yield from rdr.read(2)
            extra_len, = struct.unpack('<H', buf)
            if extra_len:
                yield from rdr.read(extra_len)

        if flag & gzip.FNAME:
            # Read and discard a null-terminated string containing the filename
            while True:
                s = yield from rdr.read(1)
                if not s or s == b'\000':
                    break

        if flag & gzip.FCOMMENT:
            # Read and discard a null-terminated string containing a comment
            while True:
                s = yield from rdr.read(1)
                if not s or s == b'\000':
                    break

        if flag & gzip.FHCRC:
            yield from rdr.read(2)  # Read & discard the 16-bit header CRC

        return last_mtime

    def _read_eof(
            self,
            rdr: PrependableBytesCoroReader,
            crc: int,
            stream_size: int,
    ) -> ta.Generator[int | None, bytes, None]:
        # We've read to the end of the file.
        # We check that the computed CRC and size of the uncompressed data matches the stored values. Note that the size
        # stored is the true file size mod 2**32.
        buf = yield from rdr.read(8)
        crc32, isize = struct.unpack('<II', buf)
        if crc32 != crc:
            raise gzip.BadGzipFile(f'CRC check failed {hex(crc32)} != {hex(crc)}')
        elif isize != (stream_size & 0xffffffff):
            raise gzip.BadGzipFile('Incorrect length of data produced')

        # Gzip files can be padded with zeroes and still have archives. Consume all zero bytes and set the file position
        # to the first non-zero byte. See http://www.gzip.org/#faq8
        c = b'\0'
        while c == b'\0':
            c = yield from rdr.read(1)
        if c:
            rdr.prepend(c)

    def __call__(self) -> BytesSteppedReaderCoro:
        rdr = PrependableBytesCoroReader()

        pos = 0  # Current offset in decompressed stream

        crc = _zero_crc()
        stream_size = 0  # Decompressed size of unconcatenated stream
        new_member = True

        decompressor = self._factory()

        while True:
            # For certain input data, a single call to decompress() may not return any data. In this case, retry until
            # we get some data or reach EOF.
            while True:
                if decompressor.eof:
                    # Ending case: we've come to the end of a member in the file, so finish up this member, and read a
                    # new gzip header. Check the CRC and file size, and set the flag so we read a new member
                    yield from self._read_eof(rdr, crc, stream_size)
                    new_member = True
                    decompressor = self._factory()

                if new_member:
                    # If the _new_member flag is set, we have to jump to the next member, if there is one.
                    crc = _zero_crc()
                    stream_size = 0  # Decompressed size of unconcatenated stream
                    last_mtime = yield from self._read_gzip_header(rdr)
                    if not last_mtime:
                        check.none((yield b''))
                        return
                    new_member = False

                # Read a chunk of data from the file
                if not decompressor.unconsumed_tail:
                    buf = yield from rdr.read(None)
                    uncompress = decompressor.decompress(buf)
                else:
                    uncompress = decompressor.decompress(b'')

                if decompressor.unused_data != b'':
                    # Prepend the already read bytes to the fileobj so they can be seen by _read_eof() and
                    # _read_gzip_header()
                    rdr.prepend(decompressor.unused_data)

                if uncompress != b'':
                    break
                if buf == b'':  # noqa
                    raise EOFError('Compressed file ended before the end-of-stream marker was reached')

            crc = zlib.crc32(uncompress, crc)
            stream_size += len(uncompress)
            pos += len(uncompress)
            check.none((yield uncompress))


##


GZIP_CODEC = make_compression_codec('gzip', GzipCompression, aliases=['gz'])

# @omlish-manifest
_GZIP_LAZY_CODEC = make_compression_lazy_loaded_codec(__name__, 'GZIP_CODEC', GZIP_CODEC)
