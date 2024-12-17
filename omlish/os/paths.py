# @omlish-lite
import os.path
import typing as ta


def abs_real_path(p: str) -> str:
    return os.path.abspath(os.path.realpath(p))


def is_path_in_dir(base_dir: str, target_path: str) -> bool:
    base_dir = abs_real_path(base_dir)
    target_path = abs_real_path(target_path)

    return target_path.startswith(base_dir + os.path.sep)


def relative_symlink(src: str, dst: str, **kwargs: ta.Any) -> None:
    os.symlink(os.path.relpath(src, os.path.dirname(dst)), dst, **kwargs)
