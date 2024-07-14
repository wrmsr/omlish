import typing as ta

from .base import BatchedIterableKeyValue
from .base import BatchedKeyValue
from .base import BatchedSortedIterableKeyValue
from .base import IterableKeyValue
from .base import KeyValue
from .base import NOT_SET
from .base import SortedIterableKeyValue
from .iterators import ManagedIterator


K = ta.TypeVar('K')
V = ta.TypeVar('V')

KOrNotSet = ta.Union[K, ta.Type[NOT_SET]]
VOrNotSet = ta.Union[V, ta.Type[NOT_SET]]


class WrapperKeyValue(
    KeyValue[K, V]
):

    def __init__(self, wrapped: KeyValue[K, V]) -> None:
        super().__init__()

        self._wrapped = self.__wrapped__ = wrapped

    def __getitem__(self, key: K) -> V:
        return self._wrapped[key]

    def __setitem__(self, key: K, value: V) -> None:
        self._wrapped[key] = value

    def __delitem__(self, key: K) -> None:
        del self._wrapped[key]


class WrapperBatchedKeyValue(
    WrapperKeyValue[K, V],
    BatchedKeyValue[K, V]
):

    _wrapped: BatchedKeyValue[K, V]

    def __init__(self, wrapped: BatchedKeyValue[K, V]) -> None:
        super().__init__(wrapped)

    def get_item_batch(self, keys: ta.Iterable[K], default: KOrNotSet = NOT_SET) -> ta.Iterable[V]:
        return self._wrapped.get_item_batch(keys, default)

    def set_item_batch(self, items: ta.Iterable[ta.Tuple[K, V]]) -> None:
        self._wrapped.set_item_batch(items)

    def del_item_batch(self, keys: ta.Iterable[K], ignore_missing: bool = False) -> None:
        self._wrapped.del_item_batch(keys, ignore_missing)


class WrapperIterableKeyValue(
    WrapperKeyValue[K, V],
    IterableKeyValue[K, V]
):

    _wrapped: IterableKeyValue[K, V]

    def __init__(self, wrapped: IterableKeyValue[K, V]) -> None:
        super().__init__(wrapped)

    def iter_keys(self) -> ManagedIterator[K]:
        return self._wrapped.iter_keys()


class WrapperBatchedIterableKeyValue(
    WrapperIterableKeyValue[K, V],
    BatchedIterableKeyValue[K, V]
):

    _wrapped: BatchedIterableKeyValue[K, V]

    def __init__(self, wrapped: BatchedIterableKeyValue[K, V]) -> None:
        super().__init__(wrapped)

    def iter_key_batches(self, size: int) -> ManagedIterator[ta.Iterable[K]]:
        return self._wrapped.iter_key_batches(size)

    def get_item_batch(self, keys: ta.Iterable[K], default: VOrNotSet = NOT_SET) -> ta.Iterable[V]:
        return self._wrapped.get_item_batch(keys, default)

    def set_item_batch(self, items: ta.Iterable[ta.Tuple[K, V]]) -> None:
        self._wrapped.set_item_batch(items)

    def del_item_batch(self, keys: ta.Iterable[K], ignore_missing: bool = False) -> None:
        self._wrapped.del_item_batch(keys, ignore_missing)


class WrapperSortedIterableKeyValue(
    WrapperIterableKeyValue[K, V],
    SortedIterableKeyValue[K, V]
):

    _wrapped: SortedIterableKeyValue[K, V]

    def __init__(self, wrapped: SortedIterableKeyValue[K, V]) -> None:
        super().__init__(wrapped)

    def sorted_iter_keys(self, start: KOrNotSet = NOT_SET) -> ManagedIterator[K]:
        return self._wrapped.sorted_iter_keys(start)

    def reverse_sorted_iter_keys(self, start: KOrNotSet = NOT_SET) -> ManagedIterator[K]:
        return self._wrapped.reverse_sorted_iter_keys(start)


class WrapperBatchedSortedIterableKeyValue(
    WrapperBatchedIterableKeyValue[K, V],
    WrapperSortedIterableKeyValue[K, V],
    BatchedSortedIterableKeyValue[K, V]
):

    _wrapped: BatchedSortedIterableKeyValue[K, V]

    def __init__(self, wrapped: SortedIterableKeyValue[K, V]) -> None:
        super().__init__(wrapped)

    def sorted_iter_key_batches(self, size: int, start: KOrNotSet = NOT_SET) -> ManagedIterator[ta.Iterable[K]]:
        return self._wrapped.sorted_iter_key_batches(size, start)

    def reverse_sorted_iter_key_batches(self, size: int, start: KOrNotSet = NOT_SET) -> ManagedIterator[ta.Iterable[K]]:
        return self._wrapped.reverse_sorted_iter_key_batches(size, start)
