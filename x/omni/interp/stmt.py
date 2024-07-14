import ast
import typing as ta

from .. import dataclasses as dc
from .base import SimpleInterpVisitor
from .expr import SimpleInterpExprVisitor


class StmtResult(dc.Data, frozen=True, sealed=True, abstract=True):
    pass


class BreakStmtResult(StmtResult, frozen=True, final=True):
    pass


class ContinueStmtResult(StmtResult, frozen=True, final=True):
    pass


class ReturnStmtResult(StmtResult, frozen=True, final=True):
    value: ta.Any


class SimpleInterpStmtVisitor(SimpleInterpVisitor):
    """
    AnnAssign
    Assert
    AsyncFor
    AsyncFunctionDef
    AsyncWith
    ClassDef
    Delete
    Global
    Import
    ImportFrom
    Nonlocal
    Raise
    Try
    With
    """

    _ast_cls = ast.stmt

    def set_local(self, name: str, value: ta.Any) -> ta.Any:
        self._locals[name] = value
        return value

    def _interp_expr(self, node):
        interp = SimpleInterpExprVisitor(parent=self)
        return interp.visit(node)

    def visit_Assign(self, node):
        if len(node.targets) != 1:
            raise TypeError(node)
        [target] = node.targets
        if not isinstance(target, ast.Name):
            raise TypeError(node)
        value = self._interp_expr(node.value)
        self.set_local(target.id, value)
        return None

    def visit_AugAssign(self, node):
        if not isinstance(node.target, ast.Name):
            raise TypeError(node)
        left = self.get_local(node.target.id)
        right = self._interp_expr(node.value)
        if isinstance(node.op, ast.Add):
            left += right
        elif isinstance(node.op, ast.BitAnd):
            left &= right
        elif isinstance(node.op, ast.BitOr):
            left |= right
        elif isinstance(node.op, ast.BitXor):
            left ^= right
        elif isinstance(node.op, ast.Div):
            left /= right
        elif isinstance(node.op, ast.FloorDiv):
            left //= right
        elif isinstance(node.op, ast.LShift):
            left <<= right
        elif isinstance(node.op, ast.MatMult):
            left @= right
        elif isinstance(node.op, ast.Mod):
            left %= right
        elif isinstance(node.op, ast.Mult):
            left *= right
        elif isinstance(node.op, ast.RShift):
            left >>= right
        elif isinstance(node.op, ast.Sub):
            left -= right
        else:
            raise TypeError(node)
        self.set_local(node.target.id, left)
        return None

    def visit_Break(self, node):
        return BreakStmtResult()

    def visit_Continue(self, node):
        return ContinueStmtResult()

    def visit_Expr(self, node):
        self._interp_expr(node.value)
        return None

    def visit_For(self, node):
        if not isinstance(node.target, ast.Name):
            raise TypeError(node)
        it = self._interp_expr(node.iter)
        for item in it:
            self.set_local(node.target.id, item)
            ret = None
            for bnode in node.body:
                ret = self.visit(bnode)
                if ret is not None:
                    break
            if isinstance(ret, BreakStmtResult):
                break
            elif isinstance(ret, ContinueStmtResult):
                continue
            elif ret is not None:
                return ret
        if node.orelse:
            for bnode in node.orelse:
                ret = self.visit(bnode)
                if ret is not None:
                    return ret
        return None

    def visit_FunctionDef(self, node):
        def inner(*args):
            if not len(args) == len(fargs):
                raise TypeError(node, args)
            child = SimpleInterpStmtVisitor(dict(zip(fargs, args)), self)
            for snode in node.body:
                ret = child.visit(snode)
                if ret is not None:
                    return ret
            return None
        if node.decorator_list:
            raise TypeError(node)
        fargs = self._get_args(node.args)
        self._locals[node.name] = inner
        return None

    def visit_If(self, node):
        test = self._interp_expr(node.test)
        path = node.body if test else node.orelse
        for pnode in path:
            ret = self.visit(pnode)
            if ret is not None:
                return ret
        return None

    def visit_Pass(self, node):
        return None

    def visit_Return(self, node):
        return ReturnStmtResult(self._interp_expr(node.value))

    def visit_While(self, node):
        while True:
            test = self._interp_expr(node.test)
            if not test:
                break
            ret = None
            for bnode in node.body:
                ret = self.visit(bnode)
                if ret is not None:
                    break
            if isinstance(ret, BreakStmtResult):
                break
            elif isinstance(ret, ContinueStmtResult):
                continue
            elif ret is not None:
                return ret
        if node.orelse:
            for bnode in node.orelse:
                ret = self.visit(bnode)
                if ret is not None:
                    return ret
        return None


def simple_interp_stmt(
        node_or_string: ta.Union[str, ast.AST],
        *,
        interp: SimpleInterpStmtVisitor = None,
) -> ta.Any:
    if isinstance(node_or_string, str):
        node_or_string = ast.parse(node_or_string, mode='exec')
    if isinstance(node_or_string, ast.Module):
        nodes = node_or_string.body
    else:
        nodes = [node_or_string]
    if interp is None:
        interp = SimpleInterpStmtVisitor()
    for node in nodes:
        ret = interp.visit(node)
        if ret is not None:
            return ret
    return None
