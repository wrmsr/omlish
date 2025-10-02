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
from ..base.contexts import MarshalContext
from ..base.contexts import MarshalFactoryContext
from ..base.contexts import UnmarshalContext
from ..base.contexts import UnmarshalFactoryContext
from ..base.types import Marshaler
from ..base.types import Unmarshaler
from ..base.values import Value
from ..factories.method import MarshalerFactoryMethodClass
from ..factories.method import UnmarshalerFactoryMethodClass


##


DEFAULT_ITERABLE_CONCRETE_TYPES: dict[type[collections.abc.Iterable], type[collections.abc.Iterable]] = {
    collections.abc.Iterable: tuple,  # type: ignore
    collections.abc.Sequence: tuple,  # type: ignore
    collections.abc.MutableSequence: list,  # type: ignore
}


#


@dc.dataclass(frozen=True)
class IterableMarshaler(Marshaler):
    e: Marshaler

    def marshal(self, ctx: MarshalContext, o: ta.Iterable) -> Value:
        return list(map(functools.partial(self.e.marshal, ctx), o))


class IterableMarshalerFactory(MarshalerFactoryMethodClass):
    @MarshalerFactoryMethodClass.make_marshaler.register
    def _make_generic(self, ctx: MarshalFactoryContext, rty: rfl.Type) -> ta.Callable[[], Marshaler] | None:
        if not (isinstance(rty, rfl.Generic) and issubclass(rty.cls, collections.abc.Iterable)):
            return None
        return lambda: IterableMarshaler(ctx.make_marshaler(check.single(rty.args)))

    @MarshalerFactoryMethodClass.make_marshaler.register
    def _make_concrete(self, ctx: MarshalFactoryContext, rty: rfl.Type) -> ta.Callable[[], Marshaler] | None:
        if not (isinstance(rty, type) and issubclass(rty, collections.abc.Iterable)):
            return None
        return lambda: IterableMarshaler(ctx.make_marshaler(ta.Any))


#


@dc.dataclass(frozen=True)
class IterableUnmarshaler(Unmarshaler):
    ctor: ta.Callable[[ta.Iterable[ta.Any]], ta.Iterable]
    e: Unmarshaler

    def unmarshal(self, ctx: UnmarshalContext, v: Value) -> ta.Iterable:
        return self.ctor(map(functools.partial(self.e.unmarshal, ctx), check.isinstance(v, collections.abc.Iterable)))


class IterableUnmarshalerFactory(UnmarshalerFactoryMethodClass):
    @UnmarshalerFactoryMethodClass.make_unmarshaler.register
    def _make_generic(self, ctx: UnmarshalFactoryContext, rty: rfl.Type) -> ta.Callable[[], Unmarshaler] | None:
        if not (isinstance(rty, rfl.Generic) and issubclass(rty.cls, collections.abc.Iterable)):
            return None
        cty = DEFAULT_ITERABLE_CONCRETE_TYPES.get(rty.cls, rty.cls)  # noqa
        return lambda: IterableUnmarshaler(cty, ctx.make_unmarshaler(check.single(rty.args)))  # noqa

    @UnmarshalerFactoryMethodClass.make_unmarshaler.register
    def _make_concrete(self, ctx: UnmarshalFactoryContext, rty: rfl.Type) -> ta.Callable[[], Unmarshaler] | None:
        if not (isinstance(rty, type) and issubclass(rty, collections.abc.Iterable)):
            return None
        return lambda: IterableUnmarshaler(check.isinstance(rty, type), ctx.make_unmarshaler(ta.Any))
