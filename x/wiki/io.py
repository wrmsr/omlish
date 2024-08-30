import abc
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
