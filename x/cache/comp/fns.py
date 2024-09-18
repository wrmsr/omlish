import functools
import importlib
import typing as ta

from omlish import cached
from omlish import check
from omlish import collections as col
from omlish import dataclasses as dc
from omlish import lang

from .contexts import cacheable_context
from .contexts import get_current_cache
from .types import Cacheable
from .types import CacheableName
from .types import CacheableResolver
from .types import CacheKey
from .types import CacheResult


T = ta.TypeVar('T')


##


@dc.dataclass(frozen=True)
class FnCacheableName(CacheableName, lang.Final):
    module: str
    qualname: str


@dc.dataclass(frozen=True)
class FnCacheable(Cacheable, lang.Final):
    fn: ta.Callable
    version: int = dc.xfield(override=True)

    @cached.property
    def name(self) -> FnCacheableName:
        return FnCacheableName(self.fn.__module__, self.fn.__qualname__)  # noqa


class FnCacheableResolver(CacheableResolver):
    def __init__(self) -> None:
        super().__init__()

    def resolve(self, name: CacheableName) -> Cacheable:
        fname = check.isinstance(name, FnCacheableName)

        mod = importlib.import_module(fname.module)
        obj = mod
        for a in fname.qualname.split('.'):
            obj = getattr(obj, a)

        check.callable(obj)
        fc = check.isinstance(obj.__cacheable__, FnCacheable)

        return fc


@dc.dataclass(frozen=True)
class FnCacheKey(CacheKey[FnCacheableName], lang.Final):
    args: tuple
    kwargs: col.frozendict[str, ta.Any]

    @dc.validate
    def _check_fn_types(self) -> bool:
        return (
                isinstance(self.name, FnCacheableName) and
                isinstance(self.args, tuple) and
                isinstance(self.kwargs, col.frozendict)
        )


##


def cached_fn(version: int) -> ta.Callable[[T], T]:
    def outer(fn):
        cacheable = FnCacheable(
            fn,
            version,
        )

        fn.__cacheable__ = cacheable

        @functools.wraps(fn)
        def inner(*args, **kwargs):
            if (cache := get_current_cache()) is not None:
                key = FnCacheKey(
                    cacheable.name,
                    args,
                    col.frozendict(kwargs),
                )

                with cacheable_context(
                        cacheable,
                        key,
                ) as ctx:
                    if (hit := cache.get(key)).present:
                        val = hit.must()
                        ctx.set_result(CacheResult(True, val))
                        return val

                    val = fn(*args, **kwargs)
                    ctx.set_result(CacheResult(False, val))
                    cache.put(
                        key,
                        ctx.build_version_map(),
                        val,
                    )
                    return val

            else:
                return fn(*args, **kwargs)

        return inner

    return outer  # noqa
