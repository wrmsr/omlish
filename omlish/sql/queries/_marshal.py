"""
FIXME:
 - refuse to marshal anon params
"""
import enum
import typing as ta

from ... import cached
from ... import check
from ... import collections as col
from ... import dataclasses as dc
from ... import lang
from ... import marshal as msh
from .base import Node
from .binary import BinaryOp
from .binary import BinaryOps
from .multi import MultiKind
from .relations import JoinKind
from .unary import UnaryOp
from .unary import UnaryOps


##


@dc.dataclass(frozen=True)
class OpMarshalerUnmarshaler(msh.Marshaler, msh.Unmarshaler):
    ty: type
    ns: type[lang.Namespace]

    @cached.property
    @dc.init
    def by_name(self) -> ta.Mapping[str, ta.Any]:
        return col.make_map(((o.name, o) for _, o in self.ns), strict=True)

    def marshal(self, ctx: msh.MarshalContext, o: ta.Any) -> msh.Value:
        return check.isinstance(o, self.ty).name

    def unmarshal(self, ctx: msh.UnmarshalContext, v: msh.Value) -> ta.Any:
        return self.by_name[check.isinstance(v, str)]


@dc.dataclass(frozen=True)
class LowerEnumMarshaler(msh.Marshaler, msh.Unmarshaler):
    ty: type[enum.Enum]

    @cached.property
    @dc.init
    def by_name(self) -> ta.Mapping[str, ta.Any]:
        return col.make_map(((o.name.lower(), o) for o in self.ty), strict=True)

    def marshal(self, ctx: msh.MarshalContext, o: ta.Any) -> msh.Value:
        return o.name.lower()

    def unmarshal(self, ctx: msh.UnmarshalContext, v: msh.Value) -> ta.Any:
        return self.by_name[check.isinstance(v, str).lower()]


@lang.static_init
def _install_standard_marshaling() -> None:
    for ty, ns in [
        (BinaryOp, BinaryOps),
        (UnaryOp, UnaryOps),
    ]:
        msh.install_standard_factories(
            msh.TypeMapMarshalerFactory({ty: OpMarshalerUnmarshaler(ty, ns)}),
            msh.TypeMapUnmarshalerFactory({ty: OpMarshalerUnmarshaler(ty, ns)}),
        )

    ets = [
        JoinKind,
        MultiKind,
    ]
    msh.install_standard_factories(
        msh.TypeMapMarshalerFactory({t: LowerEnumMarshaler(t) for t in ets}),
        msh.TypeMapUnmarshalerFactory({t: LowerEnumMarshaler(t) for t in ets}),
    )

    np = msh.polymorphism_from_subclasses(
        Node,
        naming=msh.Naming.SNAKE,
        strip_suffix=msh.AutoStripSuffix,
    )
    msh.install_standard_factories(
        msh.PolymorphismMarshalerFactory(np),
        msh.PolymorphismUnmarshalerFactory(np),
        msh.PolymorphismUnionMarshalerFactory(np.impls, allow_partial=True),
        msh.PolymorphismUnionUnmarshalerFactory(np.impls, allow_partial=True),
    )
