import dataclasses as dc
import typing as ta

from ... import reflect as rfl
from ..base.contexts import MarshalFactoryContext
from ..base.contexts import UnmarshalFactoryContext
from ..base.errors import ForbiddenTypeError
from ..base.types import Marshaler
from ..base.types import MarshalerFactory
from ..base.types import Unmarshaler
from ..base.types import UnmarshalerFactory


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
