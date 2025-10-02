import threading
import typing as ta

from ... import reflect as rfl
from ..base.contexts import MarshalFactoryContext
from ..base.contexts import UnmarshalFactoryContext
from ..base.types import Marshaler
from ..base.types import MarshalerFactory
from ..base.types import Unmarshaler
from ..base.types import UnmarshalerFactory


FactoryT = ta.TypeVar('FactoryT', bound=MarshalerFactory | UnmarshalerFactory)


##


class _InvalidatableFactory(ta.Generic[FactoryT]):
    def __init__(
            self,
            fac_fac: ta.Callable,
            check_fn: ta.Callable[[], bool] | None = None,
    ) -> None:
        super().__init__()

        self._fac_fac = fac_fac
        self._check_fn: ta.Callable[[], bool] | None = check_fn

        self._lock = threading.RLock()

    #

    __fac: FactoryT | None = None

    def _invalidate(self) -> None:
        self.__fac = None

    def invalidate(self) -> None:
        with self._lock:
            self._invalidate()

    def _maybe_invalidate(self) -> None:
        if self._check_fn is not None:
            if self._check_fn():
                with self._lock:
                    if self._check_fn():
                        self._invalidate()

    def _fac(self) -> FactoryT:
        self._maybe_invalidate()

        if (f := self.__fac) is None:
            with self._lock:
                if (f := self.__fac) is None:
                    f = self.__fac = self._fac_fac()

        return f


class InvalidatableMarshalerFactory(_InvalidatableFactory[MarshalerFactory], MarshalerFactory):
    def make_marshaler(self, ctx: MarshalFactoryContext, rty: rfl.Type) -> ta.Callable[[], Marshaler] | None:
        return self._fac().make_marshaler(ctx, rty)


class InvalidatableUnmarshalerFactory(_InvalidatableFactory[UnmarshalerFactory], UnmarshalerFactory):
    def make_unmarshaler(self, ctx: UnmarshalFactoryContext, rty: rfl.Type) -> ta.Callable[[], Unmarshaler] | None:
        return self._fac().make_unmarshaler(ctx, rty)
