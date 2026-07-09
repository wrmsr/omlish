import typing as ta

from ... import check
from ... import dataclasses as dc
from ... import reflect as rfl
from ..api.contexts import MarshalContext
from ..api.contexts import MarshalFactoryContext
from ..api.contexts import UnmarshalContext
from ..api.contexts import UnmarshalFactoryContext
from ..api.types import Marshaler
from ..api.types import MarshalerFactory
from ..api.types import Unmarshaler
from ..api.types import UnmarshalerFactory
from ..api.values import Value


##


def get_literal_types(rty: rfl.Type) -> ta.Sequence[rfl.LiteralType] | None:
    """
    The literal members of a reflected literal type - a single LiteralType or a union of nothing but LiteralTypes
    (`Literal['a', 'b']` reflects as the latter). Enum-backed literals are excluded - their reflected values are member
    *names*, not the runtime literal values these marshalers traffic in.
    """

    lits: ta.Sequence[rfl.Type]
    if isinstance(rty, rfl.LiteralType):
        lits = [rty]
    elif isinstance(rty, rfl.UnionType) and all(isinstance(it, rfl.LiteralType) for it in rty.items):
        lits = rty.items
    else:
        return None

    ret: list[rfl.LiteralType] = []
    for lit in lits:
        lit = check.isinstance(lit, rfl.LiteralType)
        if lit.fallback.type.is_enum:
            return None
        ret.append(lit)
    return ret


def _single_literal_value_type(lits: ta.Sequence[rfl.LiteralType]) -> type | None:
    v_tys = {type(lit.value) for lit in lits}
    if len(v_tys) != 1:
        return None
    return check.single(v_tys)


##


@dc.dataclass(frozen=True)
class LiteralMarshaler(Marshaler):
    e: Marshaler
    vs: frozenset

    def marshal(self, ctx: MarshalContext, o: ta.Any | None) -> Value:
        return self.e.marshal(ctx, check.in_(o, self.vs))


class LiteralMarshalerFactory(MarshalerFactory):
    def make_marshaler(self, ctx: MarshalFactoryContext, rty: rfl.Type) -> ta.Callable[[], Marshaler] | None:
        if (lits := get_literal_types(rty)) is None or (ety := _single_literal_value_type(lits)) is None:
            return None
        return lambda: LiteralMarshaler(ctx.make_marshaler(ety), frozenset(lit.value for lit in lits))


@dc.dataclass(frozen=True)
class LiteralUnmarshaler(Unmarshaler):
    e: Unmarshaler
    vs: frozenset

    def unmarshal(self, ctx: UnmarshalContext, v: Value) -> ta.Any | None:
        return check.in_(self.e.unmarshal(ctx, v), self.vs)


class LiteralUnmarshalerFactory(UnmarshalerFactory):
    def make_unmarshaler(self, ctx: UnmarshalFactoryContext, rty: rfl.Type) -> ta.Callable[[], Unmarshaler] | None:
        if (lits := get_literal_types(rty)) is None or (ety := _single_literal_value_type(lits)) is None:
            return None
        return lambda: LiteralUnmarshaler(ctx.make_unmarshaler(ety), frozenset(lit.value for lit in lits))
