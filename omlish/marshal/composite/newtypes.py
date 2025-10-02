import typing as ta

from ... import check
from ... import reflect as rfl
from ..base.contexts import MarshalContext
from ..base.contexts import UnmarshalContext
from ..base.types import Marshaler
from ..base.types import MarshalerFactory
from ..base.types import Unmarshaler
from ..base.types import UnmarshalerFactory


##


class NewtypeMarshalerFactory(MarshalerFactory):
    def make_marshaler(self, ctx: MarshalContext, rty: rfl.Type) -> ta.Callable[[], Marshaler] | None:
        if not isinstance(rty, rfl.NewType):
            return None
        return lambda: ctx.make(check.isinstance(rty, rfl.NewType).ty)


class NewtypeUnmarshalerFactory(UnmarshalerFactory):
    def make_unmarshaler(self, ctx: UnmarshalContext, rty: rfl.Type) -> ta.Callable[[], Unmarshaler] | None:
        if not isinstance(rty, rfl.NewType):
            return None
        return lambda: ctx.make(check.isinstance(rty, rfl.NewType).ty)
