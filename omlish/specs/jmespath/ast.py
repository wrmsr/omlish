import typing as ta


class Ast(ta.TypedDict):
    type: str
    children: list['Ast']
    value: ta.NotRequired[ta.Any]


def arithmetic_unary(operator, expression) -> Ast:
    return {'type': 'arithmetic_unary', 'children': [expression], 'value': operator}


def arithmetic(operator, left, right) -> Ast:
    return {'type': 'arithmetic', 'children': [left, right], 'value': operator}


def assign(name, expr) -> Ast:
    return {'type': 'assign', 'children': [expr], 'value': name}


def comparator(name, first, second) -> Ast:
    return {'type': 'comparator', 'children': [first, second], 'value': name}


def current_node() -> Ast:
    return {'type': 'current', 'children': []}


def root_node() -> Ast:
    return {'type': 'root', 'children': []}


def expref(expression) -> Ast:
    return {'type': 'expref', 'children': [expression]}


def function_expression(name, args) -> Ast:
    return {'type': 'function_expression', 'children': args, 'value': name}


def field(name) -> Ast:
    return {'type': 'field', 'children': [], 'value': name}


def filter_projection(left, right, comparator) -> Ast:
    return {'type': 'filter_projection', 'children': [left, right, comparator]}


def flatten(node) -> Ast:
    return {'type': 'flatten', 'children': [node]}


def identity() -> Ast:
    return {'type': 'identity', 'children': []}


def index(index) -> Ast:
    return {'type': 'index', 'value': index, 'children': []}


def index_expression(children) -> Ast:
    return {'type': 'index_expression', 'children': children}


def key_val_pair(key_name, node) -> Ast:
    return {'type': 'key_val_pair', 'children': [node], 'value': key_name}


def let_expression(bindings, expr) -> Ast:
    return {'type': 'let_expression', 'children': [*bindings, expr]}


def literal(literal_value) -> Ast:
    return {'type': 'literal', 'value': literal_value, 'children': []}


def multi_select_dict(nodes) -> Ast:
    return {'type': 'multi_select_dict', 'children': nodes}


def multi_select_list(nodes) -> Ast:
    return {'type': 'multi_select_list', 'children': nodes}


def or_expression(left, right) -> Ast:
    return {'type': 'or_expression', 'children': [left, right]}


def and_expression(left, right) -> Ast:
    return {'type': 'and_expression', 'children': [left, right]}


def not_expression(expr) -> Ast:
    return {'type': 'not_expression', 'children': [expr]}


def pipe(left, right) -> Ast:
    return {'type': 'pipe', 'children': [left, right]}


def projection(left, right) -> Ast:
    return {'type': 'projection', 'children': [left, right]}


def subexpression(children) -> Ast:
    return {'type': 'subexpression', 'children': children}


def slice(start, end, step) -> Ast:  # noqa
    return {'type': 'slice', 'children': [start, end, step]}


def value_projection(left, right) -> Ast:
    return {'type': 'value_projection', 'children': [left, right]}


def variable_ref(name: str) -> Ast:
    return {'type': 'variable_ref', 'children': [], 'value': name}
