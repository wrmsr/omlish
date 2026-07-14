import typing as ta

from .. import dataclasses as dc
from .values import _UNIQUE_BASES
from .values import TypedValue
from .values import UniqueTypedValue


T = ta.TypeVar('T')


##


class ScalarTypedValue(TypedValue, dc.Box[T], abstract=True):
    def __init_subclass__(cls, **kwargs: ta.Any) -> None:
        super().__init_subclass__(**kwargs)

        if UniqueTypedValue in (mro := cls.__mro__) and mro.index(ScalarTypedValue) > mro.index(UniqueTypedValue):
            raise TypeError(f'Class {cls} must not have UniqueTypedValue before ScalarTypedValue in mro')


##


class UniqueScalarTypedValue(ScalarTypedValue[T], UniqueTypedValue, abstract=True):
    pass


##


_UNIQUE_BASES.add(UniqueScalarTypedValue)
