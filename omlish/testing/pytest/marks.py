import shutil
import sys
import sysconfig
import typing as ta

import pytest

from ... import lang  # noqa
from ..testing import can_import
from .plugins.managermarks import ManagerMark  # noqa


if ta.TYPE_CHECKING:
    import asyncio
else:
    asyncio = lang.proxy_import('asyncio')


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


def skip_if_nogil():
    return pytest.mark.skipif(sysconfig.get_config_var('Py_GIL_DISABLED'), reason='requires gil build')


class drain_asyncio(ManagerMark):  # noqa
    def __call__(self, item: pytest.Function) -> ta.Iterator[None]:
        loop = asyncio.get_event_loop()
        try:
            yield
        finally:
            while loop._ready or loop._scheduled:  # type: ignore  # noqa
                loop._run_once()  # type: ignore  # noqa
