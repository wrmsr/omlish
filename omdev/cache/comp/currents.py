"""
TODO:
 - threadlocal / contextvar / whatever
"""
import contextlib
import typing as ta

from omlish import check

from .cache import Cache
from .contexts import ActiveContext
from .contexts import Context
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
        key: CacheKey | None = None,
        **kwargs: ta.Any,
) -> ta.Iterator[Context]:
    global _CURRENT_CONTEXT
    prev = _CURRENT_CONTEXT

    ctx_kw = dict(
        parent=prev,
        **kwargs,
    )

    ctx: Context
    if obj.passive:
        check.none(key)
        ctx = PassiveContext(obj, **ctx_kw)
    else:
        ctx = ActiveContext(obj, check.isinstance(key, CacheKey), **ctx_kw)

    try:
        _CURRENT_CONTEXT = ctx
        yield ctx

    finally:
        check.is_(_CURRENT_CONTEXT, ctx)
        _CURRENT_CONTEXT = prev
