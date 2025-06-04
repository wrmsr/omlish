import typing as ta

from omlish import check
from omlish import dataclasses as dc
from omlish import lang
from omlish import marshal as msh
from omlish import reflect as rfl
from omlish import typedvalues as tv

from .requests import Request
from .responses import Response


##


def _is_rr_rty(rty: rfl.Type) -> bool:
    return (
        isinstance(rty, (type, rfl.Generic)) and
        issubclass(check.not_none(rfl.get_concrete_type(rty)), (Request, Response))
    )


@dc.dataclass(frozen=True)
class _RequestResponseMarshaler(msh.Marshaler):
    rty: rfl.Type
    v_m: msh.Marshaler | None

    def marshal(self, ctx: msh.MarshalContext, o: ta.Any) -> msh.Value:
        tv_types_set = o._typed_values_info().tv_types_set  # noqa  # FIXME
        tv_ta = tv.TypedValues[ta.Union[*tv_types_set]]  # type: ignore
        tv_m = ctx.make(tv_ta)
        tv_v = check.isinstance(tv_m.marshal(ctx, o._typed_values), ta.Sequence)  # noqa
        if self.v_m is None:
            orty: rfl.Generic = check.isinstance(rfl.type_(rfl.get_orig_class(o)), rfl.Generic)
            check.state(orty.cls in (Request, Response))
            v_rty, tv_rty = orty.args
            v_v = ctx.make(v_rty).marshal(ctx, o.v)
        else:
            v_v = self.v_m.marshal(ctx, o.v)
        return [v_v, *tv_v]


class _RequestResponseMarshalerFactory(msh.SimpleMarshalerFactory):
    def guard(self, ctx: msh.MarshalContext, rty: rfl.Type) -> bool:
        return _is_rr_rty(rty)

    def fn(self, ctx: msh.MarshalContext, rty: rfl.Type) -> msh.Marshaler:
        if isinstance(rty, type):
            rty = rfl.type_(rfl.get_orig_class(rty))
        if isinstance(rty, rfl.Generic):
            v_rty, tv_rty = rty.args
        else:
            # FIXME: ...
            raise TypeError(rty)
        v_m: msh.Marshaler | None = None
        if not isinstance(v_rty, ta.TypeVar):
            v_m = ctx.make(v_rty)
        return _RequestResponseMarshaler(rty, v_m)


@dc.dataclass(frozen=True)
class _RequestResponseUnmarshaler(msh.Unmarshaler):
    rty: rfl.Type
    v_u: msh.Unmarshaler
    tv_u: msh.Unmarshaler

    def unmarshal(self, ctx: msh.UnmarshalContext, v: msh.Value) -> ta.Any:
        check.not_isinstance(v, str)
        v_v, *tv_vs = check.isinstance(v, ta.Sequence)
        v = self.v_u.unmarshal(ctx, v_v)
        tvs = self.tv_u.unmarshal(ctx, tv_vs)
        cty = rfl.get_concrete_type(self.rty)
        return cty(v, tvs)  # type: ignore


class _RequestResponseUnmarshalerFactory(msh.SimpleUnmarshalerFactory):
    def guard(self, ctx: msh.UnmarshalContext, rty: rfl.Type) -> bool:
        return _is_rr_rty(rty)

    def fn(self, ctx: msh.UnmarshalContext, rty: rfl.Type) -> msh.Unmarshaler:
        if isinstance(rty, rfl.Generic):
            v_rty, tv_rty = rty.args
        else:
            # FIXME: ...
            raise TypeError(rty)
        tv_types_set = check.isinstance(tv_rty, rfl.Union).args
        tv_ta = tv.TypedValues[ta.Union[*tv_types_set]]  # type: ignore
        tv_u = ctx.make(tv_ta)
        v_u = ctx.make(v_rty)
        return _RequestResponseUnmarshaler(rty, v_u, tv_u)


@lang.static_init
def _install_standard_marshalling() -> None:
    msh.install_standard_factories(
        _RequestResponseMarshalerFactory(),
        _RequestResponseUnmarshalerFactory(),
    )
