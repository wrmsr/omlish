import collections.abc
import typing as ta

from ... import check
from ... import lang
from ... import reflect as rfl
from ..base.contexts import MarshalFactoryContext
from ..base.contexts import UnmarshalFactoryContext
from ..base.types import Marshaler
from ..base.types import MarshalerFactory
from ..base.types import Unmarshaler
from ..base.types import UnmarshalerFactory
from .iterables import DEFAULT_ITERABLE_CONCRETE_TYPES
from .iterables import IterableMarshaler
from .iterables import IterableUnmarshaler


##


class SequenceNotStrMarshalerFactory(MarshalerFactory):
    def make_marshaler(self, ctx: MarshalFactoryContext, rty: rfl.Type) -> ta.Callable[[], Marshaler] | None:
        if not (isinstance(rty, rfl.Protocol) and rty.cls is lang.SequenceNotStr):
            return None
        return lambda: IterableMarshaler(ctx.make_marshaler(check.single(rty.args)))


class SequenceNotStrUnmarshalerFactory(UnmarshalerFactory):
    def make_unmarshaler(self, ctx: UnmarshalFactoryContext, rty: rfl.Type) -> ta.Callable[[], Unmarshaler] | None:
        if not (isinstance(rty, rfl.Protocol) and rty.cls is lang.SequenceNotStr):
            return None
        cty = DEFAULT_ITERABLE_CONCRETE_TYPES[collections.abc.Sequence]  # type: ignore[type-abstract]
        return lambda: IterableUnmarshaler(cty, ctx.make_unmarshaler(check.single(rty.args)))
