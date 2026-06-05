import abc
import typing as ta

from .. import lang


T = ta.TypeVar('T')
K = ta.TypeVar('K')
V = ta.TypeVar('V')


##


class PersistentSequence(ta.Sequence[T], lang.Abstract, ta.Generic[T]):
    @abc.abstractmethod
    def __len__(self) -> int:
        raise NotImplementedError

    @abc.abstractmethod
    def __iter__(self) -> ta.Iterator[T]:
        raise NotImplementedError

    @abc.abstractmethod
    def iter_from(self, idx: int) -> ta.Iterator[T]:
        raise NotImplementedError

    @ta.overload
    @abc.abstractmethod
    def __getitem__(self, item: int) -> T:
        raise NotImplementedError

    @ta.overload
    @abc.abstractmethod
    def __getitem__(self, item: slice) -> ta.Self:
        raise NotImplementedError

    @abc.abstractmethod
    def __getitem__(self, item):
        raise NotImplementedError

    @abc.abstractmethod
    def splice(
            self,
            start: int | None,
            stop: int | None,
            items: ta.Iterable[T],
    ) -> ta.Self:
        raise NotImplementedError

    @abc.abstractmethod
    def with_(self, idx: int, item: T) -> ta.Self:
        raise NotImplementedError

    @abc.abstractmethod
    def without(self, item: int | slice) -> ta.Self:
        raise NotImplementedError

    @abc.abstractmethod
    def append(self, item: T) -> ta.Self:
        raise NotImplementedError

    @abc.abstractmethod
    def extend(self, items: ta.Iterable[T]) -> ta.Self:
        raise NotImplementedError


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
    def iteritems(self) -> ta.Iterator[tuple[K, V]]:
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
