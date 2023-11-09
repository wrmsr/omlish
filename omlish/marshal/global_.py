from .registries import Registry
from .standard import new_standard_marshaler_factory
from .base import MarshalContext
from .base import UnmarshalContext
from .standard import new_standard_unmarshaler_factory


##


GLOBAL_REGISTRY = Registry()


##


GLOBAL_MARSHALER_FACTORY = new_standard_marshaler_factory()


def marshal(obj, ty=None, **kwargs):
    mc = MarshalContext(GLOBAL_REGISTRY, factory=GLOBAL_MARSHALER_FACTORY, **kwargs)
    return mc.make(ty if ty is not None else type(obj)).marshal(mc, obj)


##


GLOBAL_UNMARSHALER_FACTORY = new_standard_unmarshaler_factory()


def unmarshal(v, ty, **kwargs):
    uc = UnmarshalContext(GLOBAL_REGISTRY, factory=GLOBAL_UNMARSHALER_FACTORY, **kwargs)
    return uc.make(ty).unmarshal(uc, v)
