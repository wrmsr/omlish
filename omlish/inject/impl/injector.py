"""
TODO:
 - ** can currently bind in a child/private scope shadowing an external parent binding **
 - better source tracking
 - cache/export ElementCollections lol
 - scope bindings, auto in root
 - injector-internal / blacklisted bindings (Injector itself, default scopes) without rebuilding ElementCollection
 - config - proxies, impl select, etc
  - config is probably shared with ElementCollection... but not 'bound', must be shared everywhere
  - InjectorRoot object?
 - ** eagers in any scope, on scope init/open
 - injection listeners
 - unions - raise on ambiguous - usecase: sql.AsyncEngineLike
 - multiple live request scopes on single injector - use private injectors?
"""
import contextlib
import functools
import itertools
import logging
import typing as ta
import weakref

from ... import check
from ... import lang
from ..elements import Elements
from ..exceptions import CyclicDependencyError
from ..exceptions import UnboundKeyError
from ..injector import Injector
from ..inspect import KwargsTarget
from ..keys import Key
from ..keys import as_key
from ..listeners import ProvisionListener
from ..listeners import ProvisionListenerBinding
from ..scopes import ScopeBinding
from ..scopes import Singleton
from ..scopes import ThreadScope
from ..types import Scope
from ..types import Unscoped
from .elements import ElementCollection
from .inspect import build_kwargs_target
from .scopes import ScopeImpl
from .scopes import make_scope_impl


log = logging.getLogger(__name__)


##


DEFAULT_SCOPES: list[Scope] = [
    Unscoped(),
    Singleton(),
    ThreadScope(),
]


class InjectorImpl(Injector, lang.Final):
    def __init__(self, ec: ElementCollection, p: ta.Optional['InjectorImpl'] = None) -> None:
        super().__init__()

        self._ec = check.isinstance(ec, ElementCollection)
        self._p: InjectorImpl | None = check.isinstance(p, (InjectorImpl, None))

        self._internal_consts: dict[Key, ta.Any] = {
            Key(Injector): self,
        }

        self._bim = ec.binding_impl_map()
        self._ekbs = ec.eager_keys_by_scope()
        self._pls: tuple[ProvisionListener, ...] = tuple(
            b.listener
            for b in itertools.chain(
                ec.elements_of_type(ProvisionListenerBinding),
                (p._pls if p is not None else ()),  # noqa
            )
        )

        self._cs: weakref.WeakSet[InjectorImpl] | None = None
        self._root: InjectorImpl = p._root if p is not None else self  # noqa

        self.__cur_req: InjectorImpl._Request | None = None

        ss = [
            *DEFAULT_SCOPES,
            *[sb.scope for sb in ec.elements_of_type(ScopeBinding)],
        ]
        self._scopes: dict[Scope, ScopeImpl] = {
            s: make_scope_impl(s) for s in ss
        }

        self._instantiate_eagers(Unscoped())
        self._instantiate_eagers(Singleton())

    _root: 'InjectorImpl'

    def _instantiate_eagers(self, sc: Scope) -> None:
        for k in self._ekbs.get(sc, ()):
            self.provide(k)

    def get_scope_impl(self, sc: Scope) -> ScopeImpl:
        return self._scopes[sc]

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
            self._provisions: dict[Key, lang.Maybe] = {}
            self._seen_keys: set[Key] = set()
            self._source_stack: list[ta.Any] = []

        def handle_key(self, key: Key) -> lang.Maybe[lang.Maybe]:
            try:
                return lang.just(self._provisions[key])
            except KeyError:
                pass
            if key in self._seen_keys:
                raise CyclicDependencyError(key)
            self._seen_keys.add(key)
            return lang.empty()

        def handle_provision(self, key: Key, mv: lang.Maybe) -> lang.Maybe:
            check.in_(key, self._seen_keys)
            check.not_in(key, self._provisions)
            self._provisions[key] = mv
            return mv

        @contextlib.contextmanager
        def push_source(self, source: ta.Any) -> ta.Iterator[None]:
            self._source_stack.append(source)
            try:
                yield
            finally:
                nsource = self._source_stack.pop()
                if source is not nsource:
                    raise Exception(f'Stack error: {source=} is not {nsource=}')

        def __enter__(self) -> ta.Self:
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

    def _try_provide(self, key: ta.Any, *, source: ta.Any = None) -> lang.Maybe[ta.Any]:
        key = as_key(key)

        cr: InjectorImpl._Request
        with self._current_request() as cr:
            with cr.push_source(source):
                if (rv := cr.handle_key(key)).present:
                    return rv.must()

                ic = self._internal_consts.get(key)
                if ic is not None:
                    return cr.handle_provision(key, lang.just(ic))

                bi = self._bim.get(key)
                if bi is not None:
                    sc = self._scopes[bi.scope]

                    fn = lambda: sc.provide(bi, self)  # noqa
                    for pl in self._pls:
                        fn = functools.partial(pl, self, key, bi.binding, fn)
                    v = fn()

                    return cr.handle_provision(key, lang.just(v))

                if self._p is not None:
                    pv = self._p._try_provide(key, source=source)  # noqa
                    if pv.present:
                        return cr.handle_provision(key, pv)

                return cr.handle_provision(key, lang.empty())

    def _provide(self, key: ta.Any, *, source: ta.Any = None) -> ta.Any:
        v = self._try_provide(key, source=source)
        if v.present:
            return v.must()
        raise UnboundKeyError(key)

    #

    def try_provide(self, key: ta.Any) -> lang.Maybe[ta.Any]:
        return self.try_provide(key)

    def provide(self, key: ta.Any) -> ta.Any:
        v = self._try_provide(key)
        if v.present:
            return v.must()
        raise UnboundKeyError(key)

    def provide_kwargs(self, kt: KwargsTarget) -> ta.Mapping[str, ta.Any]:
        ret: dict[str, ta.Any] = {}
        for kw in kt.kwargs:
            if kw.has_default:
                if not (mv := self._try_provide(kw.key, source=kt)).present:
                    continue
                v = mv.must()
            else:
                v = self._provide(kw.key, source=kt)
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


def create_injector(es: Elements) -> Injector:
    return InjectorImpl(ElementCollection(es))
