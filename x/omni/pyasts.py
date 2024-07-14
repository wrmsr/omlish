import ast
import typing as ta

from . import check
from . import collections as col
from . import properties
from .graphs import trees


class PyAstNode(ta.NamedTuple):
    type: str
    fields: ta.Mapping[str, ta.Any]


def reduce_py_ast(obj: ta.Any) -> ta.Any:
    if obj is None:
        return None
    elif isinstance(obj, ast.AST):
        return PyAstNode(
            type(obj).__name__,
            col.frozendict((a, reduce_py_ast(getattr(obj, a))) for a in type(obj)._fields),
        )
    elif isinstance(obj, list):
        return col.frozenlist(reduce_py_ast(e) for e in obj)
    elif isinstance(obj, (int, str)):
        return obj
    else:
        raise TypeError(obj)


NON_UNIQUE_NODE_TYPES: ta.AbstractSet[ta.Type[ast.AST]] = {
    ast.cmpop,
    ast.expr_context,
    ast.operator,
    ast.unaryop,
}

NON_UNIQUE_NODE_TYPES_TUP = tuple(NON_UNIQUE_NODE_TYPES)


def iter_unique_child_nodes(node: ast.AST) -> ta.Iterator[ast.AST]:
    for child in ast.iter_child_nodes(node):
        if not isinstance(child, NON_UNIQUE_NODE_TYPES_TUP):
            yield child


class BasicAnalysis(trees.BasicTreeAnalysis[ast.AST]):

    def __init__(
            self,
            root: ast.AST,
            walker: trees.NodeWalker[ast.AST] = iter_unique_child_nodes,
            **kwargs,
    ) -> None:
        super().__init__(check.isinstance(root, ast.AST), walker, **kwargs)

    @properties.cached
    @property
    def node_seqs_by_lineno(self) -> col.SortedMapping[int, col.IndexedSeq[ast.AST]]:
        dct: ta.Dict[int, ta.List[ast.AST]] = {}
        for n in self._nodes:
            ln = getattr(n, 'lineno', None)
            if ln is not None:
                check.isinstance(ln, int)
                dct.setdefault(ln, []).append(n)
        return col.SkipListDict((ln, self._idx_seq_fac(ns)) for ln, ns in dct.items())


def analyze(root: ast.AST) -> BasicAnalysis:
    return BasicAnalysis(root)
