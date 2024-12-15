# ruff: noqa: N802 N815
import ast
import typing as ta

from omlish import check


MAGIC_VARS: ta.Mapping[str, ta.AbstractSet[str]] = {
    'index': {'i', 'idx', 'index'},
    'loop': {'line', 'x', 'l'},
    'input': {'lines', 'stdin'},
}


def is_magic_var(name: str) -> bool:
    return any(name in names for names in MAGIC_VARS.values())


class NameFinder(ast.NodeVisitor):
    """
    Finds undefined names, top-level defined names and wildcard imports in the given AST.

    A top-level defined name is any name that is stored to in the top-level scopes of ``trees``. An undefined name is
    any name that is loaded before it is defined (in any scope).

    Notes: a) we ignore deletes, b) used builtins will appear in undefined names, c) this logic doesn't fully support
    nonlocal / global / late-binding scopes.
    """

    def __init__(self, *trees: ast.AST) -> None:
        self._scopes: list[set[str]] = [set()]
        self._comprehension_scopes: list[int] = []

        self.undefined: set[str] = set()
        self.wildcard_imports: list[str] = []
        for tree in trees:
            self.visit(tree)
        check.equal(len(self._scopes), 1)

    @property
    def top_level_defined(self) -> set[str]:
        return self._scopes[0]

    def flexible_visit(self, value: ta.Any) -> None:
        if isinstance(value, list):
            for item in value:
                if isinstance(item, ast.AST):
                    self.visit(item)
        elif isinstance(value, ast.AST):
            self.visit(value)

    def generic_visit(self, node: ast.AST) -> None:
        def order(f_v: tuple[str, ta.Any]) -> int:
            # This ordering fixes comprehensions, dict comps, loops, assignments
            return {'generators': -3, 'iter': -3, 'key': -2, 'value': -1}.get(f_v[0], 0)

        # Adapted from ast.NodeVisitor.generic_visit, but re-orders traversal a little
        for _, value in sorted(ast.iter_fields(node), key=order):
            self.flexible_visit(value)

    def visit_Name(self, node: ast.Name) -> None:
        if isinstance(node.ctx, ast.Load):
            if all(node.id not in d for d in self._scopes):
                self.undefined.add(node.id)
        elif isinstance(node.ctx, ast.Store):
            self._scopes[-1].add(node.id)
        # Ignore deletes, see docstring
        self.generic_visit(node)

    def visit_Global(self, node: ast.Global) -> None:
        self._scopes[-1] |= self._scopes[0] & set(node.names)

    def visit_Nonlocal(self, node: ast.Nonlocal) -> None:
        if len(self._scopes) >= 2:
            self._scopes[-1] |= self._scopes[-2] & set(node.names)

    def visit_AugAssign(self, node: ast.AugAssign) -> None:
        if isinstance(node.target, ast.Name):
            # TODO: think about global, nonlocal
            if node.target.id not in self._scopes[-1]:
                self.undefined.add(node.target.id)
        self.generic_visit(node)

    def visit_NamedExpr(self, node: ta.Any) -> None:
        self.visit(node.value)
        # PEP 572 has weird scoping rules
        check.isinstance(node.target, ast.Name)
        check.isinstance(node.target.ctx, ast.Store)
        scope_index = len(self._scopes) - 1
        comp_index = len(self._comprehension_scopes) - 1
        while comp_index >= 0 and scope_index == self._comprehension_scopes[comp_index]:
            scope_index -= 1
            comp_index -= 1
        self._scopes[scope_index].add(node.target.id)

    def visit_alias(self, node: ast.alias) -> None:
        if node.name != '*':
            self._scopes[-1].add(
                node.asname if node.asname is not None else node.name.split('.')[0],
            )

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        if node.module is not None and '*' in (a.name for a in node.names):
            self.wildcard_imports.append(node.module)
        self.generic_visit(node)

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        self.flexible_visit(node.decorator_list)
        self.flexible_visit(node.bases)
        self.flexible_visit(node.keywords)

        self._scopes.append(set())
        self.flexible_visit(node.body)
        self._scopes.pop()
        # Classes are not okay with self-reference, so define ``name`` afterwards
        self._scopes[-1].add(node.name)

    def visit_function_helper(self, node: ta.Any, name: str | None = None) -> None:
        # Functions are okay with recursion, but not self-reference while defining default values
        self.flexible_visit(node.args)
        if name is not None:
            self._scopes[-1].add(name)

        self._scopes.append(set())
        for arg_node in ast.iter_child_nodes(node.args):
            if isinstance(arg_node, ast.arg):
                self._scopes[-1].add(arg_node.arg)
        self.flexible_visit(node.body)
        self._scopes.pop()

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self.flexible_visit(node.decorator_list)
        self.visit_function_helper(node, node.name)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self.flexible_visit(node.decorator_list)
        self.visit_function_helper(node, node.name)

    def visit_Lambda(self, node: ast.Lambda) -> None:
        self.visit_function_helper(node)

    def visit_ExceptHandler(self, node: ast.ExceptHandler) -> None:
        # ExceptHandler's name is scoped to the handler. If name exists and the name is not already
        # defined, we'll define then undefine it to mimic the scope.
        if not node.name or node.name in self._scopes[-1]:
            self.generic_visit(node)
            return

        self.flexible_visit(node.type)
        check.not_none(node.name)
        self._scopes[-1].add(node.name)
        self.flexible_visit(node.body)
        self._scopes[-1].remove(node.name)

    def visit_comprehension_helper(self, node: ta.Any) -> None:
        self._comprehension_scopes.append(len(self._scopes))
        self._scopes.append(set())
        self.generic_visit(node)
        self._scopes.pop()
        self._comprehension_scopes.pop()

    visit_ListComp = visit_comprehension_helper
    visit_SetComp = visit_comprehension_helper
    visit_GeneratorExp = visit_comprehension_helper
    visit_DictComp = visit_comprehension_helper
