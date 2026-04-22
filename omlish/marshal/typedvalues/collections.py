import typing as ta

from ... import check
from ... import lang
from ... import reflect as rfl
from ... import typedvalues as tv
from ..api.contexts import MarshalFactoryContext
from ..api.contexts import UnmarshalFactoryContext
from ..api.types import Marshaler
from ..api.types import Unmarshaler
from ..composite.iterables import IterableMarshaler
from ..composite.iterables import IterableUnmarshaler
from ..factories.method import MarshalerFactoryMethodClass
from ..factories.method import UnmarshalerFactoryMethodClass


##


def build_typed_values_marshaler(ctx: MarshalFactoryContext, rty: rfl.Type) -> Marshaler:
    gty = check.isinstance(rty, rfl.Generic)
    check.is_(gty.cls, tv.TypedValues)

    return IterableMarshaler(
        ctx.make_marshaler(check.single(gty.args)),
    )


class TypedValuesMarshalerFactory(MarshalerFactoryMethodClass):
    @MarshalerFactoryMethodClass.make_marshaler.register
    def _make_generic(self, ctx: MarshalFactoryContext, rty: rfl.Type) -> ta.Callable[[], Marshaler] | None:
        if not (isinstance(rty, rfl.Generic) and rty.cls is tv.TypedValues):
            return None
        return lambda: build_typed_values_marshaler(ctx, rty)

    @MarshalerFactoryMethodClass.make_marshaler.register
    def _make_concrete(self, ctx: MarshalFactoryContext, rty: rfl.Type) -> ta.Callable[[], Marshaler] | None:
        if rty is not tv.TypedValues:
            return None
        return lambda: lang.raise_(NotImplementedError)


def build_typed_values_unmarshaler(ctx: UnmarshalFactoryContext, rty: rfl.Type) -> Unmarshaler:
    gty = check.isinstance(rty, rfl.Generic)
    check.is_(gty.cls, tv.TypedValues)

    return IterableUnmarshaler(
        tv.TypedValues,
        ctx.make_unmarshaler(check.single(gty.args)),
        ctor=lambda it: tv.TypedValues(*it),
    )


class TypedValuesUnmarshalerFactory(UnmarshalerFactoryMethodClass):
    @UnmarshalerFactoryMethodClass.make_unmarshaler.register
    def _build(self, ctx: UnmarshalFactoryContext, rty: rfl.Type) -> ta.Callable[[], Unmarshaler] | None:
        if not (isinstance(rty, rfl.Generic) and rty.cls is tv.TypedValues):
            return None
        return lambda: build_typed_values_unmarshaler(ctx, rty)

    @UnmarshalerFactoryMethodClass.make_unmarshaler.register
    def _build_concrete(self, ctx: UnmarshalFactoryContext, rty: rfl.Type) -> ta.Callable[[], Unmarshaler] | None:  # noqa
        if rty is not tv.TypedValues:
            return None
        return lambda: lang.raise_(NotImplementedError)
