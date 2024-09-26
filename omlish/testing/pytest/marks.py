import typing as ta

import pytest

from ... import lang  # noqa
from .plugins.managermarks import ManagerMark  # noqa


if ta.TYPE_CHECKING:
    from ...asyncs import asyncio as aiu
else:
    aiu = lang.proxy_import('...asyncs.asyncio', __package__)


class drain_asyncio(ManagerMark):  # noqa
    def __call__(self, item: pytest.Function) -> ta.Iterator[None]:
        with aiu.draining_asyncio_tasks():
            yield
