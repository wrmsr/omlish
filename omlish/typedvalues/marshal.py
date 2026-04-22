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


def _is_valid_abstract_typed_value(rty: rfl.Type) -> bool:
    return (
        isinstance(rty, type) and
        issubclass(rty, TypedValue) and
        lang.is_abstract_class(rty) and
        issubclass(rty, lang.Sealed)
    )


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
        if not _is_valid_abstract_typed_value(rty):
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
        if not _is_valid_abstract_typed_value(rty):
            return None

        return lambda: msh.make_polymorphism_unmarshaler(
            _build_typed_value_poly(rty).impls,
            msh.WrapperTypeTagging(),
            ctx,
        )


##


def _is_typed_values_union(rty: rfl.Type) -> bool:
    return (
        isinstance(rty, rfl.Union) and
        all(
            (isinstance(a, type) and issubclass(a, TypedValue)) or
            (isinstance(a, rfl.Generic) and issubclass(a.cls, TypedValue))
            for a in rty.args
        )
    )


def _build_typed_value_union_poly(ctx: msh.BaseContext, rty: rfl.Type) -> msh.Impls:
    def gus(sty: type) -> list[type]:
        if isinstance(ctx, msh.MarshalFactoryContext):
            m = ctx.make_marshaler(sty)  # noqa
            impls = check.isinstance(m, msh.PolymorphismMarshaler).get_impls()
        elif isinstance(ctx, msh.UnmarshalFactoryContext):
            u = ctx.make_unmarshaler(sty)  # noqa
            impls = check.isinstance(u, msh.PolymorphismUnmarshaler).get_impls()
        else:
            raise TypeError(ctx)

        impls = check.not_none(impls)

        return [i.ty for i in impls]

    tv_cls_set = reflect_typed_values_impls(
        rty,
        find_abstract_subclasses=True,
        get_unsealed_subclasses=gus,
    )

    return msh.Impls([
        msh.Impl(
            tv_cls,
            msh.translate_name(tv_cls.__name__, msh.Naming.SNAKE),
        )
        for tv_cls in tv_cls_set
    ])


class TypedValueUnionMarshalerFactory(msh.MarshalerFactoryMethodClass):
    @msh.MarshalerFactoryMethodClass.make_marshaler.register
    def _make_union(self, ctx: msh.MarshalFactoryContext, rty: rfl.Type) -> ta.Callable[[], msh.Marshaler] | None:
        if not _is_typed_values_union(rty):
            return None

        return lambda: msh.make_polymorphism_marshaler(
            _build_typed_value_union_poly(ctx, rty),
            msh.WrapperTypeTagging(),
            ctx,
        )


class TypedValueUnionUnmarshalerFactory(msh.UnmarshalerFactoryMethodClass):
    @msh.UnmarshalerFactoryMethodClass.make_unmarshaler.register
    def _make_union(self, ctx: msh.UnmarshalFactoryContext, rty: rfl.Type) -> ta.Callable[[], msh.Unmarshaler] | None:
        if not _is_typed_values_union(rty):
            return None

        return lambda: msh.make_polymorphism_unmarshaler(
            _build_typed_value_union_poly(ctx, rty),
            msh.WrapperTypeTagging(),
            ctx,
        )


##


def build_typed_values_marshaler(ctx: msh.MarshalFactoryContext, rty: rfl.Type) -> msh.Marshaler:
    gty = check.isinstance(rty, rfl.Generic)
    check.is_(gty.cls, TypedValues)

    return msh.IterableMarshaler(
        ctx.make_marshaler(check.single(gty.args)),
    )


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


def build_typed_values_unmarshaler(ctx: msh.UnmarshalFactoryContext, rty: rfl.Type) -> msh.Unmarshaler:
    gty = check.isinstance(rty, rfl.Generic)
    check.is_(gty.cls, TypedValues)

    return msh.IterableUnmarshaler(
        TypedValues,
        ctx.make_unmarshaler(check.single(gty.args)),
        ctor=lambda it: TypedValues(*it),
    )


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

        TypedValueUnionMarshalerFactory(),
        TypedValueUnionUnmarshalerFactory(),

        TypedValuesMarshalerFactory(),
        TypedValuesUnmarshalerFactory(),
    )
