import typing as ta

from ... import dataclasses as dc
from ... import lang
from ... import marshal as msh
from .base import Node
from .binary import BinaryOp
from .binary import BinaryOps
from .exprs import Expr
from .relations import Relation
from .stmts import Stmt
from .unary import UnaryOp
from .unary import UnaryOps


@dc.dataclass(frozen=True)
class OpMarshaler(msh.Marshaler):
    ty: type
    ns: type

    def marshal(self, ctx: msh.MarshalContext, o: ta.Any) -> msh.Value:
        raise NotImplementedError


@dc.dataclass(frozen=True)
class OpUnmarshaler(msh.Unmarshaler):
    ty: type
    ns: type

    def unmarshal(self, ctx: msh.UnmarshalContext, v: msh.Value) -> ta.Any:
        raise NotImplementedError


@lang.static_init
def _install_standard_marshalling() -> None:
    for ty, ns in [
        (BinaryOp, BinaryOps),
        (UnaryOp, UnaryOps),
    ]:
        msh.STANDARD_MARSHALER_FACTORIES[0:0] = [msh.TypeMapMarshalerFactory({ty: OpMarshaler(ty, ns)})]
        msh.STANDARD_UNMARSHALER_FACTORIES[0:0] = [msh.TypeMapUnmarshalerFactory({ty: OpUnmarshaler(ty, ns)})]

    for cls in [
        Expr,
        Node,
        Relation,
        Stmt,
    ]:
        p = msh.polymorphism_from_subclasses(cls, naming=msh.Naming.SNAKE)
        msh.STANDARD_MARSHALER_FACTORIES[0:0] = [msh.PolymorphismMarshalerFactory(p)]
        msh.STANDARD_UNMARSHALER_FACTORIES[0:0] = [msh.PolymorphismUnmarshalerFactory(p)]
