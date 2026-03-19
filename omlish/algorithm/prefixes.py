# ruff: noqa: UP006
# @omlish-lite
"""
TODO:
 - full radix lol, each node has set? of terminals
"""
import dataclasses as dc
import typing as ta


T = ta.TypeVar('T')


##


@dc.dataclass()
class MinUniquePrefixLenNode(ta.Generic[T]):
    part: ta.Tuple[T, ...] = ()
    children: ta.Dict[T, 'MinUniquePrefixLenNode[T]'] = dc.field(default_factory=dict)
    count: int = 0  # number of items in this subtree
    terminals: ta.Set[ta.Tuple[T, ...]] = dc.field(default_factory=set)

    @property
    def terminal_count(self) -> int:
        return len(self.terminals)


def build_min_unique_prefix_tree(items: ta.Sequence[ta.Sequence[T]]) -> MinUniquePrefixLenNode:
    if not items:
        return MinUniquePrefixLenNode()

    if len(items) == 1:
        part = tuple(items[0])
        return MinUniquePrefixLenNode(
            part=part,
            count=1,
            terminals={part},
        )

    def common_prefix_len(item: 'ta.Sequence[T]', item_pos: int, part: 'ta.Tuple[T, ...]') -> int:
        n = min(len(item) - item_pos, len(part))
        i = 0
        while i < n and item[item_pos + i] == part[i]:
            i += 1
        return i

    root: MinUniquePrefixLenNode[T] = MinUniquePrefixLenNode()

    for item in items:
        root.count += 1

        node = root
        pos = 0

        while True:
            if pos == len(item):
                term = node.part
                if term in node.terminals:
                    raise ValueError('duplicate items present')
                node.terminals.add(term)
                break

            key = item[pos]
            child = node.children.get(key)
            if child is None:
                part = tuple(item[pos:])
                node.children[key] = MinUniquePrefixLenNode(
                    part=part,
                    count=1,
                    terminals={part},
                )
                break

            common_len = common_prefix_len(item, pos, child.part)

            if common_len == len(child.part):
                child.count += 1
                node = child
                pos += common_len
                continue

            if pos + common_len == len(item):
                child.count += 1
                term = child.part[:common_len]
                if term in child.terminals:
                    raise ValueError('duplicate items present')
                child.terminals.add(term)
                break

            split = MinUniquePrefixLenNode(
                part=child.part[:common_len],
                count=child.count + 1,
            )
            node.children[key] = split

            old_terminals = child.terminals
            child.terminals = set()

            new_child_part = child.part[common_len:]
            child.part = new_child_part

            for term in old_terminals:
                if len(term) <= common_len:
                    split.terminals.add(term)
                else:
                    child.terminals.add(term[common_len:])

            split.children[child.part[0]] = child

            pos += common_len
            new_part = tuple(item[pos:])
            split.children[new_part[0]] = MinUniquePrefixLenNode(
                part=new_part,
                count=1,
                terminals={new_part},
            )

            break

    stack = [root]
    while stack:
        node = stack.pop()

        if len(node.terminals) > 1:
            raise ValueError('at least one item is a prefix of another')

        if node.terminals:
            term = next(iter(node.terminals))
            if len(term) < len(node.part):
                raise ValueError('at least one item is a prefix of another')
            if node.children:
                raise ValueError('at least one item is a prefix of another')

        stack.extend(node.children.values())

    return root


##


def min_unique_prefix_lens(items: ta.Sequence[ta.Sequence[T]]) -> ta.List[int]:
    if len(items) <= 1:
        return [0] * len(items)

    root = build_min_unique_prefix_tree(items)

    out = []

    for item in items:
        node = root
        pos = 0
        depth = 0

        while True:
            child = node.children[item[pos]]

            if child.count == 1:
                out.append(depth + 1)
                break

            part_len = len(child.part)
            pos += part_len
            depth += part_len
            node = child

    return out


def min_unique_prefix_len(items: ta.Sequence[ta.Sequence[T]]) -> int:
    return max(min_unique_prefix_lens(items), default=0)
