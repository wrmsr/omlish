# type: ignore
# ruff: noqa
# flake8: noqa
# @omlish-generated
import dataclasses
import types


def _transform_dataclass(
        *,
        __dataclass__cls,
        __dataclass__init__fields__0__annotation,
        __dataclass__init__fields__1__annotation,
        __dataclass__isinstance=isinstance,  # noqa
        __dataclass__None=None,  # noqa
        __dataclass__property=property,  # noqa
        __dataclass__object_setattr=object.__setattr__,  # noqa
        __dataclass__FrozenInstanceError=dataclasses.FrozenInstanceError,  # noqa
        __dataclass__HAS_DEFAULT_FACTORY=dataclasses._HAS_DEFAULT_FACTORY,  # noqa
        __dataclass__MISSING=dataclasses.MISSING,  # noqa
        __dataclass__FunctionType=types.FunctionType,  # noqa
        __dataclass__FieldFnValidationError,  # noqa
        __dataclass__FieldTypeValidationError,  # noqa
        __dataclass__FnValidationError,  # noqa
):
    def __copy__(self):
        if self.__class__ is not __dataclass__cls:
            raise TypeError(self)
        return __dataclass__cls(  # noqa
            x=self.x,
            y=self.y,
        )

    __copy__.__qualname__ = f"{__dataclass__cls.__qualname__}.__copy__"
    if '__copy__' in __dataclass__cls.__dict__:
        raise AttributeError('__copy__')
    setattr(__dataclass__cls, '__copy__', __copy__)

    def __eq__(self, other):
        if self is other:
            return True
        if self.__class__ is not other.__class__:
            return NotImplemented
        return (
                self.x == other.x and
                self.y == other.y
        )

    __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
    if '__eq__' in __dataclass__cls.__dict__:
        raise AttributeError('__eq__')
    setattr(__dataclass__cls, '__eq__', __eq__)

    setattr(__dataclass__cls, '__hash__', None)

    def __init__(
            __dataclass__self,
            x: __dataclass__init__fields__0__annotation,
            y: __dataclass__init__fields__1__annotation,
    ) -> __dataclass__None:
        __dataclass__self.x = x
        __dataclass__self.y = y

    __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
    if '__init__' in __dataclass__cls.__dict__:
        raise AttributeError('__init__')
    setattr(__dataclass__cls, '__init__', __init__)

    def __repr__(self):
        parts = []
        parts.append(f"x={self.x!r}")
        parts.append(f"y={self.y!r}")
        return (
            f"{self.__class__.__qualname__}("
            f"{', '.join(parts)}"
            f")"
        )

    __repr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__repr__"
    if '__repr__' in __dataclass__cls.__dict__:
        raise AttributeError('__repr__')
    setattr(__dataclass__cls, '__repr__', __repr__)
