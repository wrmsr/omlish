"""This module is considered part of the api."""
import threading
import typing as ta

from ... import reflect2 as rfl
from ..api.contexts import MarshalFactoryContext
from ..api.contexts import UnmarshalFactoryContext
from ..api.types import Marshaler
from ..api.types import MarshalerFactory
from ..api.types import Unmarshaler
from ..api.types import UnmarshalerFactory


FactoryT = ta.TypeVar('FactoryT', bound=MarshalerFactory | UnmarshalerFactory)


##


_LAZY_FACTORY_LOCK = threading.RLock()


class _LazyFactory(ta.Generic[FactoryT]):
    def __init__(self, fn: ta.Callable[[], FactoryT]) -> None:
        super().__init__()

        self._fn = fn

    def __repr__(self) -> str:
        try:
            fac = self._fac_
        except AttributeError:
            return f'{type(self).__name__}<fn={self._fn}>'
        else:
            return f'{type(self).__name__}({fac})'

    _fac_: FactoryT

    def _fac(self) -> FactoryT:
        try:
            return self._fac_
        except AttributeError:
            pass

        with _LAZY_FACTORY_LOCK:
            try:
                return self._fac_
            except AttributeError:
                pass

            fac = self._fn()
            self._fac_ = fac
            return fac


class LazyMarshalerFactory(_LazyFactory[MarshalerFactory], MarshalerFactory):
    def make_marshaler(self, ctx: MarshalFactoryContext, rty: rfl.Type) -> ta.Callable[[], Marshaler] | None:
        return self._fac().make_marshaler(ctx, rty)


class LazyUnmarshalerFactory(_LazyFactory[UnmarshalerFactory], UnmarshalerFactory):
    def make_unmarshaler(self, ctx: UnmarshalFactoryContext, rty: rfl.Type) -> ta.Callable[[], Unmarshaler] | None:
        return self._fac().make_unmarshaler(ctx, rty)
