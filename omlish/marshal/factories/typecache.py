import threading
import typing as ta

from ... import check
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


class _TypeCacheFactory(mfs.MatchFn[[C, rfl.Type], R]):
    def __init__(self, f: mfs.MatchFn[[C, rfl.Type], R]) -> None:
        super().__init__()

        self._f = f
        self._dct: dict[rfl.Type, R | None] = {}
        self._lock = threading.RLock()

    def guard(self, ctx: C, rty: rfl.Type) -> bool:
        check.isinstance(rty, rfl.TYPES)

        try:
            return self._dct[rty] is not None
        except KeyError:
            pass

        with self._lock:
            try:
                e = self._dct[rty]

            except KeyError:
                if self._f.guard(ctx, rty):
                    return True
                else:
                    self._dct[rty] = None
                    return False

            else:
                return e is not None

    def fn(self, ctx: C, rty: rfl.Type) -> R:
        check.isinstance(rty, rfl.TYPES)

        try:
            e = self._dct[rty]
        except KeyError:
            pass
        else:
            if e is None:
                raise mfs.MatchGuardError(ctx, rty)
            else:
                return e

        with self._lock:
            try:
                e = self._dct[rty]

            except KeyError:
                try:
                    ret = self._f(ctx, rty)
                except mfs.MatchGuardError:
                    self._dct[rty] = None
                    raise
                else:
                    self._dct[rty] = ret
                    return ret

            if e is None:
                raise mfs.MatchGuardError(ctx, rty)
            else:
                return e


##


class TypeCacheMarshalerFactory(MarshalerFactory):
    def __init__(self, f: MarshalerFactory) -> None:
        super().__init__()

        self._f = f
        self._tcf: _TypeCacheFactory[MarshalContext, Marshaler] = _TypeCacheFactory(f.make_marshaler)

    @property
    def make_marshaler(self) -> MarshalerMaker:
        return self._tcf


class TypeCacheUnmarshalerFactory(UnmarshalerFactory):
    def __init__(self, f: UnmarshalerFactory) -> None:
        super().__init__()

        self._f = f
        self._tcf: _TypeCacheFactory[UnmarshalContext, Unmarshaler] = _TypeCacheFactory(f.make_unmarshaler)

    @property
    def make_unmarshaler(self) -> UnmarshalerMaker:
        return self._tcf
