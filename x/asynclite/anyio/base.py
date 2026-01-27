from omlish.lite.abstract import Abstract

from ..base import AsyncliteObject
from ..base import AsyncliteApi


##


class AnyioAsyncliteObject(AsyncliteObject, Abstract):
    pass


class AnyioAsyncliteApi(AsyncliteApi, Abstract):
    pass
