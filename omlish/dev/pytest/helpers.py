import sys
import typing as ta

import pytest

from ..testing import can_import


def skip_if_cant_import(module: str, *args, **kwargs):
    return pytest.mark.skipif(not can_import(module, *args, **kwargs), reason=f'requires import {module}')


def skip_if_python_version_less_than(num: ta.Sequence[int]):
    return pytest.mark.skipif(sys.version_info < tuple(num), reason=f'python version {tuple(sys.version_info)} < {tuple(num)}')  # noqa
