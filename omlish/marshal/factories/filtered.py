"""This module is considered part of the api."""
import typing as ta

from ... import reflect2 as rfl
from ..api.contexts import MarshalFactoryContext
from ..api.contexts import UnmarshalFactoryContext
from ..api.types import Marshaler
from ..api.types import MarshalerFactory
from ..api.types import Unmarshaler
from ..api.types import UnmarshalerFactory


FactoryT = ta.TypeVar('FactoryT', bound=MarshalerFactory | UnmarshalerFactory)
FactoryContextT = ta.TypeVar('FactoryContextT', bound=MarshalFactoryContext | UnmarshalFactoryContext)


##


class _FilteredFactory(ta.Generic[FactoryContextT, FactoryT]):
    def __init__(
            self,
            fn: ta.Callable[[FactoryContextT, rfl.Type], bool],
            fac: FactoryT,
    ) -> None:
        super().__init__()

        self._fn = fn
        self._fac = fac

    def __repr__(self) -> str:
        return f'{type(self).__name__}({self._fn}, {self._fac})'


class FilteredMarshalerFactory(_FilteredFactory[MarshalFactoryContext, MarshalerFactory], MarshalerFactory):
    def make_marshaler(self, ctx: MarshalFactoryContext, rty: rfl.Type) -> ta.Callable[[], Marshaler] | None:
        if not self._fn(ctx, rty):
            return None
        return self._fac.make_marshaler(ctx, rty)


class FilteredUnmarshalerFactory(_FilteredFactory[UnmarshalFactoryContext, UnmarshalerFactory], UnmarshalerFactory):
    def make_unmarshaler(self, ctx: UnmarshalFactoryContext, rty: rfl.Type) -> ta.Callable[[], Unmarshaler] | None:
        if not self._fn(ctx, rty):
            return None
        return self._fac.make_unmarshaler(ctx, rty)
