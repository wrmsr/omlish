import contextlib
import typing as ta

from omlish import check
from omlish import lang

from .cache import Cache
from .types import Cacheable
from .types import CacheableVersionMap
from .types import CacheKey
from .types import CacheResult
from .types import merge_version_maps


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
            check.state(not parent.has_result)
            parent._children.append(self)  # noqa

    #

    @property
    def cacheable(self) -> Cacheable:
        return self._cacheable

    @property
    def key(self) -> CacheKey:
        return self._key

    @property
    def parent(self) -> ta.Optional['CacheableContext']:
        return self._parent

    @property
    def children(self) -> ta.Sequence['CacheableContext']:
        return self._children

    #

    @property
    def has_result(self) -> bool:
        return self._result is not None

    def result(self) -> CacheResult:
        return check.not_none(self._result)

    def set_hit(self, result: CacheResult) -> None:
        check.state(result.hit)
        self._result = check.replacing_none(self._result, result)
        self.result_versions()

    def set_miss(self, val: ta.Any) -> None:
        self._result = check.replacing_none(self._result, CacheResult(
            False,
            CacheableVersionMap(),
            val,
        ))
        self.result_versions()

    @lang.cached_function
    def result_versions(self) -> CacheableVersionMap:
        r = check.not_none(self._result)
        return merge_version_maps(
            self._cacheable.as_version_map,
            r.versions,
            *[c.result_versions() for c in self._children],
        )


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
