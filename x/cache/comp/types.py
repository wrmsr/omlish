import abc
import typing as ta

from omlish import collections as col
from omlish import dataclasses as dc
from omlish import lang


T = ta.TypeVar('T')

CacheableVersion: ta.TypeAlias = ta.Hashable
CacheableVersionMap: ta.TypeAlias = col.frozendict['CacheableName', CacheableVersion]

CacheableNameT = ta.TypeVar('CacheableNameT', bound='CacheableName')


class CacheableName(lang.Abstract):
    pass


class Cacheable(lang.Abstract):
    @property
    @abc.abstractmethod
    def name(self) -> CacheableName:
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def version(self) -> CacheableVersion:
        raise NotImplementedError


class CacheableResolver(lang.Abstract):
    @abc.abstractmethod
    def resolve(self, name: CacheableName) -> Cacheable:
        raise NotImplementedError


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
    value: T
