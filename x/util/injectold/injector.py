"""
TODO:
 - unify reflect with marshal - fix type anns (ta.Seq is not a `type`)
 - defer
 - defaults
"""
import typing as ta

from omlish.lite.check import check_isinstance
from omlish.lite.maybes import Maybe

from .bindings import build_provider_map
from .exceptions import UnboundKeyException
from .inspect import build_kwargs_target
from .keys import as_key
from .types import Bindings
from .types import Injector


class _Injector(Injector):
    def __init__(self, bs: Bindings, p: ta.Optional[Injector] = None) -> None:
        super().__init__()

        self._bs = check_isinstance(bs, Bindings)
        self._p: ta.Optional[Injector] = check_isinstance(p, (Injector, type(None)))

        self._pfm = {k: v.provider_fn() for k, v in build_provider_map(bs).items()}

    def try_provide(self, key: ta.Any) -> Maybe[ta.Any]:
        key = as_key(key)

        fn = self._pfm.get(key)
        if fn is not None:
            return Maybe.just(fn(self))

        if self._p is not None:
            pv = self._p.try_provide(key)
            if pv is not None:
                return Maybe.empty()

        return Maybe.empty()

    def provide(self, key: ta.Any) -> ta.Any:
        v = self.try_provide(key)
        if v.present:
            return v.must()
        raise UnboundKeyException(key)

    def provide_kwargs(self, obj: ta.Any) -> ta.Mapping[str, ta.Any]:
        kt = build_kwargs_target(obj)
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
        kws = self.provide_kwargs(obj)
        return obj(**kws)


def create_injector(bs: Bindings, p: ta.Optional[Injector] = None) -> Injector:
    return _Injector(bs, p)
