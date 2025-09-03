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

from omlish import check
from omlish import lang


if ta.TYPE_CHECKING:
    import bz2

    import lz4.frame as lz4_frame

else:
    bz2 = lang.proxy_import('bz2')

    lz4_frame = lang.proxy_import('lz4.frame')


##


class BytesReaderWrapper(ta.IO[bytes], lang.Abstract):
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
            f'{int(bytes_ela / time_ela):_} B/s',  # type: ignore
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
) -> ta.Iterator[tuple[ta.IO, FileProgressReporter | None]]:
    bs: ta.IO
    fpr: FileProgressReporter | None
    with contextlib.ExitStack() as es:
        if fp.endswith('.bz2'):
            if not use_subprocess:
                f = es.enter_context(open(fp, 'rb'))
                fpr = FileProgressReporter(f, time_interval=5)

                bs = es.enter_context(contextlib.closing(bz2.open(f, 'rb')))

            else:
                f = es.enter_context(open(fp, 'rb'))

                # FIXME: os.dup?
                # fpr = FileProgressReporter(f, time_interval=5)
                fpr = None

                proc = subprocess.Popen(['bzip2', '-cdk', fp], stdout=subprocess.PIPE, stdin=f)
                bs = check.not_none(proc.stdout)

        elif fp.endswith('.lz4'):
            if not use_subprocess:
                f = es.enter_context(open(fp, 'rb'))
                fpr = FileProgressReporter(f, time_interval=5)

                bs = es.enter_context(contextlib.closing(lz4_frame.open(f, 'rb')))

            else:
                f = es.enter_context(open(fp, 'rb'))

                # FIXME: os.dup?
                # fpr = FileProgressReporter(f, time_interval=5)
                fpr = None

                proc = subprocess.Popen(['lz4', '-cdk', fp], stdout=subprocess.PIPE, stdin=f)
                bs = check.not_none(proc.stdout)

        else:
            raise RuntimeError(fp)

        yield bs, fpr


##


class MultiFileWriter:
    @ta.runtime_checkable
    class File(ta.Protocol):
        def close(self) -> None:
            ...

        def tell(self) -> int:
            ...

        def write(self, buf: bytes) -> None:
            ...

    def __init__(
            self,
            file_opener: ta.Callable[[str], File],
            file_pat: str,
            file_size: int = 2 * 1024 * 1024 * 1024,
            *,
            use_input_size: bool = False,
    ) -> None:
        super().__init__()

        self._file_opener = file_opener
        self._file_pat = file_pat
        self._file_size = file_size
        self._use_input_size = use_input_size

        self._cur_n = 0
        self._total_b = 0
        self._cur_b = 0
        self._cur_f: MultiFileWriter.File | None = None

    def close(self) -> None:
        if self._cur_f is not None:
            self._cur_f.close()
            self._cur_f = None

        self._cur_b = 0

    def write(self, *bufs: bytes) -> None:
        if self._cur_f is None:
            self._cur_f = self._file_opener(self._file_pat % (self._cur_n,))

        for buf in bufs:
            self._cur_b += len(buf)
            self._total_b += len(buf)
            self._cur_f.write(buf)

        if (self._cur_f.tell() if self._use_input_size else self._cur_b) >= self._file_size:
            self.close()
            self._cur_n += 1


@lang.protocol_check(MultiFileWriter.File)
class Lz4MfwFile:
    def __init__(self, fp: str) -> None:
        super().__init__()

        self._raw_f = open(fp, 'wb')  # noqa
        self._z_f = lz4_frame.open(self._raw_f, 'wb')

    def close(self) -> None:
        self._z_f.close()
        self._raw_f.close()

    def tell(self) -> int:
        return self._raw_f.tell()

    def write(self, buf: bytes) -> None:
        self._z_f.write(buf)
