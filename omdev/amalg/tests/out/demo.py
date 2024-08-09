#!/usr/bin/env python3
"""
Hi!
"""
# also
# ruff: noqa: UP006 UP007
import contextlib
import functools
import logging
import os.path  # noqa
import pprint
import resource
import shutil
import subprocess
import sys
import tempfile
import typing as ta  # noqa


T = ta.TypeVar('T')


########################################
# ../../../std/cached.py


class cached_nullary:  # noqa
    def __init__(self, fn):
        super().__init__()
        self._fn = fn
        self._value = self._missing = object()
        functools.update_wrapper(self, fn)

    def __call__(self, *args, **kwargs):  # noqa
        if self._value is self._missing:
            self._value = self._fn()
        return self._value

    def __get__(self, instance, owner):  # noqa
        bound = instance.__dict__[self._fn.__name__] = self.__class__(self._fn.__get__(instance, owner))
        return bound


########################################
# ../../../std/check.py


def check_not_none(v: ta.Optional[T]) -> T:  # noqa
    if v is None:
        raise ValueError
    return v


def check_not(v: ta.Any) -> None:
    if v:
        raise ValueError(v)
    return v


########################################
# ../../../std/logging.py
"""
TODO:
 - debug
"""


log = logging.getLogger(__name__)


def setup_standard_logging() -> None:
    logging.root.addHandler(logging.StreamHandler())
    logging.root.setLevel('INFO')


########################################
# ../../../std/runtime.py


REQUIRED_PYTHON_VERSION = (3, 8)


def check_runtime_version() -> None:
    if sys.version_info < REQUIRED_PYTHON_VERSION:
        raise OSError(
            f'Requires python {REQUIRED_PYTHON_VERSION}, got {sys.version_info} from {sys.executable}')  # noqa


########################################
# ../../../../../omlish/os.py


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


########################################
# ../../../std/subprocesses.py


def _mask_env_kwarg(kwargs):
    return {**kwargs, **({'env': '...'} if 'env' in kwargs else {})}


def subprocess_check_call(*args, stdout=sys.stderr, **kwargs):
    log.debug((args, _mask_env_kwarg(kwargs)))
    return subprocess.check_call(*args, stdout=stdout, **kwargs)  # type: ignore


def subprocess_check_output(*args, **kwargs):
    log.debug((args, _mask_env_kwarg(kwargs)))
    return subprocess.check_output(*args, **kwargs)


########################################
# demo.py


@cached_nullary
def _foo():
    return 5


def _main() -> None:
    """Docstring"""

    check_runtime_version()
    setup_standard_logging()
    log.info('hi')

    # Comment
    check_not_none(_foo())  # Inline comment

    pprint.pprint('hi')

    print(subprocess_check_output('uptime'))

    print(PAGE_SIZE)


if __name__ == '__main__':
    _main()
