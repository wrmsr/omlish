import typing as ta

from .. import lang
from .base import MarshalContext
from .base import MarshalerFactory
from .base import UnmarshalContext
from .base import UnmarshalerFactory
from .registries import Registry
from .standard import new_standard_marshaler_factory
from .standard import new_standard_unmarshaler_factory
from .values import Value


T = ta.TypeVar('T')


##


GLOBAL_REGISTRY = Registry()


##


@lang.cached_function(lock=True)
def global_marshaler_factory() -> MarshalerFactory:
    return new_standard_marshaler_factory()


def marshal(obj: ta.Any, ty: type | None = None, **kwargs: ta.Any) -> Value:
    mc = MarshalContext(GLOBAL_REGISTRY, factory=global_marshaler_factory(), **kwargs)
    return mc.make(ty if ty is not None else type(obj)).marshal(mc, obj)


##


@lang.cached_function(lock=True)
def global_unmarshaler_factory() -> UnmarshalerFactory:
    return new_standard_unmarshaler_factory()


def unmarshal(v: Value, ty: type[T], **kwargs: ta.Any) -> T:
    uc = UnmarshalContext(GLOBAL_REGISTRY, factory=global_unmarshaler_factory(), **kwargs)
    return uc.make(ty).unmarshal(uc, v)
