"""
TODO:
 - only quote when necessary (for extract)
 - pretty output - no duplication in a pprint.py
  - include comments (reqs carrying antlr into nodes)
 - custom open/close on paren?
 - ** comments **
  - placement - linearize parts
   - ** preserve hot comments ** but can move others
"""
import collections.abc
import io
import typing as ta

from omnibus import check
from omnibus import dataclasses as dc
from omnibus import dispatch

from . import nodes as no
from .quoting import quote
from .types import AstQuery
from .types import Query
from .types import StrQuery


T = ta.TypeVar('T')
NoneType = type(None)


Part = ta.Union[str, ta.Sequence['Part'], 'DataPart']


class DataPart(dc.Enum):
    pass


class Paren(DataPart):
    part: Part


class List(DataPart):
    parts: ta.Sequence[ta.Optional[Part]]
    delimiter: str = ','


class Concat(DataPart):
    parts: ta.Sequence[Part]


class Node(DataPart):
    node: no.Node


NEEDS_PAREN_TYPES: ta.AbstractSet[ta.Type[no.Node]] = {
    no.BinaryExpr,
    no.IsNull,
    no.SelectExpr,
}


def needs_paren(node: no.Node) -> bool:
    return type(node) in NEEDS_PAREN_TYPES


class Renderer(dispatch.Class):
    render = dispatch.property()

    def __call__(self, node: ta.Optional[no.Node]) -> Part:
        if node is None:
            return []
        return [Node(node), self.render(node)]

    def render(self, node: no.Node) -> Part:  # noqa
        raise TypeError(node)

    def paren(self, node: no.Node) -> Part:  # noqa
        return Paren(self(node)) if needs_paren(node) else self(node)

    def render(self, node: no.AliasedRelation) -> Part:  # noqa
        return [
            self.paren(node.relation),
            ['as', self(node.alias)] if node.alias is not None else [],
            Paren(List([self(i) for i in node.columns])) if node.columns else [],
        ]

    def render(self, node: no.AllSelectItem) -> Part:  # noqa
        return '*'

    def render(self, node: no.Between) -> Part:  # noqa
        return [
            self(node.value),
            'between',
            self(node.lower),
            'and',
            self(node.upper),
        ]

    def render(self, node: no.BinaryExpr) -> Part:  # noqa
        return [
            self.paren(node.left),
            node.op.value,
            self.paren(node.right),
        ]

    def render(self, node: no.Case) -> Part:  # noqa
        return [
            'case',
            self(node.value),
            [self(i) for i in node.items] if node.items else [],
            ['else', self(node.default)] if node.default is not None else [],
            'end',
        ]

    def render(self, node: no.CaseItem) -> Part:  # noqa
        return ['when', self(node.when), 'then', self(node.then)]

    def render(self, node: no.Cast) -> Part:  # noqa
        return Paren(Concat([self(node.value), '::', self(node.type)]))

    def render(self, node: no.CastCall) -> Part:  # noqa
        return Concat(['cast', Paren([self(node.value), 'as', self(node.type)])])

    def render(self, node: no.ColSpec) -> Part:  # noqa
        return [self(node.name), self(node.type)]

    def render(self, node: no.CreateTable) -> Part:  # noqa
        return [
            'create',
            'table',
            self(node.name),
            Paren(List([self(c) for c in node.cols])) if node.cols else [],
            ['as', self(node.select)] if node.select is not None else [],
        ]

    def render(self, node: no.Cte) -> Part:  # noqa
        return [self(node.name), 'as', Paren(self(node.select))]

    def render(self, node: no.CteSelect) -> Part:  # noqa
        return ['with', List([self(c) for c in node.ctes]), self(node.select)]

    def render(self, node: no.CurrentRowFrameBound) -> Part:  # noqa
        return ['current', 'row']

    def render(self, node: no.Date) -> Part:  # noqa
        return ['date', self(node.value)]

    def render(self, node: no.Decimal) -> Part:  # noqa
        return node.value

    def render(self, node: no.Delete) -> Part:  # noqa
        return [
            'delete',
            'from',
            self(node.name),
            ['where', self(node.where)] if node.where is not None else [],
        ]

    def render(self, node: no.DoubleFrame) -> Part:  # noqa
        return [
            node.rows_or_range.value,
            'between',
            self(node.min),
            'and',
            self(node.max),
        ]

    def render(self, node: no.EFalse) -> Part:  # noqa
        return 'false'

    def render(self, node: no.ETrue) -> Part:  # noqa
        return 'true'

    def render(self, node: no.ExprSelectItem) -> Part:  # noqa
        return [
            self.paren(node.value),
            ['as', self(node.label)] if node.label is not None else [],
        ]

    def render(self, node: no.Extract) -> Part:  # noqa
        return Concat(['extract', Paren([self(node.part), 'from', self(node.value)])])

    def render(self, node: no.FlatGrouping) -> Part:  # noqa
        return List([self(i) for i in node.items])

    def render(self, node: no.Float) -> Part:  # noqa
        return node.value

    def render(self, node: no.FunctionCall) -> Part:  # noqa
        return [
            Concat([
                self(node.name),
                Paren([
                    node.set_quantifier.value if node.set_quantifier is not None else [],
                    List([self.paren(a) for a in [*node.args, *node.kwargs]]),
                ]),
            ]),
            [node.nulls.value, 'nulls'] if node.nulls is not None else [],
            [
                'within', 'group', Paren([
                    'order', 'by',
                    List([self(g) for g in node.within_group])
                ])
            ] if node.within_group else [],
            ['over', Paren([self(node.over)])] if node.over is not None else [],
        ]

    def render(self, node: no.FunctionCallExpr) -> Part:  # noqa
        return self(node.call)

    def render(self, node: no.FunctionCallRelation) -> Part:  # noqa
        return self(node.call)

    def render(self, node: no.GroupingSet) -> Part:  # noqa
        return Paren(List([self(i) for i in node.items]))

    def render(self, node: no.Identifier) -> Part:  # noqa
        return quote(node.name, '"')

    def render(self, node: no.IdentifierAllSelectItem) -> Part:  # noqa
        return Concat([self(node.identifier), '.*'])

    def render(self, node: no.InJinja) -> Part:  # noqa
        return [
            self(node.needle),
            'not' if node.not_ else [], 'in',
            '{{', node.text, '}}',
        ]

    def render(self, node: no.InList) -> Part:  # noqa
        return [
            self(node.needle),
            'not' if node.not_ else [], 'in',
            Paren(List([self.paren(e) for e in node.haystack])),
        ]

    def render(self, node: no.InSelect) -> Part:  # noqa
        return [
            self(node.needle),
            'not' if node.not_ else [], 'in',
            Paren(self(node.haystack)),
        ]

    def render(self, node: no.Insert) -> Part:  # noqa
        return ['insert', 'into', self(node.name), self(node.select) if node.select is not None else []]

    def render(self, node: no.Integer) -> Part:  # noqa
        return str(node.value)

    def render(self, node: no.Interval) -> Part:  # noqa
        return ['interval', self(node.value), node.unit.value if node.unit is not None else []]

    def render(self, node: no.IsNull) -> Part:  # noqa
        return [self(node.value), 'is', 'not' if node.not_ else [], 'null']

    def render(self, node: no.JinjaExpr) -> Part:  # noqa
        return ['{{', node.text, '}}']

    def render(self, node: no.JinjaRelation) -> Part:  # noqa
        return ['{{', node.text, '}}']

    def render(self, node: no.Join) -> Part:  # noqa
        return [
            self(node.left),
            node.type.value if node.type != no.JoinType.DEFAULT else [],
            'join',
            self(node.right),
            List([
                ['on', self(node.condition)] if node.condition is not None else [],
                ['using', Paren(List([self(i) for i in node.using]))] if node.using is not None else [],
            ])
        ]

    def render(self, node: no.Kwarg) -> Part:  # noqa
        return [self(node.name), '=>', self(node.value)]

    def render(self, node: no.Lateral) -> Part:  # noqa
        return ['lateral', self(node.relation)]

    def render(self, node: no.Like) -> Part:  # noqa
        return [
            self(node.value),
            'not' if node.not_ else [],
            node.kind.value,
            ['any', Paren(List([self(p) for p in node.patterns]))]
            if len(node.patterns) != 1 else self(next(iter(node.patterns))),
            ['escape', self(node.escape)] if node.escape is not None else [],
        ]

    def render(self, node: no.Null) -> Part:  # noqa
        return 'null'

    def render(self, node: no.NumFrameBound) -> Part:  # noqa
        return [str(node.num), node.precedence.value]

    def render(self, node: no.Over) -> Part:  # noqa
        return [
            ['partition', 'by', List([self(e) for e in node.partition_by])] if node.partition_by else [],
            ['order', 'by', List([self(e) for e in node.order_by])] if node.order_by else [],
            self(node.frame),
        ]

    def render(self, node: no.Param) -> Part:  # noqa
        return ':' + node.name

    def render(self, node: no.Pivot) -> Part:  # noqa
        return [
            self(node.relation),
            Concat(['pivot', Paren([
                self(node.func),
                Paren(self(node.pivot_col)),
                'for',
                self(node.value_col),
                'in',
                Paren(List([self(e) for e in node.values])),
            ])]),
        ]

    def render(self, node: no.QualifiedNameNode) -> Part:  # noqa
        return Concat([Concat(['.' if i else [], self(p)]) for i, p in enumerate(node.parts)])

    def render(self, node: no.Select) -> Part:  # noqa
        return [
            'select',
            ['top', self(node.top_n)] if node.top_n is not None else [],
            node.set_quantifier.value if node.set_quantifier is not None else [],
            List([self(i) for i in node.items]),
            ['from', List([self.paren(r) for r in node.relations])] if node.relations else [],
            ['where', self(node.where)] if node.where is not None else [],
            ['group', 'by', self(node.group_by)] if node.group_by is not None else [],
            ['having', self(node.having)] if node.having is not None else [],
            ['qualify', self(node.qualify)] if node.qualify is not None else [],
            ['order', 'by', List([self(e) for e in node.order_by])] if node.order_by else [],
            ['limit', str(node.limit)] if node.limit is not None else [],
        ]

    def render(self, node: no.SelectExpr) -> Part:  # noqa
        return self(node.select)

    def render(self, node: no.SelectRelation) -> Part:  # noqa
        return Paren(self(node.select))

    def render(self, node: no.SetsGrouping) -> Part:  # noqa
        return ['grouping', 'sets', Paren(List([self(i) for i in node.sets]))]

    def render(self, node: no.SetSelect) -> Part:  # noqa
        return [
            self(node.left),
            [self(i) for i in node.items] if node.items else [],
        ]

    def render(self, node: no.SetSelectItem) -> Part:  # noqa
        return [
            node.kind.value,
            node.set_quantifier.value if node.set_quantifier is not None else [],
            self(node.right),
        ]

    def render(self, node: no.SingleFrame) -> Part:  # noqa
        return [node.rows_or_range.value, self(node.bound)]

    def render(self, node: no.SortItem) -> Part:  # noqa
        return [
            self(node.value),
            node.direction.value if node.direction is not None else [],
            ['nulls', node.nulls.value] if node.nulls is not None else [],
        ]

    def render(self, node: no.StarExpr) -> Part:  # noqa
        return '*'

    def render(self, node: no.String) -> Part:  # noqa
        return quote(node.value, "'")

    def render(self, node: no.Table) -> Part:  # noqa
        return self(node.name)

    def render(self, node: no.Traversal) -> Part:  # noqa
        return Concat([
            self(node.value),
            ':',
            *[
                Concat(['[', r, ']']) if isinstance(k, no.Integer) else Concat(['.' if i else [], r])
                for i, k in enumerate(node.keys)
                for r in [self(k)]
            ],
        ])

    def render(self, node: no.TypeSpec) -> Part:  # noqa
        return [
            self(node.name),
            Paren(List([self(a) for a in node.args])) if node.args else [],
        ]

    def render(self, node: no.UnaryExpr) -> Part:  # noqa
        parts = [node.op.value, self.paren(node.value)]
        return Concat(parts) if node.op != no.UnaryOp.NOT else parts

    def render(self, node: no.UnboundedFrameBound) -> Part:  # noqa
        return ['unbounded', node.precedence.value]

    def render(self, node: no.Unpivot) -> Part:  # noqa
        return [
            self(node.relation),
            Concat(['unpivot', Paren([
                self(node.value_col),
                'for',
                self(node.name_col),
                'in',
                Paren(List([self(c) for c in node.pivot_cols])),
            ])]),
        ]

    def render(self, node: no.Var) -> Part:  # noqa
        return '$' + node.name


