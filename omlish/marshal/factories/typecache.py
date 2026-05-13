import typing as ta
import threading
import weakref

from ... import check
from ... import dataclasses as dc
from ... import reflect as rfl
from ..api.contexts import MarshalFactoryContext
from ..api.contexts import UnmarshalFactoryContext
from ..api.types import Marshaler
from ..api.types import MarshalerFactory
from ..api.types import Unmarshaler
from ..api.types import UnmarshalerFactory
from ..api.configs import Config
from ... import typedvalues as tv
from ... import lang
from ..api.configs import ConfigRegistry


FactoryT = ta.TypeVar('FactoryT', bound=MarshalerFactory | UnmarshalerFactory)
ImplT = ta.TypeVar('ImplT', bound=Marshaler | Unmarshaler)


##


class _TypeCacheFactory(ta.Generic[FactoryT, ImplT]):
    def __init__(self, fac: FactoryT) -> None:
        super().__init__()

        self._fac = fac

    #

    @dc.dataclass(frozen=True, eq=False)
    class _StateMap(Config, tv.UniqueTypedValue, lang.Final):
        dct: weakref.WeakKeyDictionary[_TypeCacheFactory, _TypeCacheFactory._State] = dc.field(
            default_factory=weakref.WeakKeyDictionary,
        )

    @dc.dataclass(frozen=True, eq=False)
    class _State(lang.Final):
        dct: dict[rfl.Type, ta.Any | None] = dc.field(default_factory=dict)

        lock: threading.RLock = dc.field(default_factory=threading.RLock)

    def _get_state(self, cfgs: ConfigRegistry) -> _State:
        try:
            sm = cfgs.get(None)[_TypeCacheFactory._StateMap]
        except KeyError:
            with cfgs._lock:
                try:
                    sm = cfgs.get(None)[_TypeCacheFactory._StateMap]
                except KeyError:
                    cfgs.update(None, sm := _TypeCacheFactory._StateMap())

        try:
            return sm.dct[self]
        except KeyError:
            with cfgs._lock:
                try:
                    return sm.dct[self]
                except KeyError:
                    sm.dct[self] = st = _TypeCacheFactory._State()
                    return st

    #

    def _make(
            self,
            cfgs: ConfigRegistry,
            rty: rfl.Type,
            dfl: ta.Callable[[], ta.Callable[[], ImplT] | None],
    ) -> ta.Callable[[], ImplT] | None:
        check.isinstance(rty, rfl.TYPES)

        st = self._get_state(cfgs)

        try:
            return st.dct[rty]
        except KeyError:
            pass

        with st.lock:
            try:
                return st.dct[rty]
            except KeyError:
                pass

            if (m := dfl()) is None:
                st.dct[rty] = None
                return None

            x = None

            def inner():
                nonlocal x
                if x is None:
                    x = m()
                return x

            st.dct[rty] = inner
            return inner


class TypeCacheMarshalerFactory(_TypeCacheFactory[MarshalerFactory, Marshaler], MarshalerFactory):
    def make_marshaler(self, ctx: MarshalFactoryContext, rty: rfl.Type) -> ta.Callable[[], Marshaler] | None:
        return self._make(
            check.isinstance(ctx.configs, ConfigRegistry),
            rty,
            lambda: self._fac.make_marshaler(ctx, rty),
        )


class TypeCacheUnmarshalerFactory(_TypeCacheFactory[UnmarshalerFactory, Unmarshaler], UnmarshalerFactory):
    def make_unmarshaler(self, ctx: UnmarshalFactoryContext, rty: rfl.Type) -> ta.Callable[[], Unmarshaler] | None:
        return self._make(
            check.isinstance(ctx.configs, ConfigRegistry),
            rty,
            lambda: self._fac.make_unmarshaler(ctx, rty),
        )
