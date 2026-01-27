# @omlish-lite
from omlish.lite.abstract import Abstract

from ..base import AsyncliteObject
from ..base import AsyncliteApi


##


class SyncAsyncliteBase(Abstract):
    pass


class SyncAsyncliteObject(AsyncliteObject, SyncAsyncliteBase, Abstract):
    pass


class SyncAsyncliteApi(AsyncliteApi, SyncAsyncliteBase, Abstract):
    pass
