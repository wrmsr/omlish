# ruff: noqa: UP006 UP007
# @omlish-lite
import contextlib
import os
import shutil
import tempfile
import typing as ta

from .files import unlink_if_exists


def make_temp_file(**kwargs: ta.Any) -> str:
    file_fd, file = tempfile.mkstemp(**kwargs)
    os.close(file_fd)
    return file


@contextlib.contextmanager
def temp_file_context(**kwargs: ta.Any) -> ta.Iterator[str]:
    path = make_temp_file(**kwargs)
    try:
        yield path
    finally:
        unlink_if_exists(path)


@contextlib.contextmanager
def temp_dir_context(
        root_dir: ta.Optional[str] = None,
        **kwargs: ta.Any,
) -> ta.Iterator[str]:
    path = tempfile.mkdtemp(dir=root_dir, **kwargs)
    try:
        yield path
    finally:
        shutil.rmtree(path, ignore_errors=True)


@contextlib.contextmanager
def temp_named_file_context(
        root_dir: ta.Optional[str] = None,
        cleanup: bool = True,
        **kwargs: ta.Any,
) -> ta.Iterator[tempfile._TemporaryFileWrapper]:  # noqa
    with tempfile.NamedTemporaryFile(dir=root_dir, delete=False, **kwargs) as f:
        try:
            yield f
        finally:
            if cleanup:
                shutil.rmtree(f.name, ignore_errors=True)
