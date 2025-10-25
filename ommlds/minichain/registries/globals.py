"""
TODO:
 - queue register_types + late load manifests ? less urgent than late loading marshal lol
"""
import threading
import typing as ta

from omlish import check
from omlish import lang
from omlish.manifests.globals import GlobalManifestLoader

from .manifests import RegistryManifest
from .manifests import RegistryTypeManifest
from .registry import Registry


T = ta.TypeVar('T')
U = ta.TypeVar('U')


##


class _GlobalRegistry(lang.Final, lang.NotInstantiable):
    _lock: ta.ClassVar[threading.RLock] = threading.RLock()

    _instance: ta.ClassVar[Registry | None] = None

    @classmethod
    def instance(cls) -> Registry:
        if (i := cls._instance) is None:
            with cls._lock:
                if (i := cls._instance) is None:
                    i = cls._instance = cls._create_instance()
        return i

    @classmethod
    def _create_instance(cls) -> Registry:
        r = Registry(
            GlobalManifestLoader.load_values_of(RegistryTypeManifest),
            GlobalManifestLoader.load_values_of(RegistryManifest),
        )

        for qrt in check.not_none(cls._register_type_queue):
            r.register_type(
                qrt.cls,
                module=qrt.module,
            )
        cls._register_type_queue = None

        return r

    #

    class _QueuedRegisterType(ta.NamedTuple):
        cls: ta.Any
        module: str | None = None

    _register_type_queue: ta.ClassVar[list[_QueuedRegisterType] | None] = []

    @classmethod
    def register_type(
            cls,
            clz: T,
            *,
            module: str | None = None,
    ) -> None:
        with cls._lock:
            if (i := cls._instance) is not None:
                i.register_type(
                    clz,
                    module=module,
                )
            else:
                check.not_none(cls._register_type_queue).append(_GlobalRegistry._QueuedRegisterType(
                    clz,
                    module=module,
                ))


##


def get_global_registry() -> Registry:
    return _GlobalRegistry.instance()


def register_type(
        cls: T,
        *,
        module: str | None = None,
) -> T:
    _GlobalRegistry.register_type(
        cls,
        module=module,
    )
    return cls


@ta.overload
def get_registry_cls(cls: type[T], name: str) -> type[T]:
    ...


@ta.overload
def get_registry_cls(cls: ta.Any, name: str) -> ta.Any:
    ...


def get_registry_cls(cls, name, *args, **kwargs):
    be_cls = _GlobalRegistry.instance().get_registry_cls(cls, name)
    if isinstance(cls, type):
        be_cls = check.issubclass(be_cls, cls)  # noqa
    return be_cls


@ta.overload
def registry_new(cls: type[T], name: str, *args: ta.Any, **kwargs: ta.Any) -> T:
    ...


@ta.overload
def registry_new(cls: ta.Any, name: str, *args: ta.Any, **kwargs: ta.Any) -> ta.Any:
    ...


def registry_new(cls, name, *args, **kwargs):
    return get_registry_cls(cls, name)(*args, **kwargs)


#


class _RegistryOf(lang.BindableClass[T]):  # noqa
    @classmethod
    def new(cls, name: str, *args: ta.Any, **kwargs: ta.Any) -> T:  # noqa
        return registry_new(check.not_none(cls._bound), name, *args, **kwargs)


registry_of = _RegistryOf
