import typing as ta

from ... import check
from ... import dataclasses as dc
from ... import lang
from ... import marshal as msh
from ... import reflect as rfl
from ...funcs import match as mfs
from .types import NotSpecified


_NOT_SPECIFIED_RTY = rfl.type_(type[NotSpecified])


@dc.dataclass(frozen=True)
class NotSpecifiedUnionMarshaler(msh.Marshaler):
    m: msh.Marshaler

    def marshal(self, ctx: msh.MarshalContext, o: ta.Any) -> msh.Value:
        if o is NotSpecified:
            raise TypeError(o)
        return self.m.marshal(ctx, o)


class NotSpecifiedUnionMarshalerFactory(msh.MarshalerFactoryMatchClass):
    @mfs.simple(lambda _, ctx, rty: (
        isinstance(rty, rfl.Union) and
        not rty.is_optional and
        _NOT_SPECIFIED_RTY in rty.args
    ))
    def _build(self, ctx: msh.MarshalContext, rty: rfl.Type) -> msh.Marshaler:
        args = set(check.isinstance(rty, rfl.Union).args) - {_NOT_SPECIFIED_RTY}
        nty = rfl.type_(ta.Union[*args])
        m = ctx.make(nty)
        return NotSpecifiedUnionMarshaler(m)


class NotSpecifiedUnionUnmarshalerFactory(msh.UnmarshalerFactoryMatchClass):
    @mfs.simple(lambda _, ctx, rty: (
        isinstance(rty, rfl.Union) and
        not rty.is_optional and
        _NOT_SPECIFIED_RTY in rty.args
    ))
    def _build(self, ctx: msh.UnmarshalContext, rty: rfl.Type) -> msh.Unmarshaler:
        args = set(check.isinstance(rty, rfl.Union).args) - {_NOT_SPECIFIED_RTY}
        nty = rfl.type_(ta.Union[*args])
        return ctx.make(nty)


@lang.static_init
def _install_standard_marshalling() -> None:
    msh.STANDARD_MARSHALER_FACTORIES[0:0] = [
        msh.ForbiddenTypeMarshalerFactory({_NOT_SPECIFIED_RTY}),
        NotSpecifiedUnionMarshalerFactory(),
    ]
    msh.STANDARD_UNMARSHALER_FACTORIES[0:0] = [
        msh.ForbiddenTypeUnmarshalerFactory({_NOT_SPECIFIED_RTY}),
        NotSpecifiedUnionUnmarshalerFactory(),
    ]
