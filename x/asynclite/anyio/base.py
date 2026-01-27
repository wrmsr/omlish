from omlish.lite.abstract import Abstract

from ..base import AsyncliteObject
from ..base import AsyncliteApi


##


class AnyioAsyncliteBase(Abstract):
    pass


class AnyioAsyncliteObject(AsyncliteObject, AnyioAsyncliteBase, Abstract):
    pass


class AnyioAsyncliteApi(AsyncliteApi, AnyioAsyncliteBase, Abstract):
    pass
