import contextlib
import typing as ta
import weakref

from ... import check
from ... import lang
from ..exceptions import CyclicDependencyException
from ..exceptions import UnboundKeyException
from ..injector import Injector
from ..inspect import KwargsTarget
from ..keys import Key
from ..keys import as_key
from .elements import ElementCollection
from .inspect import build_kwargs_target


class InjectorImpl(Injector, lang.Final):
    def __init__(self, ec: ElementCollection, p: ta.Optional['InjectorImpl'] = None) -> None:
        super().__init__()

        ec.binding_map()

        self._ec = check.isinstance(ec, ElementCollection)
        self._p: ta.Optional[InjectorImpl] = check.isinstance(p, (InjectorImpl, None))

        self._cs: weakref.WeakSet[InjectorImpl] | None = None
        self._root: InjectorImpl = p._root if p is not None else self

        self.__cur_req: InjectorImpl._Request | None = None

        self._instantiate_eagers()

    _root: 'InjectorImpl'

    def _instantiate_eagers(self) -> None:
        pass

    def create_child(self, ec: ElementCollection) -> Injector:
        c = InjectorImpl(ec, self)
        if self._cs is None:
            self._cs = weakref.WeakSet()
        self._cs.add(c)
        return c

    class _Request:
        def __init__(self, injector: 'InjectorImpl') -> None:
            super().__init__()
            self._injector = injector
            self._provisions: dict[Key, ta.Any] = {}
            self._seen_keys: set[Key] = set()

        def handle_key(self, key: Key) -> lang.Maybe:
            try:
                return lang.just(self._provisions[key])
            except KeyError:
                pass
            if key in self._seen_keys:
                raise CyclicDependencyException(key)
            self._seen_keys.add(key)
            return lang.empty()

        def handle_provision(self, key: Key, v: ta.Any) -> None:
            check.in_(key, self._seen_keys)
            check.not_in(key, self._provisions)
            self._provisions[key] = v

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
            if (rv := cr.handle_key(key)).present:
                return rv

            pi = self._ec.binding_map().get(key)
            if pi is not None:
                v = pi.provider.provide(self)
                cr.handle_provision(key, v)
                return lang.just(v)

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
        if isinstance(obj, KwargsTarget):
            obj, kt = obj.obj, obj
        else:
            kt = build_kwargs_target(obj)
        kws = self.provide_kwargs(kt)
        # FIXME: still 'injecting' (as in has a req) if ctor needs and uses Injector
        return obj(**kws)
