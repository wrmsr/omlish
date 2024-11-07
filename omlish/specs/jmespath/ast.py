import typing as ta


class Node(ta.TypedDict):
    type: str
    children: list['Node']
    value: ta.NotRequired[ta.Any]


def arithmetic_unary(operator, expression) -> Node:
    return {'type': 'arithmetic_unary', 'children': [expression], 'value': operator}


def arithmetic(operator, left, right) -> Node:
    return {'type': 'arithmetic', 'children': [left, right], 'value': operator}


def assign(name, expr) -> Node:
    return {'type': 'assign', 'children': [expr], 'value': name}


def comparator(name, first, second) -> Node:
    return {'type': 'comparator', 'children': [first, second], 'value': name}


def current_node() -> Node:
    return {'type': 'current', 'children': []}


def root_node() -> Node:
    return {'type': 'root', 'children': []}


def expref(expression) -> Node:
    return {'type': 'expref', 'children': [expression]}


def function_expression(name, args) -> Node:
    return {'type': 'function_expression', 'children': args, 'value': name}


def field(name) -> Node:
    return {'type': 'field', 'children': [], 'value': name}


def filter_projection(left, right, comparator) -> Node:
    return {'type': 'filter_projection', 'children': [left, right, comparator]}


def flatten(node) -> Node:
    return {'type': 'flatten', 'children': [node]}


def identity() -> Node:
    return {'type': 'identity', 'children': []}


def index(index) -> Node:
    return {'type': 'index', 'value': index, 'children': []}


def index_expression(children) -> Node:
    return {'type': 'index_expression', 'children': children}


def key_val_pair(key_name, node) -> Node:
    return {'type': 'key_val_pair', 'children': [node], 'value': key_name}


def let_expression(bindings, expr) -> Node:
    return {'type': 'let_expression', 'children': [*bindings, expr]}


def literal(literal_value) -> Node:
    return {'type': 'literal', 'value': literal_value, 'children': []}


def multi_select_dict(nodes) -> Node:
    return {'type': 'multi_select_dict', 'children': nodes}


def multi_select_list(nodes) -> Node:
    return {'type': 'multi_select_list', 'children': nodes}


def or_expression(left, right) -> Node:
    return {'type': 'or_expression', 'children': [left, right]}


def and_expression(left, right) -> Node:
    return {'type': 'and_expression', 'children': [left, right]}


def not_expression(expr) -> Node:
    return {'type': 'not_expression', 'children': [expr]}


def pipe(left: Node, right: Node) -> Node:
    return {'type': 'pipe', 'children': [left, right]}


def projection(left: Node, right: Node) -> Node:
    return {'type': 'projection', 'children': [left, right]}


def subexpression(children) -> Node:
    return {'type': 'subexpression', 'children': children}


def slice(start, end, step) -> Node:  # noqa
    return {'type': 'slice', 'children': [start, end, step]}


def value_projection(left: Node, right: Node) -> Node:
    return {'type': 'value_projection', 'children': [left, right]}


def variable_ref(name: str) -> Node:
    return {'type': 'variable_ref', 'children': [], 'value': name}
