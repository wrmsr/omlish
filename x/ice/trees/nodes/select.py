import enum
import operator
import typing as ta

from omnibus import collections as col
from omnibus import dataclasses as dc
from omnibus.serde import mapping as sm

from ...utils import build_enum_value_map
from .base import Expr
from .base import Identifier
from .base import Integer
from .base import Node
from .base import QualifiedNameNode
from .base import SetQuantifier
from .base import SortItem
from .base import Stmt
from .func import FunctionCall


class Relation(Node, abstract=True):
    pass


class Selectable(Node, abstract=True):
    pass


class InSelect(Expr):
    needle: Expr
    haystack: Selectable
    not_: bool = False


class JoinType(enum.Enum):
    DEFAULT = ''
    INNER = 'inner'
    LEFT = 'left'
    LEFT_OUTER = 'left outer'
    RIGHT = 'right'
    RIGHT_OUTER = 'right outer'
    FULL = 'full'
    FULL_OUTER = 'full outer'
    CROSS = 'cross'
    NATURAL = 'natural'


JOIN_TYPE_MAP: ta.Mapping[str, JoinType] = build_enum_value_map(JoinType)


class Join(Relation):
    left: Relation
    type: JoinType
    right: Relation
    condition: ta.Optional[Expr] = None
    using: ta.Optional[ta.Sequence[Identifier]] = dc.field(None, coerce=col.seq_or_none)


class Pivot(Relation):
    relation: Relation
    func: QualifiedNameNode
    pivot_col: Identifier
    value_col: Identifier
    values: ta.Sequence[Expr] = dc.field(coerce=col.seq)


class Unpivot(Relation):
    relation: Relation
    value_col: Identifier
    name_col: Identifier
    pivot_cols: ta.Sequence[Identifier] = dc.field(coerce=col.seq)


class Lateral(Relation):
    relation: Relation


class FunctionCallRelation(Relation):
    call: FunctionCall


class Table(Relation):
    name: QualifiedNameNode


class AliasedRelation(Relation):
    relation: Relation = dc.field(check=lambda r: not isinstance(r, AliasedRelation))
    alias: Identifier
    columns: ta.Sequence[Identifier] = dc.field((), coerce=col.seq)


class SelectItem(Node, abstract=True):
    pass


class AllSelectItem(SelectItem):
    pass


class IdentifierAllSelectItem(SelectItem):
    identifier: Identifier


class ExprSelectItem(SelectItem):
    value: Expr
    label: ta.Optional[Identifier] = dc.field(None, metadata={sm.Ignore: operator.not_})


class Grouping(Node, abstract=True):
    pass


class FlatGrouping(Grouping):
    items: ta.Sequence[Expr] = dc.field(coerce=col.seq)


class GroupingSet(Node):
    items: ta.Sequence[Expr] = dc.field(coerce=col.seq)


class SetsGrouping(Grouping):
    sets: ta.Sequence[GroupingSet] = dc.field(coerce=col.seq)


class Select(Selectable, Stmt):
    items: ta.Sequence[SelectItem] = dc.field(coerce=col.seq)
    relations: ta.Sequence[Relation] = dc.field((), coerce=col.seq, metadata={sm.Ignore: operator.not_})
    where: ta.Optional[Expr] = dc.field(None, metadata={sm.Ignore: operator.not_})
    top_n: ta.Optional[Integer] = dc.field(None, metadata={sm.Ignore: operator.not_})
    set_quantifier: ta.Optional[SetQuantifier] = dc.field(None, metadata={sm.Ignore: operator.not_})
    group_by: ta.Optional[Grouping] = dc.field(None, metadata={sm.Ignore: operator.not_})
    having: ta.Optional[Expr] = dc.field(None, metadata={sm.Ignore: operator.not_})
    qualify: ta.Optional[Expr] = dc.field(None, metadata={sm.Ignore: operator.not_})
    order_by: ta.Optional[ta.Sequence[SortItem]] = dc.field(None, coerce=col.seq_or_none, metadata={sm.Ignore: operator.not_})  # noqa
    limit: ta.Optional[int] = dc.field(None, metadata={sm.Ignore: operator.not_})


class Cte(Node):
    name: Identifier
    select: Selectable


class CteSelect(Selectable):
    ctes: ta.Sequence[Cte] = dc.field(coerce=col.seq)
    select: Selectable


class SetSelectKind(enum.Enum):
    INTERSECT = 'intersect'
    MINUS = 'minus'
    EXCEPT = 'except'
    UNION = 'union'
    UNION_ALL = 'union all'


SET_SELECT_KIND_MAP: ta.Mapping[str, SetSelectKind] = build_enum_value_map(SetSelectKind)


class SetSelectItem(Node):
    kind: SetSelectKind
    right: Selectable
    set_quantifier: ta.Optional[SetQuantifier] = None


class SetSelect(Selectable):
    left: Selectable
    items: ta.Sequence[SetSelectItem] = dc.field(coerce=col.seq)


class SelectExpr(Expr):
    select: Selectable


class SelectRelation(Relation):
    select: Selectable
