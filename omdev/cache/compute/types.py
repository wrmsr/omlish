import abc
import typing as ta

from omlish import cached
from omlish import collections as col
from omlish import dataclasses as dc
from omlish import lang


T = ta.TypeVar('T')


##


NameT = ta.TypeVar('NameT', bound='Name')


class Name(lang.Abstract):
    pass


##


Version: ta.TypeAlias = ta.Hashable


def version(**kwargs: Version) -> Version:
    return col.frozendict(**kwargs)


VersionMap: ta.TypeAlias = col.frozendict[Name, Version]


def merge_version_maps(
        *dcts: ta.Mapping[Name, Version],
) -> VersionMap:
    out: dict[Name, Version] = {}
    for dct in dcts:
        for name, version in dct.items():
            try:
                ex = out[name]
            except KeyError:
                out[name] = version
            else:
                if ex != version:
                    raise Exception(f'Version mismatch: {ex} {version}')
    return col.frozendict(out)


##


Metadata: ta.TypeAlias = ta.Mapping[str, ta.Any]  # *not* hashed - advisory


class Object(lang.Abstract):
    @property
    @abc.abstractmethod
    def name(self) -> Name:
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def version(self) -> Version:
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def dependencies(self) -> ta.AbstractSet[Name]:
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def passive(self) -> bool:
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def metadata(self) -> Metadata:
        raise NotImplementedError

    @cached.property
    def as_version_map(self) -> VersionMap:
        return col.frozendict({self.name: self.version})


##


@dc.dataclass(frozen=True)
@dc.extra_class_params(cache_hash=True)
class CacheKey(lang.Abstract, ta.Generic[NameT]):
    name: NameT

    @dc.validate
    def _check_types(self) -> bool:
        hash(self)
        return isinstance(self.name, Name)


@dc.dataclass(frozen=True)
class CacheResult(lang.Final, ta.Generic[T]):
    hit: bool
    versions: VersionMap
    value: T


##


class ObjectResolver(lang.Abstract):
    @abc.abstractmethod
    def resolve(self, name: Name) -> Object:
        raise NotImplementedError


##


@dc.dataclass()
class CacheStats:
    num_hits: int = 0
    num_misses: int = 0
    num_invalidates: int = 0
    num_puts: int = 0


##


@dc.dataclass(frozen=True)
class CacheEntry:
    key: CacheKey
    versions: VersionMap
    value: ta.Any

    @dc.validate
    def _check_types(self) -> bool:
        return (
            isinstance(self.key, CacheKey) and
            isinstance(self.versions, col.frozendict)
        )
