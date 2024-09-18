import contextlib
import typing as ta

from omlish import check
from omlish import lang

from .cache import Cache
from .types import CacheKey
from .types import CacheResult
from .types import Cacheable
from .types import CacheableName
from .types import CacheableVersion
from .types import CacheableVersionMap


CacheT = ta.TypeVar('CacheT', bound='Cache')


##


_CURRENT_CACHE: Cache | None = None


@contextlib.contextmanager
def cache_context(cache: CacheT) -> ta.Iterator[CacheT]:
    global _CURRENT_CACHE
    prev = _CURRENT_CACHE
    try:
        _CURRENT_CACHE = cache
        yield cache
    finally:
        check.is_(_CURRENT_CACHE, cache)
        _CURRENT_CACHE = prev


def get_current_cache() -> Cache | None:
    return _CURRENT_CACHE


##


class CacheableContext(lang.Final):
    def __init__(
            self,
            cacheable: Cacheable,
            key: CacheKey,
            *,
            parent: ta.Optional['CacheableContext'] = None,
    ) -> None:
        super().__init__()
        self._cacheable = cacheable
        self._key = key
        self._parent = parent

        self._result: CacheResult | None = None
        self._children: list[CacheableContext] = []

        if parent is not None:
            parent._children.append(self)  # noqa

    @property
    def cacheable(self) -> Cacheable:
        return self._cacheable

    @property
    def key(self) -> CacheKey:
        return self._key

    @property
    def parent(self) -> 'CacheableContext | None':
        return self._parent

    @property
    def children(self) -> ta.Sequence['CacheableContext']:
        return self._children

    def set_result(self, result: CacheResult) -> None:
        check.replacing_none(self._result, result)

    def walk(self) -> ta.Iterator['CacheableContext']:
        yield self
        for child in self.children:
            yield from child.walk()

    def build_version_map(self) -> CacheableVersionMap:
        versions: dict[CacheableName, CacheableVersion] = {}
        for ctx in self.walk():
            c = ctx.cacheable
            try:
                ex = versions[c.name]
            except KeyError:
                versions[c.name] = c.version
            else:
                if ex != c.version:
                    raise Exception(f'Version mismatch: {ex} {c}')
        return versions


#


_CURRENT_CACHEABLE_CONTEXT: CacheableContext | None = None


@contextlib.contextmanager
def cacheable_context(
        cacheable: Cacheable,
        key: CacheKey,
) -> ta.Iterator[CacheableContext]:
    global _CURRENT_CACHEABLE_CONTEXT
    prev = _CURRENT_CACHEABLE_CONTEXT
    ctx = CacheableContext(
        cacheable,
        key,
        parent=prev,
    )
    try:
        _CURRENT_CACHEABLE_CONTEXT = ctx
        yield ctx
    finally:
        check.is_(_CURRENT_CACHEABLE_CONTEXT, ctx)
        _CURRENT_CACHEABLE_CONTEXT = prev
