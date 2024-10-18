from ... import lang
from ... import marshal as msh
from .base import Node
from .exprs import Expr
from .relations import Relation
from .stmts import Stmt


@lang.static_init
def _install_standard_marshalling() -> None:
    for cls in [
        Expr,
        Node,
        Relation,
        Stmt,
    ]:
        p = msh.polymorphism_from_subclasses(cls, naming=msh.Naming.SNAKE)
        msh.STANDARD_MARSHALER_FACTORIES[0:0] = [msh.PolymorphismMarshalerFactory(p)]
        msh.STANDARD_UNMARSHALER_FACTORIES[0:0] = [msh.PolymorphismUnmarshalerFactory(p)]
