import typing as ta

from .... import check
from .... import collections as col
from .... import dataclasses as dc
from .... import lang
from .... import reflect as rfl
from ...api.contexts import MarshalContext
from ...api.contexts import MarshalFactoryContext
from ...api.contexts import UnmarshalContext
from ...api.contexts import UnmarshalFactoryContext
from ...api.types import Marshaler
from ...api.types import MarshalerFactory
from ...api.types import Unmarshaler
from ...api.types import UnmarshalerFactory
from ...api.values import Value


##


LITERAL_UNION_TYPES: tuple[type, ...] = (
    int,
    str,
)


class DestructuredLiteralUnionType(ta.NamedTuple):
    v_ty: type
    lit: rfl.Literal
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
    if v_ty in rty.args or v_ty not in LITERAL_UNION_TYPES:
        return None
    return DestructuredLiteralUnionType(v_ty, lit, check.single(non_lits))


#


@dc.dataclass(frozen=True)
class LiteralUnionMarshaler(Marshaler):
    v_ty: type
    l: Marshaler
    x: Marshaler

    def marshal(self, ctx: MarshalContext, o: ta.Any | None) -> Value:
        if isinstance(o, self.v_ty):
            return self.l.marshal(ctx, o)
        else:
            return self.x.marshal(ctx, o)


class LiteralUnionMarshalerFactory(MarshalerFactory):
    def make_marshaler(self, ctx: MarshalFactoryContext, rty: rfl.Type) -> ta.Callable[[], Marshaler] | None:
        if (ds := _destructure_literal_union_type(rty)) is None:
            return None
        return lambda: LiteralUnionMarshaler(ds.v_ty, ctx.make_marshaler(ds.lit), ctx.make_marshaler(ds.non_lit))


#


@dc.dataclass(frozen=True)
class LiteralUnionUnmarshaler(Unmarshaler):
    v_ty: type
    l: Unmarshaler
    x: Unmarshaler

    def unmarshal(self, ctx: UnmarshalContext, v: Value) -> ta.Any | None:
        if isinstance(v, self.v_ty):
            return self.l.unmarshal(ctx, v)  # type: ignore[arg-type]
        else:
            return self.x.unmarshal(ctx, v)


class LiteralUnionUnmarshalerFactory(UnmarshalerFactory):
    def make_unmarshaler(self, ctx: UnmarshalFactoryContext, rty: rfl.Type) -> ta.Callable[[], Unmarshaler] | None:
        if (ds := _destructure_literal_union_type(rty)) is None:
            return None
        return lambda: LiteralUnionUnmarshaler(ds.v_ty, ctx.make_unmarshaler(ds.lit), ctx.make_unmarshaler(ds.non_lit))
