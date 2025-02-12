from ... import check
from ... import reflect as rfl
from ..base import MarshalContext
from ..base import Marshaler
from ..base import MarshalerFactory
from ..base import UnmarshalContext
from ..base import Unmarshaler
from ..base import UnmarshalerFactory


class NewtypeMarshalerFactory(MarshalerFactory):
    def guard(self, ctx: MarshalContext, rty: rfl.Type) -> bool:
        return isinstance(rty, rfl.NewType)

    def fn(self, ctx: MarshalContext, rty: rfl.Type) -> Marshaler:
        return ctx.make(check.isinstance(rty, rfl.NewType).ty)


class NewtypeUnmarshalerFactory(UnmarshalerFactory):
    def guard(self, ctx: UnmarshalContext, rty: rfl.Type) -> bool:
        return isinstance(rty, rfl.NewType)

    def fn(self, ctx: UnmarshalContext, rty: rfl.Type) -> Unmarshaler:
        return ctx.make(check.isinstance(rty, rfl.NewType).ty)
