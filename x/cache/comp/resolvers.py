from .types import Cacheable
from .types import CacheableName
from .types import CacheableResolver


class CachingCacheableResolver(CacheableResolver):
    def __init__(self, child: CacheableResolver) -> None:
        super().__init__()

        self._child = child
        self._dct: dict[CacheableName, Cacheable] = {}

    def clear(self) -> None:
        self._dct.clear()

    def resolve(self, name: CacheableName) -> Cacheable:
        try:
            return self._dct[name]
        except KeyError:
            pass
        ret = self._child.resolve(name)
        self._dct[name] = ret
        return ret
