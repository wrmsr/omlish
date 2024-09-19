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
    def passive(self) -> bool:
        raise NotImplementedError

    @cached.property
    def as_version_map(self) -> VersionMap:
        return col.frozendict({self.name: self.version})


##


@dc.dataclass(frozen=True)
@dc.extra_params(cache_hash=True)
class CacheKey(lang.Abstract, ta.Generic[NameT]):
    name: NameT

    @dc.validate
    def _check_types(self) -> bool:
        hash(self)
        return isinstance(self.name, Name)


@dc.dataclass(frozen=True)
class CacheResult(ta.Generic[T], lang.Final):
    hit: bool
    versions: VersionMap
    value: T


##


class ObjectResolver(lang.Abstract):
    @abc.abstractmethod
    def resolve(self, name: Name) -> Object:
        raise NotImplementedError
