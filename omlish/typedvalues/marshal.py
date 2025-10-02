import typing as ta

from .. import check
from .. import dataclasses as dc
from .. import lang
from .. import marshal as msh
from .. import reflect as rfl
from .collection import TypedValues
from .reflect import reflect_typed_values_impls
from .values import ScalarTypedValue
from .values import TypedValue


##


def _build_typed_value_poly(rty: rfl.Type) -> msh.Polymorphism:
    ty: type[TypedValue] = check.issubclass(check.isinstance(rty, type), TypedValue)  # noqa
    check.state(lang.is_abstract_class(ty))
    return msh.polymorphism_from_subclasses(
        ty,
        naming=msh.Naming.SNAKE,
        strip_suffix=msh.AutoStripSuffix,
    )


class TypedValueMarshalerFactory(msh.MarshalerFactoryMethodClass):
    @msh.MarshalerFactoryMethodClass.make_marshaler.register
    def _make_scalar(self, ctx: msh.MarshalFactoryContext, rty: rfl.Type) -> ta.Callable[[], msh.Marshaler] | None:
        if not (
            isinstance(rty, type) and
            issubclass(rty, ScalarTypedValue) and
            not lang.is_abstract_class(rty)
        ):
            return None

        def inner() -> msh.Marshaler:
            dc_rfl = dc.reflect(check.isinstance(rty, type))
            v_rty = check.single(dc_rfl.fields_inspection.generic_replaced_field_annotations.values())
            v_m = ctx.make_marshaler(v_rty)
            return msh.WrappedMarshaler(lambda _, o: o.v, v_m)

        return inner

    @msh.MarshalerFactoryMethodClass.make_marshaler.register
    def _make_abstract(self, ctx: msh.MarshalFactoryContext, rty: rfl.Type) -> ta.Callable[[], msh.Marshaler] | None:
        if not (
            isinstance(rty, type) and
            issubclass(rty, TypedValue) and
            lang.is_abstract_class(rty)
        ):
            return None

        return lambda: msh.make_polymorphism_marshaler(
            _build_typed_value_poly(rty).impls,
            msh.WrapperTypeTagging(),
            ctx,
        )


class TypedValueUnmarshalerFactory(msh.UnmarshalerFactoryMethodClass):
    @msh.UnmarshalerFactoryMethodClass.make_unmarshaler.register
    def _make_scalar(self, ctx: msh.UnmarshalFactoryContext, rty: rfl.Type) -> ta.Callable[[], msh.Unmarshaler] | None:
        if not (
            isinstance(rty, type) and
            issubclass(rty, ScalarTypedValue) and
            not lang.is_abstract_class(rty)
        ):
            return None

        def inner() -> msh.Unmarshaler:
            dc_rfl = dc.reflect(rty)
            v_rty = check.single(dc_rfl.fields_inspection.generic_replaced_field_annotations.values())
            v_u = ctx.make_unmarshaler(v_rty)
            return msh.WrappedUnmarshaler(lambda _, v: rty(v), v_u)

        return inner

    @msh.UnmarshalerFactoryMethodClass.make_unmarshaler.register
    def _make_abstract(self, ctx: msh.UnmarshalFactoryContext, rty: rfl.Type) -> ta.Callable[[], msh.Unmarshaler] | None:  # noqa
        if not (
            isinstance(rty, type) and
            issubclass(rty, TypedValue) and
            lang.is_abstract_class(rty)
        ):
            return None

        return lambda: msh.make_polymorphism_unmarshaler(
            _build_typed_value_poly(rty).impls,
            msh.WrapperTypeTagging(),
            ctx,
        )


##


def _build_typed_values_impls(rty: rfl.Type) -> msh.Impls:
    gty = check.isinstance(rty, rfl.Generic)
    check.is_(gty.cls, TypedValues)

    tv_cls_set = reflect_typed_values_impls(
        check.single(gty.args),
        find_abstract_subclasses=True,
    )

    tv_impls: list[msh.Impl] = [
        msh.Impl(
            tv_cls,
            msh.translate_name(tv_cls.__name__, msh.Naming.SNAKE),
        )
        for tv_cls in tv_cls_set
    ]
    return msh.Impls(tv_impls)


#


def build_typed_values_marshaler(ctx: msh.MarshalFactoryContext, rty: rfl.Type) -> msh.Marshaler:
    tv_m = msh.make_polymorphism_marshaler(
        msh.Impls(_build_typed_values_impls(rty)),
        msh.WrapperTypeTagging(),
        ctx,
    )
    return msh.IterableMarshaler(tv_m)


class TypedValuesMarshalerFactory(msh.MarshalerFactoryMethodClass):
    @msh.MarshalerFactoryMethodClass.make_marshaler.register
    def _make_generic(self, ctx: msh.MarshalFactoryContext, rty: rfl.Type) -> ta.Callable[[], msh.Marshaler] | None:
        if not (isinstance(rty, rfl.Generic) and rty.cls is TypedValues):
            return None
        return lambda: build_typed_values_marshaler(ctx, rty)

    @msh.MarshalerFactoryMethodClass.make_marshaler.register
    def _make_concrete(self, ctx: msh.MarshalFactoryContext, rty: rfl.Type) -> ta.Callable[[], msh.Marshaler] | None:
        if rty is not TypedValues:
            return None
        return lambda: lang.raise_(NotImplementedError)


#


def build_typed_values_unmarshaler(ctx: msh.UnmarshalFactoryContext, rty: rfl.Type) -> msh.Unmarshaler:
    tv_u = msh.make_polymorphism_unmarshaler(
        msh.Impls(_build_typed_values_impls(rty)),
        msh.WrapperTypeTagging(),
        ctx,
    )
    return msh.IterableUnmarshaler(lambda it: TypedValues(*it), tv_u)  # noqa


class TypedValuesUnmarshalerFactory(msh.UnmarshalerFactoryMethodClass):
    @msh.UnmarshalerFactoryMethodClass.make_unmarshaler.register
    def _build(self, ctx: msh.UnmarshalFactoryContext, rty: rfl.Type) -> ta.Callable[[], msh.Unmarshaler] | None:
        if not (isinstance(rty, rfl.Generic) and rty.cls is TypedValues):
            return None
        return lambda: build_typed_values_unmarshaler(ctx, rty)

    @msh.UnmarshalerFactoryMethodClass.make_unmarshaler.register
    def _build_concrete(self, ctx: msh.UnmarshalFactoryContext, rty: rfl.Type) -> ta.Callable[[], msh.Unmarshaler] | None:  # noqa
        if rty is not TypedValues:
            return None
        return lambda: lang.raise_(NotImplementedError)


##


@lang.static_init
def _install_standard_marshaling() -> None:
    msh.install_standard_factories(
        TypedValueMarshalerFactory(),
        TypedValueUnmarshalerFactory(),

        TypedValuesMarshalerFactory(),
        TypedValuesUnmarshalerFactory(),
    )
