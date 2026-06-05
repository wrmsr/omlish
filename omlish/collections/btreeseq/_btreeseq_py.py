import typing as ta

from ... import dataclasses as dc
from ... import lang


T = ta.TypeVar('T')

Node: ta.TypeAlias = ta.Union['_Leaf[T]', '_Branch[T]']


##


MAX_LEAF_LEN = 32
MAX_BRANCH_LEN = 32


class _MISSING(lang.Marker):  # noqa
    pass


@dc.dataclass(frozen=True, slots=True)
class _Leaf(ta.Generic[T]):
    items: tuple[T, ...]
    count: int
    height: int = 0


@dc.dataclass(frozen=True, slots=True)
class _Branch(ta.Generic[T]):
    children: tuple[Node[T], ...]
    counts: tuple[int, ...]
    count: int
    height: int


def _make_leaf(items: tuple[T, ...]) -> Node[T] | None:
    if not items:
        return None

    return _Leaf(
        items=items,
        count=len(items),
    )


def _make_branch_raw(children: tuple[Node[T], ...]) -> Node[T] | None:
    if not children:
        return None

    if len(children) == 1:
        return children[0]

    return _Branch(
        children=children,
        counts=tuple(c.count for c in children),
        count=sum(c.count for c in children),
        height=1 + max(c.height for c in children),
    )


def _can_merge(a: Node[T], b: Node[T]) -> bool:
    if isinstance(a, _Leaf) and isinstance(b, _Leaf):
        return len(a.items) + len(b.items) <= MAX_LEAF_LEN

    if isinstance(a, _Branch) and isinstance(b, _Branch):
        return len(a.children) + len(b.children) <= MAX_BRANCH_LEN

    return False


def _merge(a: Node[T], b: Node[T]) -> Node[T]:
    if isinstance(a, _Leaf) and isinstance(b, _Leaf):
        return ta.cast('Node[T]', _make_leaf(a.items + b.items))

    if isinstance(a, _Branch) and isinstance(b, _Branch):
        return ta.cast('Node[T]', _make_branch_raw(a.children + b.children))

    raise TypeError((a, b))


def _compact_children(children: tuple[Node[T], ...]) -> tuple[Node[T], ...]:
    out: list[Node[T]] = []

    for child in children:
        if out and _can_merge(out[-1], child):
            out[-1] = _merge(out[-1], child)
        else:
            out.append(child)

    return tuple(out)


def _pack_children(children: tuple[Node[T], ...]) -> Node[T] | None:
    children = _compact_children(tuple(c for c in children if c.count))

    if not children:
        return None

    if len(children) <= MAX_BRANCH_LEN:
        return _make_branch_raw(children)

    groups = tuple(
        ta.cast('Node[T]', _make_branch_raw(children[i:i + MAX_BRANCH_LEN]))
        for i in range(0, len(children), MAX_BRANCH_LEN)
    )

    return _pack_children(groups)


def _concat(a: Node[T] | None, b: Node[T] | None) -> Node[T] | None:
    if a is None:
        return b

    if b is None:
        return a

    if isinstance(a, _Leaf) and isinstance(b, _Leaf) and len(a.items) + len(b.items) <= MAX_LEAF_LEN:
        return _make_leaf(a.items + b.items)

    left = a.children if isinstance(a, _Branch) else (a,)
    right = b.children if isinstance(b, _Branch) else (b,)

    return _pack_children(left + right)


def _find_child(n: _Branch[T], idx: int) -> tuple[int, int]:
    base = 0

    for i, count in enumerate(n.counts):
        nxt = base + count

        if idx < nxt:
            return i, idx - base

        base = nxt

    raise IndexError(idx)


def _get(n: Node[T], idx: int) -> T:
    while isinstance(n, _Branch):
        child_idx, idx = _find_child(n, idx)
        n = n.children[child_idx]

    return n.items[idx]


def _iter_items(n: Node[T] | None) -> ta.Iterator[T]:
    if n is None:
        return

    if isinstance(n, _Leaf):
        yield from n.items
        return

    for child in n.children:
        yield from _iter_items(child)


