from .base import Builder
from .binary import BinaryBuilder
from .deletes import DeleteBuilder
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
from .updates import UpdateBuilder


##


class StdBuilder(
    DeleteBuilder,
    InsertBuilder,
    SelectBuilder,
    StmtBuilder,
    UnionBuilder,
    UpdateBuilder,

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
