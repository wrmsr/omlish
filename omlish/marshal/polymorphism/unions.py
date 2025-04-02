import typing as ta

from ... import cached
from ... import check
from ... import dataclasses as dc
from ... import lang
from ... import reflect as rfl
from ...funcs import match as mfs
from ..base import MarshalContext
from ..base import Marshaler
from ..base import SimpleMarshalerFactory
from ..base import SimpleUnmarshalerFactory
from ..base import UnmarshalContext
from ..base import Unmarshaler
from ..values import Value
from .marshal import make_polymorphism_marshaler
from .metadata import Impls
from .metadata import TypeTagging
from .metadata import WrapperTypeTagging
from .unmarshal import make_polymorphism_unmarshaler


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
class PrimitiveUnionMarshalerFactory(SimpleMarshalerFactory):
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
class PrimitiveUnionUnmarshalerFactory(SimpleUnmarshalerFactory):
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
class _BasePolymorphismUnionFactory(lang.Abstract):
    impls: Impls
    tt: TypeTagging = WrapperTypeTagging()
    allow_partial: bool = dc.field(default=False, kw_only=True)

    @cached.property
    @dc.init
    def rtys(self) -> frozenset[rfl.Type]:
        return frozenset(i.ty for i in self.impls)

    def guard(self, ctx: MarshalContext | UnmarshalContext, rty: rfl.Type) -> bool:
        if not isinstance(rty, rfl.Union):
            return False
        if self.allow_partial:
            return not (rty.args - self.rtys)
        else:
            return rty.args == self.rtys

    def get_impls(self, rty: rfl.Type) -> Impls:
        uty = check.isinstance(rty, rfl.Union)
        return Impls([self.impls.by_ty[check.isinstance(a, type)] for a in uty.args])


@dc.dataclass(frozen=True)
class PolymorphismUnionMarshalerFactory(_BasePolymorphismUnionFactory, SimpleMarshalerFactory):
    def fn(self, ctx: MarshalContext, rty: rfl.Type) -> Marshaler:
        return make_polymorphism_marshaler(self.get_impls(rty), self.tt, ctx)


@dc.dataclass(frozen=True)
class PolymorphismUnionUnmarshalerFactory(_BasePolymorphismUnionFactory, SimpleUnmarshalerFactory):
    def fn(self, ctx: UnmarshalContext, rty: rfl.Type) -> Unmarshaler:
        return make_polymorphism_unmarshaler(self.get_impls(rty), self.tt, ctx)
