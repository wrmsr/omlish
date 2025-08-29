from omlish import dataclasses as dc
from omlish import marshal as msh
from omlish import reflect as rfl
from omlish.funcs import match as mfs
from omlish.typedvalues.marshal import build_typed_values_marshaler
from omlish.typedvalues.marshal import build_typed_values_unmarshaler


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
