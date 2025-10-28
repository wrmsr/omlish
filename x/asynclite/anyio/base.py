from omlish.lite.abstract import Abstract

from ..base import AsyncliteObject
from ..base import AsyncliteObjects


##


class AnyioAsyncliteObject(AsyncliteObject, Abstract):
    pass


class AnyioAsyncliteObjects(AsyncliteObjects, Abstract):
    pass
