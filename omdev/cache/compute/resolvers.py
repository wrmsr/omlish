from .types import Name
from .types import Object
from .types import ObjectResolver


##


class CachingObjectResolver(ObjectResolver):
    def __init__(self, child: ObjectResolver) -> None:
        super().__init__()

        self._child = child
        self._dct: dict[Name, Object] = {}

    def clear(self) -> None:
        self._dct.clear()

    def resolve(self, name: Name) -> Object:
        try:
            return self._dct[name]
        except KeyError:
            pass
        ret = self._child.resolve(name)
        self._dct[name] = ret
        return ret
