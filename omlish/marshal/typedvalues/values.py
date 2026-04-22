import typing as ta

from ... import check
from ... import dataclasses as dc
from ... import lang
from ... import reflect as rfl
from ... import typedvalues as tv
from ..api.contexts import MarshalFactoryContext
from ..api.contexts import UnmarshalFactoryContext
from ..api.naming import Naming
from ..api.types import Marshaler
from ..api.types import Unmarshaler
from ..composite.wrapped import WrappedMarshaler
from ..composite.wrapped import WrappedUnmarshaler
from ..factories.method import MarshalerFactoryMethodClass
from ..factories.method import UnmarshalerFactoryMethodClass
from ..polymorphism.api import AutoStripSuffix
from ..polymorphism.api import Polymorphism
from ..polymorphism.api import WrapperTypeTagging
from ..polymorphism.api import polymorphism_from_subclasses
from ..polymorphism.marshal import make_polymorphism_marshaler
from ..polymorphism.unmarshal import make_polymorphism_unmarshaler


##


def _is_valid_abstract_typed_value(rty: rfl.Type) -> bool:
    return (
        isinstance(rty, type) and
        issubclass(rty, tv.TypedValue) and
        lang.is_abstract_class(rty) and
        issubclass(rty, lang.Sealed)
    )


def _build_typed_value_poly(rty: rfl.Type) -> Polymorphism:
    ty: type[tv.TypedValue] = check.issubclass(check.isinstance(rty, type), tv.TypedValue)  # noqa
    check.state(lang.is_abstract_class(ty))

    return polymorphism_from_subclasses(
        ty,
        naming=Naming.SNAKE,
        strip_suffix=AutoStripSuffix,
    )


class TypedValueMarshalerFactory(MarshalerFactoryMethodClass):
    @MarshalerFactoryMethodClass.make_marshaler.register
    def _make_scalar(self, ctx: MarshalFactoryContext, rty: rfl.Type) -> ta.Callable[[], Marshaler] | None:
        if not (
            isinstance(rty, type) and
            issubclass(rty, tv.ScalarTypedValue) and
            not lang.is_abstract_class(rty)
        ):
            return None

        def inner() -> Marshaler:
            dc_rfl = dc.reflect(check.isinstance(rty, type))
            v_rty = check.single(dc_rfl.fields_inspection.generic_replaced_field_annotations.values())
            v_m = ctx.make_marshaler(v_rty)
            return WrappedMarshaler(lambda _, o: o.v, v_m)

        return inner

    @MarshalerFactoryMethodClass.make_marshaler.register
    def _make_abstract(self, ctx: MarshalFactoryContext, rty: rfl.Type) -> ta.Callable[[], Marshaler] | None:
        if not _is_valid_abstract_typed_value(rty):
            return None

        return lambda: make_polymorphism_marshaler(
            _build_typed_value_poly(rty).impls,
            WrapperTypeTagging(),
            ctx,
        )


class TypedValueUnmarshalerFactory(UnmarshalerFactoryMethodClass):
    @UnmarshalerFactoryMethodClass.make_unmarshaler.register
    def _make_scalar(self, ctx: UnmarshalFactoryContext, rty: rfl.Type) -> ta.Callable[[], Unmarshaler] | None:
        if not (
            isinstance(rty, type) and
            issubclass(rty, tv.ScalarTypedValue) and
            not lang.is_abstract_class(rty)
        ):
            return None

        def inner() -> Unmarshaler:
            dc_rfl = dc.reflect(rty)
            v_rty = check.single(dc_rfl.fields_inspection.generic_replaced_field_annotations.values())
            v_u = ctx.make_unmarshaler(v_rty)
            return WrappedUnmarshaler(lambda _, v: rty(v), v_u)

        return inner

    @UnmarshalerFactoryMethodClass.make_unmarshaler.register
    def _make_abstract(self, ctx: UnmarshalFactoryContext, rty: rfl.Type) -> ta.Callable[[], Unmarshaler] | None:  # noqa
        if not _is_valid_abstract_typed_value(rty):
            return None

        return lambda: make_polymorphism_unmarshaler(
            _build_typed_value_poly(rty).impls,
            WrapperTypeTagging(),
            ctx,
        )
