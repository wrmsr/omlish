import typing as ta

from .. import codecs as cod
from .base import KeyValue
from .base import NOT_SET
from .iterators import ManagedIterator
from .iterators import TransformedManagedIterator
from .wrappers import WrapperBatchedIterableKeyValue
from .wrappers import WrapperBatchedKeyValue
from .wrappers import WrapperBatchedSortedIterableKeyValue
from .wrappers import WrapperIterableKeyValue
from .wrappers import WrapperKeyValue
from .wrappers import WrapperSortedIterableKeyValue


K = ta.TypeVar('K')
FK = ta.TypeVar('FK')
TK = ta.TypeVar('TK')

V = ta.TypeVar('V')
FV = ta.TypeVar('FV')
TV = ta.TypeVar('TV')

KOrNotSet = ta.Union[K, ta.Type[NOT_SET]]
VOrNotSet = ta.Union[V, ta.Type[NOT_SET]]


class KeyCodecKeyValue(
    WrapperKeyValue[FK, V],
    ta.Generic[FK, TK, V]
):

    def __init__(self, codec: cod.Codec[FK, TK], wrapped: KeyValue[TK, V]) -> None:
        super().__init__(wrapped)

        self._codec = codec

    def __getitem__(self, key: FK) -> V:
        return super().__getitem__(self._codec.encode(key))

    def __setitem__(self, key: FK, value: V) -> None:
        super().__setitem__(self._codec.encode(key), value)

    def __delitem__(self, key: FK) -> None:
        super().__delitem__(self._codec.encode(key))


class KeyCodecBatchedKeyValue(
    KeyCodecKeyValue[FK, TK, V],
    WrapperBatchedKeyValue[FK, V],
    ta.Generic[FK, TK, V]
):

    def get_item_batch(self, keys: ta.Iterable[FK], default: VOrNotSet = NOT_SET) -> ta.Iterable[V]:
        return super().get_item_batch(map(self._codec.encode, keys), default)

    def set_item_batch(self, items: ta.Iterable[ta.Tuple[FK, V]]) -> None:
        super().set_item_batch((self._codec.enode(key), value) for key, value in items)

    def del_item_batch(self, keys: ta.Iterable[FK], ignore_missing: bool = False) -> None:
        super().del_item_batch(map(self._codec.encode, keys), ignore_missing)


class KeyCodecIterableKeyValue(
    KeyCodecKeyValue[FK, TK, V],
    WrapperIterableKeyValue[FK, V],
    ta.Generic[FK, TK, V]
):

    def iter_keys(self) -> ManagedIterator[K]:
        return TransformedManagedIterator(lambda it: map(self._codec.decode, it), super().iter_keys())


class KeyCodecBatchedIterableKeyValue(
    KeyCodecBatchedKeyValue[FK, TK, V],
    KeyCodecIterableKeyValue[FK, TK, V],
    WrapperBatchedIterableKeyValue[FK, V],
    ta.Generic[FK, TK, V]
):

    def iter_key_batches(self, size: int) -> ManagedIterator[ta.Iterable[K]]:
        return TransformedManagedIterator(lambda it: (map(self._codec.decode, batch) for batch in it), super().iter_key_batches(size))  # noqa


class KeyCodecSortedIterableKeyValue(
    KeyCodecIterableKeyValue[FK, TK, V],
    WrapperSortedIterableKeyValue[FK, V],
    ta.Generic[FK, TK, V]
):

    def sorted_iter_keys(self, start: KOrNotSet = NOT_SET) -> ManagedIterator[K]:
        if start is not NOT_SET:
            start = self._codec.encode(start)
        return TransformedManagedIterator(lambda it: map(self._codec.decode, it), super().sorted_iter_keys(start))

    def reverse_sorted_iter_keys(self, start: KOrNotSet = NOT_SET) -> ManagedIterator[K]:
        if start is not NOT_SET:
            start = self._codec.encode(start)
        return TransformedManagedIterator(lambda it: map(self._codec.decode, it), super().reverse_sorted_iter_keys(start))  # noqa


class KeyCodecBatchedSortedIterableKeyValue(
    KeyCodecBatchedIterableKeyValue[FK, TK, V],
    KeyCodecSortedIterableKeyValue[FK, TK, V],
    WrapperBatchedSortedIterableKeyValue[FK, V],
    ta.Generic[FK, TK, V]
):

    def sorted_iter_key_batches(self, size: int, start: KOrNotSet = NOT_SET) -> ManagedIterator[K]:
        if start is not NOT_SET:
            start = self._codec.encode(start)
        return TransformedManagedIterator(lambda it: (map(self._codec.decode, batch) for batch in it), super().sorted_iter_keys(start))  # noqa

    def reverse_sorted_iter_key_batches(self, size: int, start: KOrNotSet = NOT_SET) -> ManagedIterator[K]:
        if start is not NOT_SET:
            start = self._codec.encode(start)
        return TransformedManagedIterator(lambda it: (map(self._codec.decode, batch) for batch in it), super().reverse_sorted_iter_keys(start))  # noqa


class ValueCodecKeyValue(
    WrapperKeyValue[K, FV],
    ta.Generic[K, FV, TV]
):

    def __init__(self, codec: cod.Codec[FK, TK], wrapped: KeyValue[TK, V]) -> None:
        super().__init__(wrapped)

        self._codec = codec

    def __getitem__(self, key: K) -> V:
        return self._codec.decode(super().__getitem__(key))

    def __setitem__(self, key: FK, value: V) -> None:
        super().__setitem__(key, self._codec.encode(value))


class ValueCodecBatchedKeyValue(
    ValueCodecKeyValue[K, FV, TV],
    WrapperBatchedKeyValue[K, FV],
    ta.Generic[K, FV, TV]
):

    def get_item_batch(self, keys: ta.Iterable[FK], default: VOrNotSet = NOT_SET) -> ta.Iterable[V]:
        return map(self._codec.decode, super().get_item_batch(keys, default))

    def set_item_batch(self, items: ta.Iterable[ta.Tuple[FK, V]]) -> None:
        super().set_item_batch((key, self._codec.enode(value)) for key, value in items)


class ValueCodecIterableKeyValue(
    ValueCodecKeyValue[K, FV, TV],
    WrapperIterableKeyValue[K, FV],
    ta.Generic[K, FV, TV]
):
    pass


class ValueCodecBatchedIterableKeyValue(
    ValueCodecBatchedKeyValue[K, FV, TV],
    ValueCodecIterableKeyValue[K, FV, TV],
    WrapperBatchedIterableKeyValue[K, FV],
    ta.Generic[K, FV, TV]
):
    pass


class ValueCodecSortedIterableKeyValue(
    ValueCodecIterableKeyValue[K, FV, TV],
    WrapperSortedIterableKeyValue[K, FV],
    ta.Generic[K, FV, TV]
):
    pass


class ValueCodecBatchedSortedIterableKeyValue(
    ValueCodecBatchedIterableKeyValue[K, FV, TV],
    ValueCodecSortedIterableKeyValue[K, FV, TV],
    WrapperBatchedSortedIterableKeyValue[K, FV],
    ta.Generic[K, FV, TV]
):
    pass
