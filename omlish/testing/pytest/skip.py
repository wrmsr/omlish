"""
TODO:
 - if_not_single? switches does this
"""
import shutil
import sys
import sysconfig
import typing as ta

import pytest

from ... import lang


##


def if_cant_import(*modules: str, **kwargs):
    missing = [m for m in modules if not lang.can_import(m, **kwargs)]
    return pytest.mark.skipif(
        bool(missing),
        reason=f'requires import {", ".join(missing)}',
    )


def if_not_on_path(exe: str):
    return pytest.mark.skipif(
        shutil.which(exe) is None,
        reason=f'requires exe on path {exe}',
    )


def if_python_version_less_than(num: ta.Sequence[int]):
    return pytest.mark.skipif(
        sys.version_info < tuple(num),
        reason=f'python version {tuple(sys.version_info)} < {tuple(num)}',
    )


def if_not_platform(*platforms: str):
    return pytest.mark.skipif(
        sys.platform not in platforms,
        reason=f'requires platform in {platforms}',
    )


def if_nogil():
    return pytest.mark.skipif(
        sysconfig.get_config_var('Py_GIL_DISABLED'),
        reason='requires gil build',
    )
