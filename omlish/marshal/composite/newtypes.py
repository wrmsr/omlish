from ... import check
from ... import reflect as rfl
from ..base.contexts import MarshalContext
from ..base.contexts import UnmarshalContext
from ..base.types import Marshaler
from ..base.types import Unmarshaler
from ..factories.simple import SimpleMarshalerFactory
from ..factories.simple import SimpleUnmarshalerFactory


##


class NewtypeMarshalerFactory(SimpleMarshalerFactory):
    def guard(self, ctx: MarshalContext, rty: rfl.Type) -> bool:
        return isinstance(rty, rfl.NewType)

    def fn(self, ctx: MarshalContext, rty: rfl.Type) -> Marshaler:
        return ctx.make(check.isinstance(rty, rfl.NewType).ty)


class NewtypeUnmarshalerFactory(SimpleUnmarshalerFactory):
    def guard(self, ctx: UnmarshalContext, rty: rfl.Type) -> bool:
        return isinstance(rty, rfl.NewType)

    def fn(self, ctx: UnmarshalContext, rty: rfl.Type) -> Unmarshaler:
        return ctx.make(check.isinstance(rty, rfl.NewType).ty)
