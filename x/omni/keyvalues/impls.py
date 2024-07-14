"""
TODO:
 - sqlite
 - dbapi/sqla
 - dbm (.dumb)
 - python-rocksdb
 - leveldb
 - lmdb
 - redis
 - router
"""
import operator
import typing as ta

from .. import collections as ocol
from .base import IterableKeyValue
from .base import NOT_SET
from .base import SortedIterableKeyValue
from .iterators import ManagedIterator
from .stubs import StubManagedIterator


K = ta.TypeVar('K')
V = ta.TypeVar('V')

KOrNotSet = ta.Union[K, ta.Type[NOT_SET]]
VOrNotSet = ta.Union[V, ta.Type[NOT_SET]]


class MappingKeyValue(IterableKeyValue[K, V]):

    def __init__(self, mapping: ta.Optional[ta.MutableMapping[K, V]] = None) -> None:
        super().__init__()

        if mapping is None:
            mapping = {}
        self._mapping = mapping

    def __getitem__(self, key: K) -> V:
        return self._mapping[key]

    def __setitem__(self, key: K, value: V) -> None:
        self._mapping[key] = value

    def __delitem__(self, key: K) -> None:
        del self._mapping[key]

    def iter_keys(self) -> ManagedIterator[K]:
        return StubManagedIterator(iter(self._mapping.keys()))


class SortedMappingKeyValue(MappingKeyValue[K, V], SortedIterableKeyValue[K, V]):

    _mapping: ocol.SortedMutableMapping[K, V]

    def __init__(self, mapping: ta.Optional[ocol.SortedMutableMapping[K, V]] = None) -> None:
        if mapping is None:
            mapping = ocol.SkipListDict()
        super().__init__(mapping)

    def sorted_iter_keys(self, start: KOrNotSet = NOT_SET) -> ManagedIterator[K]:
        items = self._mapping.items() if start is NOT_SET else self._mapping.itemsfrom(start)
        return StubManagedIterator(iter(map(operator.itemgetter(0), items)))

    def reverse_sorted_iter_keys(self, start: KOrNotSet = NOT_SET) -> ManagedIterator[K]:
        items = self._mapping.ritems() if start is NOT_SET else self._mapping.ritemsfrom(start)
        return StubManagedIterator(iter(map(operator.itemgetter(0), items)))
