"""
TODO:
 - can this for reuse
"""
import typing as ta

from omlish import check
from omlish import dataclasses as dc
from omlish import lang
from omlish import marshal as msh
from omlish import reflect as rfl

from .tokens import Tokens


##


class TokensMarshalerFactory(msh.MarshalerFactory):
    def make_marshaler(self, ctx: msh.MarshalFactoryContext, rty: rfl.Type) -> ta.Callable[[], msh.Marshaler] | None:
        if rty is not Tokens:
            return None

        dc_rfl = dc.reflect(Tokens)
        dc_f = check.single(dc_rfl.fields.values())
        v_rty = rfl.type_(dc_f.type)
        v_m = ctx.make_marshaler(v_rty)
        f_n = dc_f.name

        def inner() -> msh.Marshaler:
            return msh.WrappedMarshaler(lambda _, o: getattr(o, f_n), v_m)

        return inner


class TokensUnmarshalerFactory(msh.UnmarshalerFactory):
    def make_unmarshaler(self, ctx: msh.UnmarshalFactoryContext, rty: rfl.Type) -> ta.Callable[[], msh.Unmarshaler] | None:  # noqa
        if rty is not Tokens:
            return None

        dc_rfl = dc.reflect(Tokens)
        dc_f = check.single(dc_rfl.fields.values())
        v_rty = rfl.type_(dc_f.type)
        v_u = ctx.make_unmarshaler(v_rty)

        def inner() -> msh.Unmarshaler:
            return msh.WrappedUnmarshaler(lambda _, v: Tokens(v), v_u)

        return inner


@lang.static_init
def _install_standard_marshaling() -> None:
    msh.install_standard_factories(
        TokensMarshalerFactory(),
        TokensUnmarshalerFactory(),
    )
