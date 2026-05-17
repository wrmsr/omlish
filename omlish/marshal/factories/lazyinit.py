import threading
import typing as ta

from ... import check
from ... import lang
from ... import reflect as rfl
from ..api.configs import ConfigRegistry
from ..api.contexts import BaseContext
from ..api.contexts import MarshalFactoryContext
from ..api.contexts import UnmarshalFactoryContext
from ..api.contexts import _PreReflectFactory
from ..api.internalstate import InternalState
from ..api.types import Marshaler
from ..api.types import MarshalerFactory
from ..api.types import Unmarshaler
from ..api.types import UnmarshalerFactory
from .api import LazyInit


FactoryT = ta.TypeVar('FactoryT', bound=MarshalerFactory | UnmarshalerFactory)


##


class _LazyInitRunningFactory(_PreReflectFactory, ta.Generic[FactoryT]):
    def __init__(
            self,
            fac: FactoryT,
            callback: ta.Callable[[], None] | None = None,
    ) -> None:
        super().__init__()

        self._fac = fac
        self._callback = callback

    class _State(InternalState.ByConfig.Entry, lang.Final):
        def __init__(self) -> None:
            self.lock = threading.RLock()

            self.last_lazy_inits: ta.Any | None = None
            self.already_run_lazy_inits: frozenset[LazyInit] | None = None

    def _do_run(self, st: _State, cfgs: ConfigRegistry, lis: ta.Sequence[LazyInit]) -> None:
        ars = st.already_run_lazy_inits

        lst: list[LazyInit] = []
        for li in lis:
            if ars is not None and li in ars:
                continue
            li.fn(cfgs)
            lst.append(li)

        if not lst:
            return

        if ars is not None and ars:
            lst.extend(ars)
        st.already_run_lazy_inits = frozenset(lst)

        if self._callback is not None:
            self._callback()

    def _run_if_necessary(self, ctx: BaseContext) -> None:
        cfgs = ctx.configs
        st = ctx.internal_state_by_config.get(_LazyInitRunningFactory._State)
        if (lis := cfgs.get().get(LazyInit)) and lis is not st.last_lazy_inits:
            with st.lock:
                if (lis := cfgs.get().get(LazyInit)) and lis is not st.last_lazy_inits:
                    self._do_run(st, check.isinstance(cfgs, ConfigRegistry), lis)
                    st.last_lazy_inits = lis

    def _pre_reflect(self, ctx: BaseContext) -> None:
        self._run_if_necessary(ctx)


class LazyInitRunningMarshalerFactory(_LazyInitRunningFactory[MarshalerFactory], MarshalerFactory):
    def make_marshaler(self, ctx: MarshalFactoryContext, rty: rfl.Type) -> ta.Callable[[], Marshaler] | None:
        self._run_if_necessary(ctx)
        return self._fac.make_marshaler(ctx, rty)


class LazyInitRunningUnmarshalerFactory(_LazyInitRunningFactory[UnmarshalerFactory], UnmarshalerFactory):
    def make_unmarshaler(self, ctx: UnmarshalFactoryContext, rty: rfl.Type) -> ta.Callable[[], Unmarshaler] | None:
        self._run_if_necessary(ctx)
        return self._fac.make_unmarshaler(ctx, rty)
