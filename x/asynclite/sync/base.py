# @omlish-lite
import contextlib
import typing as ta

from omlish.lite.abstract import Abstract

from ..base import AsyncliteObject
from ..base import AsyncliteApi


##


class SyncAsyncliteBase(Abstract):
    @classmethod
    @contextlib.contextmanager
    def _translate_exceptions(cls) -> ta.Generator[None, None, None]:
        # sync (queue.Queue) already raises the correct exceptions (queue.Empty, queue.Full)
        yield


class SyncAsyncliteObject(AsyncliteObject, SyncAsyncliteBase, Abstract):
    pass


class SyncAsyncliteApi(AsyncliteApi, SyncAsyncliteBase, Abstract):
    pass
