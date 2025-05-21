"""
TODO:
 - can this for reuse
"""
from omlish import check
from omlish import dataclasses as dc
from omlish import lang
from omlish import marshal as msh
from omlish import reflect as rfl

from .tokens import Tokens


##


class TokensMarshalerFactory(msh.SimpleMarshalerFactory):
    def guard(self, ctx: msh.MarshalContext, rty: rfl.Type) -> bool:
        return rty is Tokens

    def fn(self, ctx: msh.MarshalContext, rty: rfl.Type) -> msh.Marshaler:
        rty = check.isinstance(check.is_(rty, Tokens), type)
        dc_rfl = dc.reflect(rty)
        dc_f = check.single(dc_rfl.fields.values())
        v_rty = rfl.type_(dc_f.type)
        v_m = ctx.make(v_rty)
        f_n = dc_f.name
        return msh.WrappedMarshaler(lambda _, o: getattr(o, f_n), v_m)


class TokensUnmarshalerFactory(msh.SimpleUnmarshalerFactory):
    def guard(self, ctx: msh.UnmarshalContext, rty: rfl.Type) -> bool:
        return rty is Tokens

    def fn(self, ctx: msh.UnmarshalContext, rty: rfl.Type) -> msh.Unmarshaler:
        rty = check.isinstance(check.is_(rty, Tokens), type)
        dc_rfl = dc.reflect(rty)
        dc_f = check.single(dc_rfl.fields.values())
        v_rty = rfl.type_(dc_f.type)
        v_u = ctx.make(v_rty)
        return msh.WrappedUnmarshaler(lambda _, v: rty(v), v_u)


@lang.static_init
def _install_standard_marshalling() -> None:
    msh.install_standard_factories(
        TokensMarshalerFactory(),
        TokensUnmarshalerFactory(),
    )
