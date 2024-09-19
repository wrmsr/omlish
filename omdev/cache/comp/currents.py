import contextlib
import typing as ta

from omlish import check

from .cache import Cache
from .contexts import Context
from .contexts import ActiveContext
from .contexts import PassiveContext
from .types import CacheKey
from .types import Object


CacheT = ta.TypeVar('CacheT', bound='Cache')


##


_CURRENT_CACHE: Cache | None = None


@contextlib.contextmanager
def setting_current_cache(cache: CacheT) -> ta.Iterator[CacheT]:
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


#


_CURRENT_CONTEXT: Context | None = None


@contextlib.contextmanager
def setting_current_context(
        obj: Object,
        key: CacheKey,
) -> ta.Iterator[Context]:
    global _CURRENT_CONTEXT
    prev = _CURRENT_CONTEXT
    ctx_cls = PassiveContext if obj.passive else ActiveContext
    ctx = ctx_cls(
        obj,
        key,
        parent=prev,
    )
    try:
        _CURRENT_CONTEXT = ctx
        yield ctx
    finally:
        check.is_(_CURRENT_CONTEXT, ctx)
        _CURRENT_CONTEXT = prev
