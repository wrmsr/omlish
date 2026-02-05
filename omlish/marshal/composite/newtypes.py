import typing as ta

from ... import check
from ... import reflect as rfl
from ..api.contexts import MarshalFactoryContext
from ..api.contexts import UnmarshalFactoryContext
from ..api.types import Marshaler
from ..api.types import MarshalerFactory
from ..api.types import Unmarshaler
from ..api.types import UnmarshalerFactory


##


class NewtypeMarshalerFactory(MarshalerFactory):
    def make_marshaler(self, ctx: MarshalFactoryContext, rty: rfl.Type) -> ta.Callable[[], Marshaler] | None:
        if not isinstance(rty, rfl.NewType):
            return None
        return lambda: ctx.make_marshaler(check.isinstance(rty, rfl.NewType).ty)


class NewtypeUnmarshalerFactory(UnmarshalerFactory):
    def make_unmarshaler(self, ctx: UnmarshalFactoryContext, rty: rfl.Type) -> ta.Callable[[], Unmarshaler] | None:
        if not isinstance(rty, rfl.NewType):
            return None
        return lambda: ctx.make_unmarshaler(check.isinstance(rty, rfl.NewType).ty)
