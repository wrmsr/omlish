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
from ....funcs import match as mfs
from ...base.contexts import BaseContext
from ...base.contexts import MarshalContext
from ...base.contexts import UnmarshalContext
from ...base.types import Marshaler
from ...base.types import MarshalerFactory
from ...base.types import MarshalerMaker
from ...base.types import Unmarshaler
from ...base.types import UnmarshalerFactory
from ...base.types import UnmarshalerMaker
from .configs import ModuleImport


R = ta.TypeVar('R')
ContextT = ta.TypeVar('ContextT', bound=BaseContext)


##


class _ModuleImportingFactory(mfs.MatchFn[[ContextT, rfl.Type], R]):
    def __init__(
            self,
            f: mfs.MatchFn[[ContextT, rfl.Type], R],
            callback: ta.Callable[[], None] | None = None,
    ) -> None:
        super().__init__()

        self._f = f
        self._callback = callback

        self._lock = threading.RLock()
        self._last_mis: ta.Any = None

    def _do_import(self, ctx: ContextT, mis: ta.Sequence[ModuleImport]) -> None:
        c = 0
        for mi in mis:
            if mi.import_if_necessary():
                c += 1

        if c:
            if self._callback is not None:
                self._callback()

    def _import_if_necessary(self, ctx: ContextT) -> None:
        if (mis := ctx.config_registry.get_of(None, ModuleImport)) and mis is not self._last_mis:
            with self._lock:
                if (mis := ctx.config_registry.get_of(None, ModuleImport)) and mis is not self._last_mis:
                    self._do_import(ctx, mis)
                    self._last_mis = mis

    def guard(self, ctx: ContextT, rty: rfl.Type) -> bool:
        self._import_if_necessary(ctx)
        return self._f.guard(ctx, rty)

    def fn(self, ctx: ContextT, rty: rfl.Type) -> R:
        self._import_if_necessary(ctx)
        return self._f(ctx, rty)


##


class ModuleImportingMarshalerFactory(MarshalerFactory):
    def __init__(
            self,
            f: MarshalerFactory,
            callback: ta.Callable[[], None] | None = None,
    ) -> None:
        super().__init__()

        self._f = f
        self._tcf: _ModuleImportingFactory[MarshalContext, Marshaler] = _ModuleImportingFactory(
            f.make_marshaler,
            callback,
        )

    @property
    def make_marshaler(self) -> MarshalerMaker:
        return self._tcf


class ModuleImportingUnmarshalerFactory(UnmarshalerFactory):
    def __init__(
            self,
            f: UnmarshalerFactory,
            callback: ta.Callable[[], None] | None = None,
    ) -> None:
        super().__init__()

        self._f = f
        self._tcf: _ModuleImportingFactory[UnmarshalContext, Unmarshaler] = _ModuleImportingFactory(
            f.make_unmarshaler,
            callback,
        )

    @property
    def make_unmarshaler(self) -> UnmarshalerMaker:
        return self._tcf
