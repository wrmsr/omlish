"""
TODO:
 - Accessor inputs/outputs should *ideally* be subtype of class generic param
  - but can't make a typevar with a bound of another typevar
"""
import abc
import typing as ta

from .. import check
from .. import lang
from .values import TypedValue  # noqa
from .values import UniqueTypedValue  # noqa


T = ta.TypeVar('T')

TypedValueT0 = ta.TypeVar('TypedValueT0', bound='TypedValue')
TypedValueU = ta.TypeVar('TypedValueU', bound='TypedValue')

UniqueTypedValueU = ta.TypeVar('UniqueTypedValueU', bound='UniqueTypedValue')


##


class _NOT_SET(lang.Marker):  # noqa
    pass


class TypedValuesAccessor(
    lang.Abstract,
    ta.Sequence[TypedValueT0],
    ta.Generic[TypedValueT0],
):
    def __iter__(self):
        raise TypeError(
            'TypedValuesAccessor does not implement __iter__ - it is reserved for implementation by subclasses.',
        )

    #

    @ta.final
    def __contains__(self, cls: type[TypedValueU]) -> bool:  # type: ignore[override]
        return self._typed_value_contains(cls)

    @abc.abstractmethod
    def _typed_value_contains(self, cls):
        raise NotImplementedError

    #

    @ta.overload  # type: ignore[override]
    def __getitem__(self, idx: int) -> TypedValueT0:
        ...

    @ta.overload
    def __getitem__(self, cls: type[UniqueTypedValueU]) -> UniqueTypedValueU:  # type: ignore[overload-overlap]
        ...

    @ta.overload
    def __getitem__(self, cls: type[TypedValueU]) -> ta.Sequence[TypedValueU]:
        ...

    @ta.final
    def __getitem__(self, key):
        return self._typed_value_getitem(key)

    @abc.abstractmethod
    def _typed_value_getitem(self, key):
        raise NotImplementedError

    #

    @ta.overload
    def get(
            self,
            tv: UniqueTypedValueU,
    ) -> UniqueTypedValueU:
        ...

    @ta.overload
    def get(
            self,
            cls: type[UniqueTypedValueU],
            /,
            default: UniqueTypedValueU,
    ) -> UniqueTypedValueU:
        ...

    @ta.overload
    def get(  # type: ignore[overload-overlap]
            self,
            cls: type[UniqueTypedValueU],
            /,
            default: None = None,
    ) -> UniqueTypedValueU | None:
        ...

    @ta.overload
    def get(
            self,
            cls: type[TypedValueU],
            /,
            default: ta.Iterable[TypedValueU] | None = None,
    ) -> ta.Sequence[TypedValueU]:
        ...

    @ta.final
    def get(self, key, /, default=_NOT_SET):
        if not isinstance(key, type):
            if default is not _NOT_SET:
                raise RuntimeError('Must not provide both an instance key and a default')
            default = key
            key = type(default)
        elif default is _NOT_SET:
            default = None

        check.issubclass(key, TypedValue)
        try:
            return self._typed_value_getitem(key)
        except KeyError:
            return default

    #

    @ta.final
    def get_any(self, cls: type[T] | tuple[type[T], ...]) -> ta.Sequence[T]:
        return self._typed_value_get_any(cls)

    @abc.abstractmethod
    def _typed_value_get_any(self, cls):
        raise NotImplementedError
