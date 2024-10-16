import shutil
import sys
import sysconfig
import typing as ta

import pytest

from ... import lang


def if_cant_import(module: str, *args, **kwargs):
    return pytest.mark.skipif(not lang.can_import(module, *args, **kwargs), reason=f'requires import {module}')


def if_not_on_path(exe: str):
    return pytest.mark.skipif(shutil.which(exe) is None, reason=f'requires exe on path {exe}')


def if_python_version_less_than(num: ta.Sequence[int]):
    return pytest.mark.skipif(sys.version_info < tuple(num), reason=f'python version {tuple(sys.version_info)} < {tuple(num)}')  # noqa


def if_not_single():
    # FIXME
    # [resolve_collection_argument(a) for a in session.config.args]
    raise NotImplementedError


def if_nogil():
    return pytest.mark.skipif(sysconfig.get_config_var('Py_GIL_DISABLED'), reason='requires gil build')
