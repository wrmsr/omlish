import typing as ta

from omlish import check
from omlish import lang

from .types import CacheKey
from .types import CacheResult
from .types import Object
from .types import VersionMap
from .types import merge_version_maps


##


class Context(lang.Final):
    def __init__(
            self,
            obj: Object,
            key: CacheKey,
            *,
            parent: ta.Optional['Context'] = None,
    ) -> None:
        super().__init__()
        self._obj = obj
        self._key = key
        self._parent = parent

        self._result: CacheResult | None = None
        self._children: list[Context] = []

        if parent is not None:
            check.state(not parent.has_result)
            parent._children.append(self)  # noqa

    #

    @property
    def object(self) -> Object:
        return self._obj

    @property
    def key(self) -> CacheKey:
        return self._key

    @property
    def parent(self) -> ta.Optional['Context']:
        return self._parent

    @property
    def children(self) -> ta.Sequence['Context']:
        return self._children

    #

    @property
    def has_result(self) -> bool:
        return self._result is not None

    def result(self) -> CacheResult:
        return check.not_none(self._result)

    def set_hit(self, result: CacheResult) -> None:
        check.state(result.hit)
        self._result = check.replacing_none(self._result, result)
        self.result_versions()

    def set_miss(self, val: ta.Any) -> None:
        self._result = check.replacing_none(self._result, CacheResult(
            False,
            VersionMap(),
            val,
        ))
        self.result_versions()

    @lang.cached_function
    def result_versions(self) -> VersionMap:
        r = check.not_none(self._result)
        return merge_version_maps(
            self._obj.as_version_map,
            r.versions,
            *[c.result_versions() for c in self._children],
        )
