import typing as ta


K = ta.TypeVar('K')
V = ta.TypeVar('V')
K2 = ta.TypeVar('K2')
V2 = ta.TypeVar('V2')


##


class Trie(ta.MutableMapping[ta.Sequence[K], V], ta.Generic[K, V]):
    class Node(ta.Generic[K2, V2]):
        def __init__(self) -> None:
            self._children: dict[K2, Trie.Node[K2, V2]] = {}

        _value: V2

        def __init_subclass__(cls, **kwargs):
            raise TypeError

        @property
        def has_value(self) -> bool:
            try:
                self._value  # noqa
            except AttributeError:
                return False
            else:
                return True

        @property
        def value(self) -> V2:
            return self._value

        @property
        def children(self) -> ta.Mapping[K2, 'Trie.Node[K2, V2]']:
            return self._children

    def __init__(self) -> None:
        super().__init__()

        self._len = 0
        self._root: Trie.Node[K, V] = Trie.Node()

    def __len__(self) -> int:
        return self._len

    def get_node(self, k: ta.Iterable[K]) -> Node[K, V]:
        cur = self._root
        for x in k:
            cur = cur._children[x]  # noqa
        return cur

    def __getitem__(self, k: ta.Iterable[K]) -> V:
        node = self.get_node(k)
        try:
            return node.value
        except AttributeError:
            raise KeyError(k) from None

    def __setitem__(self, k: ta.Iterable[K], v: V) -> None:
        cur = self._root
        for x in k:
            try:
                cur = cur._children[x]  # noqa
            except KeyError:
                nxt: Trie.Node[K, V] = Trie.Node()
                cur._children[x] = nxt  # noqa
                cur = nxt

        try:
            cur._value  # noqa
        except AttributeError:
            self._len += 1
        cur._value = v  # noqa

    def __delitem__(self, k: ta.Iterable[K]) -> None:
        stack: list[tuple[K, Trie.Node[K, V]]] = []
        cur = self._root
        for x in k:
            stack.append((x, cur))
            cur = cur._children[x]  # noqa

        try:
            del cur._value  # noqa
        except AttributeError:
            raise KeyError(k) from None

        self._len -= 1
        for x, parent in reversed(stack):
            if cur.has_value or cur._children:  # noqa
                break
            del parent._children[x]  # noqa
            cur = parent

    def iter_nodes(self, *, share_key: bool = False) -> ta.Iterator[tuple[ta.Sequence[K], Node[K, V]]]:
        key: list[K] = []
        stack: list[tuple[Trie.Node[K, V], ta.Iterator[tuple[K, Trie.Node[K, V]]]]] = []

        stack.append((self._root, iter(self._root._children.items())))  # noqa
        yield (key if share_key else tuple(key), self._root)

        while stack:
            node, it = stack[-1]

            try:
                k, c = next(it)
            except StopIteration:
                stack.pop()
                if stack:
                    key.pop()
                continue
            key.append(k)

            stack.append((c, iter(c._children.items())))  # noqa
            yield (key if share_key else tuple(key), c)

    def iter_items(self, *, share_key: bool = False) -> ta.Iterator[tuple[ta.Sequence[K], V]]:
        for k, node in self.iter_nodes(share_key=share_key):
            try:
                yield (k, node._value)  # noqa
            except AttributeError:
                pass

    def __iter__(self) -> ta.Iterator[ta.Sequence[K]]:
        for k, _ in self.iter_items():
            yield k
