"""
TODO:
 - further decomp?
  - Sized + Iterable?
  - COM-style QueryInterface? :|
 - OpKv
 - table ala guava - (row key, column key) keys, sparse storage
 - router
 - value thunker idiom - for key-iterable-only storage, transform Kv[K, V], to Kv[K, ta.Callable[[], V]]
 - zict classes
  - AsyncBuffer
  - Buffer
  - Cache
  - File
  - Func
  - LMDB
  - LRU
  - Sieve
  - Zip
"""
import abc
import typing as ta

from ... import lang


K = ta.TypeVar('K')
V = ta.TypeVar('V')


##


class Kv(lang.Abstract, ta.Generic[K, V]):
    @abc.abstractmethod
    def __getitem__(self, k: K, /) -> V:
        raise NotImplementedError

    @abc.abstractmethod
    def __len__(self) -> int:
        raise NotImplementedError

    @abc.abstractmethod
    def items(self) -> ta.Iterator[tuple[K, V]]:
        raise NotImplementedError


class MutableKv(Kv[K, V], lang.Abstract):
    @abc.abstractmethod
    def __setitem__(self, k: K, v: V, /) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def __delitem__(self, k: K, /) -> None:
        raise NotImplementedError
