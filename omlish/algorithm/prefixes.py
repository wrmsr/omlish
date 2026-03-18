# ruff: noqa: UP006
# @omlish-lite
import dataclasses as dc
import typing as ta


T = ta.TypeVar('T')


##


@dc.dataclass()
class _MinUniquePrefixLenTrieNode(ta.Generic[T]):
    children: ta.Dict[T, '_MinUniquePrefixLenTrieNode[T]'] = dc.field(default_factory=dict)
    count: int = 0  # number of items passing through this node
    terminal_count: int = 0  # number of items ending exactly at this node


def min_unique_prefix_lens(items: ta.Sequence[ta.Sequence[T]]) -> ta.List[int]:
    if len(items) <= 1:
        return [0] * len(items)

    root: _MinUniquePrefixLenTrieNode[T] = _MinUniquePrefixLenTrieNode()

    for item in items:
        node = root
        node.count += 1
        for x in item:
            node = node.children.setdefault(x, _MinUniquePrefixLenTrieNode())
            node.count += 1
        node.terminal_count += 1

    def check_impossible(node: _MinUniquePrefixLenTrieNode[T]) -> None:
        if node.terminal_count > 1:
            raise ValueError('duplicate items present')
        if node.terminal_count and node.children:
            raise ValueError('at least one item is a prefix of another')
        for child in node.children.values():
            check_impossible(child)

    check_impossible(root)

    out = []
    for item in items:
        node = root
        depth = 0
        for x in item:
            node = node.children[x]
            depth += 1  # noqa
            if node.count == 1:
                out.append(depth)
                break
        else:
            raise RuntimeError('unreachable')

    return out


def min_unique_prefix_len(items: ta.Sequence[ta.Sequence[T]]) -> int:
    return max(min_unique_prefix_lens(items), default=0)
