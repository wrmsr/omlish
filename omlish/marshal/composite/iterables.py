"""
TODO:
 - heterogeneous tuples
"""
import collections.abc
import functools
import typing as ta

from ... import check
from ... import dataclasses as dc
from ... import reflect as rfl
from ..api.contexts import MarshalContext
from ..api.contexts import MarshalFactoryContext
from ..api.contexts import UnmarshalContext
from ..api.contexts import UnmarshalFactoryContext
from ..api.options import Options
from ..api.types import Marshaler
from ..api.types import Unmarshaler
from ..api.values import Value
from ..factories.method import MarshalerFactoryMethodClass
from ..factories.method import UnmarshalerFactoryMethodClass
from .api import DefaultIterableConstructors


##


DEFAULT_ITERABLE_CONCRETE_TYPES: dict[type[collections.abc.Iterable], type[collections.abc.Iterable]] = {
    collections.abc.Iterable: tuple,  # type: ignore
    collections.abc.Sequence: tuple,  # type: ignore
    collections.abc.MutableSequence: list,  # type: ignore
}


def get_default_iterable_constructor(
        cls: type,
        options: Options | None = None,
) -> ta.Callable[[collections.abc.Iterable], ta.Any]:
    if options is not None and (opt := options.get(DefaultIterableConstructors)) is not None:
        opt = check.isinstance(opt, DefaultIterableConstructors)
        o_ctor: ta.Any = None
        if cls == collections.abc.Iterable:
            o_ctor = opt.iterable
        elif cls == collections.abc.Sequence:
            o_ctor = opt.sequence
        elif cls == collections.abc.MutableSequence:
            o_ctor = opt.mutable_sequence
        if o_ctor is not None:
            return o_ctor

    return DEFAULT_ITERABLE_CONCRETE_TYPES.get(cls, cls)  # noqa


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
    cls: type
    e: Unmarshaler

    ctor: ta.Callable[[collections.abc.Iterable], ta.Any] | None = None

    def unmarshal(self, ctx: UnmarshalContext, v: Value) -> ta.Iterable:
        if (ctor := self.ctor) is None:
            ctor = get_default_iterable_constructor(self.cls, ctx.options)
        return ctor(map(functools.partial(self.e.unmarshal, ctx), check.isinstance(v, collections.abc.Iterable)))


class IterableUnmarshalerFactory(UnmarshalerFactoryMethodClass):
    @UnmarshalerFactoryMethodClass.make_unmarshaler.register
    def _make_generic(self, ctx: UnmarshalFactoryContext, rty: rfl.Type) -> ta.Callable[[], Unmarshaler] | None:
        if not (isinstance(rty, rfl.Generic) and issubclass(rty.cls, collections.abc.Iterable)):
            return None
        return lambda: IterableUnmarshaler(rty.cls, ctx.make_unmarshaler(check.single(rty.args)))  # noqa

    @UnmarshalerFactoryMethodClass.make_unmarshaler.register
    def _make_concrete(self, ctx: UnmarshalFactoryContext, rty: rfl.Type) -> ta.Callable[[], Unmarshaler] | None:
        if not (isinstance(rty, type) and issubclass(rty, collections.abc.Iterable)):
            return None
        return lambda: IterableUnmarshaler(check.isinstance(rty, type), ctx.make_unmarshaler(ta.Any))
