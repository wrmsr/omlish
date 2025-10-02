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

from .types import Vector


##


@dc.dataclass(frozen=True)
class _VectorMarshaler(msh.Marshaler):
    et: msh.Marshaler

    def marshal(self, ctx: msh.MarshalContext, o: ta.Any) -> msh.Value:
        return self.et.marshal(ctx, list(map(float, check.isinstance(o, Vector))))


class _VectorMarshalerFactory(msh.MarshalerFactory):
    def make_marshaler(self, ctx: msh.MarshalFactoryContext, rty: rfl.Type) -> ta.Callable[[], msh.Marshaler] | None:
        if rty is not Vector:
            return None
        return lambda: _VectorMarshaler(ctx.make_marshaler(ta.Sequence[float]))


@dc.dataclass(frozen=True)
class _VectorUnmarshaler(msh.Unmarshaler):
    et: msh.Unmarshaler

    def unmarshal(self, ctx: msh.UnmarshalContext, v: msh.Value) -> ta.Any:
        return Vector(self.et.unmarshal(ctx, v))


class _VectorUnmarshalerFactory(msh.UnmarshalerFactory):
    def make_unmarshaler(self, ctx: msh.UnmarshalFactoryContext, rty: rfl.Type) -> ta.Callable[[], msh.Unmarshaler] | None:  # noqa
        if rty is not Vector:
            return None
        return lambda: _VectorUnmarshaler(ctx.make_unmarshaler(ta.Sequence[float]))


##


@lang.static_init
def _install_standard_marshaling() -> None:
    msh.install_standard_factories(
        _VectorMarshalerFactory(),
        _VectorUnmarshalerFactory(),
    )
