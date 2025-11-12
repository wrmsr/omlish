"""
Quite, quite lame, but sufficient for immediate needs. Accurate static symbol resolution is in development but can't
block other work.
"""
import ast
import dataclasses as dc
import typing as ta

from omlish import check


##


@dc.dataclass(frozen=True, kw_only=True)
class TopLevelImport:
    spec: str
    name: str
    node: ast.Import | ast.ImportFrom


@dc.dataclass(frozen=True, kw_only=True)
class TopLevelCall:
    node: ast.Call
    imp: TopLevelImport


@dc.dataclass(frozen=True, kw_only=True)
class TopLevelFindings:
    imports: ta.Mapping[str, TopLevelImport]
    calls: ta.Sequence[TopLevelCall]


##


class _TopLevelModuleVisitor(ast.NodeVisitor):
    def __init__(self, module_name: str) -> None:
        super().__init__()

        self.module_name = module_name
        self.module_name_parts = module_name.split('.')

        self.imports: dict[str, TopLevelImport] = {}
        self.calls: list[TopLevelCall] = []

    #

    def visit_Import(self, node: ast.Import) -> None:
        for alias in node.names:
            name = alias.asname if alias.asname else alias.name
            self.imports[name] = TopLevelImport(
                spec=alias.name,
                name=name,
                node=node,
            )

        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        if node.level:
            check.state(node.level < len(self.module_name_parts))
            module = '.'.join([
                *self.module_name_parts[:-node.level],
                *([node.module] if node.module else []),
            ])
        else:
            module = check.not_none(node.module)

        for alias in node.names:
            name = alias.asname if alias.asname else alias.name
            self.imports[name] = TopLevelImport(
                spec='.'.join([module, alias.name]),
                name=name,
                node=node,
            )

        self.generic_visit(node)

    #

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        pass

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        pass

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        pass

    #

    def handle_call(self, node: ast.Call) -> None:
        if not (
                isinstance(attr := node.func, ast.Attribute) and
                isinstance(attr.ctx, ast.Load) and
                isinstance(name := attr.value, ast.Name) and
                isinstance(name.ctx, ast.Load)
        ):
            return

        if (imp := self.imports.get(name.id)) is None:
            return

        self.calls.append(TopLevelCall(
            node=node,
            imp=imp,
        ))

    def visit_Call(self, node: ast.Call) -> None:
        self.handle_call(node)


def analyze_module_top_level(
        module: ast.Module,
        module_name: str,
) -> TopLevelFindings:
    visitor = _TopLevelModuleVisitor(module_name)
    visitor.visit(module)
    return TopLevelFindings(
        imports=visitor.imports,
        calls=visitor.calls,
    )
