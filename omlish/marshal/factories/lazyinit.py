import dataclasses as dc
import typing as ta

from ... import check
from ... import lang
from ... import reflect as rfl
from ... import typedvalues as tv
from ..api.configs import Config
from ..api.configs import ConfigRegistry
from ..api.contexts import BaseContext
from ..api.contexts import MarshalFactoryContext
from ..api.contexts import UnmarshalFactoryContext
from ..api.contexts import _PreReflectFactory
from ..api.types import Marshaler
from ..api.types import MarshalerFactory
from ..api.types import Unmarshaler
from ..api.types import UnmarshalerFactory
from .api import LazyInit


FactoryT = ta.TypeVar('FactoryT', bound=MarshalerFactory | UnmarshalerFactory)


##


@dc.dataclass(frozen=True, eq=False)
class _AlreadyRunLazyInits(Config, tv.UniqueTypedValue, lang.Final):
    lis: frozenset[LazyInit]


class _LazyInitRunningFactory(_PreReflectFactory, ta.Generic[FactoryT]):
    def __init__(
            self,
            fac: FactoryT,
            callback: ta.Callable[[], None] | None = None,
    ) -> None:
        super().__init__()

        self._fac = fac
        self._callback = callback

        self._last_lis: ta.Any = None

    def _do_run(self, cfgs: ConfigRegistry, lis: ta.Sequence[LazyInit]) -> None:
        ars = cfgs.get().get(_AlreadyRunLazyInits)

        lst: list[LazyInit] = []
        for li in lis:
            if ars is not None and li in ars.lis:
                continue
            li.fn(cfgs)
            lst.append(li)

        if not lst:
            return

        if ars is not None and ars.lis:
            lst.extend(ars.lis)
        ars = _AlreadyRunLazyInits(frozenset(lst))
        cfgs.register(None, ars, replace=True)

        if self._callback is not None:
            self._callback()

    def _run_if_necessary(self, cfgs: ConfigRegistry) -> None:
        if (lis := cfgs.get().get(LazyInit)) and lis is not self._last_lis:
            with cfgs._lock:  # noqa
                if (lis := cfgs.get().get(LazyInit)) and lis is not self._last_lis:
                    self._do_run(cfgs, lis)
                    self._last_lis = lis

    def _pre_reflect(self, ctx: BaseContext) -> None:
        self._run_if_necessary(check.isinstance(ctx.configs, ConfigRegistry))


class LazyInitRunningMarshalerFactory(_LazyInitRunningFactory[MarshalerFactory], MarshalerFactory):
    def make_marshaler(self, ctx: MarshalFactoryContext, rty: rfl.Type) -> ta.Callable[[], Marshaler] | None:
        self._run_if_necessary(check.isinstance(ctx.configs, ConfigRegistry))
        return self._fac.make_marshaler(ctx, rty)


class LazyInitRunningUnmarshalerFactory(_LazyInitRunningFactory[UnmarshalerFactory], UnmarshalerFactory):
    def make_unmarshaler(self, ctx: UnmarshalFactoryContext, rty: rfl.Type) -> ta.Callable[[], Unmarshaler] | None:
        self._run_if_necessary(check.isinstance(ctx.configs, ConfigRegistry))
        return self._fac.make_unmarshaler(ctx, rty)
