# ruff: noqa: SLF001
import threading
import typing as ta

from ... import check
from ... import dataclasses as dc
from ... import lang
from ... import reflect2 as rfl
from ..api.contexts import MarshalFactoryContext
from ..api.contexts import UnmarshalFactoryContext
from ..api.internalstate import InternalState
from ..api.types import Marshaler
from ..api.types import MarshalerFactory
from ..api.types import Unmarshaler
from ..api.types import UnmarshalerFactory


FactoryT = ta.TypeVar('FactoryT', bound=MarshalerFactory | UnmarshalerFactory)
HandlerT = ta.TypeVar('HandlerT', bound=Marshaler | Unmarshaler)


##


class _TypeCacheFactory(ta.Generic[FactoryT, HandlerT]):
    def __init__(self, fac: FactoryT) -> None:
        super().__init__()

        self._fac = fac

    #

    @dc.dataclass(frozen=True, eq=False)
    class _State(InternalState.ByConfig.ByHandler.Entry, lang.Final):
        dct: dict[rfl.TypeKey, ta.Any | None] = dc.field(default_factory=dict)

        lock: threading.RLock = dc.field(default_factory=threading.RLock)

    def _make(
            self,
            st: _State,
            rty: rfl.Type,
            dfl: ta.Callable[[], ta.Callable[[], HandlerT] | None],
    ) -> ta.Callable[[], HandlerT] | None:
        check.isinstance(rty, rfl.Type)

        key = rty.type_key()

        try:
            return st.dct[key]
        except KeyError:
            pass

        with st.lock:
            try:
                return st.dct[key]
            except KeyError:
                pass

            if (m := dfl()) is None:
                st.dct[key] = None
                return None

            x = None

            def inner():
                nonlocal x
                if x is None:
                    x = m()
                return x

            st.dct[key] = inner
            return inner


class TypeCacheMarshalerFactory(_TypeCacheFactory[MarshalerFactory, Marshaler], MarshalerFactory):
    def make_marshaler(self, ctx: MarshalFactoryContext, rty: rfl.Type) -> ta.Callable[[], Marshaler] | None:
        return self._make(
            ctx.internal_state_by_config.by_handler(self).get(self._State),
            rty,
            lambda: self._fac.make_marshaler(ctx, rty),
        )


class TypeCacheUnmarshalerFactory(_TypeCacheFactory[UnmarshalerFactory, Unmarshaler], UnmarshalerFactory):
    def make_unmarshaler(self, ctx: UnmarshalFactoryContext, rty: rfl.Type) -> ta.Callable[[], Unmarshaler] | None:
        return self._make(
            ctx.internal_state_by_config.by_handler(self).get(self._State),
            rty,
            lambda: self._fac.make_unmarshaler(ctx, rty),
        )
