import abc
import typing as ta


K = ta.TypeVar('K')
V = ta.TypeVar('V')


##


class PersistentMap(ta.Generic[K, V], abc.ABC):
    @abc.abstractmethod
    def __len__(self) -> int:
        raise NotImplementedError

    @abc.abstractmethod
    def __contains__(self, item: K) -> bool:
        raise NotImplementedError

    @abc.abstractmethod
    def __getitem__(self, item: K) -> V:
        raise NotImplementedError

    @abc.abstractmethod
    def __iter__(self) -> ta.Iterator[tuple[K, V]]:
        raise NotImplementedError

    @abc.abstractmethod
    def with_(self, k: K, v: V) -> 'PersistentMap[K, V]':
        raise NotImplementedError

    @abc.abstractmethod
    def without(self, k: K) -> 'PersistentMap[K, V]':
        raise NotImplementedError

    @abc.abstractmethod
    def default(self, k: K, v: V) -> 'PersistentMap[K, V]':
        raise NotImplementedError
