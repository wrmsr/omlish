"""
TODO:
 - integrate further with colls
 - intersection types?
"""
import abc
import typing as ta

from .. import lang
from .iterators import ManagedIterator


class NOT_SET(lang.Marker):
    pass


K = ta.TypeVar('K')
V = ta.TypeVar('V')

KOrNotSet = ta.Union[K, ta.Type[NOT_SET]]
VOrNotSet = ta.Union[V, ta.Type[NOT_SET]]


class KeyValue(lang.Abstract, lang.ContextManaged, ta.Generic[K, V]):

    @abc.abstractmethod
    def __getitem__(self, key: K) -> V:
        raise NotImplementedError

    @abc.abstractmethod
    def __setitem__(self, key: K, value: V) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def __delitem__(self, key: K) -> None:
        raise NotImplementedError


class BatchedKeyValue(KeyValue[K, V], lang.Abstract):

    @abc.abstractmethod
    def get_item_batch(self, keys: ta.Iterable[K], default: VOrNotSet = NOT_SET) -> ta.Iterable[V]:
        raise NotImplementedError

    @abc.abstractmethod
    def set_item_batch(self, items: ta.Iterable[ta.Tuple[K, V]]) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def del_item_batch(self, keys: ta.Iterable[K], ignore_missing: bool = False) -> None:
        raise NotImplementedError


class IterableKeyValue(KeyValue[K, V], lang.Abstract):

    @abc.abstractmethod
    def iter_keys(self) -> ManagedIterator[K]:
        raise NotImplementedError


class BatchedIterableKeyValue(BatchedKeyValue[K, V], IterableKeyValue[K, V], lang.Abstract):

    @abc.abstractmethod
    def iter_key_batches(self, size: int) -> ManagedIterator[ta.Iterable[K]]:
        raise NotImplementedError


class SortedIterableKeyValue(IterableKeyValue[K, V], lang.Abstract):

    @abc.abstractmethod
    def sorted_iter_keys(self, start: KOrNotSet = NOT_SET) -> ManagedIterator[K]:
        raise NotImplementedError

    @abc.abstractmethod
    def reverse_sorted_iter_keys(self, start: KOrNotSet = NOT_SET) -> ManagedIterator[K]:
        raise NotImplementedError


class BatchedSortedIterableKeyValue(BatchedIterableKeyValue[K, V], SortedIterableKeyValue[K, V], lang.Abstract):

    @abc.abstractmethod
    def sorted_iter_key_batches(self, size: int, start: KOrNotSet = NOT_SET) -> ManagedIterator[ta.Iterable[K]]:
        raise NotImplementedError

    @abc.abstractmethod
    def reverse_sorted_iter_key_batches(self, size: int, start: KOrNotSet = NOT_SET) -> ManagedIterator[ta.Iterable[K]]:
        raise NotImplementedError
