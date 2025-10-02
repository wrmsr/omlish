import typing as ta

from omlish import dataclasses as dc
from omlish import lang
from omlish import marshal as msh
from omlish import reflect as rfl
from omlish.typedvalues.marshal import build_typed_values_marshaler
from omlish.typedvalues.marshal import build_typed_values_unmarshaler

from .json import JsonValue


##


@dc.dataclass()
class _TypedValuesFieldMarshalerFactory(msh.MarshalerFactory):
    tvs_rty: rfl.Type

    def make_marshaler(self, ctx: msh.MarshalFactoryContext, rty: rfl.Type) -> ta.Callable[[], msh.Marshaler] | None:
        return lambda: build_typed_values_marshaler(ctx, self.tvs_rty)


@dc.dataclass()
class _TypedValuesFieldUnmarshalerFactory(msh.UnmarshalerFactory):
    tvs_rty: rfl.Type

    def make_unmarshaler(self, ctx: msh.UnmarshalFactoryContext, rty: rfl.Type) -> ta.Callable[[], msh.Unmarshaler] | None:  # noqa
        return lambda: build_typed_values_unmarshaler(ctx, self.tvs_rty)


##


class MarshalJsonValue(lang.NotInstantiable, lang.Final):
    pass


class _JsonValueMarshalerFactory(msh.MarshalerFactory):
    def make_marshaler(self, ctx: msh.MarshalFactoryContext, rty: rfl.Type) -> ta.Callable[[], msh.Marshaler] | None:
        if rty is not MarshalJsonValue:
            return None
        return lambda: msh.NopMarshalerUnmarshaler()


class _JsonValueUnmarshalerFactory(msh.UnmarshalerFactory):
    def make_unmarshaler(self, ctx: msh.UnmarshalFactoryContext, rty: rfl.Type) -> ta.Callable[[], msh.Unmarshaler] | None:  # noqa
        if rty is not MarshalJsonValue:
            return None
        return lambda: msh.NopMarshalerUnmarshaler()


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
