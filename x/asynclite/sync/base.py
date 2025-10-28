# @omlish-lite
from omlish.lite.abstract import Abstract

from ..base import AsyncliteObject
from ..base import AsyncliteObjects


##


class SyncAsyncliteObject(AsyncliteObject, Abstract):
    pass


class SyncAsyncliteObjects(AsyncliteObjects, Abstract):
    pass
