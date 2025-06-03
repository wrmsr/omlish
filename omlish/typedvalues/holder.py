import abc
import typing as ta

from .. import lang
from .accessor import TypedValuesAccessor
from .collection import TypedValues
from .generic import TypedValueGeneric
from .values import TypedValue


TypedValueT1 = ta.TypeVar('TypedValueT1', bound=TypedValue)


##


class TypedValueHolder(
    TypedValuesAccessor[TypedValueT1],
    TypedValueGeneric[TypedValueT1],
    lang.Abstract,
):
    @property
    @abc.abstractmethod
    def _typed_values(self) -> TypedValues[TypedValueT1] | None:
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

    def _typed_value_get_any(self, cls):
        if (tvs := self._typed_values) is not None:
            return tvs.get_any(cls)
        return []