def _split(n: Node[T] | None, idx: int) -> tuple[Node[T] | None, Node[T] | None]:
    if n is None:
        return None, None

    if idx <= 0:
        return None, n

    if idx >= n.count:
        return n, None

    if isinstance(n, _Leaf):
        return (
            _make_leaf(n.items[:idx]),
            _make_leaf(n.items[idx:]),
        )

    left_children: list[Node[T]] = []
    right_children: list[Node[T]] = []

    base = 0
    done = False

    for child in n.children:
        nxt = base + child.count

        if done:
            right_children.append(child)

        elif idx <= base:
            right_children.append(child)

        elif idx >= nxt:
            left_children.append(child)

        else:
            left, right = _split(child, idx - base)

            if left is not None:
                left_children.append(left)

            if right is not None:
                right_children.append(right)

            done = True

        base = nxt

    return (
        _pack_children(tuple(left_children)),
        _pack_children(tuple(right_children)),
    )


def _slice(n: Node[T] | None, start: int, stop: int) -> Node[T] | None:
    if n is None or start == stop:
        return None

    _, rest = _split(n, start)
    mid, _ = _split(rest, stop - start)

    return mid


def _replace_same(
        n: Node[T],
        start: int,
        items: tuple[T, ...],
) -> Node[T]:
    if not items:
        return n

    if isinstance(n, _Leaf):
        stop = start + len(items)

        return ta.cast('Node[T]', _make_leaf(n.items[:start] + items + n.items[stop:]))

    children = list(n.children)
    end = start + len(items)
    base = 0
    item_base = 0

    for i, child in enumerate(n.children):
        nxt = base + child.count

        if nxt <= start:
            base = nxt
            continue

        if base >= end:
            break

        child_start = max(start, base) - base
        child_stop = min(end, nxt) - base
        item_stop = item_base + (child_stop - child_start)

        children[i] = _replace_same(
            child,
            child_start,
            items[item_base:item_stop],
        )

        item_base = item_stop
        base = nxt

    return ta.cast('Node[T]', _make_branch_raw(tuple(children)))


def _splice(
        n: Node[T] | None,
        start: int,
        stop: int,
        items: tuple[T, ...],
) -> Node[T] | None:
    remove_len = stop - start

    if n is None:
        return from_iterable(items)

    if remove_len == len(items):
        if remove_len == 0:
            return n

        return _replace_same(n, start, items)

    left, rest = _split(n, start)
    _, right = _split(rest, remove_len)
    mid = from_iterable(items)

    return _concat(_concat(left, mid), right)


##


class BtreeSeqIterator(ta.Iterator[T], ta.Generic[T]):
    __slots__ = ('_it', '_next')

    def __init__(self, root: Node[T] | None) -> None:
        super().__init__()

        self._it = _iter_items(root)
        self._next: ta.Any = _MISSING

    def __iter__(self) -> ta.Self:
        return self

    def __next__(self) -> T:
        return self.next()

    def has_next(self) -> bool:
        if self._next is not _MISSING:
            return True

        try:
            self._next = next(self._it)
        except StopIteration:
            return False

        return True

    def next(self) -> T:
        if self._next is not _MISSING:
            ret = self._next
            self._next = _MISSING
            return ret

        return next(self._it)


##


def from_iterable(items: ta.Iterable[T]) -> Node[T] | None:
    leaves: list[Node[T]] = []
    cur: list[T] = []

    for item in items:
        cur.append(item)

        if len(cur) >= MAX_LEAF_LEN:
            leaves.append(ta.cast('Node[T]', _make_leaf(tuple(cur))))
            cur.clear()

    if cur:
        leaves.append(ta.cast('Node[T]', _make_leaf(tuple(cur))))

    return _pack_children(tuple(leaves))


def len_(root: Node[T] | None) -> int:
    return root.count if root is not None else 0


def get(root: Node[T] | None, idx: int) -> T:
    if root is None:
        raise IndexError(idx)

    return _get(root, idx)


def iter(root: Node[T] | None) -> BtreeSeqIterator[T]:  # noqa
    return BtreeSeqIterator(root)


def slice(root: Node[T] | None, start: int, stop: int):  # noqa
    return _slice(root, start, stop)


def splice(
        root: Node[T] | None,
        start: int,
        stop: int,
        items: ta.Iterable[T],
):
    return _splice(root, start, stop, tuple(items))
