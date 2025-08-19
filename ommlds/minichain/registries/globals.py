"""
TODO:
 - queue register_types + late load manifests ? less urgent than late loading marshal lol
"""
import os
import typing as ta

from omlish import cached
from omlish import check
from omlish import lang
from omlish.manifests.globals import GlobalManifestLoader

from .manifests import RegistryManifest
from .manifests import RegistryTypeManifest
from .registry import Registry


T = ta.TypeVar('T')
U = ta.TypeVar('U')


##


def _load_manifests(cls: type[T]) -> ta.Sequence[T]:
    ldr = GlobalManifestLoader.instance()
    pkgs = ldr.scan_or_discover_packages(fallback_root_dir=os.getcwd())  # FIXME
    mfs = ldr.load(*pkgs, only=[cls])
    return [mf.value() for mf in mfs]


@cached.function
def _load_registry_type_manifests() -> ta.Sequence[RegistryTypeManifest]:
    return _load_manifests(RegistryTypeManifest)


@cached.function
def _load_registry_manifests() -> ta.Sequence[RegistryManifest]:
    return _load_manifests(RegistryManifest)


@cached.function(lock=True)
def _registry() -> Registry:
    return Registry(
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


@ta.overload
def registry_new(cls: type[T], name: str, *args: ta.Any, **kwargs: ta.Any) -> T:
    ...


@ta.overload
def registry_new(cls: ta.Any, name: str, *args: ta.Any, **kwargs: ta.Any) -> ta.Any:
    ...


def registry_new(cls, name, *args, **kwargs):
    be_cls = _registry().get_registry_cls(cls, name)
    if isinstance(cls, type):
        be_cls = check.issubclass(be_cls, cls)  # noqa
    return be_cls(*args, **kwargs)


#


class _RegistryOf(lang.BindableClass[T]):  # noqa
    @classmethod
    def new(cls, name: str, *args: ta.Any, **kwargs: ta.Any) -> T:  # noqa
        return registry_new(check.not_none(cls._bound), name, *args, **kwargs)


registry_of = _RegistryOf
