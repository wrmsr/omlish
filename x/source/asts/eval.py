import ast
import operator
import typing as ta

from omlish import check
from omlish import dispatch


T = ta.TypeVar('T')
C = ta.TypeVar('C')


##


class AstVisitor(ta.Generic[C, T]):
    def visit(self, n: ast.AST, c: C) -> T:
        return self._visit(n, c)

    @dispatch.method
    def _visit(self, n: ast.AST, c: C) -> T:
        raise TypeError(n)


class EvalAstVisitor(AstVisitor[None, ta.Any]):
    @AstVisitor._visit.register  # noqa
    def _visit_Expr(self, n: ast.Expr, c: None) -> ta.Any:  # noqa
        return self.visit(n.value, c)

    _BIN_OP_CLS_TO_OPERATOR: ta.Mapping[type[ast.operator], ta.Callable] = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.Mod: operator.mod,
        ast.FloorDiv: operator.floordiv,
        ast.Pow: operator.pow,
        ast.MatMult: operator.matmul,

        ast.BitAnd: operator.and_,
        ast.BitOr: operator.or_,
        ast.BitXor: operator.xor,
        ast.LShift: operator.lshift,
        ast.RShift: operator.rshift,
    }

    @AstVisitor._visit.register  # noqa
    def _visit_BinOp(self, n: ast.BinOp, c: None) -> ta.Any:  # noqa
        left = self.visit(n.left, c)
        right = self.visit(n.right, c)
        op = self._BIN_OP_CLS_TO_OPERATOR[type(n.op)]
        return op(left, right)

    _CMP_OP_CLS_TO_OPERATOR: ta.Mapping[type[ast.cmpop], ta.Callable] = {
        ast.Eq: operator.eq,
        ast.NotEq: operator.ne,
        ast.Lt: operator.lt,
        ast.LtE: operator.le,
        ast.Gt: operator.gt,
        ast.GtE: operator.ge,

        ast.Is: operator.is_,
        ast.IsNot: operator.is_not,

        ast.In: operator.contains,
        ast.NotIn: lambda *a: not operator.contains(*a),
    }

    @AstVisitor._visit.register  # noqa
    def _visit_Compare(self, n: ast.Compare, c: None) -> ta.Any:  # noqa
        left = self.visit(n.left, c)
        for o, r in zip(n.ops, n.comparators):
            right = self.visit(r, c)
            op = self._CMP_OP_CLS_TO_OPERATOR[type(o)]
            if not op(left, right):
                return False
            left = right
        return True

    @AstVisitor._visit.register  # noqa
    def _visit_Constant(self, n: ast.Constant, c: None) -> ta.Any:  # noqa
        return n.value


##


def _main():
    for s, e in [
        ('2 + 3 + (4 * 2)', 13),
        ('2 > 1', True),
    ]:
        a = ast.parse(s)
        n = check.single(check.isinstance(a, ast.Module).body)
        o = EvalAstVisitor().visit(n, None)
        assert o == e


if __name__ == '__main__':
    _main()
