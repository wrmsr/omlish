# ruff: noqa: UP007 UP045
# @omlish-lite
"""
TODO:
 - 'json pids', with code version? '.json.pid'? '.jpid'?
  - json*L* pidfiles - first line is bare int, following may be json - now `head -n1 foo.pid` not cat
"""
import errno
import fcntl
import os
import signal
import typing as ta


##


class Pidfile:
    def __init__(
            self,
            path: str,
            *,
            inheritable: bool = True,
            no_create: bool = False,
    ) -> None:
        super().__init__()

        self._path = path
        self._inheritable = inheritable
        self._no_create = no_create

    @property
    def path(self) -> str:
        return self._path

    @property
    def inheritable(self) -> bool:
        return self._inheritable

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({self._path!r})'

    #

    _f: ta.TextIO

    def fileno(self) -> ta.Optional[int]:
        if hasattr(self, '_f'):
            return self._f.fileno()
        else:
            return None

    #

    _fd_to_dup: int

    def dup(self) -> 'Pidfile':
        fd = self._f.fileno()
        dup = Pidfile(
            self._path,
            inheritable=self._inheritable,
        )
        dup._fd_to_dup = fd  # noqa
        return dup

    #

    def __enter__(self) -> 'Pidfile':
        if hasattr(self, '_fd_to_dup'):
            fd = os.dup(self._fd_to_dup)
            del self._fd_to_dup

        else:
            ofl = os.O_RDWR
            if not self._no_create:
                ofl |= os.O_CREAT
            fd = os.open(self._path, ofl, 0o600)

        try:
            if self._inheritable:
                os.set_inheritable(fd, True)

            f = os.fdopen(fd, 'r+')

        except BaseException:
            os.close(fd)
            raise

        self._f = f
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    #

    def __getstate__(self):
        state = self.__dict__.copy()

        if '_f' in state:
            # self._inheritable may be decoupled from actual file inheritability - for example when using the manager.
            if os.get_inheritable(fd := state.pop('_f').fileno()):
                state['__fd'] = fd

        return state

    def __setstate__(self, state):
        if '_f' in state:
            raise RuntimeError

        if '__fd' in state:
            state['_f'] = os.fdopen(state.pop('__fd'), 'r+')

        self.__dict__.update(state)

    #

    def close(self) -> bool:
        if not hasattr(self, '_f'):
            return False

        self._f.close()
        del self._f
        return True

    def try_acquire_lock(self) -> bool:
        try:
            fcntl.flock(self._f, fcntl.LOCK_EX | fcntl.LOCK_NB)
            return True

        except BlockingIOError as e:
            if e.errno == errno.EAGAIN:
                return False
            else:
                raise

    #

    class Error(Exception):
        pass

    class LockedError(Error):
        pass

    def acquire_lock(self) -> None:
        if not self.try_acquire_lock():
            raise self.LockedError

    class NotLockedError(Error):
        pass

    def ensure_cannot_lock(self) -> None:
        if self.try_acquire_lock():
            raise self.NotLockedError

    #

    def write(
            self,
            pid: ta.Optional[int] = None,
            *,
            suffix: ta.Optional[str] = None,
    ) -> None:
        self.acquire_lock()

        if pid is None:
            pid = os.getpid()

        self._f.seek(0)
        self._f.truncate()
        self._f.write('\n'.join([
            str(pid),
            *([suffix] if suffix is not None else []),
            '',
        ]))
        self._f.flush()

    def clear(self) -> None:
        self.acquire_lock()

        self._f.seek(0)
        self._f.truncate()

    #

    def read_raw(self) -> ta.Optional[str]:
        self.ensure_cannot_lock()

        self._f.seek(0)
        buf = self._f.read()
        if not buf:
            return None
        return buf

    def read(self) -> ta.Optional[int]:
        buf = self.read_raw()
        if not buf:
            return None
        return int(buf.splitlines()[0].strip())

    def kill(self, sig: int = signal.SIGTERM) -> None:
        if (pid := self.read()) is None:
            raise self.Error(f'Pidfile locked but empty')
        os.kill(pid, sig)
