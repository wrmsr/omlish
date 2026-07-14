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


def _get_typed_values_element(rty: rfl.Type) -> rfl.Type | None:
    if not (isinstance(rty, rfl.Instance) and rty.type.runtime_object is tv.TypedValues and len(rty.args) == 1):
        return None

    ety = check.single(rty.args)

    # A bare `TypedValues` (implicit Any element) is not marshalable - preserved from the old system's concrete-class
    # rejection.
    if isinstance(ety, rfl.AnyType) and ety.type_of_any == rfl.TypeOfAny.FROM_OMITTED_GENERICS:
        return None

    return ety


def _is_bare_typed_values(rty: rfl.Type) -> bool:
    return (
        isinstance(rty, rfl.Instance) and
        rty.type.runtime_object is tv.TypedValues and
        _get_typed_values_element(rty) is None
    )


def build_typed_values_marshaler(ctx: MarshalFactoryContext, rty: rfl.Type) -> Marshaler:
    ety = check.not_none(_get_typed_values_element(ctx._reflect(rty) if not isinstance(rty, rfl.Type) else rty))  # noqa

    return IterableMarshaler(
        ctx.make_marshaler(ety),
    )


class TypedValuesMarshalerFactory(MarshalerFactoryMethodClass):
    @MarshalerFactoryMethodClass.make_marshaler.register
    def _make_generic(self, ctx: MarshalFactoryContext, rty: rfl.Type) -> ta.Callable[[], Marshaler] | None:
        if _get_typed_values_element(rty) is None:
            return None
        return lambda: build_typed_values_marshaler(ctx, rty)

    @MarshalerFactoryMethodClass.make_marshaler.register
    def _make_concrete(self, ctx: MarshalFactoryContext, rty: rfl.Type) -> ta.Callable[[], Marshaler] | None:
        if not _is_bare_typed_values(rty):
            return None
        return lambda: lang.raise_(NotImplementedError)


def build_typed_values_unmarshaler(ctx: UnmarshalFactoryContext, rty: rfl.Type) -> Unmarshaler:
    ety = check.not_none(_get_typed_values_element(ctx._reflect(rty) if not isinstance(rty, rfl.Type) else rty))  # noqa

    return IterableUnmarshaler(
        tv.TypedValues,
        ctx.make_unmarshaler(ety),
        ctor=lambda it: tv.collect(*it),
    )


class TypedValuesUnmarshalerFactory(UnmarshalerFactoryMethodClass):
    @UnmarshalerFactoryMethodClass.make_unmarshaler.register
    def _build(self, ctx: UnmarshalFactoryContext, rty: rfl.Type) -> ta.Callable[[], Unmarshaler] | None:
        if _get_typed_values_element(rty) is None:
            return None
        return lambda: build_typed_values_unmarshaler(ctx, rty)

    @UnmarshalerFactoryMethodClass.make_unmarshaler.register
    def _build_concrete(self, ctx: UnmarshalFactoryContext, rty: rfl.Type) -> ta.Callable[[], Unmarshaler] | None:  # noqa
        if not _is_bare_typed_values(rty):
            return None
        return lambda: lang.raise_(NotImplementedError)
