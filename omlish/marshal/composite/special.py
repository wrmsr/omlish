import collections.abc
import typing as ta

from ... import check
from ... import lang
from ... import reflect2 as rfl
from ..api.contexts import MarshalFactoryContext
from ..api.contexts import UnmarshalFactoryContext
from ..api.types import Marshaler
from ..api.types import MarshalerFactory
from ..api.types import Unmarshaler
from ..api.types import UnmarshalerFactory
from .iterables import DEFAULT_ITERABLE_CONCRETE_TYPES
from .iterables import IterableMarshaler
from .iterables import IterableUnmarshaler


##


def _is_sequence_not_str(rty: rfl.Type) -> bool:
    return (
        isinstance(rty, rfl.Instance) and
        rty.type.runtime_object is lang.SequenceNotStr and
        len(rty.args) == 1
    )


class SequenceNotStrMarshalerFactory(MarshalerFactory):
    def make_marshaler(self, ctx: MarshalFactoryContext, rty: rfl.Type) -> ta.Callable[[], Marshaler] | None:
        if not _is_sequence_not_str(rty):
            return None
        return lambda: IterableMarshaler(ctx.make_marshaler(check.single(check.isinstance(rty, rfl.Instance).args)))


class SequenceNotStrUnmarshalerFactory(UnmarshalerFactory):
    def make_unmarshaler(self, ctx: UnmarshalFactoryContext, rty: rfl.Type) -> ta.Callable[[], Unmarshaler] | None:
        if not _is_sequence_not_str(rty):
            return None
        cty = DEFAULT_ITERABLE_CONCRETE_TYPES[collections.abc.Sequence]  # type: ignore[type-abstract]
        return lambda: IterableUnmarshaler(cty, ctx.make_unmarshaler(check.single(check.isinstance(rty, rfl.Instance).args)))  # noqa
