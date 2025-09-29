import typing as ta

from ... import cached
from ... import check
from ... import collections as col
from ... import dataclasses as dc
from ... import lang
from ... import reflect as rfl
from ...funcs import match as mfs
from ..base.contexts import MarshalContext
from ..base.contexts import UnmarshalContext
from ..base.types import Marshaler
from ..base.types import Unmarshaler
from ..base.values import Value
from ..factories.simple import SimpleMarshalerFactory
from ..factories.simple import SimpleUnmarshalerFactory
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
    bool,
)


class DestructuredPrimitiveUnionType(ta.NamedTuple):
    prim: ta.Sequence[type]
    non_prim: ta.Sequence[rfl.Type]


def _destructure_primitive_union_type(
        rty: rfl.Type,
        prim_tys: ta.Container[type] = PRIMITIVE_UNION_TYPES,
) -> DestructuredPrimitiveUnionType | None:
    if not isinstance(rty, rfl.Union):
        return None

    pr = col.partition(rty.args, lambda a: isinstance(a, type) and a in prim_tys)
    if not pr.t or len(pr.f) > 1:
        return None

    return DestructuredPrimitiveUnionType(*pr)  # type: ignore[arg-type]


#


@dc.dataclass(frozen=True)
class PrimitiveUnionMarshaler(Marshaler):
    tys: ta.Sequence[type]
    x: Marshaler | None = None

    def marshal(self, ctx: MarshalContext, o: ta.Any) -> Value:
        if type(o) not in self.tys:
            if self.x is not None:
                return self.x.marshal(ctx, o)
            raise TypeError(o)
        return o


@dc.dataclass(frozen=True)
class PrimitiveUnionMarshalerFactory(SimpleMarshalerFactory):
    tys: ta.Sequence[type] = PRIMITIVE_UNION_TYPES

    def guard(self, ctx: MarshalContext, rty: rfl.Type) -> bool:
        return _destructure_primitive_union_type(rty, self.tys) is not None

    def fn(self, ctx: MarshalContext, rty: rfl.Type) -> Marshaler:
        prim, non_prim = check.not_none(_destructure_primitive_union_type(rty, self.tys))
        return PrimitiveUnionMarshaler(
            prim,
            ctx.make(check.single(non_prim)) if non_prim else None,
        )


#


@dc.dataclass(frozen=True)
class PrimitiveUnionUnmarshaler(Unmarshaler):
    tys: ta.Sequence[type]
    x: Unmarshaler | None = None

    def unmarshal(self, ctx: UnmarshalContext, v: Value) -> ta.Any:
        if type(v) not in self.tys:
            if self.x is not None:
                return self.x.unmarshal(ctx, v)
            raise TypeError(v)
        return v


@dc.dataclass(frozen=True)
class PrimitiveUnionUnmarshalerFactory(SimpleUnmarshalerFactory):
    tys: ta.Sequence[type] = PRIMITIVE_UNION_TYPES

    def guard(self, ctx: UnmarshalContext, rty: rfl.Type) -> bool:
        return _destructure_primitive_union_type(rty, self.tys) is not None

    def fn(self, ctx: UnmarshalContext, rty: rfl.Type) -> Unmarshaler:
        prim, non_prim = check.not_none(_destructure_primitive_union_type(rty, self.tys))
        return PrimitiveUnionUnmarshaler(
            prim,
            ctx.make(check.single(non_prim)) if non_prim else None,
        )


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
