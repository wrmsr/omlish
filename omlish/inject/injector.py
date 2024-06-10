"""
TODO:
 - ** thread/async/gener/greenlet/* safety ** - dyn?
 - unify reflect with marshal - fix type anns (ta.Seq is not a `type`)
 - circular proxies
 - listeners
 - scopes
 - cache provider_map, make provider_fn lazy? don't need to hit every elem every new injector
 - elem abstraction?
"""
import contextlib
import typing as ta
import weakref

from .. import check
from .. import lang
from .bindings import build_provider_map
from .exceptions import CyclicDependencyException
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
        self._p: ta.Optional[_Injector] = check.isinstance(p, (Injector, None))
        self._cs: weakref.WeakSet[Injector] = weakref.WeakSet()
        self._root: Injector = p.root if p is not None else p

        self._pfm = {k: v.provider_fn() for k, v in build_provider_map(bs).items()}
        self.__cur_req: _Injector._Request | None = None

    @property
    def parent(self) -> Injector | None:
        return self._p

    @property
    def root(self) -> Injector:
        return self._root

    class _Request:
        def __init__(self, injector: '_Injector') -> None:
            super().__init__()
            self._injector = injector
            self._seen_keys: set[Key] = set()

        def handle_key(self, key: Key) -> None:
            if key in self._seen_keys:
                raise CyclicDependencyException(key)
            self._seen_keys.add(key)

        def __enter__(self: ta.Self) -> ta.Self:
            return self

        def __exit__(self, *exc) -> None:
            pass

    @contextlib.contextmanager
    def _current_request(self) -> ta.Generator[_Request, None, None]:
        if (cr := self.__cur_req) is not None:
            yield cr
            return
        with self._Request(self) as cr:
            try:
                self.__cur_req = cr
                yield cr
            finally:
                self.__cur_req = None

    def try_provide(self, key: ta.Any) -> lang.Maybe[ta.Any]:
        key = as_key(key)

        with self._current_request() as cr:
            cr.handle_key(key)

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
