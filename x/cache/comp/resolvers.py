from .types import Cacheable
from .types import CacheableName
from .types import CacheableResolver


class CachingCacheableResolver(CacheableResolver):
    def __init__(self, child: CacheableResolver) -> None:
        super().__init__()

        self._child = child
        self._cache: dict[CacheableName, Cacheable] = {}

    def resolve(self, name: CacheableName) -> Cacheable:
        try:
            return self._cache[name]
        except KeyError:
            pass
        ret = self._child.resolve(name)
        self._cache[name] = ret
        return ret
