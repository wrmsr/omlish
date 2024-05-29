import contextlib
import sys
import typing as ta

import pytest

from ..testing import can_import


def skip_if_cant_import(module: str, *args, **kwargs):
    return pytest.mark.skipif(not can_import(module, *args, **kwargs), reason=f'requires import {module}')


def skip_if_python_version_less_than(num: ta.Sequence[int]):
    return pytest.mark.skipif(sys.version_info < tuple(num), reason=f'python version {tuple(sys.version_info)} < {tuple(num)}')  # noqa


def skip_if_not_single():
    # [resolve_collection_argument(a) for a in session.config.args]
    raise NotImplementedError


@contextlib.contextmanager
def assert_raises_star(et):
    num_caught = 0
    try:
        yield
    except* et as eg:
        num_caught += 1
    assert num_caught > 0


