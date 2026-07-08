import typing as ta

from ... import reflect2 as rfl
from ..api.contexts import MarshalFactoryContext
from ..api.contexts import UnmarshalFactoryContext
from ..api.types import Marshaler
from ..api.types import MarshalerFactory
from ..api.types import Unmarshaler
from ..api.types import UnmarshalerFactory


##


def _get_newtype_supertype(rty: rfl.Type) -> rfl.Type | None:
    if not isinstance(rty, rfl.Instance):
        return None
    return rty.type.new_type_supertype


class NewtypeMarshalerFactory(MarshalerFactory):
    def make_marshaler(self, ctx: MarshalFactoryContext, rty: rfl.Type) -> ta.Callable[[], Marshaler] | None:
        if (st := _get_newtype_supertype(rty)) is None:
            return None
        return lambda: ctx.make_marshaler(st)


class NewtypeUnmarshalerFactory(UnmarshalerFactory):
    def make_unmarshaler(self, ctx: UnmarshalFactoryContext, rty: rfl.Type) -> ta.Callable[[], Unmarshaler] | None:
        if (st := _get_newtype_supertype(rty)) is None:
            return None
        return lambda: ctx.make_unmarshaler(st)
