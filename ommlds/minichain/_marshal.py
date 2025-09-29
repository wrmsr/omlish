from omlish import dataclasses as dc
from omlish import lang
from omlish import marshal as msh
from omlish import reflect as rfl
from omlish.funcs import match as mfs
from omlish.typedvalues.marshal import build_typed_values_marshaler
from omlish.typedvalues.marshal import build_typed_values_unmarshaler

from .json import JsonValue


##


@dc.dataclass()
class _TypedValuesFieldMarshalerFactory(msh.MarshalerFactoryMatchClass):
    tvs_rty: rfl.Type

    @mfs.simple(lambda _, ctx, rty: True)
    def _build(self, ctx: msh.MarshalContext, rty: rfl.Type) -> msh.Marshaler:
        return build_typed_values_marshaler(ctx, self.tvs_rty)


@dc.dataclass()
class _TypedValuesFieldUnmarshalerFactory(msh.UnmarshalerFactoryMatchClass):
    tvs_rty: rfl.Type

    @mfs.simple(lambda _, ctx, rty: True)
    def _build(self, ctx: msh.UnmarshalContext, rty: rfl.Type) -> msh.Unmarshaler:
        return build_typed_values_unmarshaler(ctx, self.tvs_rty)


##


class MarshalJsonValue(lang.NotInstantiable, lang.Final):
    pass


class _JsonValueMarshalerFactory(msh.MarshalerFactoryMatchClass):
    @mfs.simple(lambda _, ctx, rty: rty is MarshalJsonValue)
    def _build(self, ctx: msh.MarshalContext, rty: rfl.Type) -> msh.Marshaler:
        return msh.NopMarshalerUnmarshaler()


class _JsonValueUnmarshalerFactory(msh.UnmarshalerFactoryMatchClass):
    @mfs.simple(lambda _, ctx, rty: rty is MarshalJsonValue)
    def _build(self, ctx: msh.UnmarshalContext, rty: rfl.Type) -> msh.Unmarshaler:
        return msh.NopMarshalerUnmarshaler()


##


@lang.static_init
def _install_standard_marshaling() -> None:
    msh.register_global_config(
        JsonValue,
        msh.ReflectOverride(MarshalJsonValue),
        identity=True,
    )

    msh.install_standard_factories(
        _JsonValueMarshalerFactory(),
        _JsonValueUnmarshalerFactory(),
    )
