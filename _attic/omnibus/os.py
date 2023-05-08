"""
TODO:
 - diag.py? or just psutil..
 - os.readenv - bash exec script args (like ~/.bashrc) -> run env, return map
  - default to bashrc
  - loadenv to set envs read
  - mitigator for osx pycharm not loading bashrc
  - option to not inherit existing env
  - option to not overwrite existing keys
  - keep: ta.Iterable[str] = None
"""
import codecs
import contextlib
import errno
import fcntl
import functools
import locale
import os
import resource
import shutil
import signal
import socket
import stat
import struct
import subprocess
import sys
import tempfile
import time
import typing as ta

from . import lang
from . import libc
from .libc import DARWIN
from .libc import LINUX


PAGE_SIZE = resource.getpagesize()


def round_to_page_size(sz: int) -> int:
    sz += PAGE_SIZE - 1
    return sz - (sz % PAGE_SIZE)


def check_locales() -> None:
    try:
        fs_enc = codecs.lookup(locale.getpreferredencoding()).name
    except Exception:  # noqa
        fs_enc = 'ascii'
    if fs_enc == 'ascii':
        raise RuntimeError('Rerun with env LC_ALL=en_US.utf-8;LANG=en_US.utf-8')


@contextlib.contextmanager
def signal_handling(
        handler: ta.Union['signal.Handlers', ta.Callable[[int, ta.Any], None]],
        sigs: ta.Iterable[int]
):
    if not callable(handler):
        raise TypeError(handler)

    sigs = list(sigs)

    previous_handlers = [
        signal.signal(
            sig,
            handler if not isinstance(handler, signal.Handlers) else functools.partial(handler, sig))  # type: ignore
        for sig in sigs]

    try:
        yield

    finally:
        # Per https://bugs.python.org/msg236894 don't bother when interpreter is shutting down
        if not sys.is_finalizing():
            for sig, previous_handler in zip(sigs, previous_handlers):
                signal.signal(sig, previous_handler)


def get_sock_cred(conn: socket.socket) -> ta.Tuple[int, int, int]:
    if LINUX:
        creds = conn.getsockopt(socket.SOL_SOCKET, libc.SO_PEERCRED, struct.calcsize('3i'))
    elif DARWIN:
        creds = conn.getsockopt(libc.SOL_LOCAL, libc.LOCAL_PEERCRED, struct.calcsize('3i'))
    else:
        raise OSError

    pid, uid, gid = struct.unpack('3i', creds)
    return pid, uid, gid


def find_free_port() -> int:
    with contextlib.closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
        s.bind(('', 0))
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        return s.getsockname()[1]


def set_cloexec_flag(fd: int, value: bool) -> int:
    oldflags = fcntl.fcntl(fd, fcntl.F_GETFD, 0)
    if oldflags < 0:
        return oldflags
    if value:
        oldflags |= fcntl.FD_CLOEXEC
    else:
        oldflags &= ~fcntl.FD_CLOEXEC
    return fcntl.fcntl(fd, fcntl.F_SETFD, oldflags)


def try_lock(fd: int) -> bool:
    try:
        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except IOError:
        return False
    else:
        return True


def safe_rmtree(path: str) -> bool:
    if os.path.exists(path):
        shutil.rmtree(path, True)
        return True
    else:
        return False


def safe_unlink(path: str) -> bool:
    try:
        os.unlink(path)
        return True
    except OSError as e:
        if e.errno != errno.ENOENT:
            raise
        return False


@contextlib.contextmanager
def tmp_chdir(cwd: str) -> ta.Iterator[None]:
    old = os.getcwd()
    os.chdir(cwd)
    try:
        yield
    finally:
        os.chdir(old)


@contextlib.contextmanager
def tmp_dir(root_dir: str = None, cleanup: bool = True) -> ta.Iterator[str]:
    path = tempfile.mkdtemp(dir=root_dir)
    try:
        yield path
    finally:
        if cleanup:
            shutil.rmtree(path, ignore_errors=True)


@contextlib.contextmanager
def tmp_file(root_dir: str = None, cleanup: bool = True) -> ta.Iterator[tempfile._TemporaryFileWrapper]:  # type: ignore  # noqa
    with tempfile.NamedTemporaryFile(dir=root_dir, delete=False) as f:
        try:
            yield f
        finally:
            if cleanup:
                shutil.rmtree(f.name, ignore_errors=True)


def atomic_write_file(file_path: str, contents: bytes) -> None:
    base_path = os.path.dirname(file_path)
    fd, temp_file_path = tempfile.mkstemp(dir=base_path)
    try:
        os.write(fd, contents)
        os.fsync(fd)
    except Exception:
        raise
    finally:
        os.close(fd)
    os.rename(temp_file_path, file_path)


class SubprocessLike(lang.Protocol):

    @property
    def pid(self) -> int:
        raise NotImplementedError

    def poll(self) -> ta.Optional[int]:
        raise NotImplementedError

    def wait(self, timeout: int = None) -> int:
        raise NotImplementedError


@lang.protocol_check(SubprocessLike)
class TempSubprocess:

    def __init__(
            self,
            args: ta.Sequence[str],
            *,
            deathsig: int = signal.SIGTERM,
    ) -> None:
        super().__init__()

        self._args = args
        pid = os.fork()
        if not pid:
            if hasattr(libc, 'prctl'):
                libc.prctl(libc.PR_SET_PDEATHSIG, deathsig, 0, 0, 0, 0)
            os.execvp(args[0], list(args))
            raise RuntimeError
        self._pid = pid
        self._returncode: ta.Optional[int] = None

    @property
    def pid(self) -> int:
        return self._pid

    def poll(self) -> ta.Optional[int]:
        try:
            return self.wait(0)
        except subprocess.TimeoutExpired:
            return None

    def wait(self, timeout: int = None) -> int:
        if self._returncode is not None:
            return self._returncode

        if timeout is not None:
            endtime = time.time() + timeout
            delay = 0.0005
            while True:
                pid, rc = os.waitpid(self._pid, os.P_NOWAIT)
                if pid == self._pid:
                    self._returncode = rc
                    return rc
                remaining = endtime - time.time()
                if remaining < 0:
                    raise subprocess.TimeoutExpired(self._args, timeout)
                delay = min(delay * 2, remaining, .05)
                time.sleep(delay)

        else:
            pid, rc = os.waitpid(self._pid, os.P_NOWAIT)
            if pid != self._pid:
                raise RuntimeError(pid)
            self._returncode = rc
            return rc


def create_symlink(real_path: str, symlink_path: str) -> None:
    try:
        os.unlink(symlink_path)
    except OSError as ose:
        if ose.errno != errno.ENOENT:
            raise ose
    os.symlink(real_path, symlink_path)


def clone_dir(src: str, dst: str, *, deep: bool = True) -> None:
    if not os.path.isdir(src):
        raise ValueError(src)
    if os.path.exists(dst):
        raise ValueError(dst)
    os.mkdir(dst)
    for obj_name in os.listdir(src):
        src_path = os.path.join(src, obj_name)
        dst_path = os.path.join(dst, obj_name)
        if os.path.isfile(src_path):
            os.link(src_path, dst_path)
        elif os.path.isdir(src_path):
            if deep:
                clone_dir(src_path, dst_path)
        else:
            raise TypeError(src_path)


def set_path_readonly(path: str) -> None:
    mode = os.stat(path).st_mode
    mode &= ~(stat.S_IWUSR | stat.S_IWUSR | stat.S_IWOTH)
    os.chmod(path, mode)


def os_exit(status: int) -> None:
    os._exit(status)  # noqa
