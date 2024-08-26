import contextlib
import fcntl
import os
import resource
import shutil
import signal
import tempfile
import typing as ta


PAGE_SIZE = resource.getpagesize()


def round_to_page_size(sz: int) -> int:
    sz += PAGE_SIZE - 1
    return sz - (sz % PAGE_SIZE)


@contextlib.contextmanager
def tmp_dir(
        root_dir: str | None = None,
        cleanup: bool = True,
        **kwargs: ta.Any,
) -> ta.Iterator[str]:
    path = tempfile.mkdtemp(dir=root_dir, **kwargs)
    try:
        yield path
    finally:
        if cleanup:
            shutil.rmtree(path, ignore_errors=True)


@contextlib.contextmanager
def tmp_file(
        root_dir: str | None = None,
        cleanup: bool = True,
        **kwargs: ta.Any,
) -> ta.Iterator[tempfile._TemporaryFileWrapper]:  # noqa
    with tempfile.NamedTemporaryFile(dir=root_dir, delete=False, **kwargs) as f:
        try:
            yield f
        finally:
            if cleanup:
                shutil.rmtree(f.name, ignore_errors=True)


class Pidfile:
    def __init__(self, path: str) -> None:
        super().__init__()
        self._path = path

    _f: ta.TextIO

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({self._path!r})'

    def __enter__(self) -> ta.Self:
        fd = os.open(self._path, os.O_RDWR | os.O_CREAT, 0o600)
        try:
            os.set_inheritable(fd, True)
            f = os.fdopen(fd, 'r+')
        except Exception:
            try:
                os.close(fd)
            except Exception:  # noqa
                pass
            raise
        self._f = f
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._f is not None:
            self._f.close()
            del self._f

    def try_lock(self) -> bool:
        try:
            fcntl.flock(self._f, fcntl.LOCK_EX | fcntl.LOCK_NB)
            return True
        except OSError:
            return False

    def write(self, pid: int | None = None) -> None:
        if not self.try_lock():
            raise RuntimeError('Could not get lock')
        if pid is None:
            pid = os.getpid()
        self._f.write(f'{pid}\n')
        self._f.flush()

    def clear(self) -> None:
        if not self.try_lock():
            raise RuntimeError('Could not get lock')
        self._f.seek(0)
        self._f.truncate()

    def read(self) -> int:
        if self.try_lock():
            raise RuntimeError('Got lock')
        self._f.seek(0)
        return int(self._f.read())

    def kill(self, sig: int = signal.SIGTERM) -> None:
        pid = self.read()
        os.kill(pid, sig)  # Still racy
