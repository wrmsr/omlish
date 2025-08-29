"""
TODO:
 - per-type module imports
"""
import threading
import typing as ta

from ... import reflect as rfl
from ...funcs import match as mfs
from ..base.contexts import MarshalContext
from ..base.contexts import UnmarshalContext
from ..base.types import Marshaler
from ..base.types import MarshalerFactory
from ..base.types import MarshalerMaker
from ..base.types import Unmarshaler
from ..base.types import UnmarshalerFactory
from ..base.types import UnmarshalerMaker


R = ta.TypeVar('R')
C = ta.TypeVar('C')


##


class _ModuleImportingFactory(mfs.MatchFn[[C, rfl.Type], R]):
    def __init__(self, f: mfs.MatchFn[[C, rfl.Type], R]) -> None:
        super().__init__()

        self._f = f
        self._lock = threading.RLock()
        self._has_imported = False

    def _do_import(self) -> None:
        pass

    def _import_if_necessary(self) -> None:
        if not self._has_imported:
            with self._lock:
                if not self._has_imported:
                    self._do_import()
                    self._has_imported = True

    def guard(self, ctx: C, rty: rfl.Type) -> bool:
        self._import_if_necessary()
        return self._f.guard(ctx, rty)

    def fn(self, ctx: C, rty: rfl.Type) -> R:
        self._import_if_necessary()
        return self._f(ctx, rty)


##


class ModuleImportingMarshalerFactory(MarshalerFactory):
    def __init__(self, f: MarshalerFactory) -> None:
        super().__init__()

        self._f = f
        self._tcf: _ModuleImportingFactory[MarshalContext, Marshaler] = _ModuleImportingFactory(f.make_marshaler)

    @property
    def make_marshaler(self) -> MarshalerMaker:
        return self._tcf


class ModuleImportingUnmarshalerFactory(UnmarshalerFactory):
    def __init__(self, f: UnmarshalerFactory) -> None:
        super().__init__()

        self._f = f
        self._tcf: _ModuleImportingFactory[UnmarshalContext, Unmarshaler] = _ModuleImportingFactory(f.make_unmarshaler)

    @property
    def make_unmarshaler(self) -> UnmarshalerMaker:
        return self._tcf
