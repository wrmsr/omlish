# @omlish-lite
from omlish.lite.abstract import Abstract

from ..base import AsyncliteObject
from ..base import AsyncliteApi


##


class SyncAsyncliteObject(AsyncliteObject, Abstract):
    pass


class SyncAsyncliteApi(AsyncliteApi, Abstract):
    pass
