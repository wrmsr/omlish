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
from .exprs import Expr
from .multi import MultiKind
from .relations import Relation
from .stmts import Stmt
from .unary import UnaryOp
from .unary import UnaryOps


@dc.dataclass(frozen=True)
class OpMarshalerUnmarshaler(msh.Marshaler, msh.Unmarshaler):
    ty: type
    ns: type[lang.Namespace]

    @cached.property
    @dc.init
    def by_name(self) -> ta.Mapping[str, ta.Any]:
        return col.make_map(((o.name, o) for _, o in self.ns), strict=True)

    def marshal(self, ctx: msh.MarshalContext, o: ta.Any) -> msh.Value:
        return check.isinstance(o, self.ty).name  # type: ignore  # noqa

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
def _install_standard_marshalling() -> None:
    for ty, ns in [
        (BinaryOp, BinaryOps),
        (UnaryOp, UnaryOps),
    ]:
        msh.STANDARD_MARSHALER_FACTORIES[0:0] = [msh.TypeMapMarshalerFactory({ty: OpMarshalerUnmarshaler(ty, ns)})]
        msh.STANDARD_UNMARSHALER_FACTORIES[0:0] = [msh.TypeMapUnmarshalerFactory({ty: OpMarshalerUnmarshaler(ty, ns)})]

    msh.STANDARD_MARSHALER_FACTORIES[0:0] = [msh.TypeMapMarshalerFactory({MultiKind: LowerEnumMarshaler(MultiKind)})]
    msh.STANDARD_UNMARSHALER_FACTORIES[0:0] = [msh.TypeMapUnmarshalerFactory({MultiKind: LowerEnumMarshaler(MultiKind)})]  # noqa

    for cls in [
        Expr,
        Node,
        Relation,
        Stmt,
    ]:
        p = msh.polymorphism_from_subclasses(cls, naming=msh.Naming.SNAKE)
        msh.STANDARD_MARSHALER_FACTORIES[0:0] = [msh.PolymorphismMarshalerFactory(p)]
        msh.STANDARD_UNMARSHALER_FACTORIES[0:0] = [msh.PolymorphismUnmarshalerFactory(p)]
