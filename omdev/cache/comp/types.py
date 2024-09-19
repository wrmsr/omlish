import abc
import typing as ta

from omlish import cached
from omlish import collections as col
from omlish import dataclasses as dc
from omlish import lang


T = ta.TypeVar('T')


##


CacheableNameT = ta.TypeVar('CacheableNameT', bound='CacheableName')


class CacheableName(lang.Abstract):
    pass


##


CacheableVersion: ta.TypeAlias = ta.Hashable
CacheableVersionMap: ta.TypeAlias = col.frozendict['CacheableName', CacheableVersion]


def merge_version_maps(
        *dcts: ta.Mapping[CacheableName, CacheableVersion],
) -> CacheableVersionMap:
    out: dict[CacheableName, CacheableVersion] = {}
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


class Cacheable(lang.Abstract):
    @property
    @abc.abstractmethod
    def name(self) -> CacheableName:
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def version(self) -> CacheableVersion:
        raise NotImplementedError

    @cached.property
    def as_version_map(self) -> CacheableVersionMap:
        return col.frozendict({self.name: self.version})


##


@dc.dataclass(frozen=True)
@dc.extra_params(cache_hash=True)
class CacheKey(lang.Abstract, ta.Generic[CacheableNameT]):
    name: CacheableNameT

    @dc.validate
    def _check_types(self) -> bool:
        hash(self)
        return isinstance(self.name, CacheableName)


@dc.dataclass(frozen=True)
class CacheResult(ta.Generic[T], lang.Final):
    hit: bool
    versions: CacheableVersionMap
    value: T


##


class CacheableResolver(lang.Abstract):
    @abc.abstractmethod
    def resolve(self, name: CacheableName) -> Cacheable:
        raise NotImplementedError
