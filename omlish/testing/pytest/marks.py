import shutil
import sys
import typing as ta

import pytest

from ... import lang
from ..testing import can_import
from .plugins.managermarks import ManagerMark


def skip_if_cant_import(module: str, *args, **kwargs):
    return pytest.mark.skipif(not can_import(module, *args, **kwargs), reason=f'requires import {module}')


def skip_if_not_on_path(exe: str):
    return pytest.mark.skipif(shutil.which(exe) is None, reason=f'requires exe on path {exe}')


def skip_if_python_version_less_than(num: ta.Sequence[int]):
    return pytest.mark.skipif(sys.version_info < tuple(num), reason=f'python version {tuple(sys.version_info)} < {tuple(num)}')  # noqa


def skip_if_not_single():
    # FIXME
    # [resolve_collection_argument(a) for a in session.config.args]
    raise NotImplementedError


class skip_if_nogil(ManagerMark):  # noqa
    def __call__(self, item: pytest.Function) -> ta.Iterator[None]:
        if not lang.is_gil_enabled():
            pytest.skip('requires gil')
        yield
