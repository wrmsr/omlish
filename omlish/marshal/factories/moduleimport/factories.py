"""
FIXME:
 - lol support late registration and such, this is broken
  - need to cache in the registry somehow, cannot iterate over all ModuleImports each time
   - probably use something like dataclass driver context items or some such

TODO:
 - per-type module imports
"""
import threading
import typing as ta

from .... import reflect as rfl
from ...base.contexts import BaseContext
from ...base.contexts import MarshalFactoryContext
from ...base.contexts import UnmarshalFactoryContext
from ...base.types import Marshaler
from ...base.types import MarshalerFactory
from ...base.types import Unmarshaler
from ...base.types import UnmarshalerFactory
from .configs import ModuleImport


FactoryT = ta.TypeVar('FactoryT', bound=MarshalerFactory | UnmarshalerFactory)


##


class _ModuleImportingFactory(ta.Generic[FactoryT]):
    def __init__(
            self,
            fac: FactoryT,
            callback: ta.Callable[[], None] | None = None,
    ) -> None:
        super().__init__()

        self._fac = fac
        self._callback = callback

        self._lock = threading.RLock()
        self._last_mis: ta.Any = None

    def _do_import(self, ctx: BaseContext, mis: ta.Sequence[ModuleImport]) -> None:
        c = 0
        for mi in mis:
            if mi.import_if_necessary():
                c += 1

        if c:
            if self._callback is not None:
                self._callback()

    def _import_if_necessary(self, ctx: BaseContext) -> None:
        if (mis := ctx.configs.get_of(None, ModuleImport)) and mis is not self._last_mis:
            with self._lock:
                if (mis := ctx.configs.get_of(None, ModuleImport)) and mis is not self._last_mis:
                    self._do_import(ctx, mis)
                    self._last_mis = mis


class ModuleImportingMarshalerFactory(_ModuleImportingFactory[MarshalerFactory], MarshalerFactory):
    def make_marshaler(self, ctx: MarshalFactoryContext, rty: rfl.Type) -> ta.Callable[[], Marshaler] | None:
        self._import_if_necessary(ctx)
        return self._fac.make_marshaler(ctx, rty)


class ModuleImportingUnmarshalerFactory(_ModuleImportingFactory[UnmarshalerFactory], UnmarshalerFactory):
    def make_unmarshaler(self, ctx: UnmarshalFactoryContext, rty: rfl.Type) -> ta.Callable[[], Unmarshaler] | None:
        self._import_if_necessary(ctx)
        return self._fac.make_unmarshaler(ctx, rty)
