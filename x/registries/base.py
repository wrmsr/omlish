"""
TODO:
 - Generic
 - impls:
  - cached
  - dict
  - composite
  - weak
  - mro
   - method
  - multi
  - mutable
   - cache buster?
   - versioning
   - locked?
   - listeners
 - note diffs to dispatch
 - lookup -> Lookup?
  - tracks provenance
 - not a Mapping? class RegistryMapping?
 - all are multi?
 - TypeMap wrapper - just casts to spit out K=type[T] V=T
 - metadata?
  - on all Regs?
  - on RegistryLookup's?
  - MetadataWrappingRegistry? takes ownership?
  - lotsa ways..
"""
import abc
import dataclasses as dc
import typing as ta

from omlish import lang


K = ta.TypeVar('K')
V = ta.TypeVar('V')


##


class RegistryError(Exception):
    pass


@dc.dataclass()
class KeyRegistryError(RegistryError, ta.Generic[K]):
    k: K


@dc.dataclass()
class KeyNotRegisteredError(KeyRegistryError[K]):
    pass


@dc.dataclass()
class DuplicateKeyRegisteredError(KeyRegistryError[K], ta.Generic[K, V]):
    xs: ta.Sequence['RegistryLookup[K, V]'] | None = None


@dc.dataclass(frozen=True)
class RegistryLookup(lang.Final, ta.Generic[K, V]):
    v: V
    r: 'Registry[K, V]'


#


class Registry(lang.Abstract, ta.Generic[K, V]):  # noqa
    @abc.abstractmethod
    def __getitem__(self, k: K, /) -> ta.Iterator[RegistryLookup[K, V]]:
        raise NotImplementedError

    @abc.abstractmethod
    def __iter__(self) -> ta.Iterator[tuple[K, RegistryLookup[K, V]]]:
        raise NotImplementedError

    #

    @property
    def children(self) -> ta.Sequence['Registry[K, V]']:
        return ()

    #

    def values(self, k: K) -> ta.Iterator[V]:
        for x in self[k]:
            yield x.v

    #

    def __len__(self) -> int:
        i = 0
        for _ in self:
            i += 1
        return i

    #

    _NOT_SET: ta.ClassVar[ta.Any] = object()

    @ta.overload
    def unique(self, k: K) -> RegistryLookup[K, V]:
        ...

    @ta.overload
    def unique(self, k: K, default: V) -> RegistryLookup[K, V]:
        ...

    def unique(self, k, default=_NOT_SET):
        r: ta.Any = self._NOT_SET
        for x in self[k]:
            if r is self._NOT_SET:
                r = x
            else:
                raise DuplicateKeyRegisteredError(k, (r, x))
        if r is not self._NOT_SET:
            return r
        if default is not self._NOT_SET:
            return default
        raise KeyNotRegisteredError(k)

    @ta.overload
    def unique_value(self, k: K) -> V:
        ...

    @ta.overload
    def unique_value(self, k: K, default: V) -> V:
        ...

    def unique_value(self, k, default=_NOT_SET):
        return self.unique(k, default).v
