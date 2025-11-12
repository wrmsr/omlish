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

    def __init__(self, items: ta.Iterable[tuple[ta.Iterable[K], V]] | None = None) -> None:
        super().__init__()

        self._len = 0
        self._root: Trie.Node[K, V] = Trie.Node()

        if items is not None:
            for k, v in items:
                self[k] = v

    @property
    def root(self) -> Node[K, V]:
        return self._root

    def __len__(self) -> int:
        return self._len

    def get_node(self, k: ta.Iterable[K]) -> Node[K, V]:
        cur = self._root
        for x in k:
            cur = cur._children[x]  # noqa
        return cur

    def __getitem__(self, k: ta.Iterable[K]) -> V:
        try:
            node = self.get_node(k)
        except KeyError:
            raise KeyError(k) from None

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

    def iter_nodes(
            self,
            *,
            share_key: bool = False,
            root: ta.Optional['Trie.Node[K, V]'] = None,
            sort_children: bool | ta.Callable[[list[tuple[K, Node[K, V]]]], None] = False,
    ) -> ta.Iterator[tuple[ta.Sequence[K], Node[K, V]]]:
        if root is None:
            root = self._root

        ic: ta.Callable[[ta.Mapping[K, Trie.Node[K, V]]], ta.Iterator[tuple[K, Trie.Node[K, V]]]]
        if sort_children is True:
            ic = lambda cd: iter(sorted(cd.items(), key=lambda t: t[0]))  # type: ignore
        elif sort_children is False:
            ic = lambda cd: iter(cd.items())
        else:
            def ic(cd):
                il = list(cd.items())
                sort_children(il)
                return iter(il)

        key: list[K] = []
        stack: list[tuple[Trie.Node[K, V], ta.Iterator[tuple[K, Trie.Node[K, V]]]]] = []

        stack.append((root, ic(root._children)))  # noqa
        yield (key if share_key else tuple(key), root)

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

            stack.append((c, ic(c._children)))  # noqa
            yield (key if share_key else tuple(key), c)

    def iteritems(self, **kwargs: ta.Any) -> ta.Iterator[tuple[ta.Sequence[K], V]]:
        for k, node in self.iter_nodes(**kwargs):
            try:
                yield (k, node._value)  # noqa
            except AttributeError:
                pass

    def __iter__(self) -> ta.Iterator[ta.Sequence[K]]:
        for k, _ in self.iteritems():
            yield k
