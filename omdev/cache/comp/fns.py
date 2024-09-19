import functools
import importlib
import typing as ta

from omlish import cached
from omlish import check
from omlish import collections as col
from omlish import dataclasses as dc
from omlish import lang

from .contexts import get_current_cache
from .contexts import setting_current_context
from .types import CacheKey
from .types import Name
from .types import Object
from .types import ObjectResolver


T = ta.TypeVar('T')


##


@dc.dataclass(frozen=True)
class FnName(Name, lang.Final):
    module: str
    qualname: str


@dc.dataclass(frozen=True)
class FnObject(Object, lang.Final):
    fn: ta.Callable
    version: int = dc.xfield(override=True)

    passive: bool = dc.xfield(default=False, kw_only=True, override=True)

    @cached.property
    def name(self) -> FnName:
        return FnName(self.fn.__module__, self.fn.__qualname__)  # noqa


class FnObjectResolver(ObjectResolver):
    def resolve(self, name: Name) -> FnObject:
        fname = check.isinstance(name, FnName)

        mod = importlib.import_module(fname.module)
        obj = mod
        for a in fname.qualname.split('.'):
            obj = getattr(obj, a)

        check.callable(obj)
        fc = check.isinstance(obj.__cacheable__, FnObject)

        return fc


@dc.dataclass(frozen=True)
class FnCacheKey(CacheKey[FnName], lang.Final):
    args: tuple
    kwargs: col.frozendict[str, ta.Any]

    @dc.validate
    def _check_fn_types(self) -> bool:
        return (
            isinstance(self.name, FnName) and
            isinstance(self.args, tuple) and
            isinstance(self.kwargs, col.frozendict)
        )


##


def cached_fn(version: int) -> ta.Callable[[T], T]:
    def outer(fn):
        @functools.wraps(fn)
        def inner(*args, **kwargs):
            # NOTE: just for testing :x allows updating
            # TODO: proper wrapper obj probably (enforce name resolution)
            cacheable = inner.__cacheable__  # type: ignore

            if (cache := get_current_cache()) is not None:
                key = FnCacheKey(
                    cacheable.name,
                    args,
                    col.frozendict(kwargs),
                )

                with setting_current_context(
                        cacheable,
                        key,
                ) as ctx:
                    if (hit := cache.get(key)) is not None:
                        ctx.set_hit(hit)
                        return hit.value

                    val = fn(*args, **kwargs)
                    ctx.set_miss(val)
                    cache.put(
                        key,
                        ctx.result_versions(),
                        val,
                    )
                    return val

            else:
                return fn(*args, **kwargs)

        inner.__cacheable__ = FnObject(  # type: ignore
            fn,
            version,
        )

        return inner

    return outer  # noqa
