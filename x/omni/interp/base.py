"""  # noqa
TODO:
 - 'profiles'
  - full: debugging
  - restricted: configs, exprs
  - star - starlark
  - https://instagram-engineering.com/python-at-scale-strict-modules-c0bb9245c834

In [10]: [(e, e.__mro__) for a in dir(ast) for e in [getattr(ast, a)] if isinstance(e, type) and issubclass(e, ast.AST) and e.__mro__[1] is ast.AST]
Out[10]:
[(_ast.alias, (_ast.alias, _ast.AST, object)),
(_ast.arg, (_ast.arg, _ast.AST, object)),
(_ast.arguments, (_ast.arguments, _ast.AST, object)),
(_ast.boolop, (_ast.boolop, _ast.AST, object)),
(_ast.cmpop, (_ast.cmpop, _ast.AST, object)),
(_ast.comprehension, (_ast.comprehension, _ast.AST, object)),
(_ast.excepthandler, (_ast.excepthandler, _ast.AST, object)),
(_ast.expr, (_ast.expr, _ast.AST, object)),
(_ast.expr_context, (_ast.expr_context, _ast.AST, object)),
(_ast.keyword, (_ast.keyword, _ast.AST, object)),
(_ast.mod, (_ast.mod, _ast.AST, object)),
(_ast.operator, (_ast.operator, _ast.AST, object)),
(_ast.slice, (_ast.slice, _ast.AST, object)),
(_ast.stmt, (_ast.stmt, _ast.AST, object)),
(_ast.unaryop, (_ast.unaryop, _ast.AST, object)),
(_ast.withitem, (_ast.withitem, _ast.AST, object))]

In [12]: [(e, e.__mro__) for a in dir(ast) for e in [getattr(ast, a)] if isinstance(e, type) and issubclass(e, ast.AST) and e.__mro__[1] is ast.mod]
Out[12]:
[(_ast.Expression, (_ast.Expression, _ast.mod, _ast.AST, object)),
(_ast.Interactive, (_ast.Interactive, _ast.mod, _ast.AST, object)),
(_ast.Module, (_ast.Module, _ast.mod, _ast.AST, object)),
(_ast.Suite, (_ast.Suite, _ast.mod, _ast.AST, object))]
"""
import ast
import typing as ta

from .. import check
from .. import lang
from .builtins import filter_builtins


class SimpleInterpVisitor(ast.NodeVisitor, lang.Abstract):

    def __init__(
            self,
            locals: ta.Mapping[str, ta.Any] = None,
            parent: 'SimpleInterpVisitor' = None,
    ) -> None:
        super().__init__()

        self._parent = check.isinstance(parent, SimpleInterpVisitor) if parent is not None else None

        self._locals = dict(filter_builtins())
        if locals is not None:
            self._locals.update(locals)

    _ast_cls = ast.AST

    def get_local(self, name: str) -> ta.Any:
        try:
            return self._locals[name]
        except KeyError:
            if self._parent is not None:
                return self._parent.get_local(name)
            else:
                raise

    @staticmethod
    def _get_args(node: ast.arguments) -> ta.List[str]:
        args: ta.List[str] = []
        for arg in node.args:
            if isinstance(arg, ast.arg):
                args.append(arg.arg)
            else:
                raise TypeError(node)

        if (
                node.defaults or
                node.kw_defaults or
                node.kwarg or
                node.kwonlyargs or
                getattr(node, 'posonlyargs', []) or
                node.vararg
        ):
            raise TypeError(node)

        return args

    def generic_visit(self, node):
        raise TypeError(node)

    def visit(self, node):
        check.isinstance(node, self._ast_cls)
        return super().visit(node)
