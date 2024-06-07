"""
TODO:
 - unify reflect with marshal - fix type anns (ta.Seq is not a `type`)
 - eager
 - defer
 - defaults
 - private
 - circular proxies
 - cache inspect on providers
"""
import typing as ta

from .. import check
from .. import lang
from .bindings import build_provider_map
from .exceptions import UnboundKeyException
from .inspect import build_kwargs_target
from .keys import as_key
from .types import Bindings
from .types import Injector
from .types import Key
from .types import KwargsTarget


class _Injector(Injector, lang.Final):
    def __init__(self, bs: Bindings, p: ta.Optional[Injector] = None) -> None:
        super().__init__()

        self._bs = check.isinstance(bs, Bindings)
        self._p: ta.Optional[Injector] = check.isinstance(p, (Injector, None))

        self._pfm = {k: v.provider_fn() for k, v in build_provider_map(bs).items()}
        self._reqs: list[_Injector._Request] = []

    class _Request:
        def __init__(self, injector: '_Injector', key: Key) -> None:
            super().__init__()
            self._injector = injector
            self._key = key

        def __enter__(self: ta.Self) -> ta.Self:
            self._injector._reqs.append(self)
            return self

        def __exit__(self, *exc) -> None:
            check.is_(self._injector._reqs.pop(), self)

    def try_provide(self, key: ta.Any) -> lang.Maybe[ta.Any]:
        key = as_key(key)

        with _Injector._Request(self, key):
            fn = self._pfm.get(key)
            if fn is not None:
                return lang.just(fn(self))

            if self._p is not None:
                pv = self._p.try_provide(key)
                if pv is not None:
                    return pv

            return lang.empty()

    def provide(self, key: ta.Any) -> ta.Any:
        v = self.try_provide(key)
        if v.present:
            return v.must()
        raise UnboundKeyException(key)

    def provide_kwargs(self, kt: KwargsTarget) -> ta.Mapping[str, ta.Any]:
        ret: dict[str, ta.Any] = {}
        for kw in kt.kwargs:
            if kw.has_default:
                if not (mv := self.try_provide(kw.key)).present:
                    continue
                v = mv.must()
            else:
                v = self.provide(kw.key)
            ret[kw.name] = v
        return ret

    def inject(self, obj: ta.Any) -> ta.Any:
        kt = build_kwargs_target(obj)
        kws = self.provide_kwargs(kt)
        return obj(**kws)


def create_injector(bs: Bindings, p: ta.Optional[Injector] = None) -> Injector:
    return _Injector(bs, p)
