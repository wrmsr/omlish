import typing as ta

from ... import check
from ... import dataclasses as dc
from ... import marshal as msh
from ... import reflect2 as rfl
from .types import NotSpecified


##


_NOT_SPECIFIED_RTY = rfl.reflect_type(type[NotSpecified])

_NOT_SPECIFIED_RTY_KEY = _NOT_SPECIFIED_RTY.type_key()


def _split_not_specified_union(rty: rfl.Type) -> rfl.Type | None:
    """The union with NotSpecified removed, or None if this is not a non-optional union containing NotSpecified."""

    if not (isinstance(rty, rfl.UnionType) and not rfl.is_optional(rty)):
        return None

    rem = [it for it in rty.items if it.type_key() != _NOT_SPECIFIED_RTY_KEY]
    if len(rem) == len(rty.items):
        return None

    check.not_empty(rem)
    return rfl.make_union(rem)


@dc.dataclass(frozen=True)
class NotSpecifiedUnionMarshaler(msh.Marshaler):
    m: msh.Marshaler

    def marshal(self, ctx: msh.MarshalContext, o: ta.Any) -> msh.Value:
        if o is NotSpecified:
            raise TypeError(o)
        return self.m.marshal(ctx, o)


class NotSpecifiedUnionMarshalerFactory(msh.MarshalerFactory):
    def make_marshaler(self, ctx: msh.MarshalFactoryContext, rty: rfl.Type) -> ta.Callable[[], msh.Marshaler] | None:
        if (nty := _split_not_specified_union(rty)) is None:
            return None

        def inner() -> msh.Marshaler:
            m = ctx.make_marshaler(nty)
            return NotSpecifiedUnionMarshaler(m)

        return inner


class NotSpecifiedUnionUnmarshalerFactory(msh.UnmarshalerFactory):
    def make_unmarshaler(self, ctx: msh.UnmarshalFactoryContext, rty: rfl.Type) -> ta.Callable[[], msh.Unmarshaler] | None:  # noqa
        if (nty := _split_not_specified_union(rty)) is None:
            return None

        def inner() -> msh.Unmarshaler:
            return ctx.make_unmarshaler(nty)

        return inner


@msh.register_global_lazy_init
def _install_standard_marshaling(cfgs: msh.ConfigRegistry) -> None:
    msh.install_standard_factories(
        cfgs,

        msh.ForbiddenTypeMarshalerFactory({_NOT_SPECIFIED_RTY}),
        msh.ForbiddenTypeUnmarshalerFactory({_NOT_SPECIFIED_RTY}),

        NotSpecifiedUnionMarshalerFactory(),
        NotSpecifiedUnionUnmarshalerFactory(),
    )
