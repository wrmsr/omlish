import threading
import typing as ta

from ... import check
from ... import reflect as rfl
from ..base.contexts import MarshalFactoryContext
from ..base.contexts import UnmarshalFactoryContext
from ..base.types import Marshaler
from ..base.types import MarshalerFactory
from ..base.types import Unmarshaler
from ..base.types import UnmarshalerFactory


FactoryT = ta.TypeVar('FactoryT', bound=MarshalerFactory | UnmarshalerFactory)


##


class _TypeCacheFactory(ta.Generic[FactoryT]):
    def __init__(self, fac: FactoryT) -> None:
        super().__init__()

        self._fac = fac

        self._dct: dict[rfl.Type, ta.Any | None] = {}
        self._lock = threading.RLock()

    def _make(self, rty, dfl):
        check.isinstance(rty, rfl.TYPES)

        try:
            return self._dct[rty]
        except KeyError:
            pass

        with self._lock:
            try:
                return self._dct[rty]
            except KeyError:
                pass

            if (m := dfl()) is None:
                self._dct[rty] = None
                return None

            x = None

            def inner():
                nonlocal x
                if x is None:
                    x = m()
                return x

            self._dct[rty] = inner
            return inner


class TypeCacheMarshalerFactory(_TypeCacheFactory[MarshalerFactory], MarshalerFactory):
    def make_marshaler(self, ctx: MarshalFactoryContext, rty: rfl.Type) -> ta.Callable[[], Marshaler] | None:
        return self._make(rty, lambda: self._fac.make_marshaler(ctx, rty))


class TypeCacheUnmarshalerFactory(_TypeCacheFactory[UnmarshalerFactory], UnmarshalerFactory):
    def make_unmarshaler(self, ctx: UnmarshalFactoryContext, rty: rfl.Type) -> ta.Callable[[], Unmarshaler] | None:
        return self._make(rty, lambda: self._fac.make_unmarshaler(ctx, rty))
