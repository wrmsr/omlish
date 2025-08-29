import threading
import typing as ta

from .. import lang
from .base.configs import Config
from .base.configs import ConfigRegistry
from .base.types import MarshalerFactory
from .base.types import Marshaling
from .base.types import UnmarshalerFactory
from .base.values import Value
from .factories.moduleimport.configs import ModuleImport


if ta.TYPE_CHECKING:
    from . import standard
else:
    standard = lang.proxy_import('.standard', __package__)


T = ta.TypeVar('T')


##


_GLOBAL_LOCK = threading.RLock()


@lang.cached_function(lock=_GLOBAL_LOCK)
def global_config_registry() -> ConfigRegistry:
    return ConfigRegistry(lock=_GLOBAL_LOCK)


@lang.cached_function(lock=_GLOBAL_LOCK)
def global_marshaler_factory() -> MarshalerFactory:
    return standard.new_standard_marshaler_factory()


@lang.cached_function(lock=_GLOBAL_LOCK)
def global_unmarshaler_factory() -> UnmarshalerFactory:
    return standard.new_standard_unmarshaler_factory()


class _GlobalMarshaling(Marshaling, lang.Final):
    def config_registry(self) -> ConfigRegistry:
        return global_config_registry()

    def marshaler_factory(self) -> MarshalerFactory:
        return global_marshaler_factory()

    def unmarshaler_factory(self) -> UnmarshalerFactory:
        return global_unmarshaler_factory()


@lang.cached_function(lock=_GLOBAL_LOCK)
def global_marshaling() -> Marshaling:
    return _GlobalMarshaling()


##


def marshal(obj: ta.Any, ty: ta.Any | None = None, **kwargs: ta.Any) -> Value:
    return global_marshaling().marshal(obj, ty, **kwargs)


@ta.overload
def unmarshal(v: Value, ty: type[T], **kwargs: ta.Any) -> T:
    ...


@ta.overload
def unmarshal(v: Value, ty: ta.Any, **kwargs: ta.Any) -> ta.Any:
    ...


def unmarshal(v, ty, **kwargs):
    return global_marshaling().unmarshal(v, ty, **kwargs)


##


def register_global_config(
        key: ta.Any,
        *items: Config,
        identity: bool = False,
) -> None:
    global_config_registry().register(
        key,
        *items,
        identity=identity,
    )


def register_global_module_import(
        name: str,
        package: str | None = None,
) -> None:
    global_config_registry().register(
        None,
        ModuleImport(name, package),
    )
