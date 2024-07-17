import typing as ta

from .base import MarshalContext
from .base import UnmarshalContext
from .registries import Registry
from .standard import new_standard_marshaler_factory
from .standard import new_standard_unmarshaler_factory
from .values import Value


T = ta.TypeVar('T')


##


GLOBAL_REGISTRY = Registry()


##


GLOBAL_MARSHALER_FACTORY = new_standard_marshaler_factory()


def marshal(obj: ta.Any, ty: type | None = None, **kwargs: ta.Any) -> Value:
    mc = MarshalContext(GLOBAL_REGISTRY, factory=GLOBAL_MARSHALER_FACTORY, **kwargs)
    return mc.make(ty if ty is not None else type(obj)).marshal(mc, obj)


##


GLOBAL_UNMARSHALER_FACTORY = new_standard_unmarshaler_factory()


def unmarshal(v: Value, ty: type[T], **kwargs: ta.Any) -> T:
    uc = UnmarshalContext(GLOBAL_REGISTRY, factory=GLOBAL_UNMARSHALER_FACTORY, **kwargs)
    return uc.make(ty).unmarshal(uc, v)
