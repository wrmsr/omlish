import typing as ta

from ... import check
from ... import lang
from .ast import Node


##


def node_type(n: Node) -> str:
    return lang.snake_case(*lang.split_string_casing(type(n).__name__))


##


class Visitor:
    def __init__(self) -> None:
        super().__init__()

        self._method_cache: dict[str, ta.Callable] = {}
        self._node_stack: list[Node] = []

    def visit(self, node: Node, *args: ta.Any, **kwargs: ta.Any) -> ta.Any:
        nty = node_type(node)

        method = self._method_cache.get(nty)
        if method is None:
            method = check.not_none(getattr(self, f'visit_{nty}', self.default_visit))
            self._method_cache[nty] = method

        self._node_stack.append(node)
        try:
            return method(node, *args, **kwargs)
        finally:
            if (popped := self._node_stack.pop()) is not node:
                raise RuntimeError(f'Expected {node} but got {popped}')

    def default_visit(self, node, *args, **kwargs):
        raise NotImplementedError('default_visit')
