import dataclasses as dc
import typing as ta

from ... import check
from ... import lang
from ... import reflect as rfl
from ..api.configs import Config
from ..api.configs import ConfigRegistry
from ..api.contexts import BaseContext
from ..api.contexts import MarshalFactoryContext
from ..api.contexts import UnmarshalFactoryContext
from ..api.types import Marshaler
from ..api.types import MarshalerFactory
from ..api.types import Unmarshaler
from ..api.types import UnmarshalerFactory
from .api import LazyInit


FactoryT = ta.TypeVar('FactoryT', bound=MarshalerFactory | UnmarshalerFactory)


##


@dc.dataclass(frozen=True, eq=False)
class _AlreadyRunLazyInits(Config, lang.Final):
    lis: frozenset[LazyInit]


class _LazyInitRunningFactory(ta.Generic[FactoryT]):
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
        ars = check.opt_single(cfgs.get_of(None, _AlreadyRunLazyInits))

        lst: list[LazyInit] = []
        for li in lis:
            if ars is not None and li in ars.lis:
                continue
            li.fn(cfgs)
            lst.append(li)

        if not lst:
            return

        if ars:  # type: ignore[unreachable]
            lst.extend(ars.lis)
        ars = _AlreadyRunLazyInits(frozenset(lst))
        cfgs.register(None, ars, replace=True)

        if self._callback is not None:
            self._callback()

    def _run_if_necessary(self, ctx: BaseContext) -> None:
        if (lis := ctx.configs.get_of(None, LazyInit)) and lis is not self._last_lis:
            cfgs: ConfigRegistry = check.isinstance(ctx.configs, ConfigRegistry)
            with cfgs._lock:  # noqa
                if (lis := cfgs.get_of(None, LazyInit)) and lis is not self._last_lis:
                    self._do_run(cfgs, lis)
                    self._last_lis = lis


class LazyInitRunningMarshalerFactory(_LazyInitRunningFactory[MarshalerFactory], MarshalerFactory):
    def make_marshaler(self, ctx: MarshalFactoryContext, rty: rfl.Type) -> ta.Callable[[], Marshaler] | None:
        self._run_if_necessary(ctx)
        return self._fac.make_marshaler(ctx, rty)


class LazyInitRunningUnmarshalerFactory(_LazyInitRunningFactory[UnmarshalerFactory], UnmarshalerFactory):
    def make_unmarshaler(self, ctx: UnmarshalFactoryContext, rty: rfl.Type) -> ta.Callable[[], Unmarshaler] | None:
        self._run_if_necessary(ctx)
        return self._fac.make_unmarshaler(ctx, rty)
