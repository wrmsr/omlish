import functools
import gzip
import os.path
import struct
import time
import typing as ta
import zlib


COMPRESS_LEVEL_FAST = 1
COMPRESS_LEVEL_TRADEOFF = 6
COMPRESS_LEVEL_BEST = 9


##


class BufferedBytesReaderGenerator:
    def __init__(self) -> None:
        super().__init__()
        self._buffer: list[bytes] = []

    class ReadError(Exception):
        pass

    def read(self, sz: int | None) -> ta.Generator[int | None, bytes, bytes]:
        if not self._buffer:
            d = yield sz
            return d

        if sz is None:
            return self._buffer.pop(0)

        l: list[bytes] = []
        r = sz
        while r > 0 and self._buffer:
            c = self._buffer[0]

            if len(c) > r:
                l.append(c[:r])
                self._buffer[0] = c[r:]
                return b''.join(l)

            l.append(c)
            r -= len(c)
            self._buffer.pop(0)

        if r:
            c = yield r
            if not c:
                return b''
            if len(c) != r:
                raise self.ReadError(f'Buffered reader got {len(c)} bytes, expected {r}')
            l.append(c)

        return b''.join(l)

    def inject(self, d: bytes) -> None:
        if d:
            self._buffer.append(d)


##


class IncrementalGzipReader:
    def __init__(self) -> None:
        super().__init__()

        self._kwargs = dict(
            wbits=-zlib.MAX_WBITS,
        )

        self._factory = functools.partial(zlib.decompressobj, **self._kwargs)

    def _read_gzip_header(self, rdr: BufferedBytesReaderGenerator) -> ta.Generator[int, bytes, int | None]:
        magic = yield from rdr.read(2)
        if magic == b'':
            return None

        if magic != b'\037\213':
            raise gzip.BadGzipFile('Not a gzipped file (%r)' % magic)

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
                if not s or s==b'\000':
                    break

        if flag & gzip.FHCRC:
            yield from rdr.read(2)  # Read & discard the 16-bit header CRC

        return last_mtime

    def _read_eof(
            self,
            rdr: BufferedBytesReaderGenerator,
            crc: int,
            stream_size: int,
    ) -> ta.Generator[int, bytes, int | None]:
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
        c = b'\x00'
        while c == b'\x00':
            c = yield from rdr.read(1)
        if c:
            return c[0]
        else:
            return None

    _ZERO_CRC = zlib.crc32(b'')

    def gen(self) -> ta.Generator[
        ta.Union[
            int,  # Read exactly n bytes
            None,  # Read any amount of bytes
            bytes,  # Uncompressed output
        ],
        ta.Union[
            bytes,  # Bytes read
            None,  # Next output
        ],
        None,
    ]:
        rdr = BufferedBytesReaderGenerator()

        pos = 0  # Current offset in decompressed stream

        crc = self._ZERO_CRC
        stream_size = 0  # Decompressed size of unconcatenated stream
        new_member = True

        decompressor = self._factory()

        while True:
            # For certain input data, a single call to decompress() may not return any data. In this case, retry until we
            # get some data or reach EOF.
            while True:
                if decompressor.eof:
                    # Ending case: we've come to the end of a member in the file, so finish up this member, and read a new
                    # gzip header. Check the CRC and file size, and set the flag so we read a new member
                    yield from self._read_eof(rdr, crc, stream_size)
                    new_member = True
                    decompressor = self._factory()

                if new_member:
                    # If the _new_member flag is set, we have to jump to the next member, if there is one.
                    crc = self._ZERO_CRC
                    stream_size = 0  # Decompressed size of unconcatenated stream
                    last_mtime = yield from self._read_gzip_header(rdr)
                    if not last_mtime:
                        yield b''
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
                    rdr.inject(decompressor.unused_data)

                if uncompress != b'':
                    break
                if buf == b'':  # noqa
                    raise EOFError('Compressed file ended before the end-of-stream marker was reached')

            crc = zlib.crc32(uncompress, crc)
            stream_size += len(uncompress)
            pos += len(uncompress)
            yield uncompress


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
