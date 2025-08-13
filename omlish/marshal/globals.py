import typing as ta

from .. import lang
from .base import MarshalContext
from .base import MarshalerFactory
from .base import UnmarshalContext
from .base import UnmarshalerFactory
from .registries import Registry
from .registries import RegistryItem
from .standard import new_standard_marshaler_factory
from .standard import new_standard_unmarshaler_factory
from .values import Value


T = ta.TypeVar('T')


##


GLOBAL_REGISTRY: Registry = Registry()


##


@lang.cached_function(lock=True)
def global_marshaler_factory() -> MarshalerFactory:
    return new_standard_marshaler_factory()


def marshal(obj: ta.Any, ty: ta.Any | None = None, **kwargs: ta.Any) -> Value:
    return MarshalContext(
        GLOBAL_REGISTRY,
        factory=global_marshaler_factory(),
        **kwargs,
    ).marshal(obj, ty)


##


@lang.cached_function(lock=True)
def global_unmarshaler_factory() -> UnmarshalerFactory:
    return new_standard_unmarshaler_factory()


@ta.overload
def unmarshal(v: Value, ty: type[T], **kwargs: ta.Any) -> T:
    ...


@ta.overload
def unmarshal(v: Value, ty: ta.Any, **kwargs: ta.Any) -> ta.Any:
    ...


def unmarshal(v, ty, **kwargs):
    return UnmarshalContext(
        GLOBAL_REGISTRY,
        factory=global_unmarshaler_factory(),
        **kwargs,
    ).unmarshal(v, ty)


##


def register_global(
        key: ta.Any,
        *items: RegistryItem,
        identity: bool = False,
) -> None:
    GLOBAL_REGISTRY.register(
        key,
        *items,
        identity=identity,
    )
