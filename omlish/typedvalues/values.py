import typing as ta

from .. import dataclasses as dc
from .. import lang


T = ta.TypeVar('T')


##


class TypedValue(lang.Abstract):
    def __bool__(self) -> ta.NoReturn:
        raise TypeError(f"Cannot convert {self!r} to bool - use '.v' or 'is not None'.")


##


_UNIQUE_BASES: set[type[TypedValue]] = set()


class UniqueTypedValue(TypedValue, lang.Abstract):
    _unique_typed_value_cls: ta.ClassVar[type[TypedValue]]

    def __init_subclass__(cls, **kwargs: ta.Any) -> None:
        super().__init_subclass__(**kwargs)

        if any(ur in cls.__bases__ for ur in _UNIQUE_BASES):
            try:
                cls._unique_typed_value_cls  # noqa
            except AttributeError:
                cls._unique_typed_value_cls = cls
            else:
                raise TypeError(f'Class already has _unique_typed_value_cls: {cls}')


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


_UNIQUE_BASES.update([
    UniqueTypedValue,
    UniqueScalarTypedValue,
])
