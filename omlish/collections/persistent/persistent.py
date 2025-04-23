import abc
import typing as ta

from ... import lang


K = ta.TypeVar('K')
V = ta.TypeVar('V')


##


class PersistentMap(lang.Abstract, ta.Generic[K, V]):
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
    def __iter__(self) -> ta.Iterator[K]:
        raise NotImplementedError

    @abc.abstractmethod
    def items(self) -> ta.Iterator[tuple[K, V]]:
        raise NotImplementedError

    @abc.abstractmethod
    def with_(self, k: K, v: V) -> ta.Self:
        raise NotImplementedError

    @abc.abstractmethod
    def without(self, k: K) -> ta.Self:
        raise NotImplementedError

    @abc.abstractmethod
    def default(self, k: K, v: V) -> ta.Self:
        raise NotImplementedError


class PersistentMapping(
    PersistentMap[K, V],
    ta.Mapping[K, V],
    lang.Abstract,
    ta.Generic[K, V],
):
    @abc.abstractmethod
    def __contains__(self, item: K) -> bool:  # type: ignore[override]
        raise NotImplementedError

    @abc.abstractmethod
    def items(self) -> ta.Iterator[tuple[K, V]]:  # type: ignore[override]  # FIXME: ItemsView
        raise NotImplementedError
