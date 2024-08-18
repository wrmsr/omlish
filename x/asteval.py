import ast
import typing as ta

from omlish import check
from omlish import dispatch


T = ta.TypeVar('T')
C = ta.TypeVar('C')


class AstVisitor(ta.Generic[C, T]):
    @dispatch.method
    def visit(self, n: ast.AST, c: C) -> T:
        raise NotImplementedError


class EvalAstVisitor(AstVisitor[None, ta.Any]):
    @AstVisitor.visit.register
    def _visit_bin_op(self, n: ast.BinOp, c: None) -> ta.Any:
        raise NotImplementedError


def _main():
    n = ast.parse('2 + 3')
    e = check.single(check.isinstance(n, ast.Module).body)
    o = EvalAstVisitor().visit(e, None)
    print(o)


if __name__ == '__main__':
    _main()
