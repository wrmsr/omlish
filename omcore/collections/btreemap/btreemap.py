"""Persistent counted B+-ish search tree with dense leaves and opportunistic compaction."""
import typing as ta

from ... import lang
from ..intersections import PersistentSortedMapping
from ..iterators import HasNextIterator
from ..mappings import IterItemsViewMapping
from ..mappings import IterValuesViewMapping
from . import _btreemap_py as _backend


try:
    from . import _btreemap  # type: ignore
except ImportError:
    pass
else:
    _backend = _btreemap  # noqa


T = ta.TypeVar('T')
K = ta.TypeVar('K')
V = ta.TypeVar('V')


##


class _MISSING(lang.Marker):  # noqa
    pass


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

    @ta.overload
    def get(self, key: K, /) -> V | None: ...

    @ta.overload
    def get(self, key: K, /, default: V | T) -> V | T: ...

    def get(self, key, /, default=None):
        return self._backend.find_or(self._root, key, default, self._cmp)

    def __iter__(self) -> ta.Iterator[K]:
        return self._backend.iter_keys(self._root)

    def __contains__(self, item: K) -> bool:  # type: ignore[override]
        return self._backend.find_or(self._root, item, _MISSING, self._cmp) is not _MISSING

    def itervalues(self) -> ta.Iterator[V]:
        return self._backend.iter_values(self._root)

    def iteritems(self) -> HasNextIterator[tuple[K, V]]:
        return self._backend.iter(self._root)

    def items_desc(self) -> HasNextIterator[tuple[K, V]]:
        return self._backend.riter(self._root)

    def items_from(self, k: K) -> HasNextIterator[tuple[K, V]]:
        return self._backend.iter_from(self._root, k, self._cmp)

    def items_from_desc(self, k: K) -> HasNextIterator[tuple[K, V]]:
        return self._backend.riter_from(self._root, k, self._cmp)

    def with_(self, k: K, v: V) -> ta.Self:
        root = self._backend.insert(self._root, k, v, self._cmp)

        if root is self._root:
            return self

        return self.__class__(
            _root=root,
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
        if self._backend.find_or(self._root, k, _MISSING, self._cmp) is not _MISSING:
            return self

        return self.with_(k, v)


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
