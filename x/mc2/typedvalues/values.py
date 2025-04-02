import abc
import typing as ta

from omlish import check
from omlish import dataclasses as dc
from omlish import lang
from omlish import reflect as rfl


T = ta.TypeVar('T')

TypedValueT = ta.TypeVar('TypedValueT', bound='TypedValue')
TypedValueU = ta.TypeVar('TypedValueU', bound='TypedValue')

UniqueTypedValueU = ta.TypeVar('UniqueTypedValueU', bound='UniqueTypedValue')


##


class TypedValue(lang.Abstract):
    pass


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


@dc.dataclass(frozen=True)
@dc.extra_params(generic_init=True)
class ScalarTypedValue(TypedValue, lang.Abstract, ta.Generic[T]):
    v: T

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({self.v!r})'
