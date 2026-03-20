# ruff: noqa: UP006 UP045
# @omlish-lite
import dataclasses as dc
import typing as ta


T = ta.TypeVar('T')


##


@dc.dataclass()
class MinUniquePrefixNode(ta.Generic[T]):
    part: ta.Sequence[T] = ()

    children: ta.Dict[T, 'MinUniquePrefixNode[T]'] = dc.field(default_factory=dict)
    count: int = 0  # number of items in this subtree

    terminals: ta.Set[ta.Sequence[T]] = dc.field(default_factory=set)
    terminal_items: ta.Dict[ta.Sequence[T], ta.Sequence[T]] = dc.field(default_factory=dict)

    min_unique_prefix_len: int = dc.field(init=False)

    @property
    def terminal_count(self) -> int:
        return len(self.terminals)

    @dc.dataclass()
    class NonUniqueKeyError(Exception):
        key: ta.Any

    def lookup(self, prefix: ta.Sequence[T]) -> ta.Sequence[T]:
        try:
            return self._lookup(prefix)
        except MinUniquePrefixNode._NonUniqueKeyError:
            raise MinUniquePrefixNode.NonUniqueKeyError(prefix)  # noqa

    def __len__(self) -> int:
        return self.count

    def __iter__(self) -> ta.Iterator[ta.Sequence[T]]:
        yield from self.terminal_items.values()
        for child in self.children.values():
            yield from child

    #

    @staticmethod
    def _common_prefix_len(
            item: ta.Sequence[T],
            item_pos: int,
            part: ta.Sequence[T],
    ) -> int:
        n = min(len(item) - item_pos, len(part))
        i = 0
        while i < n and item[item_pos + i] == part[i]:
            i += 1
        return i

    def _match_child(
            self,
            item: ta.Sequence[T],
            item_pos: int,
    ) -> ta.Tuple[ta.Optional['MinUniquePrefixNode[T]'], int]:
        if item_pos == len(item):
            return None, 0

        child = self.children.get(item[item_pos])
        if child is None:
            return None, 0

        return child, self._common_prefix_len(item, item_pos, child.part)

    def _add_terminal(
            self,
            term: ta.Sequence[T],
            item: ta.Sequence[T],
    ) -> None:
        if term in self.terminal_items:
            raise ValueError('duplicate items present')

        self.terminals.add(term)
        self.terminal_items[term] = item

    def _set_min_unique_prefix_len(self, depth_before: int, *, is_root: bool) -> int:
        if self is is_root and self.count <= 1:
            ret = 0

        elif self.count == 1:
            ret = depth_before + 1

        else:
            child_depth_before = depth_before + len(self.part)
            ret = max(
                child._set_min_unique_prefix_len(child_depth_before, is_root=False)  # noqa
                for child in self.children.values()
            )

        self.min_unique_prefix_len = ret
        return ret

    class _NonUniqueKeyError(Exception):
        pass

    def _find_unique_terminal_item(self: 'MinUniquePrefixNode[T]') -> ta.Sequence[T]:
        cur = self

        while True:
            if cur.count != 1:
                raise MinUniquePrefixNode._NonUniqueKeyError

            if cur.terminal_items:
                if len(cur.terminal_items) != 1:
                    raise RuntimeError('invalid tree')
                return next(iter(cur.terminal_items.values()))

            if not cur.children:
                raise RuntimeError('invalid tree')

            if len(cur.children) != 1:
                raise RuntimeError('invalid tree')

            cur = next(iter(cur.children.values()))

    def _lookup(self, prefix: ta.Sequence[T]) -> ta.Sequence[T]:
        node = self
        pos = 0

        while True:
            common_len = self._common_prefix_len(prefix, pos, node.part)
            needed = min(len(prefix) - pos, len(node.part))
            if common_len != needed:
                raise KeyError(prefix)

            pos += common_len
            if pos == len(prefix):
                return node._find_unique_terminal_item()  # noqa

            child, _ = node._match_child(prefix, pos)  # noqa
            if child is None:
                raise KeyError(prefix)

            node = child


def build_min_unique_prefix_tree(
        items: ta.Sequence[ta.Sequence[T]],
        *,
        subsequence: ta.Optional[ta.Callable[[ta.Sequence[T]], ta.Sequence[T]]] = None,
) -> MinUniquePrefixNode[T]:
    if subsequence is None:
        subsequence = lambda x: x  # noqa

    root: MinUniquePrefixNode[T]

    if not items:
        root = MinUniquePrefixNode()
        root.min_unique_prefix_len = 0
        return root

    if len(items) == 1:
        part = subsequence(items[0])
        root = MinUniquePrefixNode(
            part=part,
            count=1,
        )
        root._add_terminal(part, items[0])  # noqa
        root.min_unique_prefix_len = 0
        return root

    root = MinUniquePrefixNode()

    for item in items:
        root.count += 1

        node = root
        pos = 0

        while True:
            if pos == len(item):
                node._add_terminal(node.part, item)  # noqa
                break

            child, common_len = node._match_child(item, pos)  # noqa
            if child is None:
                part = subsequence(item[pos:])
                new_child = MinUniquePrefixNode(
                    part=part,
                    count=1,
                )
                new_child._add_terminal(part, item)  # noqa
                node.children[part[0]] = new_child
                break

            if common_len == len(child.part):
                child.count += 1
                node = child
                pos += common_len
                continue

            if pos + common_len == len(item):
                child.count += 1
                child._add_terminal(child.part[:common_len], item)  # noqa
                break

            split = MinUniquePrefixNode(
                part=child.part[:common_len],
                count=child.count + 1,
            )
            node.children[item[pos]] = split

            old_terminals = child.terminals
            old_terminal_items = child.terminal_items

            child.terminals = set()
            child.terminal_items = {}

            child.part = child.part[common_len:]

            for term in old_terminals:
                old_item = old_terminal_items[term]
                if len(term) <= common_len:
                    split._add_terminal(term, old_item)  # noqa
                else:
                    child._add_terminal(term[common_len:], old_item)  # noqa

            split.children[child.part[0]] = child

            pos += common_len
            new_part = subsequence(item[pos:])
            new_child = MinUniquePrefixNode(
                part=new_part,
                count=1,
            )
            new_child._add_terminal(new_part, item)  # noqa
            split.children[new_part[0]] = new_child

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

    root._set_min_unique_prefix_len(0, is_root=True)  # noqa

    return root


##


def min_unique_prefix_lens(
        items: ta.Sequence[ta.Sequence[T]],
        *,
        subsequence: ta.Optional[ta.Callable[[ta.Sequence[T]], ta.Sequence[T]]] = None,
) -> ta.List[int]:
    if len(items) <= 1:
        return [0] * len(items)

    root = build_min_unique_prefix_tree(
        items,
        subsequence=subsequence,
    )

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


def min_unique_prefix_len(
        items: ta.Sequence[ta.Sequence[T]],
        *,
        subsequence: ta.Optional[ta.Callable[[ta.Sequence[T]], ta.Sequence[T]]] = None,
) -> int:
    if len(items) <= 1:
        return 0

    root = build_min_unique_prefix_tree(
        items,
        subsequence=subsequence,
    )

    return root.min_unique_prefix_len
