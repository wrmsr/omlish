import functools
import importlib
import typing as ta

from omlish import cached
from omlish import check
from omlish import collections as col
from omlish import dataclasses as dc
from omlish import lang

from .contexts import ActiveContext
from .contexts import PassiveContext
from .currents import get_current_cache
from .currents import setting_current_context
from .types import CacheKey
from .types import Metadata
from .types import Name
from .types import Object
from .types import ObjectResolver
from .types import Version


P = ta.ParamSpec('P')
T = ta.TypeVar('T')


##


@dc.dataclass(frozen=True)
class FnName(Name, lang.Final):
    module: str
    qualname: str


@dc.dataclass(frozen=True)
class FnObject(Object, lang.Final, ta.Generic[P, T]):
    fn: ta.Callable[P, T]
    version: Version = dc.xfield(override=True)

    passive: bool = dc.xfield(default=False, kw_only=True, override=True)
    metadata: Metadata = dc.xfield(default=col.frozendict(), kw_only=True, override=True)

    @cached.property
    def name(self) -> FnName:
        return FnName(self.fn.__module__, self.fn.__qualname__)  # noqa

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> T:
        return self.fn(*args, **kwargs)


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


def fn(
        version: Version,
        *,
        passive: bool = False,
        metadata: Metadata = col.frozendict(),
) -> ta.Callable[[T], T]:
    def outer(fn):
        @functools.wraps(fn)
        def inner(*args, **kwargs):
            # NOTE: just for testing :x allows updating
            # TODO: proper wrapper obj probably (enforce name resolution)
            obj = inner.__cacheable__  # type: ignore

            if (cache := get_current_cache()) is None:
                return fn(*args, **kwargs)

            if obj.passive:
                with setting_current_context(obj) as ctx:
                    pctx = check.isinstance(ctx, PassiveContext)
                    val = fn(*args, **kwargs)
                    pctx.finish()
                    return val

            key = FnCacheKey(
                obj.name,
                args,
                col.frozendict(kwargs),
            )

            with setting_current_context(obj, key) as ctx:
                actx = check.isinstance(ctx, ActiveContext)

                if (hit := cache.get(key)) is not None:
                    actx.set_hit(hit)
                    return hit.value

                val = fn(*args, **kwargs)
                actx.set_miss(val)
                cache.put(
                    key,
                    actx.versions(),
                    val,
                )
                return val

        inner.__cacheable__ = FnObject(  # type: ignore
            fn,
            version,
            passive=passive,
            metadata=metadata,
        )

        return inner

    return outer  # noqa
