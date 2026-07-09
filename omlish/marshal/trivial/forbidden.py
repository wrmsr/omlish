import typing as ta

from ... import reflect as rfl
from ..api.contexts import MarshalContext
from ..api.contexts import MarshalFactoryContext
from ..api.contexts import UnmarshalContext
from ..api.contexts import UnmarshalFactoryContext
from ..api.errors import ForbiddenError
from ..api.errors import ForbiddenTypeError
from ..api.types import Marshaler
from ..api.types import MarshalerFactory
from ..api.types import Unmarshaler
from ..api.types import UnmarshalerFactory
from ..api.values import Value


##


class ForbiddenMarshalerUnmarshaler(Marshaler, Unmarshaler):
    def marshal(self, ctx: MarshalContext, o: ta.Any) -> Value:
        raise ForbiddenError

    def unmarshal(self, ctx: UnmarshalContext, v: Value) -> ta.Any:
        raise ForbiddenError


#


class ForbiddenTypeMarshalerFactoryUnmarshalerFactory(MarshalerFactory, UnmarshalerFactory):
    def __init__(self, tys: ta.AbstractSet[ta.Any]) -> None:
        super().__init__()

        self._tks = frozenset([
            # FIXME: This does *not* use a marshal context mirror because it doesn't have one.
            rfl.reflect_type(t).type_key()
            for t in tys
        ])

    def make_marshaler(self, ctx: MarshalFactoryContext, rty: rfl.Type) -> ta.Callable[[], Marshaler] | None:
        if rty.type_key() not in self._tks:
            return None

        def inner():
            raise ForbiddenTypeError(rty)

        return inner

    def make_unmarshaler(self, ctx: UnmarshalFactoryContext, rty: rfl.Type) -> ta.Callable[[], Unmarshaler] | None:
        if rty.type_key() not in self._tks:
            return None

        def inner():
            raise ForbiddenTypeError(rty)

        return inner


ForbiddenTypeMarshalerFactory = ForbiddenTypeMarshalerFactoryUnmarshalerFactory
ForbiddenTypeUnmarshalerFactory = ForbiddenTypeMarshalerFactoryUnmarshalerFactory
