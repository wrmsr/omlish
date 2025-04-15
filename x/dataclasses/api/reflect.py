"""
TODO:
 - mutate dataclasses by default, installing reflected ClassSpec
"""
from ..specs import ClassSpec
from .classes.params import get_class_spec


##


class ClassReflection:
    def __init__(self, spec: ClassSpec) -> None:
        super().__init__()

        self._spec = spec

    @property
    def spec(self) -> ClassSpec:
        return self._spec


def reflect(cls: type) -> ClassReflection:
    if (cs := get_class_spec(cls)) is not None:
        return ClassReflection(cs)

    raise NotImplementedError
