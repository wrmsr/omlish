import typing as ta

from .. import lang


with lang.auto_proxy_import(globals()):
    from . import skiplist
    from .hamt import hamtmap
    from .treap import treapmap


if ta.TYPE_CHECKING:
    from .intersections import PersistentSortedMapping
    from .persistent import PersistentMapping
    from .sorted import SortedMapping
    from .sorted import SortedMutableMapping


K = ta.TypeVar('K')
V = ta.TypeVar('V')


##


def new_persistent_map(
        items: ta.Iterable[tuple[K, V]] | None = None,
) -> 'PersistentMapping[K, V]':
    if hamtmap.is_hamt_available():
        return hamtmap.new_hamt_map(items)
    else:
        return treapmap.new_treap_map(items)


#


def new_sorted_map(
        items: ta.Iterable[tuple[K, V]] | None = None,
) -> 'SortedMapping[K, V]':
    return treapmap.new_treap_map(items)


def new_sorted_mutable_map(
        items: ta.Iterable[tuple[K, V]] | None = None,
) -> 'SortedMutableMapping[K, V]':
    return skiplist.SkipListDict(items)


#


def new_persistent_sorted_map(
        items: ta.Iterable[tuple[K, V]] | None = None,
) -> 'PersistentSortedMapping[K, V]':
    return treapmap.new_treap_map(items)
