# ruff: noqa: UP006 UP007 UP045
# @omlish-lite
import os.path
import typing as ta


##


@ta.overload
def path_dirname(p: str, n: int = 1) -> str:
    ...


@ta.overload
def path_dirname(p: bytes, n: int = 1) -> bytes:
    ...


def path_dirname(p, n=1):
    if isinstance(p, bytes):
        sep: ta.Any = b'/'
    else:
        sep = '/'
    p = os.fspath(p)
    i = -1
    for _ in range(n):
        i = p.rindex(sep, 0, i)
    head = p[:i + 1]
    if head and head != sep * len(head):
        head = head.rstrip(sep)
    return head


def abs_real_path(p: str) -> str:
    return os.path.abspath(os.path.realpath(p))


def is_path_in_dir(base_dir: str, target_path: str) -> bool:
    base_dir = abs_real_path(base_dir)
    target_path = abs_real_path(target_path)

    return target_path.startswith(base_dir + os.path.sep)


def relative_symlink(
        src: str,
        dst: str,
        *,
        target_is_directory: bool = False,
        dir_fd: ta.Optional[int] = None,
        make_dirs: bool = False,
        **kwargs: ta.Any,
) -> None:
    if make_dirs:
        os.makedirs(os.path.dirname(dst), exist_ok=True)

    os.symlink(
        os.path.relpath(src, os.path.dirname(dst)),
        dst,
        target_is_directory=target_is_directory,
        dir_fd=dir_fd,
        **kwargs,
    )
