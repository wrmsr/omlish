import dataclasses as dc


class _VirtualMeta(type):

    def __subclasscheck__(cls, subclass):
        return dc.is_dataclass(subclass)

    def __instancecheck__(cls, instance):
        return dc.is_dataclass(instance)


class Virtual(metaclass=_VirtualMeta):

    def __new__(cls, *args, **kwargs):
        raise TypeError

    def __init_subclass__(cls, **kwargs):
        raise TypeError
