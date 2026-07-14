# ruff: noqa: UP006 UP007 UP045
import errno
import os
import typing as ta

from .ostypes import Fd


##


class PipeFds(ta.NamedTuple):
    r: Fd
    w: Fd


def make_pipe() -> PipeFds:
    return PipeFds(*os.pipe())  # type: ignore


def read_fd(fd: Fd) -> bytes:
    try:
        data = os.read(fd, 2 << 16)  # 128K
    except OSError as why:
        if why.args[0] not in (errno.EWOULDBLOCK, errno.EBADF, errno.EINTR):
            raise
        data = b''
    return data


def close_fd(fd: Fd) -> bool:
    try:
        os.close(fd)
    except OSError:
        return False
    return True


def is_fd_open(fd: Fd) -> bool:
    try:
        n = os.dup(fd)
    except OSError:
        return False
    os.close(n)
    return True


def get_open_fds(limit: int) -> ta.FrozenSet[Fd]:
    return frozenset(fd for i in range(limit) if is_fd_open(fd := Fd(i)))
