"""
TODO:
 - mutate dataclasses by default, installing reflected ClassSpec
"""
from ..specs import ClassSpec
from .classes.params import get_class_spec


##


def reflect(cls: type) -> ClassSpec:
    if (cs := get_class_spec(cls)) is not None:
        return cs

    raise NotImplementedError
