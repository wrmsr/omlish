import typing as ta

from ... import check
from ... import dataclasses as dc
from ... import lang
from ... import marshal as msh
from ... import reflect as rfl
from .types import NotSpecified


##


_NOT_SPECIFIED_RTY = rfl.type_(type[NotSpecified])


@dc.dataclass(frozen=True)
class NotSpecifiedUnionMarshaler(msh.Marshaler):
    m: msh.Marshaler

    def marshal(self, ctx: msh.MarshalContext, o: ta.Any) -> msh.Value:
        if o is NotSpecified:
            raise TypeError(o)
        return self.m.marshal(ctx, o)


class NotSpecifiedUnionMarshalerFactory(msh.MarshalerFactory):
    def make_marshaler(self, ctx: msh.MarshalFactoryContext, rty: rfl.Type) -> ta.Callable[[], msh.Marshaler] | None:
        if not (
            isinstance(rty, rfl.Union) and
            not rty.is_optional and
            _NOT_SPECIFIED_RTY in rty.args
        ):
            return None

        def inner() -> msh.Marshaler:
            args = set(check.isinstance(rty, rfl.Union).args) - {_NOT_SPECIFIED_RTY}
            nty = rfl.type_(ta.Union[*args])
            m = ctx.make_marshaler(nty)
            return NotSpecifiedUnionMarshaler(m)

        return inner


class NotSpecifiedUnionUnmarshalerFactory(msh.UnmarshalerFactory):
    def make_unmarshaler(self, ctx: msh.UnmarshalFactoryContext, rty: rfl.Type) -> ta.Callable[[], msh.Unmarshaler] | None:  # noqa
        if not (
            isinstance(rty, rfl.Union) and
            not rty.is_optional and
            _NOT_SPECIFIED_RTY in rty.args
        ):
            return None

        def inner() -> msh.Unmarshaler:
            args = set(check.isinstance(rty, rfl.Union).args) - {_NOT_SPECIFIED_RTY}
            nty = rfl.type_(ta.Union[*args])
            return ctx.make_unmarshaler(nty)

        return inner


@lang.static_init
def _install_standard_marshaling() -> None:
    msh.install_standard_factories(
        msh.ForbiddenTypeMarshalerFactory({_NOT_SPECIFIED_RTY}),
        msh.ForbiddenTypeUnmarshalerFactory({_NOT_SPECIFIED_RTY}),

        NotSpecifiedUnionMarshalerFactory(),
        NotSpecifiedUnionUnmarshalerFactory(),
    )
