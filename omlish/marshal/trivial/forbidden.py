import typing as ta

from ... import dataclasses as dc
from ... import reflect as rfl
from ..api.contexts import MarshalFactoryContext
from ..api.contexts import UnmarshalFactoryContext
from ..api.errors import ForbiddenTypeError
from ..api.types import Marshaler
from ..api.types import MarshalerFactory
from ..api.types import Unmarshaler
from ..api.types import UnmarshalerFactory


##


@dc.dataclass(frozen=True)
class ForbiddenTypeMarshalerFactoryUnmarshalerFactory(MarshalerFactory, UnmarshalerFactory):
    rtys: ta.AbstractSet[rfl.Type]

    def make_marshaler(self, ctx: MarshalFactoryContext, rty: rfl.Type) -> ta.Callable[[], Marshaler] | None:
        if rty not in self.rtys:
            return None

        def inner():
            raise ForbiddenTypeError(rty)

        return inner

    def make_unmarshaler(self, ctx: UnmarshalFactoryContext, rty: rfl.Type) -> ta.Callable[[], Unmarshaler] | None:
        if rty not in self.rtys:
            return None

        def inner():
            raise ForbiddenTypeError(rty)

        return inner


ForbiddenTypeMarshalerFactory = ForbiddenTypeMarshalerFactoryUnmarshalerFactory
ForbiddenTypeUnmarshalerFactory = ForbiddenTypeMarshalerFactoryUnmarshalerFactory
