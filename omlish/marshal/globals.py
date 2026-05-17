import threading
import typing as ta

from .. import lang
from .api.configs import Config
from .api.configs import ConfigRegistry
from .api.internalstate import InternalState
from .api.options import Option
from .api.types import MarshalerFactory
from .api.types import Marshaling
from .api.types import UnmarshalerFactory
from .api.values import Value
from .factories.api import LazyInit
from .factories.api import LazyInitFn
from .factories.api import ModuleImport


if ta.TYPE_CHECKING:
    from .standard import factories as _sf
else:
    _sf = lang.proxy_import('.standard.factories', __package__)


T = ta.TypeVar('T')


##


_GLOBAL_LOCK = threading.RLock()


@lang.cached_function(lock=_GLOBAL_LOCK)
def global_config_registry() -> ConfigRegistry:
    return ConfigRegistry(lock=_GLOBAL_LOCK)


@lang.cached_function(lock=_GLOBAL_LOCK)
def global_internal_state() -> InternalState:
    return InternalState()


@lang.cached_function(lock=_GLOBAL_LOCK)
def global_marshaler_factory() -> MarshalerFactory:
    return _sf.new_standard_marshaler_factory()


@lang.cached_function(lock=_GLOBAL_LOCK)
def global_unmarshaler_factory() -> UnmarshalerFactory:
    return _sf.new_standard_unmarshaler_factory()


class _GlobalMarshaling(Marshaling, lang.Final):
    def get_config_registry(self) -> ConfigRegistry:
        return global_config_registry()

    def get_internal_state(self) -> InternalState:
        return global_internal_state()

    def get_marshaler_factory(self) -> MarshalerFactory:
        return global_marshaler_factory()

    def get_unmarshaler_factory(self) -> UnmarshalerFactory:
        return global_unmarshaler_factory()


@lang.cached_function(lock=_GLOBAL_LOCK)
def global_marshaling() -> Marshaling:
    return _GlobalMarshaling()


##


def marshal(
        obj: ta.Any,
        ty: ta.Any | None = None,
        *options: Option,
) -> Value:
    return global_marshaling().marshal(obj, ty, *options)


@ta.overload
def unmarshal(
        v: Value,
        ty: type[T],
        *options: Option,
) -> T:
    ...


@ta.overload
def unmarshal(
        v: Value,
        ty: ta.Any,
        *options: Option,
) -> ta.Any:
    ...


def unmarshal(v, ty, *options):
    return global_marshaling().unmarshal(v, ty, *options)


##


def register_global_lazy_init(
        fn: LazyInitFn,
) -> None:
    global_config_registry().update(
        None,
        LazyInit(fn),
    )


def register_global_module_import(
        name: str,
        package: str | None = None,
) -> None:
    global_config_registry().update(
        None,
        LazyInit(ModuleImport(name, package)),
    )
