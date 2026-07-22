import typing as ta

from .. import lang


with lang.auto_proxy_import(globals()):
    from . import skiplist
    from .btreemap import btreemap
    from .btreeseq import btreeseq
    from .hamt import hamtmap


if ta.TYPE_CHECKING:
    from .intersections import PersistentSortedMapping
    from .persistent import PersistentMapping
    from .persistent import PersistentSequence
    from .sorted import SortedMapping
    from .sorted import SortedMutableMapping


##


def new_persistent_seq[T](
        items: ta.Iterable[T] | None = None,
) -> PersistentSequence[T]:
    return btreeseq.new_btree_seq(items)


##


def new_persistent_map[K, V](
        items: ta.Iterable[tuple[K, V]] | None = None,
) -> PersistentMapping[K, V]:
    if hamtmap.is_hamt_available():
        return hamtmap.new_hamt_map(items)
    else:
        return btreemap.new_btree_map(items, cmp=lang.hash_eq_id_cmp)


#


def new_sorted_map[K, V](
        items: ta.Iterable[tuple[K, V]] | None = None,
) -> SortedMapping[K, V]:
    return btreemap.new_btree_map(items)


def new_sorted_mutable_map[K, V](
        items: ta.Iterable[tuple[K, V]] | None = None,
) -> SortedMutableMapping[K, V]:
    return skiplist.SkipListDict(items)


#


def new_persistent_sorted_map[K, V](
        items: ta.Iterable[tuple[K, V]] | None = None,
) -> PersistentSortedMapping[K, V]:
    return btreemap.new_btree_map(items)
