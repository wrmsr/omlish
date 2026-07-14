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
from ..polymorphism.api import AUTO_STRIP_SUFFIX
from ..polymorphism.api import Polymorphism
from ..polymorphism.api import WrapperTypeTagging
from ..polymorphism.api import polymorphism_from_subclasses
from ..polymorphism.marshal import make_polymorphism_marshaler
from ..polymorphism.unmarshal import make_polymorphism_unmarshaler


##


def _get_scalar_typed_value_cls(rty: rfl.Type) -> type | None:
    if (
            (cls := rfl.get_runtime_type_or_none(rty)) is not None and
            issubclass(cls, tv.ScalarTypedValue) and
            not lang.is_abstract_class(cls)
    ):
        return cls
    return None


def _get_abstract_typed_value_cls(rty: rfl.Type) -> type | None:
    if (
            (cls := rfl.get_runtime_type_or_none(rty)) is not None and
            issubclass(cls, tv.TypedValue) and
            lang.is_abstract_class(cls) and
            issubclass(cls, lang.Sealed)
    ):
        return cls
    return None


def _build_typed_value_poly(cls: type) -> Polymorphism:
    ty: type[tv.TypedValue] = check.issubclass(cls, tv.TypedValue)  # noqa
    check.state(lang.is_abstract_class(ty))

    return polymorphism_from_subclasses(
        ty,
        naming=Naming.SNAKE,
        strip_suffix=AUTO_STRIP_SUFFIX,
    )


class TypedValueMarshalerFactory(MarshalerFactoryMethodClass):
    @MarshalerFactoryMethodClass.make_marshaler.register
    def _make_scalar(self, ctx: MarshalFactoryContext, rty: rfl.Type) -> ta.Callable[[], Marshaler] | None:
        if (cls := _get_scalar_typed_value_cls(rty)) is None:
            return None

        def inner() -> Marshaler:
            dc_rfl = dc.reflect(check.not_none(cls))
            v_rty = check.single(dc_rfl.fields_inspection.generic_replaced_field_annotations.values())
            v_m = ctx.make_marshaler(v_rty)
            return WrappedMarshaler(lambda _, o: o.v, v_m)

        return inner

    @MarshalerFactoryMethodClass.make_marshaler.register
    def _make_abstract(self, ctx: MarshalFactoryContext, rty: rfl.Type) -> ta.Callable[[], Marshaler] | None:
        if (cls := _get_abstract_typed_value_cls(rty)) is None:
            return None

        return lambda: make_polymorphism_marshaler(
            _build_typed_value_poly(check.not_none(cls)).impls,
            WrapperTypeTagging(),
            ctx,
        )


class TypedValueUnmarshalerFactory(UnmarshalerFactoryMethodClass):
    @UnmarshalerFactoryMethodClass.make_unmarshaler.register
    def _make_scalar(self, ctx: UnmarshalFactoryContext, rty: rfl.Type) -> ta.Callable[[], Unmarshaler] | None:
        if (cls := _get_scalar_typed_value_cls(rty)) is None:
            return None

        def inner() -> Unmarshaler:
            ty = check.not_none(cls)
            dc_rfl = dc.reflect(ty)
            v_rty = check.single(dc_rfl.fields_inspection.generic_replaced_field_annotations.values())
            v_u = ctx.make_unmarshaler(v_rty)
            return WrappedUnmarshaler(lambda _, v: ty(v), v_u)

        return inner

    @UnmarshalerFactoryMethodClass.make_unmarshaler.register
    def _make_abstract(self, ctx: UnmarshalFactoryContext, rty: rfl.Type) -> ta.Callable[[], Unmarshaler] | None:  # noqa
        if (cls := _get_abstract_typed_value_cls(rty)) is None:
            return None

        return lambda: make_polymorphism_unmarshaler(
            _build_typed_value_poly(check.not_none(cls)).impls,
            WrapperTypeTagging(),
            ctx,
        )
