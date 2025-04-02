"""
TODO:
 - heterogeneous tuples
"""
import collections.abc
import dataclasses as dc
import functools
import typing as ta

from ... import check
from ... import reflect as rfl
from ...funcs import match as mfs
from ..base import MarshalContext
from ..base import Marshaler
from ..base import MarshalerFactoryMatchClass
from ..base import UnmarshalContext
from ..base import Unmarshaler
from ..base import UnmarshalerFactoryMatchClass
from ..values import Value


##


DEFAULT_ITERABLE_CONCRETE_TYPES: dict[type[collections.abc.Iterable], type[collections.abc.Iterable]] = {
    collections.abc.Iterable: tuple,  # type: ignore
    collections.abc.Sequence: tuple,  # type: ignore
    collections.abc.MutableSequence: list,  # type: ignore
}


@dc.dataclass(frozen=True)
class IterableMarshaler(Marshaler):
    e: Marshaler

    def marshal(self, ctx: MarshalContext, o: ta.Iterable) -> Value:
        return list(map(functools.partial(self.e.marshal, ctx), o))


class IterableMarshalerFactory(MarshalerFactoryMatchClass):
    @mfs.simple(lambda _, ctx, rty: isinstance(rty, rfl.Generic) and issubclass(rty.cls, collections.abc.Iterable))
    def _build_generic(self, ctx: MarshalContext, rty: rfl.Type) -> Marshaler:
        gty = check.isinstance(rty, rfl.Generic)
        return IterableMarshaler(ctx.make(check.single(gty.args)))

    @mfs.simple(lambda _, ctx, rty: isinstance(rty, type) and issubclass(rty, collections.abc.Iterable))
    def _build_concrete(self, ctx: MarshalContext, rty: rfl.Type) -> Marshaler:
        return IterableMarshaler(ctx.make(ta.Any))


@dc.dataclass(frozen=True)
class IterableUnmarshaler(Unmarshaler):
    ctor: ta.Callable[[ta.Iterable[ta.Any]], ta.Iterable]
    e: Unmarshaler

    def unmarshal(self, ctx: UnmarshalContext, v: Value) -> ta.Iterable:
        return self.ctor(map(functools.partial(self.e.unmarshal, ctx), check.isinstance(v, collections.abc.Iterable)))


class IterableUnmarshalerFactory(UnmarshalerFactoryMatchClass):
    @mfs.simple(lambda _, ctx, rty: isinstance(rty, rfl.Generic) and issubclass(rty.cls, collections.abc.Iterable))
    def _build_generic(self, ctx: UnmarshalContext, rty: rfl.Type) -> Unmarshaler:
        gty = check.isinstance(rty, rfl.Generic)
        cty = DEFAULT_ITERABLE_CONCRETE_TYPES.get(gty.cls, gty.cls)  # noqa
        return IterableUnmarshaler(cty, ctx.make(check.single(gty.args)))

    @mfs.simple(lambda _, ctx, rty: isinstance(rty, type) and issubclass(rty, collections.abc.Iterable))
    def _build_concrete(self, ctx: UnmarshalContext, rty: rfl.Type) -> Unmarshaler:
        return IterableUnmarshaler(check.isinstance(rty, type), ctx.make(ta.Any))
