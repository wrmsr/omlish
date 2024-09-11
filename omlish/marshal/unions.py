import dataclasses as dc
import typing as ta

from .. import check
from .. import matchfns as mfs
from .. import reflect as rfl
from .base import MarshalContext
from .base import Marshaler
from .base import MarshalerFactory
from .base import UnmarshalContext
from .base import Unmarshaler
from .base import UnmarshalerFactory
from .values import Value


##


class MatchUnionMarshaler(Marshaler):
    mmf: mfs.MultiMatchFn[[UnmarshalContext, Value], ta.Any]

    def marshal(self, ctx: MarshalContext, o: ta.Any) -> Value:
        try:
            m = self.mmf.match(ctx, o)
        except mfs.AmbiguousMatchesError:
            raise ValueError(o)  # noqa
        return m.fn(ctx, o)


class MatchUnionUnmarshaler(Unmarshaler):
    mmf: mfs.MultiMatchFn[[UnmarshalContext, Value], ta.Any]

    def unmarshal(self, ctx: UnmarshalContext, v: Value) -> ta.Any:
        try:
            m = self.mmf.match(ctx, v)
        except mfs.AmbiguousMatchesError:
            raise ValueError(v)  # noqa
        return m.fn(ctx, v)


##


PRIMITIVE_UNION_TYPES: tuple[type, ...] = (
    float,
    int,
    str,
)


#


@dc.dataclass(frozen=True)
class PrimitiveUnionMarshaler(Marshaler):
    tys: ta.Sequence[type]

    def marshal(self, ctx: MarshalContext, o: ta.Any) -> Value:
        raise NotImplementedError


@dc.dataclass(frozen=True)
class PrimitiveUnionMarshalerFactory(MarshalerFactory):
    tys: ta.Sequence[type] = PRIMITIVE_UNION_TYPES

    def guard(self, ctx: MarshalContext, rty: rfl.Type) -> bool:
        return isinstance(rty, rfl.Union) and all(a in self.tys for a in rty.args)

    def fn(self, ctx: MarshalContext, rty: rfl.Type) -> Marshaler:
        args = check.isinstance(rty, rfl.Union).args
        return PrimitiveUnionMarshaler([t for t in self.tys if t in args])


#


@dc.dataclass(frozen=True)
class PrimitiveUnionUnmarshaler(Unmarshaler):
    tys: ta.Sequence[type]

    def unmarshal(self, ctx: UnmarshalContext, v: Value) -> ta.Any:
        raise NotImplementedError


@dc.dataclass(frozen=True)
class PrimitiveUnionUnmarshalerFactory(UnmarshalerFactory):
    tys: ta.Sequence[type] = PRIMITIVE_UNION_TYPES

    def guard(self, ctx: UnmarshalContext, rty: rfl.Type) -> bool:
        return isinstance(rty, rfl.Union) and all(a in self.tys for a in rty.args)

    def fn(self, ctx: UnmarshalContext, rty: rfl.Type) -> Unmarshaler:
        args = check.isinstance(rty, rfl.Union).args
        return PrimitiveUnionUnmarshaler([t for t in self.tys if t in args])


#


PRIMITIVE_UNION_MARSHALER_FACTORY = PrimitiveUnionMarshalerFactory()
PRIMITIVE_UNION_UNMARSHALER_FACTORY = PrimitiveUnionUnmarshalerFactory()
