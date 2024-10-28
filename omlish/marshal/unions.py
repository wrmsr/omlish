import typing as ta

from .. import cached
from .. import check
from .. import dataclasses as dc
from .. import matchfns as mfs
from .. import reflect as rfl
from .base import MarshalContext
from .base import Marshaler
from .base import MarshalerFactory
from .base import UnmarshalContext
from .base import Unmarshaler
from .base import UnmarshalerFactory
from .polymorphism import Impls
from .polymorphism import TypeTagging
from .polymorphism import WrapperTypeTagging
from .polymorphism import make_polymorphism_marshaler
from .polymorphism import make_polymorphism_unmarshaler
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
        if type(o) not in self.tys:
            raise TypeError(o)
        return o


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
        if type(v) not in self.tys:
            raise TypeError(v)
        return v


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


##


@dc.dataclass(frozen=True)
class PolymorphismUnionMarshalerFactory(MarshalerFactory):
    impls: Impls
    tt: TypeTagging = WrapperTypeTagging()

    @cached.property
    @dc.init
    def rty(self) -> rfl.Union:
        return rfl.type_(ta.Union[*tuple(i.ty for i in self.impls)])  # type: ignore

    def guard(self, ctx: MarshalContext, rty: rfl.Type) -> bool:
        return isinstance(rty, rfl.Union) and rty == self.rty

    def fn(self, ctx: MarshalContext, rty: rfl.Type) -> Marshaler:
        return make_polymorphism_marshaler(self.impls, self.tt, ctx)


@dc.dataclass(frozen=True)
class PolymorphismUnionUnmarshalerFactory(UnmarshalerFactory):
    impls: Impls
    tt: TypeTagging = WrapperTypeTagging()

    @cached.property
    @dc.init
    def rty(self) -> rfl.Union:
        return rfl.type_(ta.Union[*tuple(i.ty for i in self.impls)])  # type: ignore

    def guard(self, ctx: UnmarshalContext, rty: rfl.Type) -> bool:
        return isinstance(rty, rfl.Union) and rty == self.rty

    def fn(self, ctx: UnmarshalContext, rty: rfl.Type) -> Unmarshaler:
        return make_polymorphism_unmarshaler(self.impls, self.tt, ctx)
