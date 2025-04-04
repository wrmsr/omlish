import abc
import typing as ta

from .. import check
from .. import lang
from .accessor import TypedValuesAccessor
from .collection import TypedValues
from .generic import TypedValueGeneric
from .values import TypedValue
from .values import UniqueTypedValue


TypedValueT = ta.TypeVar('TypedValueT', bound='TypedValue')


##


class TypedValueHolder(
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
