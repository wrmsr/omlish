# ruff: noqa: UP006 UP007
# @omlish-lite
import contextlib
import os
import typing as ta


def touch(path: str, mode: int = 0o666, exist_ok: bool = True) -> None:
    if exist_ok:
        # First try to bump modification time
        # Implementation note: GNU touch uses the UTIME_NOW option of the utimensat() / futimens() functions.
        try:
            os.utime(path, None)
        except OSError:
            pass
        else:
            return

    flags = os.O_CREAT | os.O_WRONLY
    if not exist_ok:
        flags |= os.O_EXCL

    fd = os.open(path, flags, mode)
    os.close(fd)


def unlink_if_exists(path: str) -> None:
    try:
        os.unlink(path)
    except FileNotFoundError:
        pass


@contextlib.contextmanager
def unlinking_if_exists(path: str) -> ta.Iterator[None]:
    try:
        yield
    finally:
        unlink_if_exists(path)
