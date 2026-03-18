# ruff: noqa: UP006
# @omlish-lite
import dataclasses as dc
import typing as ta


T = ta.TypeVar('T')


##


@dc.dataclass()
class _MinUniquePrefixLenNode(ta.Generic[T]):
    part: ta.Tuple[T, ...] = ()
    children: ta.Dict[T, '_MinUniquePrefixLenNode[T]'] = dc.field(default_factory=dict)
    count: int = 0  # number of items sharing the prefix ending at this node
    terminal_count: int = 0  # number of items ending exactly at this node


def min_unique_prefix_lens(items: ta.Sequence[ta.Sequence[T]]) -> ta.List[int]:
    if len(items) <= 1:
        return [0] * len(items)

    def common_prefix_len(
        item: ta.Sequence[T],
        item_pos: int,
        part: ta.Tuple[T, ...],
    ) -> int:
        n = min(len(item) - item_pos, len(part))
        i = 0
        while i < n and item[item_pos + i] == part[i]:
            i += 1
        return i

    root: _MinUniquePrefixLenNode[T] = _MinUniquePrefixLenNode()

    for item in items:
        root.count += 1

        node = root
        pos = 0

        while True:
            if pos == len(item):
                node.terminal_count += 1
                break

            key = item[pos]
            child = node.children.get(key)
            if child is None:
                node.children[key] = _MinUniquePrefixLenNode(
                    part=tuple(item[pos:]),
                    count=1,
                    terminal_count=1,
                )
                break

            common_len = common_prefix_len(item, pos, child.part)

            if common_len == len(child.part):
                child.count += 1
                node = child
                pos += common_len
                continue

            split = _MinUniquePrefixLenNode(
                part=child.part[:common_len],
                count=child.count + 1,
            )
            node.children[key] = split

            child.part = child.part[common_len:]
            split.children[child.part[0]] = child

            pos += common_len
            if pos == len(item):
                split.terminal_count = 1
            else:
                new_part = tuple(item[pos:])
                split.children[new_part[0]] = _MinUniquePrefixLenNode(
                    part=new_part,
                    count=1,
                    terminal_count=1,
                )

            break

    stack = [root]
    while stack:
        node = stack.pop()

        if node.terminal_count > 1:
            raise ValueError('duplicate items present')

        if node.terminal_count and node.children:
            raise ValueError('at least one item is a prefix of another')

        stack.extend(node.children.values())

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
