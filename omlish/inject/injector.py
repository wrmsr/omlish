"""
TODO:
 - unify reflect with marshal - fix type anns (ta.Seq is not a `type`)
 - eager
 - defer
 - defaults
 - private
 - circular proxies
"""
import typing as ta

from .. import check
from .. import lang
from .bindings import build_provider_map
from .exceptions import UnboundKeyException
from .inspect import build_kwarg_keys
from .keys import as_key
from .types import Bindings
from .types import Injector


class _Injector(Injector, lang.Final):
    def __init__(self, bs: Bindings, p: ta.Optional[Injector] = None) -> None:
        super().__init__()

        self._bs = check.isinstance(bs, Bindings)
        self._p: ta.Optional[Injector] = check.isinstance(p, (Injector, None))

        self._pfm = {k: v.provider_fn() for k, v in build_provider_map(bs).items()}

    def try_provide(self, key: ta.Any) -> lang.Maybe[ta.Any]:
        key = as_key(key)

        fn = self._pfm.get(key)
        if fn is not None:
            return lang.just(fn(self))

        if self._p is not None:
            pv = self._p.try_provide(key)
            if pv is not None:
                return lang.empty()

        return lang.empty()

    def provide(self, key: ta.Any) -> ta.Any:
        v = self.try_provide(key)
        if v.present:
            return v.must()
        raise UnboundKeyException(key)

    def provide_kwargs(self, obj: ta.Any) -> ta.Mapping[str, ta.Any]:
        kd = build_kwarg_keys(obj)
        ret: dict[str, ta.Any] = {}
        for n, k in kd.items():
            ret[n] = self.provide(k)
        return ret

    def inject(self, obj: ta.Any) -> ta.Any:
        kws = self.provide_kwargs(obj)
        return obj(**kws)


def create_injector(bs: Bindings, p: ta.Optional[Injector] = None) -> Injector:
    return _Injector(bs, p)
