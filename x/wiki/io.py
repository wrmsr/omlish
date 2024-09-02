"""
TODO:
 - BZ2File / _compression.DecompressionReader does this, but point is parallel decomp
  - chop stream
   - possible at all? pbzip2 explodes
   - https://github.com/ruanhuabin/pbzip2
   - https://en.wikipedia.org/wiki/Bzip2
"""
import abc
import contextlib
import os
import subprocess
import sys
import time
import typing as ta


##


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

    def report(self) -> bool:
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
            return False

        if time_cur is None:
            time_cur, time_ela = self._time_pos()
        if bytes_cur is None:
            bytes_cur, bytes_ela = self._bytes_pos()

        print(
            f'{bytes_cur:_} B / {self._bytes_tot:_} B - '
            f'{bytes_cur / self._bytes_tot * 100.:.2f} % - '
            f'{int(bytes_ela / time_ela):_} B/s',
            file=self._out,
        )

        self._bytes_last = bytes_cur
        self._time_last = time_cur

        return True


##


@contextlib.contextmanager
def open_compressed_reader(
        fp: str,
        *,
        use_subprocess: bool = False,
) -> tuple[ta.IO, FileProgressReporter | None]:
    with contextlib.ExitStack() as es:
        if fp.endswith('.bz2'):
            if not use_subprocess:
                f = es.enter_context(open(fp, 'rb'))
                fpr = FileProgressReporter(f, time_interval=5)

                import bz2
                bs = es.enter_context(contextlib.closing(bz2.open(f, 'rb')))

            else:
                f = es.enter_context(open(fp, 'rb'))

                # FIXME: os.dup?
                # fpr = FileProgressReporter(f, time_interval=5)
                fpr = None

                proc = subprocess.Popen(['bzip2', '-cdk', fp], stdout=subprocess.PIPE, stdin=f)
                bs = proc.stdout

        elif fp.endswith('.lz4'):
            if not use_subprocess:
                f = es.enter_context(open(fp, 'rb'))
                fpr = FileProgressReporter(f, time_interval=5)

                import lz4.frame
                bs = es.enter_context(contextlib.closing(lz4.frame.open(f, 'rb')))

            else:
                f = es.enter_context(open(fp, 'rb'))

                # FIXME: os.dup?
                # fpr = FileProgressReporter(f, time_interval=5)
                fpr = None

                proc = subprocess.Popen(['lz4', '-cdk', fp], stdout=subprocess.PIPE, stdin=f)
                bs = proc.stdout

        else:
            raise RuntimeError(fp)

        yield bs, fpr
