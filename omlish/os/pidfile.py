# ruff: noqa: UP007
# @omlish-lite
import fcntl
import os
import signal
import typing as ta


class Pidfile:
    def __init__(
            self,
            path: str,
            *,
            non_inheritable: bool = False,
    ) -> None:
        super().__init__()

        self._path = path
        self._non_inheritable = non_inheritable

    _f: ta.TextIO

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({self._path!r})'

    def __enter__(self) -> 'Pidfile':
        fd = os.open(self._path, os.O_RDWR | os.O_CREAT, 0o600)

        try:
            if not self._non_inheritable:
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
        self.close()

    def close(self) -> bool:
        if not hasattr(self, '_f'):
            return False

        self._f.close()
        del self._f
        return True

    def fileno(self) -> ta.Optional[int]:
        if hasattr(self, '_f'):
            return self._f.fileno()
        else:
            return None

    def try_lock(self) -> bool:
        try:
            fcntl.flock(self._f, fcntl.LOCK_EX | fcntl.LOCK_NB)
            return True
        except OSError:
            return False

    def ensure_locked(self) -> None:
        if not self.try_lock():
            raise RuntimeError('Could not get lock')

    def write(self, pid: ta.Optional[int] = None) -> None:
        self.ensure_locked()

        if pid is None:
            pid = os.getpid()

        self._f.write(f'{pid}\n')
        self._f.flush()

    def clear(self) -> None:
        self.ensure_locked()

        self._f.seek(0)
        self._f.truncate()

    def read(self) -> int:
        if self.try_lock():
            raise RuntimeError('Got lock')

        self._f.seek(0)
        return int(self._f.read())  # FIXME: could be empty or hold old value, race w proc start

    def kill(self, sig: int = signal.SIGTERM) -> None:
        pid = self.read()
        os.kill(pid, sig)  # FIXME: Still racy - pidfd_send_signal?