class PartTransform(dispatch.Class):
    __call__ = dispatch.property()

    def __call__(self, part: str) -> Part:  # noqa
        return part

    def __call__(self, part: collections.abc.Sequence) -> Part:  # noqa
        return [self(c) for c in part]

    def __call__(self, part: Paren) -> Part:  # noqa
        return Paren(self(part.part))

    def __call__(self, part: List) -> Part:  # noqa
        return List([self(c) for c in part.parts], part.delimiter)

    def __call__(self, part: Concat) -> Part:  # noqa
        return Concat([self(c) for c in part.parts])

    def __call__(self, part: Node) -> Part:  # noqa
        return part


class RemoveNodes(PartTransform):

    def __call__(self, part: Node) -> Part:  # noqa
        return []


remove_nodes = RemoveNodes()


def _drop_empties(it: ta.Iterable[T]) -> ta.List[T]:
    return [e for e in it if not (
        isinstance(e, collections.abc.Sequence) and
        not e and
        not isinstance(e, str)
    )]


class CompactPart(PartTransform):

    def __call__(self, part: collections.abc.Sequence) -> Part:  # noqa
        return _drop_empties(self(c) for c in part)

    def __call__(self, part: List) -> Part:  # noqa
        parts = _drop_empties(self(c) for c in part.parts)
        return List(parts, part.delimiter) if parts else []

    def __call__(self, part: Concat) -> Part:  # noqa
        parts = _drop_empties(self(c) for c in part.parts)
        return Concat(parts) if parts else []


compact_part = CompactPart()


def render_part(part: Part, buf: io.StringIO) -> None:
    if isinstance(part, str):
        buf.write(part)
    elif isinstance(part, collections.abc.Sequence):
        for i, c in enumerate(part):
            if i:
                buf.write(' ')
            render_part(c, buf)
    elif isinstance(part, Paren):
        buf.write('(')
        render_part(part.part, buf)
        buf.write(')')
    elif isinstance(part, List):
        for i, c in enumerate(part.parts):
            if i:
                buf.write(part.delimiter + ' ')
            render_part(c, buf)
    elif isinstance(part, Concat):
        for c in part.parts:
            render_part(c, buf)
    elif isinstance(part, Node):
        pass
    else:
        raise TypeError(part)


def render(node: no.Node) -> str:
    check.isinstance(node, no.Node)
    part = Renderer()(node)
    part = remove_nodes(part)
    part = compact_part(part)
    buf = io.StringIO()
    render_part(part, buf)
    return buf.getvalue()


def render_query(query: Query, **kwargs) -> str:
    if isinstance(query, AstQuery):
        return render(query.root, **kwargs)
    elif isinstance(query, StrQuery):
        return query.src
    else:
        raise TypeError(query)
