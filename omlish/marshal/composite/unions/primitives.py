import typing as ta

from .... import check
from .... import collections as col
from .... import dataclasses as dc
from .... import reflect as rfl
from ...base.contexts import MarshalContext
from ...base.contexts import MarshalFactoryContext
from ...base.contexts import UnmarshalContext
from ...base.contexts import UnmarshalFactoryContext
from ...base.types import Marshaler
from ...base.types import MarshalerFactory
from ...base.types import Unmarshaler
from ...base.types import UnmarshalerFactory
from ...base.values import Value


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
class PrimitiveUnionMarshalerFactory(MarshalerFactory):
    tys: ta.Sequence[type] = PRIMITIVE_UNION_TYPES

    def make_marshaler(self, ctx: MarshalFactoryContext, rty: rfl.Type) -> ta.Callable[[], Marshaler] | None:
        if (ds := _destructure_primitive_union_type(rty, self.tys)) is None:
            return None
        return lambda: PrimitiveUnionMarshaler(
            ds.prim,
            ctx.make_marshaler(check.single(ds.non_prim)) if ds.non_prim else None,
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
class PrimitiveUnionUnmarshalerFactory(UnmarshalerFactory):
    tys: ta.Sequence[type] = PRIMITIVE_UNION_TYPES

    def make_unmarshaler(self, ctx: UnmarshalFactoryContext, rty: rfl.Type) -> ta.Callable[[], Unmarshaler] | None:
        if (ds := _destructure_primitive_union_type(rty, self.tys)) is None:
            return None
        return lambda: PrimitiveUnionUnmarshaler(
            ds.prim,
            ctx.make_unmarshaler(check.single(ds.non_prim)) if ds.non_prim else None,
        )
