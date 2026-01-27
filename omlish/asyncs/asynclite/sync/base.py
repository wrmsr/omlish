# @omlish-lite
from ....lite.abstract import Abstract
from ..base import AsyncliteApi
from ..base import AsyncliteObject


##


class SyncAsyncliteBase(Abstract):
    pass


class SyncAsyncliteObject(AsyncliteObject, SyncAsyncliteBase, Abstract):
    pass


class SyncAsyncliteApi(AsyncliteApi, SyncAsyncliteBase, Abstract):
    pass
