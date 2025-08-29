import threading
import typing as ta

from .. import lang
from .base.registries import Registry
from .base.registries import RegistryItem
from .base.types import MarshalerFactory
from .base.types import Marshaling
from .base.types import UnmarshalerFactory
from .base.values import Value
from .standard import new_standard_marshaler_factory
from .standard import new_standard_unmarshaler_factory


T = ta.TypeVar('T')


##


_GLOBAL_LOCK = threading.RLock()


@lang.cached_function(lock=_GLOBAL_LOCK)
def global_registry() -> Registry:
    return Registry(lock=_GLOBAL_LOCK)


@lang.cached_function(lock=_GLOBAL_LOCK)
def global_marshaler_factory() -> MarshalerFactory:
    return new_standard_marshaler_factory()


@lang.cached_function(lock=_GLOBAL_LOCK)
def global_unmarshaler_factory() -> UnmarshalerFactory:
    return new_standard_unmarshaler_factory()


class _GlobalMarshaling(Marshaling):
    def registry(self) -> Registry:
        return global_registry()

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


def register_global(
        key: ta.Any,
        *items: RegistryItem,
        identity: bool = False,
) -> None:
    global_registry().register(
        key,
        *items,
        identity=identity,
    )
