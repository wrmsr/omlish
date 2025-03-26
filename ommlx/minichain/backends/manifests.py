import os
import typing as ta

from omlish import cached
from omlish import check
from omlish import collections as col
from omlish import dataclasses as dc
from omlish.manifests import load as manifest_load
from omlish.manifests.base import ModAttrManifest
from omlish.manifests.base import NameAliasesManifest


T = ta.TypeVar('T')
U = ta.TypeVar('U')


##


@dc.dataclass(frozen=True, kw_only=True)
class BackendTypeManifest(ModAttrManifest):
    pass


@dc.dataclass(frozen=True, kw_only=True)
class BackendManifest(NameAliasesManifest, ModAttrManifest):
    type: str


##


def _load_manifests(cls: type[T]) -> ta.Sequence[T]:
    ldr = manifest_load.MANIFEST_LOADER
    pkgs = ldr.scan_or_discover_pkgs(fallback_root=os.getcwd())  # FIXME
    mfs = ldr.load(*pkgs, only=[cls])
    return [mf.value for mf in mfs]


@cached.function
def _load_backend_type_manifests() -> ta.Sequence[BackendTypeManifest]:
    return _load_manifests(BackendTypeManifest)


@cached.function
def _load_backend_manifests() -> ta.Sequence[BackendManifest]:
    return _load_manifests(BackendManifest)


##


class _ManifestRegistry:
    def __init__(
            self,
            backend_type_manifests: ta.Iterable[BackendTypeManifest],
            backend_manifests: ta.Iterable[BackendManifest],
    ) -> None:
        super().__init__()

        self._backend_type_manifests = list(backend_type_manifests)
        self._backend_manifests = list(backend_manifests)

        self._backend_type_manifests_by_name = col.make_map(
            ((m.attr_name, m) for m in self._backend_type_manifests),
            strict=True,
        )

        self._backend_manifests_by_name_by_type = {
            t: BackendManifest.build_name_dict(l)
            for t, l in col.multi_map((m.type, m) for m in self._backend_manifests).items()
        }

        self._backend_type_cls_by_name: dict[str, type] = {}
        self._backend_cls_by_name_by_type: dict[str, dict[str, type]] = {}

    def get_backend_type_cls(self, name: str) -> type:
        try:
            return self._backend_type_cls_by_name[name]
        except KeyError:
            pass
        m = self._backend_type_manifests_by_name[name]
        cls = m.load()
        self._backend_type_cls_by_name[name] = cls
        return cls

    def get_backend_cls(self, type_name: str, name: str) -> type:
        try:
            d = self._backend_cls_by_name_by_type[type_name]
        except KeyError:
            d = self._backend_cls_by_name_by_type[type_name] = {}
        try:
            return d[name]
        except KeyError:
            pass
        m = self._backend_manifests_by_name_by_type[type_name][name]
        cls = m.load()
        d[name] = cls
        return cls


@cached.function(lock=True)
def _manifest_registry() -> _ManifestRegistry:
    return _ManifestRegistry(
        _load_backend_type_manifests(),
        _load_backend_manifests(),
    )


##


def new_backend(cls: type[T], name: str, **kwargs: ta.Any) -> T:
    mr = _manifest_registry()
    be_cls = mr.get_backend_cls(cls.__name__, name)
    be_cls = check.issubclass(be_cls, cls)
    return be_cls(**kwargs)


#


# PEP695 / https://github.com/python/mypy/issues/4717 workaround
class backend_of(ta.Generic[T]):  # noqa
    @dc.dataclass(frozen=True)
    class _bound(ta.Generic[U]):  # noqa
        cls: type[U]

        def new(self, name: str, **kwargs: ta.Any) -> U:
            return new_backend(self.cls, name, **kwargs)

    def __class_getitem__(cls, *args, **kwargs):
        [bind_cls] = args
        return backend_of._bound(bind_cls)

    @classmethod
    def new(cls, name: str, **kwargs: ta.Any) -> T:  # noqa
        raise TypeError
