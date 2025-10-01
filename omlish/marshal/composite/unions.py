import typing as ta

from ... import check
from ... import lang
from ... import collections as col
from ... import dataclasses as dc
from ... import reflect as rfl
from ...funcs import match as mfs
from ..base.contexts import MarshalContext
from ..base.contexts import UnmarshalContext
from ..base.types import Marshaler
from ..base.types import Unmarshaler
from ..base.values import Value
from ..factories.simple import SimpleMarshalerFactory
from ..factories.simple import SimpleUnmarshalerFactory


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


##


class DestructuredLiteralUnionType(ta.NamedTuple):
    lit: rfl.Literal
    v_ty: type
    non_lit: rfl.Type


def _destructure_literal_union_type(rty: rfl.Type) -> DestructuredLiteralUnionType | None:
    if not isinstance(rty, rfl.Union):
        return None
    lits, non_lits = col.partition(rty.args, lang.isinstance_of(rfl.Literal))  # noqa
    if len(lits) != 1 or len(non_lits) != 1:
        return None
    lit = check.isinstance(check.single(lits), rfl.Literal)
    v_tys = set(map(type, lit.args))
    if len(v_tys) != 1:
        return None
    [v_ty] = v_tys
    if v_ty in rty.args:
        return None
    return DestructuredLiteralUnionType(lit, v_ty, check.single(non_lits))


#


@dc.dataclass(frozen=True)
class LiteralUnionMarshaler(Marshaler):
    vty: type
    e: Marshaler
    vs: frozenset
    x: Marshaler

    def marshal(self, ctx: MarshalContext, o: ta.Any | None) -> Value:
        return self.e.marshal(ctx, check.in_(o, self.vs))


class LiteralUnionMarshalerFactory(SimpleMarshalerFactory):
    def guard(self, ctx: MarshalContext, rty: rfl.Type) -> bool:
        return _destructure_literal_union_type(rty) is not None

    def fn(self, ctx: MarshalContext, rty: rfl.Type) -> Marshaler:
        # lty = check.isinstance(rty, rfl.Literal)
        # ety = check.single(set(map(type, lty.args)))
        # return LiteralMarshaler(ctx.make(ety), frozenset(lty.args))
        ds = check.not_none(_destructure_literal_union_type(rty))
        raise NotImplementedError


#


@dc.dataclass(frozen=True)
class LiteralUnionUnmarshaler(Unmarshaler):
    vty: type
    e: Unmarshaler
    vs: frozenset
    x: Unmarshaler

    def unmarshal(self, ctx: UnmarshalContext, v: Value) -> ta.Any | None:
        return check.in_(self.e.unmarshal(ctx, v), self.vs)


class LiteralUnionUnmarshalerFactory(SimpleUnmarshalerFactory):
    def guard(self, ctx: UnmarshalContext, rty: rfl.Type) -> bool:
        return _destructure_literal_union_type(rty) is not None

    def fn(self, ctx: UnmarshalContext, rty: rfl.Type) -> Unmarshaler:
        # lty = check.isinstance(rty, rfl.Literal)
        # ety = check.single(set(map(type, lty.args)))
        # return LiteralUnmarshaler(ctx.make(ety), frozenset(lty.args))
        ds = check.not_none(_destructure_literal_union_type(rty))
        raise NotImplementedError
