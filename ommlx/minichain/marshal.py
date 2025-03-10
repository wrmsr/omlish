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
            msh.polymorphism_from_subclasses(rty).impls,
            msh.WrapperTypeTagging(),
            ctx,
        )


class OptionUnmarshalerFactory(msh.UnmarshalerFactoryMatchClass):
    @mfs.simple(lambda _, ctx, rty: isinstance(rty, type) and issubclass(rty, ScalarOption) and not lang.is_abstract_class(rty))  # noqa
    def _build_scalar(self, ctx: msh.UnmarshalContext, rty: rfl.Type) -> msh.Unmarshaler:
        dc_rfl = dc.reflect(check.isinstance(rty, type))
        v_rty = check.single(dc_rfl.generic_replaced_field_annotations.values())
        v_u = ctx.make(v_rty)
        return msh.WrappedUnmarshaler(lambda _, v: rty(v), v_u)

    @mfs.simple(lambda _, ctx, rty: isinstance(rty, type) and issubclass(rty, Option) and lang.is_abstract_class(rty))
    def _build_abstract(self, ctx: msh.UnmarshalContext, rty: rfl.Type) -> msh.Unmarshaler:
        return msh.make_polymorphism_unmarshaler(
            msh.polymorphism_from_subclasses(rty).impls,
            msh.WrapperTypeTagging(),
            ctx,
        )


##


class OptionsMarshalerFactory(msh.MarshalerFactoryMatchClass):
    @mfs.simple(lambda _, ctx, rty: isinstance(rty, rfl.Generic) and rty.cls is Options)
    def _build(self, ctx: msh.MarshalContext, rty: rfl.Type) -> msh.Marshaler:
        gty = check.isinstance(rty, rfl.Generic)
        check.is_(gty.cls, Options)
        opt_cls_set = {
            check.issubclass(check.isinstance(a, type), Option)
            for a in check.isinstance(check.single(gty.args), rfl.Union).args
        }
        for opt_cls in opt_cls_set:
            opt_m = check.isinstance(ctx.make(opt_cls), msh.PolymorphismMarshaler)
        raise NotImplementedError


class OptionsUnmarshalerFactory(msh.UnmarshalerFactoryMatchClass):
    @mfs.simple(lambda _, ctx, rty: isinstance(rty, rfl.Generic) and rty.cls is Options)
    def _build(self, ctx: msh.UnmarshalContext, rty: rfl.Type) -> msh.Unmarshaler:
        gty = check.isinstance(rty, rfl.Generic)
        check.is_(gty.cls, Options)
        raise NotImplementedError


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
