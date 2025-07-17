from .base import Builder
from .binary import BinaryBuilder
from .exprs import ExprBuilder
from .idents import IdentBuilder
from .inserts import InsertBuilder
from .multi import MultiBuilder
from .names import NameBuilder
from .params import ParamBuilder
from .relations import RelationBuilder
from .selects import SelectBuilder
from .stmts import StmtBuilder
from .unary import UnaryBuilder
from .unions import UnionBuilder


##


class StdBuilder(
    InsertBuilder,
    SelectBuilder,
    StmtBuilder,
    UnionBuilder,

    RelationBuilder,

    MultiBuilder,
    BinaryBuilder,
    UnaryBuilder,
    ExprBuilder,

    ParamBuilder,

    NameBuilder,
    IdentBuilder,

    Builder,
):
    pass
