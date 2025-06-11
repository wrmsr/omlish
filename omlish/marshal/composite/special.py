import collections.abc

from ... import check
from ... import lang
from ... import reflect as rfl
from ...funcs import match as mfs
from ..base import MarshalContext
from ..base import Marshaler
from ..base import MarshalerFactoryMatchClass
from ..base import UnmarshalContext
from ..base import Unmarshaler
from ..base import UnmarshalerFactoryMatchClass
from .iterables import DEFAULT_ITERABLE_CONCRETE_TYPES
from .iterables import IterableMarshaler
from .iterables import IterableUnmarshaler


##


class SequenceNotStrMarshalerFactory(MarshalerFactoryMatchClass):
    @mfs.simple(lambda _, ctx, rty: isinstance(rty, rfl.Protocol) and rty.cls is lang.SequenceNotStr)
    def _build_generic(self, ctx: MarshalContext, rty: rfl.Type) -> Marshaler:
        gty = check.isinstance(rty, rfl.Protocol)
        return IterableMarshaler(ctx.make(check.single(gty.args)))


class SequenceNotStrUnmarshalerFactory(UnmarshalerFactoryMatchClass):
    @mfs.simple(lambda _, ctx, rty: isinstance(rty, rfl.Protocol) and rty.cls is lang.SequenceNotStr)
    def _build_generic(self, ctx: UnmarshalContext, rty: rfl.Type) -> Unmarshaler:
        gty = check.isinstance(rty, rfl.Protocol)
        cty = DEFAULT_ITERABLE_CONCRETE_TYPES[collections.abc.Sequence]  # type: ignore[type-abstract]
        return IterableUnmarshaler(cty, ctx.make(check.single(gty.args)))
