"""
TODO:
 - serialize as base64 bytes? at least support deserializing as it
"""
import dataclasses as dc
import typing as ta

from omlish import check
from omlish import lang
from omlish import marshal as msh
from omlish import reflect as rfl
from omlish.funcs import match as mfs

from .types import Vector


##


@dc.dataclass(frozen=True)
class _VectorMarshaler(msh.Marshaler):
    et: msh.Marshaler

    def marshal(self, ctx: msh.MarshalContext, o: ta.Any) -> msh.Value:
        return self.et.marshal(ctx, list(map(float, check.isinstance(o, Vector))))


class _VectorMarshalerFactory(msh.MarshalerFactoryMatchClass):
    @mfs.simple(lambda _, ctx, rty: rty is Vector)
    def _build(self, ctx: msh.MarshalContext, rty: rfl.Type) -> msh.Marshaler:
        return _VectorMarshaler(ctx.make(ta.Sequence[float]))


@dc.dataclass(frozen=True)
class _VectorUnmarshaler(msh.Unmarshaler):
    et: msh.Unmarshaler

    def unmarshal(self, ctx: msh.UnmarshalContext, v: msh.Value) -> ta.Any:
        return Vector(self.et.unmarshal(ctx, v))


class _VectorUnmarshalerFactory(msh.UnmarshalerFactoryMatchClass):
    @mfs.simple(lambda _, ctx, rty: rty is Vector)
    def _build(self, ctx: msh.UnmarshalContext, rty: rfl.Type) -> msh.Unmarshaler:
        return _VectorUnmarshaler(ctx.make(ta.Sequence[float]))


##


@lang.static_init
def _install_standard_marshalling() -> None:
    msh.install_standard_factories(
        _VectorMarshalerFactory(),
        _VectorUnmarshalerFactory(),
    )
