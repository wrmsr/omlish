from omlish import check
from omlish import dataclasses as dc
from omlish import lang
from omlish import marshal as msh
from omlish import reflect as rfl
from omlish.funcs import match as mfs

from .collection import TypedValues
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
        v_rty = check.single(dc_rfl.generic_replaced_field_annotations.values())
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
        v_rty = check.single(dc_rfl.generic_replaced_field_annotations.values())
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

    opt_cls_set: set[type[TypedValue]] = set()

    todo = [check.single(gty.args)]
    seen = set()
    while todo:
        cur = todo.pop()
        if cur in seen:
            continue
        seen.add(cur)

        if isinstance(cur, rfl.Union):
            todo.extend(cur.args)
        else:
            opt_cls_set.add(check.issubclass(check.isinstance(cur, type), TypedValue))

    opt_impls: list[msh.Impl] = []
    for opt_cls in opt_cls_set:
        opt_impls.extend(_build_typed_value_poly(opt_cls).impls)

    return msh.Impls(opt_impls)


class TypedValuesMarshalerFactory(msh.MarshalerFactoryMatchClass):
    @mfs.simple(lambda _, ctx, rty: isinstance(rty, rfl.Generic) and rty.cls is TypedValues)
    def _build(self, ctx: msh.MarshalContext, rty: rfl.Type) -> msh.Marshaler:
        opt_m = msh.make_polymorphism_marshaler(
            msh.Impls(_build_typed_values_impls(rty)),
            msh.WrapperTypeTagging(),
            ctx,
        )
        return msh.IterableMarshaler(opt_m)


class TypedValuesUnmarshalerFactory(msh.UnmarshalerFactoryMatchClass):
    @mfs.simple(lambda _, ctx, rty: isinstance(rty, rfl.Generic) and rty.cls is TypedValues)
    def _build(self, ctx: msh.UnmarshalContext, rty: rfl.Type) -> msh.Unmarshaler:
        opt_u = msh.make_polymorphism_unmarshaler(
            msh.Impls(_build_typed_values_impls(rty)),
            msh.WrapperTypeTagging(),
            ctx,
        )
        return msh.IterableUnmarshaler(lambda it: TypedValues(*it), opt_u)  # noqa


##


@lang.static_init
def _install_standard_marshalling() -> None:
    msh.install_standard_factories(
        TypedValueMarshalerFactory(),
        TypedValueUnmarshalerFactory(),

        TypedValuesMarshalerFactory(),
        TypedValuesUnmarshalerFactory(),
    )
