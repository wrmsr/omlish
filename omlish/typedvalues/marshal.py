from .. import check
from .. import dataclasses as dc
from .. import lang
from .. import marshal as msh
from .. import reflect as rfl
from ..funcs import match as mfs
from .collection import TypedValues
from .reflect import reflect_typed_values_impls
from .values import ScalarTypedValue
from .values import TypedValue


##


def _build_typed_value_poly(rty: rfl.Type) -> msh.Polymorphism:
    ty: type[TypedValue] = check.issubclass(check.isinstance(rty, type), TypedValue)
    check.state(lang.is_abstract_class(ty))
    return msh.polymorphism_from_subclasses(
        ty,
        naming=msh.Naming.SNAKE,
        strip_suffix='auto',
    )


class TypedValueMarshalerFactory(msh.MarshalerFactoryMatchClass):
    @mfs.simple(lambda _, ctx, rty: (
        isinstance(rty, type) and
        issubclass(rty, ScalarTypedValue) and
        not lang.is_abstract_class(rty)
    ))
    def _build_scalar(self, ctx: msh.MarshalContext, rty: rfl.Type) -> msh.Marshaler:
        dc_rfl = dc.reflect(check.isinstance(rty, type))
        v_rty = check.single(dc_rfl.fields_inspection.generic_replaced_field_annotations.values())
        v_m = ctx.make(v_rty)
        return msh.WrappedMarshaler(lambda _, o: o.v, v_m)

    @mfs.simple(lambda _, ctx, rty: (
        isinstance(rty, type) and
        issubclass(rty, TypedValue) and
        lang.is_abstract_class(rty)
    ))
    def _build_abstract(self, ctx: msh.MarshalContext, rty: rfl.Type) -> msh.Marshaler:
        return msh.make_polymorphism_marshaler(
            _build_typed_value_poly(rty).impls,
            msh.WrapperTypeTagging(),
            ctx,
        )


class TypedValueUnmarshalerFactory(msh.UnmarshalerFactoryMatchClass):
    @mfs.simple(lambda _, ctx, rty: (
        isinstance(rty, type) and
        issubclass(rty, ScalarTypedValue) and
        not lang.is_abstract_class(rty)
    ))
    def _build_scalar(self, ctx: msh.UnmarshalContext, rty: rfl.Type) -> msh.Unmarshaler:
        rty = check.isinstance(rty, type)
        dc_rfl = dc.reflect(rty)
        v_rty = check.single(dc_rfl.fields_inspection.generic_replaced_field_annotations.values())
        v_u = ctx.make(v_rty)
        return msh.WrappedUnmarshaler(lambda _, v: rty(v), v_u)

    @mfs.simple(lambda _, ctx, rty: (
        isinstance(rty, type) and
        issubclass(rty, TypedValue) and
        lang.is_abstract_class(rty)
    ))
    def _build_abstract(self, ctx: msh.UnmarshalContext, rty: rfl.Type) -> msh.Unmarshaler:
        return msh.make_polymorphism_unmarshaler(
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


def build_typed_values_marshaler(ctx: msh.MarshalContext, rty: rfl.Type) -> msh.Marshaler:
    tv_m = msh.make_polymorphism_marshaler(
        msh.Impls(_build_typed_values_impls(rty)),
        msh.WrapperTypeTagging(),
        ctx,
    )
    return msh.IterableMarshaler(tv_m)


class TypedValuesMarshalerFactory(msh.MarshalerFactoryMatchClass):
    @mfs.simple(lambda _, ctx, rty: isinstance(rty, rfl.Generic) and rty.cls is TypedValues)
    def _build(self, ctx: msh.MarshalContext, rty: rfl.Type) -> msh.Marshaler:
        return build_typed_values_marshaler(ctx, rty)

    @mfs.simple(lambda _, ctx, rty: rty is TypedValues)
    def _build_concrete(self, ctx: msh.MarshalContext, rty: rfl.Type) -> msh.Marshaler:
        raise NotImplementedError


#


def build_typed_values_unmarshaler(ctx: msh.UnmarshalContext, rty: rfl.Type) -> msh.Unmarshaler:
    tv_u = msh.make_polymorphism_unmarshaler(
        msh.Impls(_build_typed_values_impls(rty)),
        msh.WrapperTypeTagging(),
        ctx,
    )
    return msh.IterableUnmarshaler(lambda it: TypedValues(*it), tv_u)  # noqa


class TypedValuesUnmarshalerFactory(msh.UnmarshalerFactoryMatchClass):
    @mfs.simple(lambda _, ctx, rty: isinstance(rty, rfl.Generic) and rty.cls is TypedValues)
    def _build(self, ctx: msh.UnmarshalContext, rty: rfl.Type) -> msh.Unmarshaler:
        return build_typed_values_unmarshaler(ctx, rty)

    @mfs.simple(lambda _, ctx, rty: rty is TypedValues)
    def _build_concrete(self, ctx: msh.UnmarshalContext, rty: rfl.Type) -> msh.Unmarshaler:
        raise NotImplementedError


##


@lang.static_init
def _install_standard_marshalling() -> None:
    msh.install_standard_factories(
        TypedValueMarshalerFactory(),
        TypedValueUnmarshalerFactory(),

        TypedValuesMarshalerFactory(),
        TypedValuesUnmarshalerFactory(),
    )
