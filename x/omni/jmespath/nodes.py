import typing as ta

from .. import dataclasses as dc
from .. import lang


class Node(dc.Enum, sealed=True):
    pass


class Operator(Node, abstract=True):
    pass


class Leaf(Node, abstract=True):
    pass


class And(Operator):
    left: Node
    right: Node


class Compare(Operator):
    class Op(lang.ValueEnum):
        EQ = '=='
        NE = '!='
        GT = '>'
        GE = '>='
        LT = '<'
        LE = '<='

    op: Op
    left: Node
    right: Node


class CreateArray(Node):
    items: ta.Sequence[Node]


class CreateObject(Node):
    fields: ta.Mapping[str, Node]


class Current(Leaf):
    pass


class ExpressionRef(Node):
    expr: Node


class FlattenArray(Leaf):
    pass


class FlattenObject(Leaf):
    pass


class FunctionCall(Node):
    name: str
    args: ta.Sequence[Node]


class Index(Leaf):
    value: int


class JsonLiteral(Leaf):
    text: str


class Negate(Node):
    item: Node


class Or(Operator):
    left: Node
    right: Node


class Parameter(Leaf):
    class Target(dc.Enum, sealed=True):
        pass

    class NumberTarget(Target):
        value: int

    class NameTarget(Target):
        value: str

    target: Target


class Project(Node):
    child: Node


class Property(Leaf):
    name: str


class Selection(Node):
    child: Node


class Sequence(Node):
    items: ta.Sequence[Node]


class Slice(Leaf):
    start: ta.Optional[int]
    stop: ta.Optional[int]
    step: ta.Optional[int]


class String(Leaf):
    value: Node
