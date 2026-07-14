"""Persistent counted B+-ish search tree with dense leaves and opportunistic compaction."""
import typing as ta

from ..intersections import PersistentSortedMapping
from ..iterators import HasNextIterator
from ..mappings import IterItemsViewMapping
from ..mappings import IterValuesViewMapping
from ..mappings import iteritems_itervalues
from ..mappings import map_contains
from . import _btreemap_py as _backend


try:
    from . import _btreemap  # type: ignore
except ImportError:
    pass
else:
    _backend = _btreemap  # noqa


K = ta.TypeVar('K')
V = ta.TypeVar('V')


##


class BtreeMap(
    IterValuesViewMapping[K, V],
    IterItemsViewMapping[K, V],
    PersistentSortedMapping[K, V],
    ta.Mapping[K, V],
    ta.Generic[K, V],
):
    __slots__ = ('_root', '_cmp')

    def __init__(
            self,
            *,
            _root: ta.Any,
            _cmp: ta.Callable[[K, K], int] | None,
    ) -> None:
        super().__init__()

        self._root = _root
        self._cmp = _cmp

    _backend: ta.Final = _backend

    @property
    def debug(self) -> ta.Mapping[K, V]:
        return dict(self)

    def __len__(self) -> int:
        return self._backend.len_(self._root)

    def __getitem__(self, item: K) -> V:
        return self._backend.find(self._root, item, self._cmp)

    def __iter__(self) -> ta.Iterator[K]:
        for k, _ in self.iteritems():
            yield k

    __contains__ = map_contains

    itervalues = iteritems_itervalues

    def iteritems(self) -> HasNextIterator[tuple[K, V]]:
        return self._backend.iter(self._root)

    def items_desc(self) -> HasNextIterator[tuple[K, V]]:
        return self._backend.riter(self._root)

    def items_from(self, k: K) -> HasNextIterator[tuple[K, V]]:
        return self._backend.iter_from(self._root, k, self._cmp)

    def items_from_desc(self, k: K) -> HasNextIterator[tuple[K, V]]:
        return self._backend.riter_from(self._root, k, self._cmp)

    def with_(self, k: K, v: V) -> ta.Self:
        return self.__class__(
            _root=self._backend.insert(self._root, k, v, self._cmp),
            _cmp=self._cmp,
        )

    def without(self, k: K) -> ta.Self:
        root = self._backend.delete(self._root, k, self._cmp)

        if root is self._root:
            return self

        return self.__class__(
            _root=root,
            _cmp=self._cmp,
        )

    def default(self, k: K, v: V) -> ta.Self:
        try:
            self[k]  # noqa
        except KeyError:
            return self.with_(k, v)
        else:
            return self


def new_btree_map(
        items: ta.Iterable[tuple[K, V]] | None = None,
        *,
        cmp: ta.Callable[[K, K], int] | None = None,
) -> BtreeMap[K, V]:
    m: BtreeMap[K, V] = BtreeMap(
        _root=None,
        _cmp=cmp,
    )

    if items is not None:
        for k, v in items:
            m = m.with_(k, v)

    return m
