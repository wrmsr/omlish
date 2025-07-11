import abc
import dataclasses as dc
import typing as ta

from ... import lang


##


@dc.dataclass(frozen=True)
class Node(lang.Abstract):
    @property
    @abc.abstractmethod
    def children(self) -> ta.Sequence['Node']:
        raise NotImplementedError


@dc.dataclass(frozen=True)
class LeafNode(Node, lang.Abstract):
    @property
    def children(self) -> ta.Sequence[Node]:
        return []


##


UnaryArithmeticOperator: ta.TypeAlias = ta.Literal[
    'plus',
    'minus',
]


@dc.dataclass(frozen=True)
class ArithmeticUnary(Node, lang.Final):
    operator: UnaryArithmeticOperator
    expression: Node

    @property
    def children(self) -> ta.Sequence[Node]:
        return [self.expression]


ArithmeticOperator: ta.TypeAlias = ta.Literal[
    'div',
    'divide',
    'minus',
    'modulo',
    'multiply',
    'plus',
]


@dc.dataclass(frozen=True)
class Arithmetic(Node, lang.Final):
    operator: ArithmeticOperator
    left: Node
    right: Node

    @property
    def children(self) -> ta.Sequence[Node]:
        return [self.left, self.right]


@dc.dataclass(frozen=True)
class Assign(Node, lang.Final):
    name: str
    expr: Node

    @property
    def children(self) -> ta.Sequence[Node]:
        return [self.expr]


ComparatorName: ta.TypeAlias = ta.Literal[
    'eq',
    'ne',
    'lt',
    'gt',
    'lte',
    'gte',
]


@dc.dataclass(frozen=True)
class Comparator(Node, lang.Final):
    name: ComparatorName
    first: Node
    second: Node

    @property
    def children(self) -> ta.Sequence[Node]:
        return [self.first, self.second]


@dc.dataclass(frozen=True)
class CurrentNode(LeafNode, lang.Final):
    pass


@dc.dataclass(frozen=True)
class RootNode(LeafNode, lang.Final):
    pass


@dc.dataclass(frozen=True)
class Expref(Node, lang.Final):
    expression: Node

    @property
    def children(self) -> ta.Sequence[Node]:
        return [self.expression]


@dc.dataclass(frozen=True)
class FunctionExpression(Node, lang.Final):
    name: str
    args: ta.Sequence[Node]

    @property
    def children(self) -> ta.Sequence[Node]:
        return tuple(self.args)


@dc.dataclass(frozen=True)
class Field(LeafNode, lang.Final):
    name: str


@dc.dataclass(frozen=True)
class FilterProjection(Node, lang.Final):
    left: Node
    right: Node
    comparator: Node

    @property
    def children(self) -> ta.Sequence[Node]:
        return [self.left, self.right, self.comparator]


@dc.dataclass(frozen=True)
class Flatten(Node, lang.Final):
    node: Node

    @property
    def children(self) -> ta.Sequence[Node]:
        return [self.node]


@dc.dataclass(frozen=True)
class Identity(LeafNode, lang.Final):
    pass


@dc.dataclass(frozen=True)
class Index(LeafNode, lang.Final):
    index: int


@dc.dataclass(frozen=True)
class IndexExpression(Node, lang.Final):
    nodes: ta.Sequence[Node]

    @property
    def children(self) -> ta.Sequence[Node]:
        return tuple(self.nodes)


@dc.dataclass(frozen=True)
class KeyValPair(Node, lang.Final):
    key_name: str
    node: Node

    @property
    def children(self) -> ta.Sequence[Node]:
        return [self.node]


@dc.dataclass(frozen=True)
class LetExpression(Node, lang.Final):
    bindings: ta.Sequence[Node]
    expr: Node

    @property
    def children(self) -> ta.Sequence[Node]:
        return [*self.bindings, self.expr]


@dc.dataclass(frozen=True)
class Literal(LeafNode, lang.Final):
    literal_value: ta.Any


@dc.dataclass(frozen=True)
class MultiSelectDict(Node, lang.Final):
    nodes: ta.Sequence[KeyValPair]

    @property
    def children(self) -> ta.Sequence[Node]:
        return tuple(self.nodes)


@dc.dataclass(frozen=True)
class MultiSelectList(Node, lang.Final):
    nodes: ta.Sequence[Node]

    @property
    def children(self) -> ta.Sequence[Node]:
        return tuple(self.nodes)


@dc.dataclass(frozen=True)
class OrExpression(Node, lang.Final):
    left: Node
    right: Node

    @property
    def children(self) -> ta.Sequence[Node]:
        return [self.left, self.right]


@dc.dataclass(frozen=True)
class AndExpression(Node, lang.Final):
    left: Node
    right: Node

    @property
    def children(self) -> ta.Sequence[Node]:
        return [self.left, self.right]


@dc.dataclass(frozen=True)
class NotExpression(Node, lang.Final):
    expr: Node

    @property
    def children(self) -> ta.Sequence[Node]:
        return [self.expr]


@dc.dataclass(frozen=True)
class Pipe(Node, lang.Final):
    left: Node
    right: Node

    @property
    def children(self) -> ta.Sequence[Node]:
        return [self.left, self.right]


@dc.dataclass(frozen=True)
class Projection(Node, lang.Final):
    left: Node
    right: Node

    @property
    def children(self) -> ta.Sequence[Node]:
        return [self.left, self.right]


@dc.dataclass(frozen=True)
class Subexpression(Node, lang.Final):
    children_nodes: ta.Sequence[Node]

    @property
    def children(self) -> ta.Sequence[Node]:
        return tuple(self.children_nodes)


@dc.dataclass(frozen=True)
class Slice(LeafNode, lang.Final):
    start: int | None
    end: int | None
    step: int | None


@dc.dataclass(frozen=True)
class TernaryOperator(Node, lang.Final):
    condition: Node
    if_truthy: Node
    if_falsy: Node

    @property
    def children(self) -> ta.Sequence[Node]:
        return [self.condition, self.if_truthy, self.if_falsy]


@dc.dataclass(frozen=True)
class ValueProjection(Node, lang.Final):
    left: Node
    right: Node

    @property
    def children(self) -> ta.Sequence[Node]:
        return [self.left, self.right]


@dc.dataclass(frozen=True)
class VariableRef(LeafNode, lang.Final):
    name: str
