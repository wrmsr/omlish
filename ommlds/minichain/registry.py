"""
TODO:
 - queue register_types + late load manifests ? less urgent than late loading marshal lol
"""
import os
import threading
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
class RegistryTypeManifest(ModAttrManifest):
    pass


@dc.dataclass(frozen=True, kw_only=True)
class RegistryManifest(NameAliasesManifest, ModAttrManifest):
    type: str


##


def _load_manifests(cls: type[T]) -> ta.Sequence[T]:
    ldr = manifest_load.MANIFEST_LOADER
    pkgs = ldr.scan_or_discover_pkgs(fallback_root=os.getcwd())  # FIXME
    mfs = ldr.load(*pkgs, only=[cls])
    return [mf.value for mf in mfs]


@cached.function
def _load_registry_type_manifests() -> ta.Sequence[RegistryTypeManifest]:
    return _load_manifests(RegistryTypeManifest)


@cached.function
def _load_registry_manifests() -> ta.Sequence[RegistryManifest]:
    return _load_manifests(RegistryManifest)


##


class _Registry:
    def __init__(
            self,
            registry_type_manifests: ta.Iterable[RegistryTypeManifest],
            registry_manifests: ta.Iterable[RegistryManifest],
    ) -> None:
        super().__init__()

        self._lock = threading.RLock()

        self._registry_type_manifests = list(registry_type_manifests)
        self._registry_manifests = list(registry_manifests)

        self._registry_type_manifests_by_name = col.make_map(
            ((m.attr_name, m) for m in self._registry_type_manifests),
            strict=True,
        )
        # self._registry_type_manifests_by_module = col

        self._registry_manifests_by_name_by_type = {
            t: RegistryManifest.build_name_dict(l)
            for t, l in col.multi_map((m.type, m) for m in self._registry_manifests).items()
        }

        self._registry_type_cls_by_name: dict[str, type] = {}
        self._registry_cls_by_name_by_type: dict[str, dict[str, type]] = {}

    def register_type(
            self,
            cls: ta.Any,
            *,
            module: str | None = None,
    ) -> None:
        with self._lock:
            pass

    def get_registry_type_cls(self, name: str) -> type:
        with self._lock:
            try:
                return self._registry_type_cls_by_name[name]
            except KeyError:
                pass
            m = self._registry_type_manifests_by_name[name]
            cls = m.load()
            self._registry_type_cls_by_name[name] = cls
            return cls

    def get_registry_cls(self, type_name: str, name: str) -> type:
        with self._lock:
            try:
                d = self._registry_cls_by_name_by_type[type_name]
            except KeyError:
                d = self._registry_cls_by_name_by_type[type_name] = {}
            try:
                return d[name]
            except KeyError:
                pass
            m = self._registry_manifests_by_name_by_type[type_name][name]
            cls = m.load()
            d[name] = cls
            return cls


@cached.function(lock=True)
def _registry() -> _Registry:
    return _Registry(
        _load_registry_type_manifests(),
        _load_registry_manifests(),
    )


##


def register_type(
        cls: T,
        *,
        module: str | None = None,
) -> T:
    _registry().register_type(
        cls,
        module=module,
    )
    return cls


def registry_new(cls: type[T], name: str, *args: ta.Any, **kwargs: ta.Any) -> T:
    be_cls = _registry().get_registry_cls(cls.__name__, name)
    be_cls = check.issubclass(be_cls, cls)
    return be_cls(*args, **kwargs)


#


# PEP695 / https://github.com/python/mypy/issues/4717 workaround
class RegistryOf(ta.Generic[T]):  # noqa
    @dc.dataclass(frozen=True)
    class _Bound(ta.Generic[U]):  # noqa
        cls: type[U]

        def new(self, name: str, *args: ta.Any, **kwargs: ta.Any) -> U:
            return registry_new(self.cls, name, *args, **kwargs)

    def __class_getitem__(cls, *args, **kwargs):
        [bind_cls] = args
        return RegistryOf._Bound(bind_cls)

    @classmethod
    def new(cls, name: str, *args: ta.Any, **kwargs: ta.Any) -> T:  # noqa
        raise TypeError


registry_of = RegistryOf
