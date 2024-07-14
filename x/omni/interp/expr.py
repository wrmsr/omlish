import ast
import typing as ta

from .base import SimpleInterpVisitor


class SimpleInterpExprVisitor(SimpleInterpVisitor):
    """
    Await
    DictComp
    FormattedValue
    GeneratorExp
    JoinedStr
    ListComp
    SetComp
    Starred
    Yield
    YieldFrom
    """

    _ast_cls = ast.expr

    def visit_Attribute(self, node):
        value = self.visit(node.value)
        return getattr(value, node.attr)

    def visit_BinOp(self, node):
        left = self.visit(node.left)
        right = self.visit(node.right)
        if isinstance(node.op, ast.Add):
            return left + right
        elif isinstance(node.op, ast.BitAnd):
            return left & right
        elif isinstance(node.op, ast.BitOr):
            return left | right
        elif isinstance(node.op, ast.BitXor):
            return left ^ right
        elif isinstance(node.op, ast.Div):
            return left / right
        elif isinstance(node.op, ast.FloorDiv):
            return left // right
        elif isinstance(node.op, ast.LShift):
            return left << right
        elif isinstance(node.op, ast.MatMult):
            return left @ right
        elif isinstance(node.op, ast.Mod):
            return left % right
        elif isinstance(node.op, ast.Mult):
            return left * right
        elif isinstance(node.op, ast.RShift):
            return left >> right
        elif isinstance(node.op, ast.Sub):
            return left - right
        else:
            raise TypeError(node)

    def visit_BoolOp(self, node):
        left = self.visit(node.values[0])
        for right in node.values[1:]:
            if isinstance(node.op, ast.And):
                if not left:
                    break
            elif isinstance(node.op, ast.Or):
                if left:
                    break
            else:
                raise TypeError(node)
            left = self.visit(right)
        return left

    def visit_Bytes(self, node):
        return node.s

    def visit_Call(self, node):
        func = self.visit(node.func)
        args = list(map(self.visit, node.args))
        if node.keywords:
            raise TypeError(node)
        return func(*args)

    def visit_Constant(self, node):
        return node.value

    def visit_Compare(self, node):
        left = self.visit(node.left)
        for op, comparator in zip(node.ops, map(self.visit, node.comparators)):
            if isinstance(op, ast.Eq):
                if not (left == comparator):
                    return False
            elif isinstance(op, ast.Gt):
                if not (left > comparator):
                    return False
            elif isinstance(op, ast.GtE):
                if not (left >= comparator):
                    return False
            elif isinstance(op, ast.In):
                if not (left in comparator):
                    return False
            elif isinstance(op, ast.Is):
                if not (left is comparator):
                    return False
            elif isinstance(op, ast.IsNot):
                if not (left is not comparator):
                    return False
            elif isinstance(op, ast.Lt):
                if not (left < comparator):
                    return False
            elif isinstance(op, ast.LtE):
                if not (left <= comparator):
                    return False
            elif isinstance(op, ast.NotEq):
                if not (left != comparator):
                    return False
            elif isinstance(op, ast.NotIn):
                if not (left not in comparator):
                    return False
            else:
                raise TypeError(node)
            left = comparator
        return True

    def visit_Dict(self, node):
        return dict(zip(map(self.visit, node.keys), map(self.visit, node.values)))

    def visit_Ellipsis(self, node):
        return ...

    def visit_IfExp(self, node):
        test = self.visit(node.test)
        if test:
            return self.visit(node.body)
        else:
            return self.visit(node.orelse)

    def visit_Lambda(self, node):
        def inner(*args):
            if not len(args) == len(largs):
                raise TypeError(node, args)
            child = SimpleInterpExprVisitor(dict(zip(largs, args)), self)
            return child.visit(node.body)
        largs = self._get_args(node.args)
        return inner

    def visit_List(self, node):
        return list(map(self.visit, node.elts))

    def visit_ListComp(self, node):
        # return list(map(self.visit, node.elts))
        raise TypeError(node)

    def visit_Name(self, node):
        return self.get_local(node.id)

    def visit_NameConstant(self, node):
        return node.value

    def visit_NamedExpr(self, node):
        raise TypeError(node)

    def visit_Num(self, node):
        return node.n

    def visit_Set(self, node):
        return set(map(self.visit, node.elts))

    def visit_Str(self, node):
        return node.s

    def visit_Subscript(self, node):
        if isinstance(node.slice, ast.Index):
            item = self.visit(node.slice.value)
        elif isinstance(node.slice, ast.Slice):
            lower, upper, step = [
                self.visit(s) if s is not None else None
                for s in [node.slice.lower, node.slice.upper, node.slice.step]
            ]
            item = slice(lower, upper, step)
        else:
            raise TypeError(node.slice)
        value = self.visit(node.value)
        return value[item]

    def visit_Tuple(self, node):
        return tuple(map(self.visit, node.elts))

    def visit_UnaryOp(self, node):
        operand = self.visit(node.operand)
        if isinstance(node.op, ast.Invert):
            return ~operand
        elif isinstance(node.op, ast.Not):
            return not operand
        elif isinstance(node.op, ast.UAdd):
            return +operand
        elif isinstance(node.op, ast.USub):
            return -operand
        else:
            raise TypeError(node)


def simple_interp_expr(
        node_or_string: ta.Union[str, ast.AST],
        *,
        interp: SimpleInterpExprVisitor = None,
) -> ta.Any:
    if isinstance(node_or_string, str):
        node_or_string = ast.parse(node_or_string, mode='eval')
    if isinstance(node_or_string, ast.Expression):
        node_or_string = node_or_string.body
    if interp is None:
        interp = SimpleInterpExprVisitor()
    return interp.visit(node_or_string)
