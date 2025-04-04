import typing as ta

from .. import dataclasses as dc
from .. import lang


T = ta.TypeVar('T')


##


class TypedValue(lang.Abstract):
    pass


##


class UniqueTypedValue(TypedValue, lang.Abstract):
    _unique_typed_value_cls: ta.ClassVar[type[TypedValue]]

    def __init_subclass__(cls, **kwargs: ta.Any) -> None:
        super().__init_subclass__(**kwargs)

        if UniqueTypedValue in cls.__bases__:
            try:
                cls._unique_typed_value_cls  # noqa
            except AttributeError:
                cls._unique_typed_value_cls = cls
            else:
                raise TypeError(f'Class already has _unique_typed_value_cls: {cls}')


##


@dc.dataclass(frozen=True)
@dc.extra_params(generic_init=True)
class ScalarTypedValue(TypedValue, lang.Abstract, ta.Generic[T]):
    v: T

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({self.v!r})'

    def __init_subclass__(cls, **kwargs: ta.Any) -> None:
        super().__init_subclass__(**kwargs)

        if UniqueTypedValue in (mro := cls.__mro__) and mro.index(ScalarTypedValue) > mro.index(UniqueTypedValue):
            raise TypeError(f'Class {cls} must have UniqueTypedValue before ScalarTypedValue in mro')
