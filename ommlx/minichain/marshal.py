from omlish import check
from omlish import dataclasses as dc
from omlish import lang
from omlish import marshal as msh
from omlish import reflect as rfl
from omlish.funcs import match as mfs

from .options import Option
from .options import Options
from .options import ScalarOption


##


def _build_option_poly(rty: rfl.Type) -> msh.Polymorphism:
    ty: type[Option] = check.issubclass(check.isinstance(rty, type), Option)
    check.state(lang.is_abstract_class(ty))
    return msh.polymorphism_from_subclasses(
        ty,
        naming=msh.Naming.SNAKE,
    )


class OptionMarshalerFactory(msh.MarshalerFactoryMatchClass):
    @mfs.simple(lambda _, ctx, rty: isinstance(rty, type) and issubclass(rty, ScalarOption) and not lang.is_abstract_class(rty))  # noqa
    def _build_scalar(self, ctx: msh.MarshalContext, rty: rfl.Type) -> msh.Marshaler:
        dc_rfl = dc.reflect(check.isinstance(rty, type))
        v_rty = check.single(dc_rfl.generic_replaced_field_annotations.values())
        v_m = ctx.make(v_rty)
        return msh.WrappedMarshaler(lambda _, o: o.v, v_m)

    @mfs.simple(lambda _, ctx, rty: isinstance(rty, type) and issubclass(rty, Option) and lang.is_abstract_class(rty))
    def _build_abstract(self, ctx: msh.MarshalContext, rty: rfl.Type) -> msh.Marshaler:
        return msh.make_polymorphism_marshaler(
            _build_option_poly(rty).impls,
            msh.WrapperTypeTagging(),
            ctx,
        )


class OptionUnmarshalerFactory(msh.UnmarshalerFactoryMatchClass):
    @mfs.simple(lambda _, ctx, rty: isinstance(rty, type) and issubclass(rty, ScalarOption) and not lang.is_abstract_class(rty))  # noqa
    def _build_scalar(self, ctx: msh.UnmarshalContext, rty: rfl.Type) -> msh.Unmarshaler:
        rty = check.isinstance(rty, type)
        dc_rfl = dc.reflect(rty)
        v_rty = check.single(dc_rfl.generic_replaced_field_annotations.values())
        v_u = ctx.make(v_rty)
        return msh.WrappedUnmarshaler(lambda _, v: rty(v), v_u)

    @mfs.simple(lambda _, ctx, rty: isinstance(rty, type) and issubclass(rty, Option) and lang.is_abstract_class(rty))
    def _build_abstract(self, ctx: msh.UnmarshalContext, rty: rfl.Type) -> msh.Unmarshaler:
        return msh.make_polymorphism_unmarshaler(
            _build_option_poly(rty).impls,
            msh.WrapperTypeTagging(),
            ctx,
        )


##


def _build_options_impls(rty: rfl.Type) -> msh.Impls:
    gty = check.isinstance(rty, rfl.Generic)
    check.is_(gty.cls, Options)

    opt_cls_set: set[type[Option]] = {
        check.issubclass(check.isinstance(a, type), Option)
        for a in check.isinstance(check.single(gty.args), rfl.Union).args
    }

    opt_impls: list[msh.Impl] = []
    for opt_cls in opt_cls_set:
        opt_impls.extend(_build_option_poly(opt_cls).impls)

    return msh.Impls(opt_impls)


class OptionsMarshalerFactory(msh.MarshalerFactoryMatchClass):
    @mfs.simple(lambda _, ctx, rty: isinstance(rty, rfl.Generic) and rty.cls is Options)
    def _build(self, ctx: msh.MarshalContext, rty: rfl.Type) -> msh.Marshaler:
        opt_m = msh.make_polymorphism_marshaler(
            msh.Impls(_build_options_impls(rty)),
            msh.WrapperTypeTagging(),
            ctx,
        )
        return msh.IterableMarshaler(opt_m)


class OptionsUnmarshalerFactory(msh.UnmarshalerFactoryMatchClass):
    @mfs.simple(lambda _, ctx, rty: isinstance(rty, rfl.Generic) and rty.cls is Options)
    def _build(self, ctx: msh.UnmarshalContext, rty: rfl.Type) -> msh.Unmarshaler:
        opt_u = msh.make_polymorphism_unmarshaler(
            msh.Impls(_build_options_impls(rty)),
            msh.WrapperTypeTagging(),
            ctx,
        )
        return msh.IterableUnmarshaler(lambda it: Options(*it), opt_u)  # noqa


##


@lang.static_init
def _install_standard_marshalling() -> None:
    msh.STANDARD_MARSHALER_FACTORIES[0:0] = [
        OptionMarshalerFactory(),
        OptionsMarshalerFactory(),
    ]
    msh.STANDARD_UNMARSHALER_FACTORIES[0:0] = [
        OptionUnmarshalerFactory(),
        OptionsUnmarshalerFactory(),
    ]
