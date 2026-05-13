"""This module is considered part of the api."""
import typing as ta

from ... import reflect as rfl
from ..api.contexts import MarshalFactoryContext
from ..api.contexts import UnmarshalFactoryContext
from ..api.types import Marshaler
from ..api.types import MarshalerFactory
from ..api.types import Unmarshaler
from ..api.types import UnmarshalerFactory


##


class FilteredMarshalerFactory(MarshalerFactory):
    def __init__(
            self,
            fn: ta.Callable[[MarshalFactoryContext, rfl.Type], bool],
            fac: MarshalerFactory,
    ) -> None:
        super().__init__()

        self._fn = fn
        self._fac = fac

    def make_marshaler(self, ctx: MarshalFactoryContext, rty: rfl.Type) -> ta.Callable[[], Marshaler] | None:
        if not self._fn(ctx, rty):
            return None
        return self._fac.make_marshaler(ctx, rty)


class FilteredUnmarshalerFactory(UnmarshalerFactory):
    def __init__(
            self,
            fn: ta.Callable[[UnmarshalFactoryContext, rfl.Type], bool],
            fac: UnmarshalerFactory,
    ) -> None:
        super().__init__()

        self._fn = fn
        self._fac = fac

    def make_unmarshaler(self, ctx: UnmarshalFactoryContext, rty: rfl.Type) -> ta.Callable[[], Unmarshaler] | None:
        if not self._fn(ctx, rty):
            return None
        return self._fac.make_unmarshaler(ctx, rty)
