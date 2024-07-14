import typing as ta

from .. import iterables as it
from .base import BatchedIterableKeyValue
from .base import BatchedKeyValue
from .base import BatchedSortedIterableKeyValue
from .base import NOT_SET
from .iterators import ManagedIterator
from .wrappers import WrapperIterableKeyValue
from .wrappers import WrapperKeyValue
from .wrappers import WrapperSortedIterableKeyValue


T = ta.TypeVar('T')
K = ta.TypeVar('K')
V = ta.TypeVar('V')

KOrNotSet = ta.Union[K, ta.Type[NOT_SET]]
VOrNotSet = ta.Union[V, ta.Type[NOT_SET]]


class StubBatchedKeyValue(
    WrapperKeyValue[K, V],
    BatchedKeyValue[K, V]
):

    def get_item_batch(self, keys: ta.Iterable[K], default: VOrNotSet = NOT_SET) -> ta.Iterable[V]:
        ret = []
        for k in keys:
            try:
                ret.append(self._wrapped[k])
            except KeyError:
                if default is not NOT_SET:
                    ret.append(default)
                else:
                    raise
        return ret

    def set_item_batch(self, items: ta.Iterable[ta.Tuple[K, V]]) -> None:
        for k, v in items:
            self._wrapped[k] = v

    def del_item_batch(self, keys: ta.Iterable[K], ignore_missing: bool = False) -> None:
        for k in keys:
            try:
                del self._wrapped[k]
            except KeyError:
                if not ignore_missing:
                    raise


class StubManagedIterator(ManagedIterator[T]):

    def __init__(self, wrapped: ta.Iterator[T]) -> None:
        super().__init__()

        self._wrapped = self.__wrapped__ = wrapped

    def __next__(self) -> T:
        return self._wrapped.__next__()


class StubBatchedIterableKeyValue(
    WrapperIterableKeyValue[K, V],
    StubBatchedKeyValue[K, V],
    BatchedIterableKeyValue[K, V]
):

    def iter_key_batches(self, size: int) -> ManagedIterator[ta.Iterable[K]]:
        return StubManagedIterator(iter(it.chunk(size)(self._wrapped.iter_keys())))


class StubBatchedSortedIterableKeyValue(
    WrapperSortedIterableKeyValue[K, V],
    StubBatchedIterableKeyValue[K, V],
    BatchedSortedIterableKeyValue[K, V]
):

    def sorted_iter_key_batches(self, size: int, start: KOrNotSet = NOT_SET) -> ManagedIterator[ta.Iterable[K]]:
        return StubManagedIterator(iter(it.chunk(size)(self._wrapped.sorted_iter_keys(start))))

    def reverse_sorted_iter_key_batches(self, size: int, start: KOrNotSet = NOT_SET) -> ManagedIterator[ta.Iterable[K]]:
        return StubManagedIterator(iter(it.chunk(size)(self._wrapped.reverse_sorted_iter_keys(start))))
