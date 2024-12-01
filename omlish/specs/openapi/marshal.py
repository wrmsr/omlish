import typing as ta

from ... import check
from ... import dataclasses as dc
from ... import lang
from ... import marshal as msh
from ... import reflect as rfl
from ...funcs import match as mfs
from .openapi import Reference


#


def _reference_union_arg(rty: rfl.Type) -> rfl.Type | None:
    if isinstance(rty, rfl.Union) and len(rty.args) == 2 and Reference in rty.args:
        return check.single(a for a in rty.args if a is not Reference)
    else:
        return None


@dc.dataclass(frozen=True)
class _ReferenceUnionMarshaler(msh.Marshaler):
    m: msh.Marshaler
    r: msh.Marshaler

    def marshal(self, ctx: msh.MarshalContext, o: ta.Any) -> msh.Value:
        if isinstance(o, Reference):
            return self.r.marshal(ctx, o)
        else:
            return self.m.marshal(ctx, o)


class _ReferenceUnionMarshalerFactory(msh.MarshalerFactoryMatchClass):
    @mfs.simple(lambda _, ctx, rty: _reference_union_arg(rty) is not None)
    def _build(self, ctx: msh.MarshalContext, rty: rfl.Type) -> msh.Marshaler:
        return _ReferenceUnionMarshaler(ctx.make(check.not_none(_reference_union_arg(rty))), ctx.make(Reference))


@dc.dataclass(frozen=True)
class _ReferenceUnionUnmarshaler(msh.Unmarshaler):
    u: msh.Unmarshaler
    r: msh.Unmarshaler

    def unmarshal(self, ctx: msh.UnmarshalContext, v: msh.Value) -> ta.Any:
        if not isinstance(v, ta.Mapping):
            raise TypeError(v)
        elif '$ref' in v:
            return self.r.unmarshal(ctx, v)
        else:
            return self.u.unmarshal(ctx, v)  # noqa


class _ReferenceUnionUnmarshalerFactory(msh.UnmarshalerFactoryMatchClass):
    @mfs.simple(lambda _, ctx, rty: _reference_union_arg(rty) is not None)
    def _build(self, ctx: msh.UnmarshalContext, rty: rfl.Type) -> msh.Unmarshaler:
        return _ReferenceUnionUnmarshaler(ctx.make(check.not_none(_reference_union_arg(rty))), ctx.make(Reference))


@lang.static_init
def _install_standard_marshalling() -> None:
    msh.STANDARD_MARSHALER_FACTORIES[0:0] = [_ReferenceUnionMarshalerFactory()]
    msh.STANDARD_UNMARSHALER_FACTORIES[0:0] = [_ReferenceUnionUnmarshalerFactory()]
