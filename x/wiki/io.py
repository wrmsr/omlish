"""
TODO:
 - BZ2File / _compression.DecompressionReader does this, but point is parallel decomp
  - chop stream
"""
import abc
import os
import sys
import time
import typing as ta

from omlish import lang


if ta.TYPE_CHECKING:
    import bz2

else:
    bz2 = lang.proxy_import('bz2')


#


class BytesReaderWrapper(ta.IO[bytes], abc.ABC):
    def __init__(self, f: ta.IO[bytes]) -> None:
        super().__init__()
        self._f = f

    def close(self):
        raise TypeError

    def fileno(self):
        return self._f.fileno()

    def flush(self):
        raise TypeError

    def isatty(self):
        return self._f.isatty()

    @abc.abstractmethod
    def read(self, n=-1):
        raise NotImplementedError

    def readable(self):
        return self._f.readable()

    def readline(self, limit=-1):
        raise TypeError

    def readlines(self, hint=-1):
        raise TypeError

    def seek(self, offset, whence=0):
        raise TypeError

    def seekable(self):
        return False

    def tell(self):
        return self._f.tell()

    def truncate(self, size=None):
        raise TypeError

    def writable(self):
        return self._f.writable()

    def write(self, s):
        raise TypeError

    def writelines(self, lines):
        raise TypeError

    def __next__(self):
        raise TypeError

    def __iter__(self):
        raise TypeError

    def __enter__(self):
        raise TypeError

    def __exit__(self, et, e, tb):
        raise TypeError


#


class Bz2ReaderWrapper(BytesReaderWrapper):
    """
    TODO:
     - parallel decompress
    """

    def __init__(self, f: ta.IO[bytes]) -> None:
        super().__init__(f)
        self._b = bz2.BZ2Decompressor()
        self._c = 0
        self._e = False
        self._x: bytes | None = None

    def read(self, n=-1):
        while True:
            if self._e or not (r := self._f.read(n)):
                self._e = True

                if self._x:
                    r = self._x
                    self._x = None
                    return r

                if self._c and not self._b.eof:
                    raise Exception('not at eof')

                return b''

            if self._b.eof:
                u = self._b.unused_data
                self._b = bz2.BZ2Decompressor()
                self._c = 0
                if u:
                    self._x = self._b.decompress(u)

            self._c += len(r)
            ret = self._b.decompress(r)
            if self._x:
                ret = self._x + ret
                self._x = None

            if self._b.eof:
                u = self._b.unused_data
                self._b = bz2.BZ2Decompressor()
                self._c = 0
                if u:
                    self._x = self._b.decompress(u)

            if ret:
                return ret


##


class FileProgressReporter:
    def __init__(
            self,
            f: ta.Any,
            *,
            out: ta.Any = sys.stderr,
            time_interval: float | None = 1.,
            bytes_interval: int | None = None,
    ) -> None:
        super().__init__()
        self._f = f
        self._out = out
        self._time_interval = time_interval
        self._bytes_interval = bytes_interval

        self._bytes_tot = os.fstat(f.fileno()).st_size
        self._bytes_last = 0
        self._time_last = time.time()

    def _time_pos(self) -> tuple[float, float]:
        time_cur = time.time()
        time_ela = time_cur - self._time_last
        return time_cur, time_ela

    def _bytes_pos(self) -> tuple[int, int]:
        bytes_cur = self._f.tell()
        bytes_ela = bytes_cur - self._bytes_last
        return bytes_cur, bytes_ela

    def report(self) -> None:
        should_report = False

        if self._time_interval is not None:
            time_cur, time_ela = self._time_pos()
            should_report |= time_ela >= self._time_interval
        else:
            time_cur, time_ela = None, None

        if self._bytes_interval is not None:
            bytes_cur, bytes_ela = self._bytes_pos()
            should_report |= bytes_ela >= self._bytes_interval
        else:
            bytes_cur, bytes_ela = None, None

        if not should_report:
            return

        if time_cur is None:
            time_cur, time_ela = self._time_pos()
        if bytes_cur is None:
            bytes_cur, bytes_ela = self._bytes_pos()

        print(
            f'{bytes_cur:_} b / {self._bytes_tot:_} b - '
            f'{bytes_cur / self._bytes_tot:.2f} % - '
            f'{int(bytes_ela / time_ela):_} b/s',
            file=self._out,
        )

        self._bytes_last = bytes_cur
        self._time_last = time_cur
