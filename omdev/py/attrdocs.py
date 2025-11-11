# ruff: noqa: N802
"""
TODO:
 - shared / global ast cache
  - weak key by module?
"""
import ast
import dataclasses as dc
import inspect
import typing as ta

from omlish import check
from omlish import lang

from .tokens import all as tks


##


@dc.dataclass(frozen=True)
class AttrDoc:
    docstring: str | None = None
    trailing_comment: str | None = None
    preceding_comment: str | None = None

    __repr__ = lang.attr_ops(lambda o: (
        o.docstring,
        o.trailing_comment,
        o.preceding_comment,
    ), repr_filter=bool).repr


_EMPTY_ATTR_DOC = AttrDoc()


##


class _AttrDocAstVisitor(ast.NodeVisitor):
    def __init__(
            self,
            *,
            tok_lines: ta.Sequence[tks.Tokens] | None = None,
    ) -> None:
        super().__init__()

        self._tok_lines = tok_lines

        self._attr_docs: dict[str, AttrDoc] = {}
        self._class_stack: list[str] = []
        self._attr_target: str | None = None
        self._prev_node_type: type[ast.AST] | None = None

    @property
    def attr_docs(self) -> ta.Mapping[str, AttrDoc]:
        return self._attr_docs

    #

    def visit(self, node: ast.AST) -> ta.Any:
        if isinstance(node, (ast.AsyncFunctionDef, ast.FunctionDef)):
            self._prev_node_type = None
            return None
        node_result = super().visit(node)
        self._prev_node_type = type(node)
        return node_result

    #

    def visit_ClassDef(self, node: ast.ClassDef) -> ta.Any:
        self._class_stack.append(node.name)
        self.generic_visit(node)
        check.equal(self._class_stack.pop(), node.name)

    #

    @staticmethod
    def _comment_tok_src(tok: tks.Token) -> str:
        check.state(tok.name == 'COMMENT')
        tc = tok.src
        check.state(tc[0] == '#')
        return tc[1:].lstrip()

    def _set_attr_target(self, node: ast.Name) -> None:
        self._attr_target = '.'.join([*self._class_stack, node.id])

        ad = _EMPTY_ATTR_DOC

        if self._tok_lines is not None:
            line = self._tok_lines[node.lineno - 1]
            for t in reversed(line):
                if t.name not in tks.WS_NAMES:
                    break
                if t.name == 'COMMENT':
                    ad = dc.replace(ad, trailing_comment=self._comment_tok_src(t))
                    break

            pll: list[str] = []
            pln = node.lineno - 1
            while pln > 0:
                line = self._tok_lines[pln - 1]
                no_ws_line = list(tks.ignore_ws(line, keep={'COMMENT'}))
                if not no_ws_line or no_ws_line[0].name != 'COMMENT':  # noqa
                    break
                pll.append(self._comment_tok_src(no_ws_line[0]))
                pln -= 1
            if pll:
                ad = dc.replace(ad, preceding_comment='\n'.join(reversed(pll)))

        if ad is not _EMPTY_ATTR_DOC:
            self._attr_docs[self._attr_target] = ad

    def visit_AnnAssign(self, node: ast.AnnAssign) -> ta.Any:
        if isinstance(target := node.target, ast.Name):
            self._set_attr_target(target)

    def visit_Assign(self, node: ast.Assign) -> ta.Any:
        if len(node.targets) == 1 and isinstance(target := node.targets[0], ast.Name):
            self._set_attr_target(target)  # noqa

    #

    def visit_Expr(self, node: ast.Expr) -> ta.Any:
        if (
                isinstance(node.value, ast.Constant) and
                isinstance(node.value.value, str) and
                self._prev_node_type in (ast.Assign, ast.AnnAssign)
        ):
            if self._attr_target:
                docstring = inspect.cleandoc(node.value.value)
                ex = self._attr_docs.get(self._attr_target, _EMPTY_ATTR_DOC)
                check.none(ex.docstring)
                self._attr_docs[self._attr_target] = dc.replace(ex, docstring=docstring)

            self._attr_target = None


def extract_attr_docs(src: str) -> ta.Mapping[str, AttrDoc]:
    if not src:
        return {}

    toks = tks.src_to_tokens(src)
    tok_lines = tks.split_lines_dense(toks)

    src_ast = ast.parse(src)

    # import astpretty
    # astpretty.pprint(src_ast)

    ast_visitor = _AttrDocAstVisitor(tok_lines=tok_lines)
    ast_visitor.visit(src_ast)
    return ast_visitor.attr_docs


##


# @omlish-manifest
_CLI_MODULE = {'!.cli.types.CliModule': {
    'name': 'py/attrdocs',
    'module': __name__,
}}


if __name__ == '__main__':
    def _main() -> None:
        import argparse

        parser = argparse.ArgumentParser()
        parser.add_argument('file')
        args = parser.parse_args()

        #

        with open(args.file) as f:
            src = f.read()

        #

        attr_docs = extract_attr_docs(src)

        #

        nested_attr_docs: dict = {}
        for k, v in attr_docs.items():
            cur = nested_attr_docs
            *kps, ekp = [f'.{kp}' for kp in k.split('.')]
            for kp in kps:
                cur = cur.setdefault(kp, {})
            check.not_in(ekp, cur)
            cur[ekp] = {k: v for k, v in dc.asdict(v).items() if v}

        #

        import json

        print(json.dumps(nested_attr_docs, indent=2))

    _main()
