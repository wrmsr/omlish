"""
TODO:
 - weak children if not in debug?
"""
import abc
import typing as ta

from omlish import check
from omlish import collections as col
from omlish import lang

from .types import CacheKey
from .types import CacheResult
from .types import Object
from .types import VersionMap
from .types import merge_version_maps


##


class Context(lang.Abstract, lang.Sealed):
    def __init__(
            self,
            obj: Object,
            *,
            dependencies: VersionMap = col.frozendict(),
            parent: ta.Optional['Context'] = None,
    ) -> None:
        super().__init__()

        self._obj = obj
        self._dependencies = dependencies
        self._parent = parent

        check.equal(set(dependencies), set(obj.dependencies))

        self._result: CacheResult | None = None
        self._children: list[Context] = []

        if parent is not None:
            check.state(not parent.done)
            parent._children.append(self)  # noqa

    #

    @property
    def object(self) -> Object:
        return self._obj

    @property
    def dependencies(self) -> VersionMap:
        return self._dependencies

    @property
    def parent(self) -> ta.Optional['Context']:
        return self._parent

    @property
    def children(self) -> ta.Sequence['Context']:
        return self._children

    @property
    @abc.abstractmethod
    def done(self) -> bool:
        raise NotImplementedError

    @lang.cached_function
    @ta.final
    def versions(self) -> VersionMap:
        check.state(self.done)
        return merge_version_maps(
            self._obj.as_version_map,
            self._dependencies,
            self._impl_versions(),
            *[c.versions() for c in self._children],
        )

    @abc.abstractmethod
    def _impl_versions(self) -> VersionMap:
        raise NotImplementedError


class ActiveContext(Context, lang.Final):
    def __init__(self, obj: Object, key: CacheKey, **kwargs: ta.Any) -> None:
        check.arg(not obj.passive)

        super().__init__(obj, **kwargs)

        self._key = key

        self._result: CacheResult | None = None

    @property
    def key(self) -> CacheKey:
        return self._key

    @property
    def done(self) -> bool:
        return self._result is not None

    def set_hit(self, result: CacheResult) -> None:
        check.state(result.hit)
        self._result = check.replacing_none(self._result, result)
        self.versions()

    def set_miss(self, val: ta.Any) -> None:
        self._result = check.replacing_none(self._result, CacheResult(
            False,
            VersionMap(),
            val,
        ))
        self.versions()

    def _impl_versions(self) -> VersionMap:
        return check.not_none(self._result).versions


class PassiveContext(Context, lang.Final):
    def __init__(self, obj: Object, **kwargs: ta.Any) -> None:
        check.arg(obj.passive)

        super().__init__(obj, **kwargs)

        self._done = False

    @property
    def done(self) -> bool:
        return self._done

    def finish(self) -> None:
        check.state(not self._done)
        self._done = True

    @lang.cached_function
    def _impl_versions(self) -> VersionMap:
        return col.frozendict()
