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


class TypedValueContainer(
    TypedValuesAccessor[TypedValueT],
    TypedValueGeneric[TypedValueT],
    lang.Abstract,
):
    @property
    @abc.abstractmethod
    def _typed_values(self) -> TypedValues[TypedValueT] | None:
        raise NotImplementedError

    #

    def _typed_value_contains(self, cls):
        if (tvs := self._typed_values) is not None:
            return cls in tvs
        return False

    def _typed_value_getitem(self, key):
        if (tvs := self._typed_values) is not None:
            return tvs[key]
        if isinstance(key, int):
            raise IndexError(key)
        elif isinstance(key, type):
            raise KeyError(key)
        else:
            raise TypeError(key)

    def _typed_value_get(self, key, /, default=None):
        if (tvs := self._typed_values) is not None:
            return tvs.get(key, default)
        check.issubclass(key, TypedValue)
        if issubclass(key, UniqueTypedValue):
            return default
        elif default is not None:
            return list(default)
        else:
            return []

    def _typed_value_get_any(self, cls):
        if (tvs := self._typed_values) is not None:
            return tvs.get_any(cls)
        return []
