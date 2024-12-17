import typing as ta

from omnibus import collections as col
from omnibus import dataclasses as dc

from .base import Expr
from .base import Identifier
from .base import Node
from .base import QualifiedNameNode
from .base import Stmt
from .base import TypeSpec
from .select import Select


class ColSpec(Node):
    name: Identifier
    type: TypeSpec


class CreateTable(Stmt):
    name: QualifiedNameNode
    cols: ta.Sequence[ColSpec] = dc.field(coerce=col.seq)
    select: ta.Optional[Select] = None


class Insert(Stmt):
    name: QualifiedNameNode
    select: ta.Optional[Select] = None


class Delete(Stmt):
    name: QualifiedNameNode
    where: ta.Optional[Expr] = None
